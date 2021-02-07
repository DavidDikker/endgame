"""
Classes for managing responses from the various exposure classes. When you run `undo`, `add_myself`, or `set_rbp`,
 instead of returning a different dict each time, we will standardize the way in which messages are sent back from those
 functions.
"""
import logging
from policy_sentry.util.arns import get_resource_path_from_arn
from endgame.shared.validate import validate_basic_policy_json
from endgame.shared import utils
logger = logging.getLogger(__name__)


class ResponseMessage:
    def __init__(self, message: str, operation: str, victim_resource_arn: str, evil_principal: str,
                 original_policy: dict, updated_policy: dict, resource_type: str, resource_name: str):
        self.message = message
        self.operation = operation
        # Operation:  ADD_MYSELF, DRY_RUN_ADD_MYSELF, UNDO, DRY_RUN_UNDO, LIST
        # self.message_code = message_code
        self.evil_principal = evil_principal
        self.victim_resource_arn = victim_resource_arn
        self.original_policy = validate_basic_policy_json(original_policy)
        self.updated_policy = validate_basic_policy_json(updated_policy)
        self.resource_type = resource_type
        self.resource_name = resource_name

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

    # def translate_response_code(self) -> dict:
    #     """Experimenting with using HTTP response codes to conceptualize the statuses/results of each function."""
    #     response = dict(
    #         message=None,
    #         message_code=self.message_code,
    #         details=None
    #     )
    #     if self.message_code == 200:
    #         response["message"] = "OK"
    #         response["details"] = "All good bruh"
    #     elif self.message_code == 201:
    #         response["message"] = "Created"
    #         response["details"] = "Mischief: The new policy was created"
    #     elif self.message_code == 202:
    #         response["message"] = "Accepted"
    #         response["details"] = "Dry run: The policy was acceptable"
    #     elif self.message_code == 404:
    #         response["message"] = "Not Found"
    #         response["details"] = "Some resource was not found"
    #     return response
