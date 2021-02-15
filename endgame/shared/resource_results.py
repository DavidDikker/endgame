import logging
import botocore
from botocore.exceptions import ClientError
from endgame.shared import utils, constants
from endgame.shared.aws_login import get_boto3_client, get_current_account_id, get_available_regions
from endgame.shared.list_resources_response import ListResourcesResponse
from endgame.exposure_via_resource_policies import glacier_vault, sqs, lambda_layer, lambda_function, kms, \
    cloudwatch_logs, efs, s3, sns, iam, ecr, secrets_manager, ses, elasticsearch, acm_pca
from endgame.exposure_via_sharing_apis import rds_snapshots, ebs_snapshots, ec2_amis

logger = logging.getLogger(__name__)


class ResourceResults:
    """A list of resources across all services"""

    def __init__(self, user_provided_service: str, user_provided_region: str,
                 current_account_id: str, excluded_names: list = None, excluded_services: list = None, profile: str = None,
                 cloak: bool = False):

        self.user_provided_service = user_provided_service
        self.user_provided_region = user_provided_region
        self.profile = profile
        self.current_account_id = current_account_id
        self.cloak = cloak
        if excluded_names:
            self.excluded_names = excluded_names
        else:
            self.excluded_names = []
        if excluded_services:
            self.excluded_services = excluded_services
        else:
            self.excluded_services = []
        self.resources = self._resources()

    def _resources(self) -> [ListResourcesResponse]:
        """Get all the resources from all specified services from all specified regions"""
        resources = []
        if self.user_provided_service == "all":
            for supported_service in constants.SUPPORTED_AWS_SERVICES:
                if supported_service not in self.excluded_services:
                    if supported_service != "all":
                        logger.info("Creating a list of resources for %s" % supported_service)
                        service_resources = ServiceResourcesMultiRegion(user_provided_service=supported_service,
                                                                        user_provided_region=self.user_provided_region,
                                                                        current_account_id=self.current_account_id,
                                                                        profile=self.profile,
                                                                        cloak=self.cloak)
                        resources.extend(service_resources.resources)
        else:
            logger.info("Combing through resources for %s" % self.user_provided_service)
            service_resources = ServiceResourcesMultiRegion(user_provided_service=self.user_provided_service,
                                                            user_provided_region=self.user_provided_region,
                                                            current_account_id=self.current_account_id,
                                                            profile=self.profile,
                                                            cloak=self.cloak)
            resources.extend(service_resources.resources)
        return resources

    def arns(self) -> [str]:
        """Get all the resource ARNs from all specified services from all specified regions"""
        arns = []
        if self.user_provided_service == "all":
            for supported_service in constants.SUPPORTED_AWS_SERVICES:
                if supported_service not in self.excluded_services:
                    if supported_service != "all":
                        service_resources = ServiceResourcesMultiRegion(user_provided_service=supported_service,
                                                                        user_provided_region=self.user_provided_region,
                                                                        current_account_id=self.current_account_id,
                                                                        profile=self.profile,
                                                                        cloak=self.cloak)
                        arns.extend(service_resources.arns)
        else:
            service_resources = ServiceResourcesMultiRegion(user_provided_service=self.user_provided_service,
                                                            user_provided_region=self.user_provided_region,
                                                            current_account_id=self.current_account_id,
                                                            profile=self.profile,
                                                            cloak=self.cloak)
            arns.extend(service_resources.arns)
        return arns


class ServiceResourcesMultiRegion:
    def __init__(
            self,
            user_provided_service: str,
            user_provided_region: str,
            current_account_id: str,
            profile: str = None,
            cloak: bool = False
    ):
        self.user_provided_service = user_provided_service
        self.boto_service = utils.get_service_translation(provided_service=user_provided_service)
        self.user_provided_region = user_provided_region
        self.current_account_id = current_account_id
        self.profile = profile
        self.cloak = cloak
        self.regions = self._regions()
        # Save the name of the service for boto3 usage
        self.resources = self._resources()

    def _regions(self) -> list:
        """List of regions to list things for."""
        if self.user_provided_region == "all":
            regions = get_available_regions(self.boto_service)
        else:
            regions = [self.user_provided_region]
        return regions

    def _resources(self) -> [ListResourcesResponse]:
        """Get all the resources within specified regions"""
        resources = []
        for region in self.regions:
            logger.debug(f"Listing resources for {self.user_provided_service} in {region}")
            try:
                region_resources = ServiceResourcesSingleRegion(user_provided_service=self.user_provided_service,
                                                                region=region,
                                                                current_account_id=self.current_account_id,
                                                                profile=self.profile,
                                                                cloak=self.cloak)
                resources.extend(region_resources.resources.resources)
            except botocore.exceptions.ClientError as error:
                logger.debug(f"The service {self.boto_service} might not exist in the region {region}. Error: {error}")
        return resources

    @property
    def arns(self) -> [str]:
        arns = []
        for resource in self.resources:
            arns.append(resource.arn)
        return arns


