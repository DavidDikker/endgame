"""
Classes for managing responses from the various exposure classes. When you run `undo`, `add_myself`, or `set_rbp`,
 instead of returning a different dict each time, we will standardize the way in which messages are sent back from those
 functions.
"""
import logging
from policy_sentry.util.arns import get_resource_path_from_arn
from endgame.shared.validate import validate_basic_policy_json
from endgame.shared import utils
from endgame.shared.policy_document import PolicyDocument
logger = logging.getLogger(__name__)


class ResponseMessage:
    def __init__(self, message: str, operation: str, success: bool, victim_resource_arn: str, evil_principal: str,
                 original_policy: dict, updated_policy: dict, resource_type: str, resource_name: str, service: str):
        self.message = message
        self.operation = operation
        self.success = success
        self.evil_principal = evil_principal
        self.victim_resource_arn = victim_resource_arn
        self.original_policy = validate_basic_policy_json(original_policy)
        self.updated_policy = validate_basic_policy_json(updated_policy)
        self.resource_type = resource_type
        self.resource_name = resource_name
        self.service = service

    @property
    def updated_policy_sids(self) -> list:
        return utils.get_sid_names_with_error_handling(self.updated_policy)

    @property
    def original_policy_sids(self) -> list:
        return utils.get_sid_names_with_error_handling(self.original_policy)

    @property
    def victim_resource_name(self) -> str:
        principal_name = get_resource_path_from_arn(self.evil_principal)
        return principal_name

    @property
    def evil_principal_name(self) -> str:
        principal_name = get_resource_path_from_arn(self.evil_principal)
        return principal_name

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


class ResponseGetRbp:
    def __init__(self, policy_document, success):
        self.policy_document = policy_document
        self.success = success
