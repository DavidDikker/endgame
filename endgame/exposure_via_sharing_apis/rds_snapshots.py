import logging
import json
import boto3
import botocore
from abc import ABC
from botocore.exceptions import ClientError
from policy_sentry.util.arns import get_resource_path_from_arn
from endgame.exposure_via_resource_policies.common import ResourceTypes, ResourceType
from endgame.shared.list_resources_response import ListResourcesResponse
from endgame.shared.response_message import ResponseGetRbp
from endgame.shared import constants
from endgame.shared.response_message import ResponseMessage
from endgame.shared.policy_document import PolicyDocument

logger = logging.getLogger(__name__)

# copy_db_snapshot
# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/rds.html#RDS.Client.copy_db_snapshot



class RdsSnapshots(ResourceTypes):
    def __init__(self, client: boto3.Session.client, current_account_id: str, region: str):
        super().__init__(client, current_account_id, region)
        self.service = "rds"
        self.resource_type = "snapshot"

    @property
    def resources(self) -> [ListResourcesResponse]:
        """Get a list of these resources"""
        resources = []
        paginator = self.client.get_paginator("describe_db_snapshots")
        # Get the most recent one. Return both automated and manual ones.
        # When you want to "undo", you will have to get the shared and public ones.
        page_iterator = paginator.paginate()
        for page in page_iterator:
            these_resources = page["DBSnapshots"]
            for resource in these_resources:
                snapshot_identifier = resource.get("DBSnapshotIdentifier")
                instance_identifier = resource.get("DBInstanceIdentifier")
                arn = resource.get("DBSnapshotArn")
                snapshot_name = get_resource_path_from_arn(arn)
                # arn:${Partition}:rds:${Region}:${Account}:snapshot:${SnapshotName}
                list_resources_response = ListResourcesResponse(
                    service=self.service, account_id=self.current_account_id, arn=arn, region=self.region,
                    resource_type=self.resource_type, name=snapshot_name)
                resources.append(list_resources_response)
        return resources