class ServiceResourcesSingleRegion:
    """A list of all the resources under a particular service in a particular region"""

    def __init__(
            self,
            user_provided_service: str,
            region: str,
            current_account_id: str,
            profile: str = None,
            cloak: bool = False
    ):
        self.user_provided_service = user_provided_service
        # Save the name of the service for boto3 usage
        self.boto_service = utils.get_service_translation(provided_service=user_provided_service)
        self.region = region
        self.current_account_id = current_account_id
        self.client = get_boto3_client(profile=profile, service=self.boto_service, region=self.region, cloak=cloak)
        self.resources = self._resources()

    @property
    def arns(self) -> [str]:
        arns = []
        results = self.resources
        for resource in results.resources:
            arns.append(resource.arn)
        return arns

    def _resources(self) -> [ListResourcesResponse]:
        resources = None
        if self.user_provided_service == "acm-pca":
            resources = acm_pca.AcmPrivateCertificateAuthorities(client=self.client,
                                                                 current_account_id=self.current_account_id,
                                                                 region=self.region)
        elif self.user_provided_service == "ecr":
            resources = ecr.EcrRepositories(client=self.client, current_account_id=self.current_account_id,
                                            region=self.region)
        elif self.user_provided_service == "efs":
            resources = efs.ElasticFileSystems(client=self.client, current_account_id=self.current_account_id,
                                               region=self.region)
        elif self.user_provided_service == "elasticsearch":
            resources = elasticsearch.ElasticSearchDomains(client=self.client,
                                                           current_account_id=self.current_account_id,
                                                           region=self.region)
        elif self.user_provided_service == "glacier":
            resources = glacier_vault.GlacierVaults(client=self.client, current_account_id=self.current_account_id,
                                                    region=self.region)
        elif self.user_provided_service == "iam":
            resources = iam.IAMRoles(client=self.client, current_account_id=self.current_account_id, region=self.region)
        elif self.user_provided_service == "kms":
            resources = kms.KmsKeys(client=self.client, current_account_id=self.current_account_id, region=self.region)
        elif self.user_provided_service == "lambda":
            resources = lambda_function.LambdaFunctions(client=self.client, current_account_id=self.current_account_id,
                                                        region=self.region)
        elif self.user_provided_service == "lambda-layer":
            resources = lambda_layer.LambdaLayers(client=self.client, current_account_id=self.current_account_id,
                                                  region=self.region)
        elif self.user_provided_service == "cloudwatch":
            resources = cloudwatch_logs.CloudwatchResourcePolicies(client=self.client,
                                                                   current_account_id=self.current_account_id,
                                                                   region=self.region)
        elif self.user_provided_service == "s3":
            resources = s3.S3Buckets(client=self.client, current_account_id=self.current_account_id, region=self.region)
        elif self.user_provided_service == "ses":
            resources = ses.SesIdentityPolicies(client=self.client, current_account_id=self.current_account_id,
                                                region=self.region)
        elif self.user_provided_service == "sns":
            resources = sns.SnsTopics(client=self.client, current_account_id=self.current_account_id,
                                      region=self.region)
        elif self.user_provided_service == "sqs":
            resources = sqs.SqsQueues(client=self.client, current_account_id=self.current_account_id,
                                      region=self.region)
        elif self.user_provided_service == "secretsmanager":
            resources = secrets_manager.SecretsManagerSecrets(client=self.client,
                                                              current_account_id=self.current_account_id,
                                                              region=self.region)
        elif self.user_provided_service == "rds":
            resources = rds_snapshots.RdsSnapshots(client=self.client, current_account_id=self.current_account_id,
                                                   region=self.region)
        elif self.user_provided_service == "ebs":
            resources = ebs_snapshots.EbsSnapshots(client=self.client, current_account_id=self.current_account_id,
                                                   region=self.region)
        elif self.user_provided_service == "ec2-ami":
            resources = ec2_amis.Ec2Images(client=self.client, current_account_id=self.current_account_id,
                                           region=self.region)
        return resources


"""
    if region == "all":
        logger.info("Listing resources in ALL regions")
        regions = get_available_regions(translated_service)
        logger.debug(f"Regions available: {', '.join(regions)}")
        for region in regions:
            list_resources_by_region(service=service, profile=profile, region=self.region, cloak=cloak,
                                     excluded_names=excluded_names, current_account_id=self.current_account_id)
    else:
        logger.info("Listing resources in %s" % region)
        list_resources_by_region(service=service, profile=profile, region=self.region, cloak=cloak,
                                 excluded_names=excluded_names, current_account_id=self.current_account_id)

"""
