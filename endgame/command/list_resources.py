"""
List exposable resources
"""
import logging
import click
from endgame import set_log_level
from endgame.shared.aws_login import get_boto3_client, get_current_account_id
from endgame.shared.validate import click_validate_supported_aws_service, click_validate_comma_separated_resource_names, \
    click_validate_comma_separated_excluded_services
from endgame.shared.resource_results import ResourceResults
from endgame.shared import constants

logger = logging.getLogger(__name__)


@click.command(name="list-resources", short_help="List all resources that can be exposed via Endgame.")
@click.option(
    "--service",
    "-s",
    type=str,
    required=True,
    help=f"The AWS service in question. Valid arguments: {', '.join(constants.SUPPORTED_AWS_SERVICES)}",
    callback=click_validate_supported_aws_service,
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
def list_resources(service, profile, region, cloak, excluded_names, excluded_services, verbosity):
    """
    List AWS resources to expose.
    """

    set_log_level(verbosity)

    # User-supplied arguments like `cloudwatch` need to be translated to the IAM name like `logs`
    user_provided_service = service
    # Get the boto3 clients
    sts_client = get_boto3_client(profile=profile, service="sts", region="us-east-1", cloak=cloak)
    current_account_id = get_current_account_id(sts_client=sts_client)
    if user_provided_service == "all" and region == "all":
        logger.critical("'--service all' and '--region all' detected; listing all resources across all services in the "
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

    # Print the results
    if len(results) == 0:
        logger.warning("There are no resources given the criteria provided.")
    else:
        # If you provide --service all, then we will list the ARNs to differentiate services
        if user_provided_service == "all":
            logger.debug("'--service all' selected; listing resources in ARN format to differentiate between services")
            for resource in results:
                if resource.name not in excluded_names:
                    print(resource.arn)
                else:
                    logger.debug(f"Excluded: {resource.name}")
        else:
            logger.debug("Listing resources by name")
            for resource in results:
                if resource.name not in excluded_names:
                    print(resource.name)
                else:
                    logger.debug(f"Excluded: {resource.name}")
