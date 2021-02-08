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


class ElasticFileSystem(ResourceType, ABC):
    def __init__(self, name: str, region: str, client: boto3.Session.client, current_account_id: str):
        self.service = "elasticfilesystem"
        self.resource_type = "file-system"
        self.region = region
        self.current_account_id = current_account_id
        self.name = name
        # Override parent defaults because EFS is weird with the resource block requirements
        self.override_resource_block = self.arn
        super().__init__(name, self.resource_type, self.service, region, client, current_account_id,
                         override_resource_block=self.override_resource_block)

    @property
    def arn(self) -> str:
        # NOTE: self.name represents the File System ID
        return f"arn:aws:{self.service}:{self.region}:{self.current_account_id}:{self.resource_type}/{self.name}"

    def _get_rbp(self) -> PolicyDocument:
        """Get the resource based policy for this resource and store it"""
        try:
            response = self.client.describe_file_system_policy(FileSystemId=self.name)
            policy = json.loads(response.get("Policy"))
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
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/efs.html#EFS.Client.put_file_system_policy
        new_policy = json.dumps(evil_policy)
        self.client.put_file_system_policy(FileSystemId=self.name, Policy=new_policy)
        return evil_policy


class ElasticFileSystems(ResourceTypes):
    def __init__(self, client: boto3.Session.client, current_account_id: str, region: str):
        super().__init__(client, current_account_id, region)

    @property
    def resources(self):
        """Get a list of these resources"""
        resources = []

        paginator = self.client.get_paginator("describe_file_systems")
        page_iterator = paginator.paginate()
        for page in page_iterator:
            these_resources = page["FileSystems"]
            for resource in these_resources:
                id = resource.get("FileSystemId")
                arn = resource.get("FileSystemArn")
                # Append the path to the list so we can rebuild the ARN later, but remove the leading /
                resources.append(id)
        resources = list(dict.fromkeys(resources))  # remove duplicates
        resources.sort()
        return resources

    @property
    def arns(self):
        """Get a list of these resources"""
        resources = []

        paginator = self.client.get_paginator("describe_file_systems")
        page_iterator = paginator.paginate()
        for page in page_iterator:
            these_resources = page["FileSystems"]
            for resource in these_resources:
                id = resource.get("FileSystemId")
                arn = resource.get("FileSystemArn")
                # Append the path to the list so we can rebuild the ARN later, but remove the leading /
                resources.append(arn)
        resources = list(dict.fromkeys(resources))  # remove duplicates
        resources.sort()
        return resources