"""
List exposable resources
"""
import logging
import click
import boto3
from endgame import set_log_level
from endgame.exposure_via_resource_policies import glacier_vault, sqs, lambda_layer, lambda_function, kms, \
    cloudwatch_logs, efs, s3,  sns, iam, ecr, secrets_manager, ses, elasticsearch, acm_pca
from endgame.exposure_via_sharing_apis import rds_snapshots, ebs_snapshots, ec2_amis
from endgame.shared.aws_login import get_boto3_client, get_current_account_id
from endgame.shared.validate import click_validate_supported_aws_service, click_validate_comma_separated_resource_names
from endgame.shared.list_resources_response import ListResourcesResponse
from endgame.shared import utils, constants

logger = logging.getLogger(__name__)


@click.command(name="list-resources", short_help="List exposable resources.")
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
    help="The AWS region",
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
    "-v",
    "--verbose",
    "verbosity",
    count=True,
)
def list_resources(service, profile, region, cloak, excluded_names, verbosity):
    """
    List AWS resources to expose.
    """

    set_log_level(verbosity)

    resources = []
    # User-supplied arguments like `cloudwatch` need to be translated to the IAM name like `logs`
    provided_service = service

    results = []
    # Get the boto3 clients
    sts_client = get_boto3_client(profile=profile, service="sts", region=region, cloak=cloak)
    current_account_id = get_current_account_id(sts_client=sts_client)
    if provided_service == "all":
        results = get_all_resources_for_all_services(profile=profile, region=region, current_account_id=current_account_id, cloak=cloak)
    else:
        translated_service = utils.get_service_translation(provided_service=provided_service)
        client = get_boto3_client(profile=profile, service=translated_service, region=region, cloak=cloak)
        result = list_resources_by_service(provided_service=service, region=region,
                                           current_account_id=current_account_id, client=client)
        results.extend(result.resources)

    # Print the results
    if len(results) == 0:
        logger.warning("There are no resources given the criteria provided.")
    else:
        # If you provide --service all, then we will list the ARNs to differentiate services
        if provided_service == "all":
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


def get_all_resources_for_all_services(profile: str, region: str, current_account_id: str, cloak: bool = False):
    results = []
    for supported_service in constants.SUPPORTED_AWS_SERVICES:
        if supported_service != "all":
            translated_service = utils.get_service_translation(provided_service=supported_service)
            result = get_all_resources(translated_service=translated_service, provided_service=supported_service,
                                       profile=profile, region=region, current_account_id=current_account_id, cloak=cloak)
            if result:
                results.extend(result)
    return results


def get_all_resources(translated_service: str, profile: str, provided_service: str, region: str,
                      current_account_id: str, cloak: bool = False) -> [ListResourcesResponse]:
    """Get resource objects for every resource under an AWS service"""
    results = []
    client = get_boto3_client(profile=profile, service=translated_service, region=region, cloak=cloak)
    result = list_resources_by_service(provided_service=provided_service, region=region,
                                       current_account_id=current_account_id, client=client)
    if result:
        if result.resources:
            results.extend(result.resources)
    return results


def list_resources_by_service(
        provided_service: str,
        region: str,
        current_account_id: str,
        client: boto3.Session.client,
):
    resources = None

    if provided_service == "acm-pca":
        resources = acm_pca.AcmPrivateCertificateAuthorities(client=client, current_account_id=current_account_id,
                                                             region=region)
    elif provided_service == "ecr":
        resources = ecr.EcrRepositories(client=client, current_account_id=current_account_id, region=region)
    elif provided_service == "efs":
        resources = efs.ElasticFileSystems(client=client, current_account_id=current_account_id, region=region)
    elif provided_service == "elasticsearch":
        resources = elasticsearch.ElasticSearchDomains(client=client, current_account_id=current_account_id,
                                                       region=region)
    elif provided_service == "glacier":
        resources = glacier_vault.GlacierVaults(client=client, current_account_id=current_account_id, region=region)
    elif provided_service == "iam":
        resources = iam.IAMRoles(client=client, current_account_id=current_account_id, region=region)
    elif provided_service == "kms":
        resources = kms.KmsKeys(client=client, current_account_id=current_account_id, region=region)
    elif provided_service == "lambda":
        resources = lambda_function.LambdaFunctions(client=client, current_account_id=current_account_id, region=region)
    elif provided_service == "lambda-layer":
        resources = lambda_layer.LambdaLayers(client=client, current_account_id=current_account_id, region=region)
    elif provided_service == "cloudwatch":
        resources = cloudwatch_logs.CloudwatchResourcePolicies(client=client, current_account_id=current_account_id,
                                                               region=region)
    elif provided_service == "s3":
        resources = s3.S3Buckets(client=client, current_account_id=current_account_id, region=region)
    elif provided_service == "ses":
        resources = ses.SesIdentityPolicies(client=client, current_account_id=current_account_id, region=region)
    elif provided_service == "sns":
        resources = sns.SnsTopics(client=client, current_account_id=current_account_id, region=region)
    elif provided_service == "sqs":
        resources = sqs.SqsQueues(client=client, current_account_id=current_account_id, region=region)
    elif provided_service == "secretsmanager":
        resources = secrets_manager.SecretsManagerSecrets(client=client, current_account_id=current_account_id,
                                                          region=region)
    elif provided_service == "rds":
        resources = rds_snapshots.RdsSnapshots(client=client, current_account_id=current_account_id, region=region)
    elif provided_service == "ebs":
        resources = ebs_snapshots.EbsSnapshots(client=client, current_account_id=current_account_id, region=region)
    elif provided_service == "ec2-ami":
        resources = ec2_amis.Ec2Images(client=client, current_account_id=current_account_id, region=region)
    return resources
