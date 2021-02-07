

## Actions

### ACM PCA

* Permissions
acm-pca:CreatePermission
acm-pca:DeletePermission
acm-pca:DeletePolicy
acm-pca:PutPolicy

* `certificate-authority`: `arn:${Partition}:acm-pca:${Region}:${Account}:certificate-authority/${CertificateAuthorityId}`

### API Gateway
apigateway:UpdateRestApiPolicy

* ARN: `arn:${Partition}:apigateway:${Region}::${ApiGatewayResourcePath}`

### AWS Backup

backup:DeleteBackupVaultAccessPolicy
backup:PutBackupVaultAccessPolicy

* `backupVault`: `arn:${Partition}:backup:${Region}:${Account}:backup-vault:${BackupVaultName}`


### Chime
chime:DeleteVoiceConnectorTerminationCredentials
chime:PutVoiceConnectorTerminationCredentials

### CloudSearch
cloudsearch:UpdateServiceAccessPolicies

### CodeArtifact

codeartifact:DeleteDomainPermissionsPolicy
codeartifact:DeleteRepositoryPermissionsPolicy

### CodeBuild

codebuild:DeleteResourcePolicy
codebuild:DeleteSourceCredentials
codebuild:ImportSourceCredentials
codebuild:PutResourcePolicy

### CodeGuru Profiler
codeguru-profiler:PutPermission
codeguru-profiler:RemovePermission

### CodeStar
codestar:AssociateTeamMember
codestar:CreateProject
codestar:DeleteProject
codestar:DisassociateTeamMember
codestar:UpdateTeamMember

### Cognito Identity

cognito-identity:CreateIdentityPool
cognito-identity:DeleteIdentities
cognito-identity:DeleteIdentityPool
cognito-identity:GetId
cognito-identity:MergeDeveloperIdentities
cognito-identity:SetIdentityPoolRoles
cognito-identity:UnlinkDeveloperIdentity
cognito-identity:UnlinkIdentity
cognito-identity:UpdateIdentityPool

### Deeplens

deeplens:AssociateServiceRoleToAccount

### Directory Service
ds:CreateConditionalForwarder
ds:CreateDirectory
ds:CreateMicrosoftAD
ds:CreateTrust
ds:ShareDirectory


### EC2

#### VPC Endpoint Network Interfaces

ec2:CreateNetworkInterfacePermission
ec2:DeleteNetworkInterfacePermission
ec2:ModifyVpcEndpointServicePermissions

#### EC2 Snapshots

ec2:ModifySnapshotAttribute
ec2:ResetSnapshotAttribute

### ECR

* Repositories

ecr:DeleteRepositoryPolicy
ecr:SetRepositoryPolicy
ecr-public:SetRepositoryPolicy

### EFS
elasticfilesystem:DeleteFileSystemPolicy
elasticfilesystem:PutFileSystemPolicy

### EMR
elasticmapreduce:PutBlockPublicAccessConfiguration

### ElasticSearch
es:CreateElasticsearchDomain
es:UpdateElasticsearchDomainConfig

### Glacier

glacier:AbortVaultLock
glacier:CompleteVaultLock
glacier:DeleteVaultAccessPolicy
glacier:InitiateVaultLock
glacier:SetDataRetrievalPolicy
glacier:SetVaultAccessPolicy

### Glue

glue:DeleteResourcePolicy
glue:PutResourcePolicy

### Greengrass

greengrass:AssociateServiceRoleToAccount


### Health

health:DisableHealthServiceAccessForOrganization
health:EnableHealthServiceAccessForOrganization

### IAM Role Trust Policy
iam:AttachRolePolicy

iam:CreatePolicy
iam:CreatePolicyVersion
iam:CreateRole
iam:DeletePolicy
iam:DeletePolicyVersion
iam:DeleteRole
iam:DeleteRolePermissionsBoundary
iam:DeleteRolePolicy
iam:DetachRolePolicy
iam:PassRole
iam:PutRolePermissionsBoundary
iam:PutRolePolicy
iam:UpdateAssumeRolePolicy
iam:UpdateRole

### Image Builder

imagebuilder:GetContainerRecipePolicy
imagebuilder:PutComponentPolicy
imagebuilder:PutContainerRecipePolicy
imagebuilder:PutImagePolicy
imagebuilder:PutImageRecipePolicy

### IOT

iot:AttachPolicy
iot:AttachPrincipalPolicy
iot:DetachPolicy
iot:DetachPrincipalPolicy
iot:SetDefaultAuthorizer
iot:SetDefaultPolicyVersion


### IOT Sitewise

iotsitewise:CreateAccessPolicy
iotsitewise:DeleteAccessPolicy
iotsitewise:UpdateAccessPolicy


### KMS

kms:CreateGrant
kms:PutKeyPolicy
kms:RetireGrant
kms:RevokeGrant

### Lake Formation

lakeformation:BatchGrantPermissions
lakeformation:BatchRevokePermissions
lakeformation:GrantPermissions
lakeformation:PutDataLakeSettings
lakeformation:RevokePermissions

### Lambda

lambda:AddLayerVersionPermission
lambda:AddPermission
lambda:DisableReplication
lambda:EnableReplication
lambda:RemoveLayerVersionPermission
lambda:RemovePermission

