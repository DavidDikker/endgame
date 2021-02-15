import logging
import click
from endgame.shared.constants import SUPPORTED_AWS_SERVICES
from policy_sentry.util.arns import get_service_from_arn
from policy_sentry.util.arns import parse_arn_for_resource_type
logger = logging.getLogger(__name__)


def click_validate_supported_aws_service(ctx, param, value):
    if value in SUPPORTED_AWS_SERVICES:
        return value
    else:
        raise click.BadParameter(
            f"Supply a supported AWS service. Supported services are: {', '.join(SUPPORTED_AWS_SERVICES)}"
        )


def click_validate_comma_separated_resource_names(ctx, param, value):
    if value is not None:
        try:
            if value == "":
                return []
            else:
                exclude_resource_names = value.split(",")
                return exclude_resource_names
        except ValueError:
            raise click.BadParameter("Supply the list of resource names to exclude from results in a comma separated string.")


def click_validate_comma_separated_excluded_services(ctx, param, value):
    if value is not None:
        try:
            if value == "":
                return []
            else:
                excluded_services = value.split(",")
                for service in excluded_services:
                    if service not in SUPPORTED_AWS_SERVICES:
                        raise click.BadParameter(f"The service name {service} is invalid. Please provide a comma "
                                                 f"separated list of supported services from the list: "
                                                 f"{','.join(SUPPORTED_AWS_SERVICES)}")
                return excluded_services
        except ValueError:
            raise click.BadParameter("Supply the list of resource names to exclude from results in a comma separated string.")


def click_validate_user_or_principal_arn(ctx, param, value):
    if validate_user_or_principal_arn(value):
        return value
    else:
        raise click.BadParameter(
            f"Please supply a valid IAM principal ARN (a user or a role)"
        )


def validate_user_or_principal_arn(arn: str):
    if arn.strip('"').strip("'") == "*":
        return True
    else:
        service = get_service_from_arn(arn)
        resource_type = parse_arn_for_resource_type(arn)
        # Make sure it is an IAM ARN
        if service != "iam":
            raise Exception("Please supply a valid IAM principal ARN (a user or a role)")
        # Make sure that it is a user or a role
        elif resource_type not in ["user", "role"]:
            raise Exception("Please supply a valid IAM principal ARN (a user or a role)")
        else:
            return True


def validate_basic_policy_json(policy_json: dict) -> dict:
    # Expect Statement in policy
    if "Version" not in policy_json or "Statement" not in policy_json:
        logger.warning("Policy does not have either 'Version' or 'Statement' block in it.")
        policy = {"Version": "2012-10-17", "Statement": []}
        return policy
    else:
        if not isinstance(policy_json.get("Statement"), list):
            logger.warning("'Statement' in Policy should be a list (ideally) or a dict")
        return policy_json
