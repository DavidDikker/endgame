import json
import copy
from endgame.shared.statement_detail import StatementDetail
from endgame.shared import constants


class PolicyDocument:
    """
    Holds a policy document
    """
    def __init__(
            self,
            policy: dict,
            service: str,
            override_action: str = None,
            include_resource_block: bool = True,
            override_resource_block: str = None,
            override_account_id_instead_of_principal: bool = False
    ):
        statement_structure = policy.get("Statement", [])
        self.policy = policy
        self.original_policy = copy.deepcopy(policy)

        self.service = service
        self.override_action = override_action
        self.include_resource_block = include_resource_block
        self.override_resource_block = override_resource_block
        self.override_account_id_instead_of_principal = override_account_id_instead_of_principal

        self.statements = self._statements(statement_structure)

    def __str__(self):
        return json.dumps(self.json)

    def __repr__(self):
        return json.dumps(self.json)

    def _statements(self, statement_structure) -> [StatementDetail]:
        # Statement can be a list or a string, but we prefer strings for uniformity
        if not isinstance(statement_structure, list):
            statement_structure = [statement_structure]  # pragma: no cover
        statements = []
        for statement in statement_structure:
            statements.append(StatementDetail(
                statement=statement,
                override_account_id_instead_of_principal=self.override_account_id_instead_of_principal,
                override_action=self.override_action,
                service=self.service
            ))
        return statements

    @property
    def sids(self):
        statement_ids = []
        for statement in self.statements:
            statement_ids.append(statement.sid)
        return statement_ids

    @property
    def json(self):
        """Return the Policy in JSON"""
        policy = {
            "Version": "2012-10-17",
            "Statement": []
        }
        for statement in self.statements:
            policy["Statement"].append(json.loads(statement.__str__()))
        return policy

    def statement_allow_account_id(
            self,
            account_id: str,
            resource_arn: str = "*",
            sid_name: str = "AllowCurrentAccount",
            principal: str = None,
    ) -> dict:

        if self.override_action:
            if "," in self.override_action:
                action_block = self.override_action.split(",")
            else:
                action_block = self.override_action
        else:
            # If override action is not supplied, just give full access to the whole service 🤡
            action_block = [f"{self.service}:*"]

        if not principal:
            principal = f"arn:aws:iam::{account_id}:root"

        statement = {
            "Sid": sid_name,
            "Action": action_block,
            "Effect": "Allow",
            "Principal": {
                "AWS": [
                    principal
                    # f"arn:aws:iam::{current_account_id}:root"
                ]
            },
        }
        if self.include_resource_block:
            statement["Resource"] = get_resource_from_override_settings(
                resource_arn=resource_arn, override_resource_block=self.override_resource_block)
        allow_current_account = StatementDetail(
                statement=statement,
                override_account_id_instead_of_principal=self.override_account_id_instead_of_principal,
                override_action=self.override_action,
                service=self.service
            )
        return json.loads(allow_current_account.__str__())

    def policy_plus_evil_principal(
            self,
            victim_account_id: str,
            evil_principal: str,
            resource_arn: str = "*",
    ) -> dict:
        policy = {
            "Version": "2012-10-17",
            "Statement": []
        }

        # Add AllowCurrentAccount to statements if there are no statements
        if len(self.sids) == 0 or constants.ALLOW_CURRENT_ACCOUNT_SID_SIGNATURE not in self.sids:
            allow_current_account_statement = self.statement_allow_account_id(
                account_id=victim_account_id,
                resource_arn=resource_arn,
            )
            self.statements.append(StatementDetail(
                statement=allow_current_account_statement,
                service=self.service,
                override_action=self.override_action,
                override_account_id_instead_of_principal=self.override_account_id_instead_of_principal
            ))
        # If Endgame is not there, add it.
        if constants.SID_SIGNATURE not in self.sids:
            evil_statement = self.statement_allow_account_id(
                account_id=victim_account_id,
                principal=evil_principal,
                resource_arn=resource_arn,
                sid_name=constants.SID_SIGNATURE
            )
            self.statements.append(StatementDetail(
                statement=evil_statement,
                service=self.service,
                override_action=self.override_action,
                override_account_id_instead_of_principal=self.override_account_id_instead_of_principal
            ))

        for statement in self.statements:
            # Set resources
            if self.include_resource_block:
                statement.resources = get_resource_from_override_settings(
                    resource_arn=resource_arn, override_resource_block=self.override_resource_block)
            policy["Statement"].append(json.loads(statement.__str__()))
        return policy

    def policy_minus_evil_principal(
            self,
            victim_account_id: str,
            evil_principal: str,
            resource_arn: str = "*",
    ):
        policy = {
            "Version": "2012-10-17",
            "Statement": []
        }

        # Add AllowCurrentAccount to statements if there are no statements
        if len(self.sids) == 0:
            allow_current_account_statement = self.statement_allow_account_id(
                account_id=victim_account_id,
                resource_arn=resource_arn
            )
            self.statements.append(StatementDetail(
                statement=allow_current_account_statement,
                service=self.service,
                override_action=self.override_action,
                override_account_id_instead_of_principal=self.override_account_id_instead_of_principal
            ))

        for statement in self.statements:
            # Skip statements that include the evil principal
            if statement.sid == constants.SID_SIGNATURE:
                continue
            # Set resources
            if self.include_resource_block:
                statement.resources = get_resource_from_override_settings(
                    resource_arn=resource_arn, override_resource_block=self.override_resource_block)
            policy["Statement"].append(json.loads(statement.__str__()))
        return policy


def get_resource_from_override_settings(resource_arn: str, override_resource_block: str) -> list:
    if not override_resource_block:
        resource_block = [resource_arn, f"{resource_arn}/*"]
    else:
        if "," in override_resource_block:
            resource_block = override_resource_block.split(",")
        else:
            resource_block = override_resource_block
    return resource_block
