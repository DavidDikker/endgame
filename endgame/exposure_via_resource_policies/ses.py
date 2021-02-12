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


class SesIdentityPolicy(ResourceType, ABC):
    def __init__(self, name: str, region: str, client: boto3.Session.client, current_account_id: str):
        self.name = name
        self.service = "ses"
        self.resource_type = "identity"
        self.region = region
        self.current_account_id = current_account_id
        self.override_resource_block = self.arn
        super().__init__(name, self.resource_type, self.service, region, client, current_account_id,
                         override_resource_block=self.override_resource_block)
        self.identity_policy_names = self._identity_policy_names()

    @property
    def arn(self) -> str:
        return f"arn:aws:{self.service}:{self.region}:{self.current_account_id}:{self.resource_type}/{self.name}"

    def _identity_policy_names(self) -> list:
        try:
            response = self.client.list_identity_policies(Identity=self.name)
            # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ses.html#SES.Client.get_identity_policies
            policy_names = response.get("PolicyNames")
        except botocore.exceptions.ClientError:
            policy_names = []
        return policy_names

    def _get_rbp(self) -> ResponseGetRbp:
        """Get the resource based policy for this resource and store it"""
        # If you do not know the names of the policies that are attached to the identity, you can use ListIdentityPolicies
        logger.debug("Getting resource policy for %s" % self.arn)
        # When there is no policy, let's return an empty policy to avoid breaking things
        policy = constants.get_empty_policy()
        try:
            # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ses.html#SES.Client.list_identity_policies
            response = self.client.list_identity_policies(Identity=self.name)
            # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ses.html#SES.Client.get_identity_policies
            policy_names = response.get("PolicyNames")
            if policy_names:
                response = self.client.get_identity_policies(Identity=self.name, PolicyNames=policy_names)
                policies = response.get("Policies")
                if constants.SID_SIGNATURE in policies:
                    policy = json.loads(policies.get(constants.SID_SIGNATURE))
                success = True
            else:
                policy = constants.get_empty_policy()
                success = True
        except botocore.exceptions.ClientError:
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
        new_policy = json.dumps(evil_policy)
        try:
            self.client.put_identity_policy(Identity=self.arn, PolicyName=constants.SID_SIGNATURE, Policy=new_policy)
            # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ses.html#SES.Client.put_identity_policy
            message = "success"
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
        """Wraps client.delete_identity_policy"""
        logger.debug(f"Removing {evil_principal} from {self.arn}")
        new_policy = {
            "Version": "2012-10-17",
            "Statement": []
        }
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ses.html#SES.Client.delete_identity_policy
        operation = "UNDO"
        # Update the list of identity policies
        success = True
        if constants.SID_SIGNATURE in self._identity_policy_names():
            if not dry_run:
                try:
                    self.client.delete_identity_policy(
                        Identity=self.name,
                        PolicyName=constants.SID_SIGNATURE
                    )
                    message = f"200: Removed identity policy called {constants.SID_SIGNATURE} for identity {self.name}"
                    success = True
                except botocore.exceptions.ClientError as error:
                    success = False
                    message = error
                    logger.critical(f"Operation was not successful for {self.service} {self.resource_type} "
                                    f"{self.name}. %s" % error)
            else:
                message = f"202: Dry run: will remove identity policy called {constants.SID_SIGNATURE} for identity {self.name}"
        else:
            message = f"404: There is no policy titled {constants.SID_SIGNATURE} attached to {self.name}"
        response_message = ResponseMessage(message=message, operation=operation, success=success, evil_principal=evil_principal,
                                           victim_resource_arn=self.arn, original_policy=self.original_policy,
                                           updated_policy=new_policy, resource_type=self.resource_type,
                                           resource_name=self.name, service=self.service)
        return response_message


class SesIdentityPolicies(ResourceTypes):
    def __init__(self, client: boto3.Session.client, current_account_id: str, region: str):
        super().__init__(client, current_account_id, region)
        self.service = "ses"
        self.resource_type = "identity"

    @property
    def resources(self) -> [ListResourcesResponse]:
        """Get a list of these resources"""
        resources = []

        paginator = self.client.get_paginator("list_identities")
        page_iterator = paginator.paginate()
        for page in page_iterator:
            these_resources = page["Identities"]
            for resource in these_resources:
                arn = f"arn:aws:ses:{self.region}:{self.current_account_id}:identity/{resource}"
                list_resources_response = ListResourcesResponse(
                    service=self.service, account_id=self.current_account_id, arn=arn, region=self.region,
                    resource_type=self.resource_type, name=resource)
                resources.append(list_resources_response)
        return resources
