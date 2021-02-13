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



class EbsSnapshots(ResourceTypes):
    def __init__(self, client: boto3.Session.client, current_account_id: str, region: str):
        super().__init__(client, current_account_id, region)
        self.service = "ebs"
        self.resource_type = "snapshot"

    @property
    def resources(self) -> [ListResourcesResponse]:
        """Get a list of these resources"""
        resources = []
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.Paginator.DescribeSnapshots
        paginator = self.client.get_paginator("describe_snapshots")
        # Apply a filter, otherwise we get public EBS snapshots too, from randos on the internet.
        page_iterator = paginator.paginate(Filters=[
            {
                "Name": "owner-id",
                "Values": [self.current_account_id]
            }
        ])
        for page in page_iterator:
            these_resources = page["Snapshots"]
            for resource in these_resources:
                snapshot_id = resource.get("SnapshotId")
                kms_key_id = resource.get("KmsKeyId")
                volume_id = resource.get("VolumeId")
                arn = f"arn:aws:ec2:{self.region}:{self.current_account_id}:snapshot/{snapshot_id}"
                list_resources_response = ListResourcesResponse(
                    service=self.service, account_id=self.current_account_id, arn=arn, region=self.region,
                    resource_type=self.resource_type, name=snapshot_id)
                resources.append(list_resources_response)
        return resources