### Logs (CloudWatch)

logs:DeleteResourcePolicy
logs:PutResourcePolicy

### MediaStore

mediastore:DeleteContainerPolicy
mediastore:PutContainerPolicy

### OpsWorks

opsworks:SetPermission
opsworks:UpdateUserProfile

### QuickSight

quicksight:CreateAdmin
quicksight:CreateGroup
quicksight:CreateGroupMembership
quicksight:CreateIAMPolicyAssignment
quicksight:CreateUser
quicksight:DeleteGroup
quicksight:DeleteGroupMembership
quicksight:DeleteIAMPolicyAssignment
quicksight:DeleteUser
quicksight:DeleteUserByPrincipalId
quicksight:DescribeDataSetPermissions
quicksight:DescribeDataSourcePermissions
quicksight:RegisterUser
quicksight:UpdateDashboardPermissions
quicksight:UpdateDataSetPermissions
quicksight:UpdateDataSourcePermissions
quicksight:UpdateGroup
quicksight:UpdateIAMPolicyAssignment
quicksight:UpdateTemplatePermissions
quicksight:UpdateUser

### RAM

ram:AcceptResourceShareInvitation
ram:AssociateResourceShare
ram:CreateResourceShare
ram:DeleteResourceShare
ram:DisassociateResourceShare
ram:EnableSharingWithAwsOrganization
ram:RejectResourceShareInvitation
ram:UpdateResourceShare

### Redshift

redshift:AuthorizeSnapshotAccess
redshift:CreateClusterUser
redshift:CreateSnapshotCopyGrant
redshift:JoinGroup
redshift:ModifyClusterIamRoles
redshift:RevokeSnapshotAccess

### Route53 Resolver
route53resolver:PutResolverRulePolicy

### S3
s3:BypassGovernanceRetention
s3:DeleteAccessPointPolicy
s3:DeleteBucketPolicy
s3:ObjectOwnerOverrideToBucketOwner
s3:PutAccessPointPolicy
s3:PutAccountPublicAccessBlock
s3:PutBucketAcl
s3:PutBucketPolicy
s3:PutBucketPublicAccessBlock
s3:PutObjectAcl
s3:PutObjectVersionAcl


### S3 outposts

s3-outposts:DeleteAccessPointPolicy
s3-outposts:DeleteBucketPolicy
s3-outposts:PutAccessPointPolicy
s3-outposts:PutBucketPolicy
s3-outposts:PutObjectAcl

### Secrets Manager

secretsmanager:DeleteResourcePolicy
secretsmanager:PutResourcePolicy
secretsmanager:ValidateResourcePolicy

### Signer

signer:AddProfilePermission
signer:ListProfilePermissions
signer:RemoveProfilePermission

### SNS
sns:AddPermission
sns:CreateTopic
sns:RemovePermission
sns:SetTopicAttributes

### SQS
sqs:AddPermission
sqs:CreateQueue
sqs:RemovePermission
sqs:SetQueueAttributes

### SSM
ssm:ModifyDocumentPermission

### SSO
sso:AssociateDirectory
sso:AssociateProfile
sso:CreateApplicationInstance
sso:CreateApplicationInstanceCertificate
sso:CreatePermissionSet
sso:CreateProfile
sso:CreateTrust
sso:DeleteApplicationInstance
sso:DeleteApplicationInstanceCertificate
sso:DeletePermissionSet
sso:DeletePermissionsPolicy
sso:DeleteProfile
sso:DisassociateDirectory
sso:DisassociateProfile
sso:ImportApplicationInstanceServiceProviderMetadata
sso:PutPermissionsPolicy
sso:StartSSO
sso:UpdateApplicationInstanceActiveCertificate
sso:UpdateApplicationInstanceDisplayData
sso:UpdateApplicationInstanceResponseConfiguration
sso:UpdateApplicationInstanceResponseSchemaConfiguration
sso:UpdateApplicationInstanceSecurityConfiguration
sso:UpdateApplicationInstanceServiceProviderConfiguration
sso:UpdateApplicationInstanceStatus
sso:UpdateDirectoryAssociation
sso:UpdatePermissionSet
sso:UpdateProfile
sso:UpdateSSOConfiguration
sso:UpdateTrust
sso-directory:AddMemberToGroup
sso-directory:CreateAlias
sso-directory:CreateGroup
sso-directory:CreateUser
sso-directory:DeleteGroup
sso-directory:DeleteUser
sso-directory:DisableUser
sso-directory:EnableUser
sso-directory:RemoveMemberFromGroup
sso-directory:UpdateGroup
sso-directory:UpdatePassword
sso-directory:UpdateUser
sso-directory:VerifyEmail


### Storage Gateway

storagegateway:DeleteChapCredentials
storagegateway:SetLocalConsolePassword
storagegateway:SetSMBGuestPassword
storagegateway:UpdateChapCredentials


### WAF

waf:DeletePermissionPolicy
waf:PutPermissionPolicy
waf-regional:DeletePermissionPolicy
waf-regional:PutPermissionPolicy
wafv2:CreateWebACL
wafv2:DeletePermissionPolicy
wafv2:DeleteWebACL
wafv2:PutPermissionPolicy
wafv2:UpdateWebACL
