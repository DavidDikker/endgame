import logging
import boto3
import botocore
from abc import ABC
from botocore.exceptions import ClientError
from policy_sentry.util.arns import get_resource_path_from_arn, get_account_from_arn
from endgame.exposure_via_resource_policies.common import ResourceTypes
from endgame.exposure_via_sharing_apis.common import ResourceSharingApi, ResponseGetSharingApi
from endgame.shared.list_resources_response import ListResourcesResponse

logger = logging.getLogger(__name__)


class Ec2Images(ResourceTypes):
    def __init__(self, client: boto3.Session.client, current_account_id: str, region: str):
        super().__init__(client, current_account_id, region)
        self.service = "ec2"
        self.resource_type = "image"

    @property
    def resources(self) -> [ListResourcesResponse]:
        """Get a list of these resources"""
        resources = []
        response = self.client.describe_images(Owners=[self.current_account_id])
        these_resources = response["Images"]
        for resource in these_resources:
            image_id = resource.get("ImageId")
            name = resource.get("Name")
            volume_id = resource.get("VolumeId")
            arn = f"arn:aws:{self.service}:{self.region}:{self.current_account_id}:{self.resource_type}/{image_id}"
            list_resources_response = ListResourcesResponse(
                service=self.service, account_id=self.current_account_id, arn=arn, region=self.region,
                resource_type=self.resource_type, name=image_id)
            resources.append(list_resources_response)
        return resources
