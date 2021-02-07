import logging
import json
import boto3
import botocore
from abc import ABC
from botocore.exceptions import ClientError
from endgame.shared import constants
from endgame.exposure_via_resource_policies.common import ResourceType, ResourceTypes
from endgame.shared.policy_document import PolicyDocument

logger = logging.getLogger(__name__)


class EcrRepository(ResourceType, ABC):
    def __init__(self, name: str, region: str, client: boto3.Session.client, current_account_id: str):
        service = "ecr"
        resource_type = "repository"
        self.include_resource_block = False
        super().__init__(name, resource_type, service, region, client, current_account_id,
                         include_resource_block=self.include_resource_block)

    @property
    def arn(self) -> str:
        return f"arn:aws:{self.service}:{self.region}:{self.current_account_id}:{self.resource_type}/{self.name}"

    def _get_rbp(self) -> PolicyDocument:
        """Get the resource based policy for this resource and store it"""
        try:
            # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ecr.html#ECR.Client.get_repository_policy
            response = self.client.get_repository_policy(repositoryName=self.name)
            policy = json.loads(response.get("policyText"))
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
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ecr.html#ECR.Client.set_repository_policy
        self.client.set_repository_policy(repositoryName=self.name, policyText=new_policy)
        return evil_policy


class EcrRepositories(ResourceTypes):
    def __init__(self, client: boto3.Session.client, current_account_id: str, region: str):
        super().__init__(client, current_account_id, region)

    @property
    def resources(self):
        """Get a list of these resources"""
        resources = []

        paginator = self.client.get_paginator("describe_repositories")
        page_iterator = paginator.paginate()
        for page in page_iterator:
            these_resources = page["repositories"]
            for resource in these_resources:
                name = resource.get("repositoryName")
                arn = resource.get("repositoryArn")
                # Append the path to the list so we can rebuild the ARN later, but remove the leading /
                resources.append(name)
        resources = list(dict.fromkeys(resources))  # remove duplicates
        resources.sort()
        return resources

