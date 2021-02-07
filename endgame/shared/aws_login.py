import logging
import boto3
from botocore.config import Config


def get_boto3_client(profile, service: str, region="us-east-1") -> boto3.Session.client:
    logging.getLogger('botocore').setLevel(logging.CRITICAL)
    session_data = {"region_name": region}
    if profile:
        session_data["profile_name"] = profile
    session = boto3.Session(**session_data)
    config = Config(connect_timeout=5, retries={"max_attempts": 10})
    client = session.client(service, config=config)
    return client


def get_current_account_id(sts_client: boto3.Session.client) -> str:
    response = sts_client.get_caller_identity()
    current_account_id = response.get("Account")
    return current_account_id
