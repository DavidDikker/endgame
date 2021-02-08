import sys
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

    def _get_rbp(self) -> PolicyDocument:
        """Get the resource based policy for this resource and store it"""
        # If you do not know the names of the policies that are attached to the identity, you can use ListIdentityPolicies
        try:
            # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ses.html#SES.Client.list_identity_policies
            response = self.client.list_identity_policies(Identity=self.name)
            # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ses.html#SES.Client.get_identity_policies
            policy_names = response.get("PolicyNames")
            response = self.client.get_identity_policies(Identity=self.name, PolicyNames=policy_names)
            policies = response.get("Policies")
            if constants.SID_SIGNATURE in policies:
                policy = json.loads(policies.get(constants.SID_SIGNATURE))
            else:
                policy = constants.get_empty_policy()
        except botocore.exceptions.ClientError:
            # When there is no policy, let's return an empty policy to avoid breaking things
            policy = constants.get_empty_policy()
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
        new_policy = json.dumps(evil_policy)
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ses.html#SES.Client.put_identity_policy
        self.client.put_identity_policy(Identity=self.arn, PolicyName=constants.SID_SIGNATURE, Policy=new_policy)
        return evil_policy

    def undo(self, evil_principal: str, dry_run: bool = False) -> ResponseMessage:
        """Wraps client.delete_identity_policy"""
        new_policy = {
            "Version": "2012-10-17",
            "Statement": []
        }
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ses.html#SES.Client.delete_identity_policy
        operation = "UNDO"
        # Update the list of identity policies
        if constants.SID_SIGNATURE in self._identity_policy_names():
            if not dry_run:
                self.client.delete_identity_policy(
                    Identity=self.name,
                    PolicyName=constants.SID_SIGNATURE
                )
                message = f"200: Removed identity policy called {constants.SID_SIGNATURE} for identity {self.name}"
            else:
                message = f"202: Dry run: will remove identity policy called {constants.SID_SIGNATURE} for identity {self.name}"
        else:
            message = f"404: There is no policy titled {constants.SID_SIGNATURE} attached to {self.name}"
        response_message = ResponseMessage(message=message, operation=operation, evil_principal=evil_principal,
                                           victim_resource_arn=self.arn, original_policy=self.original_policy,
                                           updated_policy=new_policy, resource_type=self.resource_type, resource_name=self.name)
        return response_message


class SesIdentityPolicies(ResourceTypes):
    def __init__(self, client: boto3.Session.client, current_account_id: str, region: str):
        super().__init__(client, current_account_id, region)

    @property
    def resources(self):
        """Get a list of these resources"""
        resources = []

        paginator = self.client.get_paginator("list_identities")
        page_iterator = paginator.paginate()
        for page in page_iterator:
            these_resources = page["Identities"]
            for resource in these_resources:
                resources.append(resource)
        resources = list(dict.fromkeys(resources))  # remove duplicates
        resources.sort()
        return resources

    @property
    def arns(self):
        """Get a list of these resources"""
        resources = []

        paginator = self.client.get_paginator("list_identities")
        page_iterator = paginator.paginate()
        for page in page_iterator:
            these_resources = page["Identities"]
            for resource in these_resources:
                arn = f"arn:aws:ses:{self.region}:{self.current_account_id}:identity/{resource}"
                resources.append(arn)
        resources = list(dict.fromkeys(resources))  # remove duplicates
        resources.sort()
        return resources

