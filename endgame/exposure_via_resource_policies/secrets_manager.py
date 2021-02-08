import logging
import json
import boto3
import botocore
from abc import ABC
from botocore.exceptions import ClientError
from endgame.shared import constants
from endgame.exposure_via_resource_policies.common import ResourceType, ResourceTypes
from endgame.shared.policy_document import PolicyDocument
from endgame.shared.list_resources_response import ListResourcesResponse

logger = logging.getLogger(__name__)


class SecretsManagerSecret(ResourceType, ABC):
    def __init__(self, name: str, region: str, client: boto3.Session.client, current_account_id: str):
        service = "secretsmanager"
        resource_type = "secret"
        super().__init__(name, resource_type, service, region, client, current_account_id)

    @property
    def arn(self) -> str:
        return f"arn:aws:{self.service}:{self.region}:{self.current_account_id}:{self.resource_type}/{self.name}"

    def _get_rbp(self) -> PolicyDocument:
        """Get the resource based policy for this resource and store it"""
        try:
            response = self.client.get_resource_policy(SecretId=self.name)
            if response.get("ResourcePolicy"):
                policy = json.loads(response.get("ResourcePolicy"))
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
        self.client.put_resource_policy(SecretId=self.name, ResourcePolicy=new_policy)
        return evil_policy


class SecretsManagerSecrets(ResourceTypes):
    def __init__(self, client: boto3.Session.client, current_account_id: str, region: str):
        super().__init__(client, current_account_id, region)
        self.service = "secretsmanager"
        self.resource_type = "secret"

    @property
    def resources_v2(self) -> list[ListResourcesResponse]:
        """Get a list of these resources"""
        resources = []

        paginator = self.client.get_paginator("list_secrets")
        page_iterator = paginator.paginate()
        for page in page_iterator:
            these_resources = page["SecretList"]
            for resource in these_resources:
                name = resource.get("Name")
                arn = resource.get("ARN")
                list_resources_response = ListResourcesResponse(
                    service=self.service, account_id=self.current_account_id, arn=arn, region=self.region,
                    resource_type=self.resource_type, name=name)
                resources.append(list_resources_response)
        return resources
