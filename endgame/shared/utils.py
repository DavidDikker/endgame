import copy
import logging
from colorama import Fore, Back
from policy_sentry.util.policy_files import get_sid_names_from_policy
from policy_sentry.util.arns import get_account_from_arn
from endgame.shared import constants

logger = logging.getLogger(__name__)
END = "\033[0m"
GREY = "\33[90m"


def get_sid_names_with_error_handling(policy):
    try:
        sid_names = get_sid_names_from_policy(policy)
    # This happens when there is no Sid to be found. That means there is a length of zero.
    except TypeError as error:
        logger.debug(error)
        sid_names = []
    except KeyError as error:
        logger.debug("There is no SID name in the policy")
        logger.debug(error)
        sid_names = [""]
    return sid_names


def get_service_translation(provided_service: str) -> str:
    """We have to take a user-supplied service (which is named for their understanding) and transform it into the IAM
    service. Example is cloudwatch resource policies being `logs`; `logs` is harder to remember than `cloudwatch`."""
    if provided_service == "cloudwatch":
        actual_service = "logs"
    elif provided_service == "lambda-layer":
        actual_service = "lambda"
    elif provided_service == "elasticsearch":
        actual_service = "es"
    elif provided_service == "elasticfilesystem":
        actual_service = "efs"
    elif provided_service == "ebs":
        actual_service = "ec2"
    elif provided_service == "ec2-ami":
        actual_service = "ec2"
    else:
        actual_service = provided_service
    return actual_service


def change_policy_principal_from_arn_to_account_id(policy: dict) -> dict:
    """
    Some policies like CloudWatch, SNS, SQS, and Lambda require that you submit the policy using
        Principal: {'AWS': '999888777'}
    But the policy that is returned from API call includes a full ARN like:
        Principal: {'AWS': 'arn:aws:iam::999888777:root'}
    This utility function transforms the latter into the former.
    """
    temp_statements = policy.get("Statement")
    updated_policy = constants.get_empty_policy()
    if isinstance(temp_statements, dict):
        temp_policy = constants.get_empty_policy()
        temp_policy["Statement"].append(temp_policy["Statement"])
    else:
        temp_policy = copy.deepcopy(policy)
    statements = temp_policy.get("Statement")
    for statement in statements:
        new_statement = {}
        try:
            aws_principal = statement["Principal"]["AWS"]
            new_account_ids = []
            # case: statement["Principal"]["AWS"] = list()
            if isinstance(aws_principal, list):
                for principal in aws_principal:
                    # case: principal = "*"
                    if principal == "*":
                        new_account_ids.append(principal)
                    # case: principal = "arn:aws:iam::999888777:root"
                    elif ":" in principal:
                        new_account_ids.append(get_account_from_arn(principal))
                    # case: principal = "999888777"
                    else:
                        new_account_ids.append(principal)
            else:
                if aws_principal == "*":
                    new_account_ids.append(aws_principal)
                elif ":" in aws_principal:
                    new_account_ids.append(get_account_from_arn(aws_principal))
                else:
                    new_account_ids.append(aws_principal)
            new_statement = copy.deepcopy(statement)
            new_statement["Principal"]["AWS"] = new_account_ids
            updated_policy["Statement"].append(copy.deepcopy(new_statement))
        # If statement["Principal"]["AWS"] does not exist, just copy the statement to the new policy
        except AttributeError:
            updated_policy["Statement"].append(statement)
    return updated_policy


def print_red(string):
    print(f"{Fore.RED}{string}{END}")


def print_yellow(string):
    print(f"{Fore.YELLOW}{string}{END}")


def print_blue(string):
    print(f"{Fore.BLUE}{string}{END}")


def print_green(string):
    print(f"{Fore.GREEN}{string}{END}")


def print_grey(string):
    print(f"{GREY}{string}{END}")
    # Color code from here: https://stackoverflow.com/a/39452138


def print_remove(service: str, resource_type: str, resource_name: str, principal_type: str, principal_name: str, success: bool):
    resource_message_string = f"{service.upper()} {resource_type.capitalize()} {resource_name}"
    remove_string = f"Remove {principal_type} {principal_name}"
    if success:
        success_string = f"{Fore.GREEN}SUCCESS{END}"
    else:
        success_string = f"{Fore.RED}FAILED{END}"
    message = f"{resource_message_string:<}: {remove_string}"
    print(f"{message:<80}{success_string:>20}")
    # print_blue(f"{message:<80}{success_string:>20}")


def print_add(service: str, resource_type: str, resource_name: str, principal_type: str, principal_name: str, success: bool):
    resource_message_string = f"{service.upper()} {resource_type.capitalize()} {resource_name}"
    add_string = f"Add {principal_type} {principal_name}"
    if success:
        success_string = f"{Fore.GREEN}SUCCESS{END}"
    else:
        success_string = f"{Fore.RED}FAILED{END}"
    message = f"{resource_message_string:<}: {add_string}"
    # print_blue(f"{message:<80}{success_string:>20}")
    print(f"{message:<80}{success_string:>20}")

