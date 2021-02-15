import os
import logging
import boto3
from botocore.config import Config
from endgame.shared import constants
logger = logging.getLogger(__name__)


def get_boto3_client(profile, service: str, region="us-east-1", cloak: bool = False) -> boto3.Session.client:
    logging.getLogger('botocore').setLevel(logging.CRITICAL)
    session_data = {"region_name": region}
    if profile:
        session_data["profile_name"] = profile
    session = boto3.Session(**session_data)

    if cloak:
        config = Config(connect_timeout=5, retries={"max_attempts": 10})
    else:
        config = Config(connect_timeout=5, retries={"max_attempts": 10}, user_agent=constants.USER_AGENT_INDICATOR)
    if os.environ.get('LOCALSTACK_ENDPOINT_URL'):
        client = session.client(service, config=config, endpoint_url=os.environ.get('LOCALSTACK_ENDPOINT_URL'))
    else:
        client = session.client(service, config=config, endpoint_url=os.environ.get('LOCALSTACK_ENDPOINT_URL'))
    logger.debug(f"{client.meta.endpoint_url} in {client.meta.region_name}: boto3 client login successful")
    return client


def get_current_account_id(sts_client: boto3.Session.client) -> str:
    response = sts_client.get_caller_identity()
    current_account_id = response.get("Account")
    return current_account_id


def get_available_regions(service: str):
    regions = boto3.session.Session().get_available_regions(service)
    logger.debug("The service %s does not have available regions. Returning us-east-1 as default")
    if not regions:
        regions = ["us-east-1"]
    return regions
