import copy
from abc import ABCMeta, abstractmethod
import boto3
import botocore
from botocore.exceptions import ClientError


class ResponseGetSharingApi:
    def __init__(
            self,
            shared_with_accounts: list,
            success: bool,
            resource_type: str,
            resource_name: str,
            service: str,
            updated_policy: list,  # we can format this however we want even though there are no RBPs
            original_policy: list,  # we can format this however we want even though there are no RBPs
            evil_principal: str,
            victim_resource_arn: str
    ):
        self.shared_with_accounts = shared_with_accounts
        self.success = success
        self.evil_principal = evil_principal
        self.victim_resource_arn = victim_resource_arn
        self.resource_type = resource_type
        self.resource_name = resource_name
        self.service = service
        self.original_policy = original_policy
        self.updated_policy = updated_policy

    # This is kind of silly because this is just a list of account IDs, but I am going to piggyback off of the previous
    # structure out of convenience
    # TODO: Figure out a better way to do this. Mostly because I am doing the RDS and EBS sharing last minute
    @property
    def updated_policy_sids(self) -> list:
        return self.updated_policy

    @property
    def original_policy_sids(self) -> list:
        return self.original_policy

    @property
    def added_sids(self) -> list:
        diff = []
        if len(self.updated_policy_sids) > len(self.original_policy_sids):
            diff = list(set(self.updated_policy_sids) - set(self.original_policy_sids))
        return diff

    @property
    def removed_sids(self) -> list:
        diff = []
        if len(self.original_policy_sids) > len(self.updated_policy_sids):
            diff = list(set(self.original_policy_sids) - set(self.updated_policy_sids))
        return diff


class ResourceSharingApi(object):
    __meta_class__ = ABCMeta

    def __init__(
            self,
            name: str,
            resource_type: str,
            service: str,
            region: str,
            client: boto3.Session.client,
            current_account_id: str,
    ):
        self.name = name
        self.resource_type = resource_type
        self.client = client
        self.current_account_id = current_account_id
        self.service = service
        self.region = region
        self.shared_with_accounts = self._get_shared_with_accounts().shared_with_accounts
        self.original_shared_with_accounts = copy.deepcopy(self.shared_with_accounts)

    @property
    @abstractmethod
    def arn(self) -> str:
        raise NotImplementedError("Must override arn")

    @abstractmethod
    def _get_shared_with_accounts(self) -> ResponseGetSharingApi:
        raise NotImplementedError("Must override _get_shared_with_accounts")

    @abstractmethod
    def share(self, accounts_to_add: list, accounts_to_remove: list) -> ResponseGetSharingApi:
        raise NotImplementedError("Must override share")

    @abstractmethod
    def add_myself(self, evil_policy: dict) -> ResponseGetSharingApi:
        raise NotImplementedError("Must override add_myself")

    @abstractmethod
    def undo(self, evil_principal: str, dry_run: bool = False) -> ResponseGetSharingApi:
        raise NotImplementedError("Must override undo")
