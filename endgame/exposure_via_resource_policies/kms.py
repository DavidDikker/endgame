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


# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/kms.html
class KmsKey(ResourceType, ABC):
    def __init__(self, name: str, region: str, client: boto3.Session.client, current_account_id: str):
        self.service = "kms"
        self.resource_type = "key"
        self.region = region
        self.current_account_id = current_account_id
        if name.startswith("alias"):
            self.alias = name
            name = self._get_key_id_with_alias(name, client)
            self.name = name
        else:
            self.name = name
            self.alias = None
        self.override_resource_block = self.arn
        super().__init__(name, self.resource_type, self.service, region, client, current_account_id,
                         override_resource_block=self.override_resource_block)

    # TODO: Translate the name into the ID
    @property
    def arn(self) -> str:
        return f"arn:aws:{self.service}:{self.region}:{self.current_account_id}:{self.resource_type}/{self.name}"

    def _get_key_id_with_alias(self, name: str, client: boto3.Session.client) -> str:
        """Given an alias, return the key ID"""
        response = client.describe_key(KeyId=name)
        key_id = response.get("KeyMetadata").get("KeyId")
        return key_id

    def _get_rbp(self) -> PolicyDocument:
        """Get the resource based policy for this resource and store it"""
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/kms.html#KMS.Client.get_key_policy
        try:
            response = self.client.get_key_policy(KeyId=self.arn, PolicyName="default")
            if response.get("Policy"):
                policy = constants.get_empty_policy()
                policy["Statement"].extend(json.loads(response.get("Policy")).get("Statement"))
            else:
                policy = constants.get_empty_policy()
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
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/kms.html#KMS.Client.put_key_policy
        new_policy = json.dumps(evil_policy)
        self.client.put_key_policy(KeyId=self.name, PolicyName="default", Policy=new_policy)
        # self.policy = self._get_rbp()
        return evil_policy


class KmsKeys(ResourceTypes):
    def __init__(self, client: boto3.Session.client, current_account_id: str, region: str):
        super().__init__(client, current_account_id, region)

    @property
    def resources(self):
        """Get a list of these resources"""

        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/kms.html#KMS.Paginator.ListKeys
        def list_keys() -> list:
            keys = []
            paginator = self.client.get_paginator("list_keys")
            page_iterator = paginator.paginate()
            for page in page_iterator:
                these_resources = page["Keys"]
                for resource in these_resources:
                    key_id = resource.get("KeyId")
                    arn = resource.get("KeyArn")
                    keys.append(key_id)
            return keys

        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/kms.html#KMS.Paginator.ListAliases
        def filter_with_aliases(all_key_ids) -> list:
            keys = []
            key_ids_with_aliases = []
            aws_managed_key_ids = []
            paginator = self.client.get_paginator("list_aliases")
            page_iterator = paginator.paginate()
            for page in page_iterator:
                these_resources = page["Aliases"]
                for resource in these_resources:
                    alias = resource.get("AliasName")
                    key_id = resource.get("TargetKeyId")
                    arn = resource.get("AliasArn")
                    if alias.startswith("alias/aws") or alias.startswith("aws/"):
                        aws_managed_key_ids.append(key_id)
                        continue
                    else:
                        keys.append(alias)
                        key_ids_with_aliases.append(key_id)
            # If the key does not have an alias, return the key ID
            for some_key_id in all_key_ids:
                if some_key_id not in key_ids_with_aliases and some_key_id not in aws_managed_key_ids:
                    keys.append(some_key_id)
            return keys
        key_ids = list_keys()
        keys = filter_with_aliases(key_ids)
        resources = list(dict.fromkeys(keys))  # remove duplicates
        resources.sort()
        return resources

    @property
    def arns(self):
        """Get a list of these resources"""

        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/kms.html#KMS.Paginator.ListKeys
        def list_keys() -> list:
            keys = []
            paginator = self.client.get_paginator("list_keys")
            page_iterator = paginator.paginate()
            for page in page_iterator:
                these_resources = page["Keys"]
                for resource in these_resources:
                    key_id = resource.get("KeyId")
                    arn = resource.get("KeyArn")
                    keys.append(arn)
            return keys

        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/kms.html#KMS.Paginator.ListAliases
        def filter_with_aliases(all_key_ids) -> list:
            keys = []
            key_ids_with_aliases = []
            aws_managed_key_ids = []
            paginator = self.client.get_paginator("list_aliases")
            page_iterator = paginator.paginate()
            for page in page_iterator:
                these_resources = page["Aliases"]
                for resource in these_resources:
                    alias = resource.get("AliasName")
                    key_id = resource.get("TargetKeyId")
                    arn = resource.get("AliasArn")
                    if alias.startswith("alias/aws") or alias.startswith("aws/"):
                        aws_managed_key_ids.append(arn)
                        continue
                    else:
                        keys.append(alias)
                        key_ids_with_aliases.append(arn)
            # If the key does not have an alias, return the key ID
            for some_key_id in all_key_ids:
                if some_key_id not in key_ids_with_aliases and some_key_id not in aws_managed_key_ids:
                    keys.append(some_key_id)
            return keys
        key_ids = list_keys()
        keys = filter_with_aliases(key_ids)
        resources = list(dict.fromkeys(keys))  # remove duplicates
        resources.sort()
        return resources

