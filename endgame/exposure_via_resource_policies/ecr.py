import logging
import json
import boto3
import botocore
from abc import ABC
from botocore.exceptions import ClientError
from endgame.shared import constants
from endgame.exposure_via_resource_policies.common import ResourceType, ResourceTypes
from endgame.shared.policy_document import PolicyDocument
from endgame.shared.list_resources_response import ListResourcesResponse
from endgame.shared.response_message import ResponseMessage
from endgame.shared.response_message import ResponseGetRbp

logger = logging.getLogger(__name__)


class EcrRepository(ResourceType, ABC):
    def __init__(self, name: str, region: str, client: boto3.Session.client, current_account_id: str):
        self.service = "ecr"
        self.resource_type = "repository"
        self.region = region
        self.current_account_id = current_account_id
        self.name = name
        self.include_resource_block = False
        super().__init__(name, self.resource_type, self.service, region, client, current_account_id,
                         include_resource_block=self.include_resource_block)

    @property
    def arn(self) -> str:
        return f"arn:aws:{self.service}:{self.region}:{self.current_account_id}:{self.resource_type}/{self.name}"

    def _get_rbp(self) -> ResponseGetRbp:
        """Get the resource based policy for this resource and store it"""
        logger.debug("Getting resource policy for %s" % self.arn)
        policy = constants.get_empty_policy()
        try:
            # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ecr.html#ECR.Client.get_repository_policy
            response = self.client.get_repository_policy(repositoryName=self.name)
            policy = json.loads(response.get("policyText"))
            success = True
        except self.client.exceptions.RepositoryPolicyNotFoundException:
            logger.debug("Policy not found. Setting policy document to empty.")
            success = True
        except self.client.exceptions.RepositoryNotFoundException:
            logger.critical("Repository does not exist")
            success = False
        except botocore.exceptions.ClientError:
            # When there is no policy, let's return an empty policy to avoid breaking things
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
        new_policy = json.dumps(evil_policy)
        try:
            # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ecr.html#ECR.Client.set_repository_policy
            self.client.set_repository_policy(repositoryName=self.name, policyText=new_policy)
            message = "success"
            success = True
        except botocore.exceptions.ClientError as error:
            message = str(error)
            success = False
        response_message = ResponseMessage(message=message, operation="set_rbp", success=success, evil_principal="",
                                           victim_resource_arn=self.arn, original_policy=self.original_policy,
                                           updated_policy=evil_policy, resource_type=self.resource_type,
                                           resource_name=self.name, service=self.service)
        return response_message


class EcrRepositories(ResourceTypes):
    def __init__(self, client: boto3.Session.client, current_account_id: str, region: str):
        super().__init__(client, current_account_id, region)
        self.service = "ecr"
        self.resource_type = "repository"

    @property
    def resources(self) -> [ListResourcesResponse]:
        """Get a list of these resources"""
        resources = []

        paginator = self.client.get_paginator("describe_repositories")
        page_iterator = paginator.paginate()
        for page in page_iterator:
            these_resources = page["repositories"]
            for resource in these_resources:
                name = resource.get("repositoryName")
                arn = resource.get("repositoryArn")
                list_resources_response = ListResourcesResponse(
                    service=self.service, account_id=self.current_account_id, arn=arn, region=self.region,
                    resource_type=self.resource_type, name=name)
                resources.append(list_resources_response)
        return resources
