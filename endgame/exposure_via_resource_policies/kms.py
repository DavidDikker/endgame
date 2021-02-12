import logging
import json
import boto3
import botocore
from abc import ABC
from botocore.exceptions import ClientError
from policy_sentry.util.arns import get_account_from_arn, get_resource_path_from_arn
from endgame.shared import constants
from endgame.exposure_via_resource_policies.common import ResourceType, ResourceTypes
from endgame.shared.policy_document import PolicyDocument
from endgame.shared.list_resources_response import ListResourcesResponse
from endgame.shared.response_message import ResponseMessage
from endgame.shared.response_message import ResponseGetRbp

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

    @property
    def arn(self) -> str:
        return f"arn:aws:{self.service}:{self.region}:{self.current_account_id}:{self.resource_type}/{self.name}"

    def _get_key_id_with_alias(self, name: str, client: boto3.Session.client) -> str:
        """Given an alias, return the key ID"""
        response = client.describe_key(KeyId=name)
        key_id = response.get("KeyMetadata").get("KeyId")
        return key_id

    def _get_rbp(self) -> ResponseGetRbp:
        """Get the resource based policy for this resource and store it"""
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/kms.html#KMS.Client.get_key_policy
        logger.debug("Getting resource policy for %s" % self.arn)
        try:
            response = self.client.get_key_policy(KeyId=self.arn, PolicyName="default")
            if response.get("Policy"):
                policy = constants.get_empty_policy()
                policy["Statement"].extend(json.loads(response.get("Policy")).get("Statement"))
            else:
                policy = constants.get_empty_policy()
            success = True
        except botocore.exceptions.ClientError:
            # When there is no policy, let's return an empty policy to avoid breaking things
            policy = constants.get_empty_policy()
            success = False
        policy_document = PolicyDocument(
            policy=policy,
            service=self.service,
            override_action=self.override_action,
            include_resource_block=self.include_resource_block,
            override_resource_block=self.override_resource_block,
            override_account_id_instead_of_principal=self.override_account_id_instead_of_principal,
        )
        response = ResponseGetRbp(policy_document=policy_document, success=success)
        return response

    def set_rbp(self, evil_policy: dict) -> ResponseMessage:
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/kms.html#KMS.Client.put_key_policy
        new_policy = json.dumps(evil_policy)
        logger.debug("Setting resource policy for %s" % self.arn)
        try:
            self.client.put_key_policy(KeyId=self.name, PolicyName="default", Policy=new_policy)
            message = "success"
            success = True
        except botocore.exceptions.ClientError as error:
            message = str(error)
            logger.critical(error)
            success = False
        response_message = ResponseMessage(message=message, operation="set_rbp", success=success, evil_principal="",
                                           victim_resource_arn=self.arn, original_policy=self.original_policy,
                                           updated_policy=evil_policy, resource_type=self.resource_type,
                                           resource_name=self.name, service=self.service)
        return response_message


class KmsKeys(ResourceTypes):
    def __init__(self, client: boto3.Session.client, current_account_id: str, region: str):
        super().__init__(client, current_account_id, region)
        self.service = "kms"
        self.resource_type = "key"
        self.current_account_id = current_account_id

    @property
    def resources(self) -> [ListResourcesResponse]:
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
        def filter_with_aliases(all_key_arns) -> list:
            keys = []
            key_arns_with_aliases = []
            aws_managed_key_arns = []
            paginator = self.client.get_paginator("list_aliases")
            page_iterator = paginator.paginate()
            for page in page_iterator:
                these_resources = page["Aliases"]
                for resource in these_resources:
                    alias = resource.get("AliasName")
                    key_id = resource.get("TargetKeyId")
                    arn = resource.get("AliasArn")
                    if alias.startswith("alias/aws") or alias.startswith("aws/"):
                        aws_managed_key_arns.append(arn)
                        if key_id:
                            aws_managed_key_arns.append(f"arn:aws:kms:{self.region}:{self.current_account_id}:key/{key_id}")
                        continue
                    else:
                        # keys.append(alias)
                        arn = f"arn:aws:{self.service}:{self.region}:{self.current_account_id}:{self.resource_type}/{key_id}"
                        list_resources_response = ListResourcesResponse(
                            service=self.service, account_id=self.current_account_id, arn=arn, region=self.region,
                            resource_type=self.resource_type, name=key_id, note=alias)
                        keys.append(list_resources_response)
                        key_arns_with_aliases.append(arn)
            # If the key does not have an alias, return the key ID
            for some_key_arn in all_key_arns:
                if some_key_arn not in key_arns_with_aliases and some_key_arn not in aws_managed_key_arns:
                    key_id = get_resource_path_from_arn(some_key_arn)
                    arn = f"arn:aws:{self.service}:{self.region}:{self.current_account_id}:{self.resource_type}/{key_id}"
                    list_resources_response = ListResourcesResponse(
                        service=self.service, account_id=self.current_account_id, arn=arn, region=self.region,
                        resource_type=self.resource_type, name=key_id)
                    keys.append(list_resources_response)
            return keys
        key_ids = list_keys()
        resources = filter_with_aliases(key_ids)
        return resources

