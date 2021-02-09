import json
from policy_sentry.util.arns import get_account_from_arn


# pylint: disable=too-many-instance-attributes
class StatementDetail:
    """
    Analyzes individual statements within a policy
    """

    def __init__(
            self,
            statement: dict,
            service: str,
            override_action: str = None,
            override_account_id_instead_of_principal: bool = False
    ):
        self.json = statement
        self.statement = statement
        self.sid = statement.get("Sid", "")
        self.effect = statement["Effect"]

        self.service = service
        self.override_action = override_action
        self.override_account_id_instead_of_principal = override_account_id_instead_of_principal

        self.resources = self._resources()
        self.actions = self._actions()
        self.aws_principals = self._aws_principals()
        self.other_principals = self._other_principals()
        self.condition = statement.get("Condition", None)
        self.not_action = statement.get("NotAction", None)
        self.not_principal = statement.get("NotPrincipal", None)
        self.not_resource = statement.get("NotResource", None)

    def __str__(self) -> str:
        principals_block = {}
        result = {
            "Sid": self.sid,
            "Effect": self.effect,
        }
        if self.aws_principals:
            principals_block["AWS"] = self.aws_principals
        if self.other_principals:
            principals_block.update(self.other_principals)
        result["Principal"] = principals_block
        if self.resources:
            result["Resource"] = self.resources
        if self.actions:
            result["Action"] = self.actions
        if self.condition:
            result["Condition"] = self.condition
        if self.not_action:
            result["NotAction"] = self.not_action
        if self.not_principal:
            result["NotPrincipal"] = self.not_principal
        if self.not_resource:
            result["NotResource"] = self.not_resource
        return json.dumps(result)

    def _original_actions(self):
        """Holds the actions from the original JSON"""
        actions = self.statement.get("Action")
        if not actions:
            return []
        if not isinstance(actions, list):
            actions = [actions]
        return actions

    def _actions(self):
        """Holds the actions in a statement"""
        # IAM Roles have a special case where you don't just provide "iam:*" like other resource based policies
        # - you have to provide sts:AssumeRole. For that special case, we need to be able to override the action
        #   in this method.
        if self.override_action:
            if "," in self.override_action:
                action_block = self.override_action.split(",")
            else:
                action_block = self.override_action
        else:
            # If override action is not supplied, just give full access to the whole service 🤡
            action_block = [f"{self.service}:*"]
        return action_block

    def _resources(self):
        """Holds the resource ARNs in a statement"""
        resources = self.statement.get("Resource")
        if not resources:
            return []
        # If it's a string, turn it into a list
        if not isinstance(resources, list):
            resources = [resources]
        return resources

    def _aws_principals(self):
        """Holds the principal ARNs in a statement"""
        principals_block = self.statement.get("Principal")
        principals = []
        if isinstance(principals_block, str):
            principals = principals_block
        elif isinstance(principals_block, dict):
            principals = principals_block.get("AWS", None)
        if not principals:
            return []
        # If it's a string, turn it into a list
        if not isinstance(principals, list):
            principals = [principals]
        if self.override_account_id_instead_of_principal:
            updated_principals = []
            for principal in principals:
                # Case: Principal = *
                if principal == "*":
                    updated_principals.append(principal)
                # Case: principal = "arn:aws:iam::999988887777:user/mwahahaha"
                elif ":" in principal:
                    updated_principals.append(get_account_from_arn(principal))
                # Case: principal = 999988887777
                else:
                    updated_principals.append(principal)
            return updated_principals
        else:
            return principals

    def _other_principals(self) -> dict:
        principals_block = self.statement.get("Principal")
        other_principals = {}
        if isinstance(principals_block, str):
            other_principals["*"] = principals_block
        else:
            for principal_type in principals_block:
                if principal_type != "AWS":
                    other_principals[principal_type] = principals_block[principal_type]
        return other_principals
