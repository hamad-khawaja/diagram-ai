# AWS Diagrams: Concise Instructions

Use the diagrams library (https://diagrams.mingrammer.com/) to generate AWS architecture diagrams.

**VPC Cluster Rules:**
- Only place network and compute resources inside a VPC cluster:
  - EC2, Security Groups, Subnets (as clusters), Load Balancers, NAT/Internet Gateways, Route Tables, Network ACLs, Elastic IPs
- Do NOT place S3, RDS, Lambda, DynamoDB, SQS, SNS, CloudFront, API Gateway, Cognito, or any PaaS/SaaS service inside a VPC cluster unless explicitly deployed into a subnet.

**Cluster Usage:**
- `with Cluster("VPC <name>"):` for VPC
- Nested: `with Cluster("Subnet <name>"):`

**Imports:**
- Only use valid AWS resources from diagrams library: https://diagrams.mingrammer.com/docs/nodes/aws/

**Example:**
```python
from diagrams import Diagram, Cluster
from diagrams.aws.network import VPC, PublicSubnet, PrivateSubnet, SecurityGroup, NATGateway, InternetGateway, ELB
from diagrams.aws.compute import EC2

with Diagram("AWS VPC Example", show=False):
    with Cluster("VPC my-vpc"):
        igw = InternetGateway("IGW")
        with Cluster("Public Subnet"):
            ec2_public = EC2("Web EC2")
            nat = NATGateway("NAT GW")
        with Cluster("Private Subnet"):
            ec2_private = EC2("App EC2")
            sg = SecurityGroup("App SG")
        elb = ELB("LB")
    igw >> ec2_public
    ec2_public >> nat >> ec2_private
    elb >> ec2_public
```

**Best Practices:**
- Use only resources present in the diagrams library.
- Check official docs for available AWS nodes.
- Add comments and use meaningful names.
from diagrams import Diagram
from diagrams.aws.compute import EC2
from diagrams.aws.database import RDS
from diagrams.aws.network import ELB

with Diagram("AWS Web Service", show=False):
    ELB("lb") >> EC2("web") >> RDS("userdb")
```

### Diagram Parameters

```python
from diagrams import Diagram
from diagrams.aws.compute import EC2

# Basic diagram with custom filename
with Diagram("AWS Architecture", filename="my_aws_diagram", show=False):
    EC2("web-server")

# Multiple output formats
with Diagram("AWS Multi-Output", outformat=["jpg", "png", "dot"], show=False):
    EC2("web-server")

# Custom attributes
graph_attr = {
    "fontsize": "45",
    "bgcolor": "transparent"
}
with Diagram("AWS Custom Style", show=False, graph_attr=graph_attr):
    EC2("web-server")
```

## More Guilelines

### Node Connections (Data Flow)
```python
# Basic connections
node1 >> node2  # Forward flow
node1 << node2  # Reverse flow  
node1 - node2   # Bidirectional

# Group connections
source >> [node1, node2, node3] >> destination

# Multiple sources to multiple destinations
[source1, source2] >> [dest1, dest2]
```

### Clusters (Grouping)
```python
from diagrams import Cluster, Diagram
from diagrams.aws.compute import EC2
from diagrams.aws.database import RDS

with Diagram("Clustered Architecture", show=False):
    with Cluster("Web Tier"):
        web_servers = [EC2("web1"), EC2("web2")]
    
    with Cluster("Database Tier"):
        db_primary = RDS("primary")
        db_replica = RDS("replica")
        db_primary - db_replica
    
    web_servers >> db_primary
```

### Edges with Custom Properties
```python
from diagrams import Edge

# Custom edge styling
source >> Edge(
    label="HTTPS",
    color="red", 
    style="dashed",
    minlen="2"
) >> destination


### Converting CloudFormation Templates (AWS)

CloudFormation templates can be in JSON or YAML format with Resources section being required:

1. **Parse template structure**:
```python
# CloudFormation Resource → Diagrams Node Mapping
"AWS::EC2::Instance" → EC2 (from diagrams.aws.compute)
"AWS::RDS::DBInstance" → RDS (from diagrams.aws.database)
"AWS::S3::Bucket" → S3 (from diagrams.aws.storage)
"AWS::ElasticLoadBalancing::LoadBalancer" → ELB (from diagrams.aws.network)
"AWS::Lambda::Function" → Lambda (from diagrams.aws.compute)
"AWS::AutoScaling::AutoScalingGroup" → AutoScaling (from diagrams.aws.compute)
"AWS::CloudFront::Distribution" → CloudFront (from diagrams.aws.network)
"AWS::Route53::RecordSet" → Route53 (from diagrams.aws.network)
"AWS::ECS::Service" → ECS (from diagrams.aws.compute)
"AWS::EKS::Cluster" → EKS (from diagrams.aws.compute)
```

2. **Handle CloudFormation-specific constructs**:
   - `Ref` functions → Create variable references between nodes
   - `DependsOn` → Direct node connections
   - `Parameters` → Use as diagram labels or node names
   - Nested stacks → Use nested Clusters

3. **Process template sections**:
```python
# Example CloudFormation to Diagrams conversion
def convert_cloudformation(template):
    resources = template.get('Resources', {})
    parameters = template.get('Parameters', {})
    
    # Group resources by logical relationships
    web_tier = []
    app_tier = []
    data_tier = []
    
    for logical_id, resource in resources.items():
        resource_type = resource['Type']
        if resource_type == 'AWS::EC2::Instance':
            # Check properties to determine tier
            if 'web' in logical_id.lower():
                web_tier.append(EC2(logical_id))
```


## IaC Conversion Algorithm

```python
def convert_iac_to_diagram(file_content, file_type):
    """
    Universal IaC to diagrams converter
    """
    if file_type == "terraform_state":
        return convert_terraform_state(file_content)
    elif file_type == "cloudformation":
        return convert_cloudformation(file_content)
    elif file_type == "arm_template":
        return convert_arm_template(file_content)

def convert_terraform_state(state_content):
    """
    Convert Terraform state to diagrams code
    """
    with Diagram("Infrastructure from Terraform", show=False):
        # Parse resources from state
        resources = state_content.get('resources', [])
        
        # Group by provider
        aws_resources = []
        azure_resources = []
        gcp_resources = []
        
        for resource in resources:
            provider = resource.get('provider', '')
            if 'aws' in provider:
                aws_resources.append(resource)
            elif 'azurerm' in provider:
                azure_resources.append(resource)
            elif 'google' in provider:
                gcp_resources.append(resource)
        
        # Create clusters by provider/environment
        if aws_resources:
            with Cluster("AWS Resources"):
                # Convert AWS resources
                pass
        
        if azure_resources:
            with Cluster("Azure Resources"):
                # Convert Azure resources
                pass
```

### Best Practices for IaC Conversion

1. **Provider Detection**:
   - Terraform: Look at `provider` field in state or resource prefixes
   - CloudFormation: All resources are AWS (AWS::*)
   - ARM: All resources are Azure (Microsoft.*)

2. **Resource Grouping Strategies**:
   - **By Environment**: dev, staging, prod clusters
   - **By Application Tier**: web, app, database clusters  
   - **By Network**: VPC, subnet, availability zone clusters
   - **By Service**: microservice boundary clusters

3. **Relationship Mapping**:
   - Parse `depends_on` explicitly
   - Infer relationships from resource references
   - Use security group and network ACL associations
   - Map load balancer target relationships

4. **Naming Conventions**:
   - Use original resource names from IaC when possible
   - Fallback to resource types for unnamed resources
   - Include environment/region info in cluster names

5. **Handle Complex Scenarios**:
   - Multi-region deployments → Multiple diagrams or region clusters
   - Auto-scaling groups → Show representative instances
   - Kubernetes resources → Use k8s-specific diagrams nodes

### Error Handling and Validation

1. **Unknown Resources**: 
   - Map to Generic nodes when specific diagrams node unavailable
   - Log unmapped resources for manual review
   - Suggest Custom nodes with appropriate icons

2. **Complex Dependencies**:
   - Simplify circular dependencies
   - Group tightly coupled resources
   - Use edge labels for complex relationships

3. **Large Infrastructures**:
   - Create multiple focused diagrams
   - Use hierarchical clustering
   - Consider separate network and compute diagrams

## AWS Resource Categories

### Analytics (`diagrams.aws.analytics`)

```python
from diagrams.aws.analytics import (
    AmazonOpensearchService,
    Analytics,
    Athena,
    CloudsearchSearchDocuments,
    Cloudsearch,
    DataLakeResource,
    DataPipeline,
    ElasticsearchService, ES,  # ES is alias
    EMRCluster,
    EMREngineMaprM3,
    EMREngineMaprM5,
    EMREngineMaprM7,
    EMREngine,
    EMRHdfsCluster,
    EMR,
    GlueCrawlers,
    GlueDataCatalog,
    Glue,
    KinesisDataAnalytics,
    KinesisDataFirehose,
    KinesisDataStreams,
    KinesisVideoStreams,
    Kinesis,
    LakeFormation,
    ManagedStreamingForKafka,
    Quicksight,
    RedshiftDenseComputeNode,
    RedshiftDenseStorageNode,
    Redshift
)
```

**Example:**
```python
from diagrams import Diagram, Cluster
from diagrams.aws.analytics import Kinesis, Glue, Athena, Redshift

with Diagram("AWS Analytics Pipeline", show=False):
    with Cluster("Data Ingestion"):
        kinesis = Kinesis("Kinesis Streams")
    
    with Cluster("Data Processing"):
        glue = Glue("AWS Glue")
    
    with Cluster("Data Warehouse"):
        redshift = Redshift("Redshift")
    
    with Cluster("Query Service"):
        athena = Athena("Athena")
    
    kinesis >> glue >> [redshift, athena]
```

### AR/VR (`diagrams.aws.ar`)

```python
from diagrams.aws.ar import (
    ArVr,
    Sumerian
)
```

### Blockchain (`diagrams.aws.blockchain`)

```python
from diagrams.aws.blockchain import (
    BlockchainResource,
    Blockchain,
    ManagedBlockchain,
    QuantumLedgerDatabaseQldb, QLDB  # QLDB is alias
)
```

### Business Applications (`diagrams.aws.business`)

```python
from diagrams.aws.business import (
    AlexaForBusiness, A4B,  # A4B is alias
    BusinessApplications,
    Chime,
    Workmail
)
```

### Compute (`diagrams.aws.compute`)

```python
from diagrams.aws.compute import (
    AppRunner,
    ApplicationAutoScaling, AutoScaling,  # AutoScaling is alias
    Batch,
    ComputeOptimizer,
    Compute,
    EC2Ami, AMI,  # AMI is alias
    EC2AutoScaling,
    EC2ContainerRegistryImage,
    EC2ContainerRegistryRegistry,
    EC2ContainerRegistry, ECR,  # ECR is alias
    EC2ElasticIpAddress,
    EC2ImageBuilder,
    EC2Instance,
    EC2Instances,
    EC2Rescue,
    EC2SpotInstance,
    EC2,
    ElasticBeanstalkApplication,
    ElasticBeanstalkDeployment,
    ElasticBeanstalk, EB,  # EB is alias
    ElasticContainerServiceContainer,
    ElasticContainerServiceService,
    ElasticContainerService, ECS,  # ECS is alias
    ElasticKubernetesService, EKS,  # EKS is alias
    Fargate,
    LambdaFunction,
    Lambda,
    Lightsail,
    LocalZones,
    Outposts,
    ServerlessApplicationRepository, SAR,  # SAR is alias
    ThinkboxDeadline,
    ThinkboxDraft,
    ThinkboxFrost,
    ThinkboxKrakatoa,
    ThinkboxSequoia,
    ThinkboxStoke,
    ThinkboxXmesh,
    VmwareCloudOnAWS,
    Wavelength
)
```

**Example:**
```python
from diagrams import Diagram, Cluster
from diagrams.aws.compute import EC2, ECS, Lambda, EKS

with Diagram("AWS Compute Services", show=False):
    with Cluster("Virtual Machines"):
        instances = [EC2("Web-1"), EC2("Web-2"), EC2("Web-3")]
    
    with Cluster("Containers"):
        ecs_service = ECS("ECS Service")
        eks_cluster = EKS("EKS Cluster")
    
    with Cluster("Serverless"):
        lambda_func = Lambda("Lambda Function")
    
    instances >> ecs_service
    ecs_service >> eks_cluster
    eks_cluster >> lambda_func
```

### Cost Management (`diagrams.aws.cost`)

```python
from diagrams.aws.cost import (
    Budgets,
    CostAndUsageReport,
    CostExplorer,
    CostManagement,
    ReservedInstanceReporting,
    SavingsPlans
)
```

### Database (`diagrams.aws.database`)

```python
from diagrams.aws.database import (
    AuroraInstance,
    Aurora,
    DatabaseMigrationServiceDatabaseMigrationWorkflow,
    DatabaseMigrationService, DMS,  # DMS is alias
    Database, DB,  # DB is alias
    DocumentdbMongodbCompatibility, DocumentDB,  # DocumentDB is alias
    DynamodbAttribute,
    DynamodbAttributes,
    DynamodbDax, DAX,  # DAX is alias
    DynamodbGlobalSecondaryIndex, DynamodbGSI,  # DynamodbGSI is alias
    DynamodbItem,
    DynamodbItems,
    DynamodbStreams,
    DynamodbTable,
    Dynamodb, DDB,  # DDB is alias
    ElasticacheCacheNode,
    ElasticacheForMemcached,
    ElasticacheForRedis,
    Elasticache, ElastiCache,  # ElastiCache is alias
    KeyspacesManagedApacheCassandraService,
    Neptune,
    QuantumLedgerDatabaseQldb, QLDB,  # QLDB is alias
    RDSInstance,
    RDSMariadbInstance,
    RDSMysqlInstance,
    RDSOnVmware,
    RDSOracleInstance,
    RDSPostgresqlInstance,
    RDSSqlServerInstance,
    RDS,
    RedshiftDenseComputeNode,
    RedshiftDenseStorageNode,
    Redshift,
    Timestream
)
```

**Example:**
```python
from diagrams import Diagram, Cluster
from diagrams.aws.database import RDS, DynamoDB, ElastiCache, Aurora

with Diagram("AWS Database Architecture", show=False):
    with Cluster("Relational Databases"):
        rds = RDS("RDS MySQL")
        aurora = Aurora("Aurora")
    
    with Cluster("NoSQL"):
        dynamodb = DynamoDB("DynamoDB")
    
    with Cluster("Caching"):
        elasticache = ElastiCache("ElastiCache Redis")
    
    rds >> elasticache
    aurora >> elasticache
    dynamodb >> elasticache
```

### Developer Tools (`diagrams.aws.devtools`)

```python
from diagrams.aws.devtools import (
    CloudDevelopmentKit,
    Cloud9Resource,
    Cloud9,
    Codeartifact,
    Codebuild,
    Codecommit,
    Codedeploy,
    Codepipeline,
    Codestar,
    CommandLineInterface, CLI,  # CLI is alias
    DeveloperTools, DevTools,  # DevTools is alias
    ToolsAndSdks,
    XRay
)
```

### Integration (`diagrams.aws.integration`)

```python
from diagrams.aws.integration import (
    ApplicationIntegration,
    Appsync,
    ConsoleMobileApplication,
    EventResource,
    EventbridgeCustomEventBusResource,
    EventbridgeDefaultEventBusResource,
    EventbridgeSaasPartnerEventBusResource,
    Eventbridge,
    ExpressWorkflows,
    MQ,
    SimpleNotificationServiceSnsEmailNotification,
    SimpleNotificationServiceSnsHttpNotification,
    SimpleNotificationServiceSnsTopic,
    SimpleNotificationServiceSns, SNS,  # SNS is alias
    SimpleQueueServiceSqsMessage,
    SimpleQueueServiceSqsQueue,
    SimpleQueueServiceSqs, SQS,  # SQS is alias
    StepFunctions, SF  # SF is alias
)
```

### IoT (`diagrams.aws.iot`)

```python
from diagrams.aws.iot import (
    Freertos, FreeRTOS,  # FreeRTOS is alias
    InternetOfThings,
    Iot1Click,
    IotAction,
    IotActuator,
    IotAlexaEcho,
    IotAlexaEnabledDevice,
    IotAlexaSkill,
    IotAlexaVoiceService,
    IotAnalyticsChannel,
    IotAnalyticsDataSet,
    IotAnalyticsDataStore,
    IotAnalyticsNotebook,
    IotAnalyticsPipeline,
    IotAnalytics,
    IotBank,
    IotBicycle,
    IotButton,
    IotCamera,
    IotCar,
    IotCart,
    IotCertificate,
    IotCoffeePot,
    IotCore,
    IotDesiredState,
    IotDeviceDefender,
    IotDeviceGateway,
    IotDeviceManagement,
    IotDoorLock,
    IotEvents,
    IotFactory,
    IotFireTvStick,
    IotFireTv,
    IotGeneric,
    IotGreengrassConnector,
    IotGreengrass,
    IotHardwareBoard, IotBoard,  # IotBoard is alias
    IotHouse,
    IotHttp,
    IotHttp2,
    IotJobs,
    IotLambda,
    IotLightbulb,
    IotMedicalEmergency,
    IotMqtt,
    IotOverTheAirUpdate,
    IotPolicyEmergency,
    IotPolicy,
    IotReportedState,
    IotRule,
    IotSensor,
    IotServo,
    IotShadow,
    IotSimulator,
    IotSitewise,
    IotThermostat,
    IotThingsGraph,
    IotTopic,
    IotTravel,
    IotUtility,
    IotWindfarm
)
```

### Machine Learning (`diagrams.aws.ml`)

```python
from diagrams.aws.ml import (
    ApacheMxnetOnAWS,
    AugmentedAi,
    Bedrock,
    Comprehend,
    DeepLearningAmis,
    DeepLearningContainers, DLC,  # DLC is alias
    Deepcomposer,
    Deeplens,
    Deepracer,
    ElasticInference,
    Forecast,
    FraudDetector,
    Kendra,
    Lex,
    MachineLearning,
    Personalize,
    Polly,
    RekognitionImage,
    RekognitionVideo,
    Rekognition,
    SagemakerGroundTruth,
    SagemakerModel,
    SagemakerNotebook,
    SagemakerTrainingJob,
    Sagemaker,
    TensorflowOnAWS,
    Textract,
    Transcribe,
    Translate
)
```

### Network (`diagrams.aws.network`)

```python
from diagrams.aws.network import (
    APIGatewayEndpoint,
    APIGateway,
    AppMesh,
    ClientVpn,
    CloudMap,
    CloudFrontDownloadDistribution,
    CloudFrontEdgeLocation,
    CloudFrontStreamingDistribution,
    CloudFront, CF,  # CF is alias
    DirectConnect,
    ElasticLoadBalancing, ELB,  # ELB is alias
    ElbApplicationLoadBalancer, ALB,  # ALB is alias
    ElbClassicLoadBalancer, CLB,  # CLB is alias
    ElbNetworkLoadBalancer, NLB,  # NLB is alias
    Endpoint,
    GlobalAccelerator, GAX,  # GAX is alias
    InternetGateway, IGW,  # IGW is alias
    Nacl,
    NATGateway,
    NetworkFirewall,
    NetworkingAndContentDelivery,
    PrivateSubnet,
    Privatelink,
    PublicSubnet,
    Route53HostedZone,
    Route53,
    RouteTable,
    SiteToSiteVpn,
    TransitGatewayAttachment, TGWAttach,  # TGWAttach is alias
    TransitGateway, TGW,  # TGW is alias
    VPCCustomerGateway,
    VPCElasticNetworkAdapter,
    VPCElasticNetworkInterface,
    VPCFlowLogs,
    VPCPeering,
    VPCRouter,
    VPCTrafficMirroring,
    VPC,
    VpnConnection,
    VpnGateway
)
```

**Example:**
```python
from diagrams import Diagram, Cluster
from diagrams.aws.network import ELB, ALB, Route53, VPC, CloudFront
from diagrams.aws.compute import EC2

with Diagram("AWS Network Architecture", show=False):
    with Cluster("Global"):
        dns = Route53("Route 53")
        cdn = CloudFront("CloudFront")
    
    with Cluster("Load Balancing"):
        alb = ALB("Application LB")
        elb = ELB("Classic LB")
    
    with Cluster("VPC"):
        vpc = VPC("VPC")
        instances = [EC2("Web-1"), EC2("Web-2")]
    
    dns >> cdn >> alb >> vpc
    vpc >> instances
    elb >> instances
```

### Security (`diagrams.aws.security`)

```python
from diagrams.aws.security import (
    AdConnector,
    Artifact,
    CertificateAuthority,
    CertificateManager, ACM,  # ACM is alias
    CloudDirectory,
    Cloudhsm, CloudHSM,  # CloudHSM is alias
    Cognito,
    Detective,
    DirectoryService, DS,  # DS is alias
    FirewallManager, FMS,  # FMS is alias
    Guardduty,
    IdentityAndAccessManagementIamAccessAnalyzer, IAMAccessAnalyzer,  # IAMAccessAnalyzer is alias
    IdentityAndAccessManagementIamAddOn,
    IdentityAndAccessManagementIamAWSStsAlternate,
    IdentityAndAccessManagementIamAWSSts, IAMAWSSts,  # IAMAWSSts is alias
    IdentityAndAccessManagementIamDataEncryptionKey,
    IdentityAndAccessManagementIamEncryptedData,
    IdentityAndAccessManagementIamLongTermSecurityCredential,
    IdentityAndAccessManagementIamMfaToken,
    IdentityAndAccessManagementIamPermissions, IAMPermissions,  # IAMPermissions is alias
    IdentityAndAccessManagementIamRole, IAMRole,  # IAMRole is alias
    IdentityAndAccessManagementIamTemporarySecurityCredential,
    IdentityAndAccessManagementIam, IAM,  # IAM is alias
    InspectorAgent,
    Inspector,
    KeyManagementService, KMS,  # KMS is alias
    Macie,
    ManagedMicrosoftAd,
    ResourceAccessManager, RAM,  # RAM is alias
    SecretsManager,
    SecurityHubFinding,
    SecurityHub,
    SecurityIdentityAndCompliance,
    ShieldAdvanced,
    Shield,
    SimpleAd,
    SingleSignOn,
    WAFFilteringRule,
    WAF
)
```

### Storage (`diagrams.aws.storage`)

```python
from diagrams.aws.storage import (
    Backup,
    CloudendureDisasterRecovery, CDR,  # CDR is alias
    EFSInfrequentaccessPrimaryBg,
    EFSStandardPrimaryBg,
    ElasticBlockStoreEBSSnapshot,
    ElasticBlockStoreEBSVolume,
    ElasticBlockStoreEBS, EBS,  # EBS is alias
    ElasticFileSystemEFSFileSystem,
    ElasticFileSystemEFS, EFS,  # EFS is alias
    FsxForLustre,
    FsxForWindowsFileServer,
    Fsx, FSx,  # FSx is alias
    MultipleVolumesResource,
    S3AccessPoints,
    S3GlacierArchive,
    S3GlacierVault,
    S3Glacier,
    S3ObjectLambdaAccessPoints,
    SimpleStorageServiceS3BucketWithObjects,
    SimpleStorageServiceS3Bucket,
    SimpleStorageServiceS3Object,
    SimpleStorageServiceS3, S3,  # S3 is alias
    SnowFamilySnowballImportExport,
    SnowballEdge,
    Snowball,
    Snowmobile,
    StorageGatewayCachedVolume,
    StorageGatewayNonCachedVolume,
    StorageGatewayVirtualTapeLibrary,
    StorageGateway,
    Storage
)
```

**Example:**
```python
from diagrams import Diagram, Cluster
from diagrams.aws.storage import S3, EBS, EFS
from diagrams.aws.compute import EC2

with Diagram("AWS Storage Architecture", show=False):
    with Cluster("Object Storage"):
        s3 = S3("S3 Bucket")
    
    with Cluster("Block Storage"):
        ebs = EBS("EBS Volume")
        ec2 = EC2("EC2 Instance")
    
    with Cluster("File Storage"):
        efs = EFS("EFS")
    
    ec2 >> ebs
    ec2 >> efs
    ec2 >> s3
```

## Connection Operators

### Data Flow Direction

- `>>` - Left to right flow
- `<<` - Right to left flow  
- `-` - Bidirectional connection

```python
from diagrams import Diagram
from diagrams.aws.compute import EC2
from diagrams.aws.database import RDS
from diagrams.aws.storage import S3

with Diagram("AWS Data Flow", show=False):
    web = EC2("Web Server")
    db = RDS("Database")
    storage = S3("S3 Storage")
    
    # Left to right flow
    web >> db
    
    # Right to left flow
    storage << web
    
    # Bidirectional
    web - storage
```

## Clustering

Group related resources using `Cluster`:

```python
from diagrams import Diagram, Cluster
from diagrams.aws.compute import EC2, ECS
from diagrams.aws.database import RDS
from diagrams.aws.network import ELB

with Diagram("AWS Clustered Architecture", show=False):
    with Cluster("Frontend"):
        lb = ELB("Load Balancer")
        frontend_vms = [EC2("Web-1"), EC2("Web-2")]
    
    with Cluster("Application"):
        ecs = ECS("ECS Service")
    
    with Cluster("Database"):
        db_primary = RDS("Primary DB")
        db_replica = RDS("Read Replica")
        db_primary - db_replica
    
    lb >> frontend_vms >> ecs >> db_primary
```

## Advanced Examples

### Complete AWS Web Application

```python
from diagrams import Diagram, Cluster, Edge
from diagrams.aws.compute import EC2, Lambda
from diagrams.aws.database import RDS, DynamoDB
from diagrams.aws.network import ELB, CloudFront, Route53
from diagrams.aws.storage import S3
from diagrams.aws.security import IAM, KMS
from diagrams.aws.management import Cloudwatch

with Diagram("AWS Web Application", show=False, direction="TB"):
    # Global Services
    dns = Route53("Route 53")
    cdn = CloudFront("CloudFront")
    
    with Cluster("Application Layer"):
        lb = ELB("Load Balancer")
        web_servers = [EC2("Web-1"), EC2("Web-2"), EC2("Web-3")]
        lambda_func = Lambda("Lambda Function")
    
    with Cluster("Data Layer"):
        rds = RDS("RDS MySQL")
        dynamodb = DynamoDB("DynamoDB")
        s3 = S3("S3 Storage")
    
    with Cluster("Security & Monitoring"):
        iam = IAM("IAM")
        kms = KMS("KMS")
        cloudwatch = Cloudwatch("CloudWatch")
    
    # Connections
    dns >> cdn >> lb >> web_servers
    web_servers >> [rds, dynamodb]
    lambda_func >> s3
    
    # Security connections
    web_servers >> Edge(style="dashed") >> iam
    lambda_func >> Edge(style="dashed") >> kms
    
    # Monitoring
    [web_servers, lambda_func] >> Edge(color="orange") >> cloudwatch
```

### AWS Serverless Architecture

```python
from diagrams import Diagram, Cluster
from diagrams.aws.compute import Lambda
from diagrams.aws.database import DynamoDB
from diagrams.aws.integration import SQS, SNS
from diagrams.aws.network import APIGateway
from diagrams.aws.storage import S3

with Diagram("AWS Serverless Architecture", show=False, direction="LR"):
    with Cluster("API Layer"):
        api = APIGateway("API Gateway")
    
    with Cluster("Compute"):
        functions = [
            Lambda("Auth Function"),
            Lambda("Process Function"),
            Lambda("Notification Function")
        ]
    
    with Cluster("Data Storage"):
        dynamodb = DynamoDB("DynamoDB")
        s3 = S3("S3 Storage")
    
    with Cluster("Messaging"):
        sqs = SQS("SQS Queue")
        sns = SNS("SNS Topic")
    
    # API flow
    api >> functions[0] >> dynamodb
    functions[0] >> functions[1] >> s3
    functions[1] >> sqs >> functions[2]
    functions[2] >> sns
```

### AWS Microservices with EKS

```python
from diagrams import Diagram, Cluster
from diagrams.aws.compute import EKS, ECR
from diagrams.aws.database import RDS, DynamoDB
from diagrams.aws.network import ALB, Route53
from diagrams.aws.devtools import Codepipeline, Codebuild

with Diagram("AWS Microservices with EKS", show=False, direction="TB"):
    # CI/CD
    with Cluster("CI/CD Pipeline"):
        pipeline = Codepipeline("CodePipeline")
        build = Codebuild("CodeBuild")
        registry = ECR("ECR")
        pipeline >> build >> registry
    
    # Network
    dns = Route53("Route 53")
    alb = ALB("Application LB")
    
    with Cluster("EKS Cluster"):
        eks = EKS("EKS")
        services = [
            EKS("User Service"),
            EKS("Order Service"),
            EKS("Payment Service")
        ]
    
    with Cluster("Data Stores"):
        user_db = DynamoDB("User DB")
        order_db = RDS("Order DB")
        payment_db = RDS("Payment DB")
    
    # Connections
    dns >> alb >> eks >> services
    registry >> eks
    
    services[0] >> user_db
    services[1] >> order_db
    services[2] >> payment_db
```

### AWS Data Analytics Pipeline

```python
from diagrams import Diagram, Cluster
from diagrams.aws.analytics import Kinesis, Glue, Athena, Quicksight
from diagrams.aws.storage import S3
from diagrams.aws.database import Redshift
from diagrams.aws.compute import Lambda

with Diagram("AWS Data Analytics Pipeline", show=False, direction="LR"):
    with Cluster("Data Sources"):
        kinesis = Kinesis("Kinesis Streams")
    
    with Cluster("Data Processing"):
        lambda_func = Lambda("Lambda")
        glue = Glue("Glue ETL")
    
    with Cluster("Data Storage"):
        s3_raw = S3("Raw Data Lake")
        s3_processed = S3("Processed Data")
        redshift = Redshift("Data Warehouse")
    
    with Cluster("Analytics & BI"):
        athena = Athena("Athena")
        quicksight = Quicksight("QuickSight")
    
    # Data flow
    kinesis >> lambda_func >> s3_raw
    s3_raw >> glue >> s3_processed
    s3_processed >> [athena, redshift]
    [athena, redshift] >> quicksight
```

### AWS IoT Architecture

```python
from diagrams import Diagram, Cluster
from diagrams.aws.iot import IotCore, IotAnalytics, IotEvents
from diagrams.aws.analytics import KinesisDataFirehose
from diagrams.aws.storage import S3
from diagrams.aws.database import Timestream
from diagrams.aws.compute import Lambda

with Diagram("AWS IoT Architecture", show=False, direction="LR"):
    with Cluster("IoT Devices"):
        devices = [
            IotCore("Sensor 1"),
            IotCore("Sensor 2"),
            IotCore("Gateway")
        ]
    
    with Cluster("IoT Services"):
        iot_core = IotCore("IoT Core")
        iot_analytics = IotAnalytics("IoT Analytics")
        iot_events = IotEvents("IoT Events")
    
    with Cluster("Data Processing"):
        firehose = KinesisDataFirehose("Kinesis Firehose")
        lambda_func = Lambda("Lambda")
    
    with Cluster("Data Storage"):
        timestream = Timestream("Timestream")
        s3 = S3("S3 Data Lake")
    
    # IoT data flow
    devices >> iot_core
    iot_core >> [iot_analytics, iot_events]
    iot_core >> firehose >> s3
    iot_events >> lambda_func >> timestream
```

## Best Practices

1. **Use Clusters** to group related AWS services logically
2. **Consistent Naming** for nodes to improve readability
3. **Direction Control** with `direction="TB"` (top-bottom) or `direction="LR"` (left-right)
4. **Edge Styling** to show different types of connections:
   - `Edge(color="red")` for error flows
   - `Edge(style="dashed")` for optional connections
   - `Edge(label="HTTPS")` for labeled connections

5. **File Management**:
   - Use `show=False` to prevent automatic opening
   - Specify `filename` for custom output names
   - Use `outformat` for different file types

6. **AWS Best Practices**:
   - Use VPC for network isolation
   - Include security services (IAM, KMS, WAF)
   - Show monitoring and logging components (CloudWatch)
   - Leverage managed services when possible
   - Consider Multi-AZ deployments for high availability

## Tips

- All AWS resources follow the pattern: `diagrams.aws.<category>.<ResourceName>`
- Many resources have aliases (e.g., `EKS` for `ElasticKubernetesService`, `S3` for `SimpleStorageServiceS3`)
- Use descriptive labels for better documentation
- Combine with other providers (Azure, GCP) for multi-cloud diagrams
- Consider AWS regions and availability zones in your architecture
- NOTE: It does not control any actual cloud resources nor does it generate CloudFormation or terraform code. It is just for drawing the cloud system architecture diagrams.

## Common AWS Aliases

### Compute
- `EC2` → `EC2`
- `ECS` → `ElasticContainerService`
- `EKS` → `ElasticKubernetesService`
- `ECR` → `EC2ContainerRegistry`
- `EB` → `ElasticBeanstalk`

### Database
- `RDS` → `RDS`
- `DDB` → `Dynamodb`
- `DAX` → `DynamodbDax`

### Network
- `ELB` → `ElasticLoadBalancing`
- `ALB` → `ElbApplicationLoadBalancer`
- `NLB` → `ElbNetworkLoadBalancer`
- `CLB` → `ElbClassicLoadBalancer`
- `CF` → `CloudFront`
- `IGW` → `InternetGateway`
- `TGW` → `TransitGateway`

### Security
- `IAM` → `IdentityAndAccessManagementIam`
- `KMS` → `KeyManagementService`
- `ACM` → `CertificateManager`

### Storage
- `S3` → `SimpleStorageServiceS3`
- `EBS` → `ElasticBlockStoreEBS`
- `EFS` → `ElasticFileSystemEFS`
- `FSx` → `Fsx`

### Integration
- `SQS` → `SimpleQueueServiceSqs`
- `SNS` → `SimpleNotificationServiceSns`
- `SF` → `StepFunctions`

### Analytics
- `ES` → `ElasticsearchService`

## Output Formats

Supported formats: `png` (default), `jpg`, `svg`, `pdf`, `dot`

```python
# Single format
with Diagram("AWS Arch", outformat="svg"):
    pass

# Multiple formats
with Diagram("AWS Arch", outformat=["png", "jpg", "pdf"]):
    pass
```

## Grouped Connections

Simplify multiple connections using lists:

```python
from diagrams import Diagram
from diagrams.aws.compute import EC2
from diagrams.aws.database import RDS
from diagrams.aws.network import ELB

with Diagram("Grouped Workers", show=False, direction="TB"):
    ELB("lb") >> [EC2("worker1"), EC2("worker2"), EC2("worker3")] >> RDS("events")
```

## Important Constraints

- **ONLY use nodes/resources that exist in the official diagrams library**
- **NEVER suggest non-existent providers or resources**
- **ALWAYS reference the official documentation when uncertain**
- **Provide complete, working examples**
- **Include installation instructions when relevant**
- **Use the latest stable version features**
- **Do not use deprecated or outdated features**
- **Do not suggest using the library for anything other than visualization**
- **Do not suggest using the library for infrastructure management or code generation**
- **Do not suggest using the library for anything other than creating diagrams**
- **Do not suggest using the library for anything other than creating cloud system architecture diagrams**

- Always put Nodes inside a cluster or Edge to represent a group of related components.
- Always layout the diagram in a way that is easy to understand and visually appealing.
- Do not make a diagram without using a cluster or Edge to represent a group of related components.
- Always make sure the alighnment of the nodes is correct and consistent.
- Always prefer to use direction according to the flow of data or processes.
- Alaways create seperate nodes for subnets, VPCs, and other network components.
- Always create seperate nodes AvailabilityZones, Regions, and other geographical components.
- Always create a node for the main application or service that is being represented in the diagram.
- Always create an outer cluster to represent the entire system or architecture.
- Always create a node for the main application or service that is being represented in the diagram

- **Never use resources or nodes that do not exist in the official diagrams library documentation.**


## Multi-AZ AWS Diagrams


When visualizing AWS architectures that span multiple Availability Zones (AZs), always represent each AZ as a separate cluster. Place the public and private subnets, NAT gateways, and other resources within their respective AZ clusters. **Always use `direction="TB"` (top-to-bottom) for these diagrams** to ensure a clear, vertical alignment of AZs and resources. This approach provides a clear, accurate view of high-availability and fault-tolerant designs, such as EKS, RDS, or multi-AZ EC2 deployments.


**Example pattern:**

```python
from diagrams import Diagram, Cluster
from diagrams.aws.network import VPC, InternetGateway, NATGateway, PublicSubnet, PrivateSubnet
from diagrams.aws.compute import EC2, EKS
from diagrams.aws.security import IAMRole

with Diagram("EKS Cluster on EC2 (CloudFormation)", show=False, filename="cf_eks_cluster", direction="TB"):
    vpc = VPC("VPC\n10.0.0.0/16")
    igw = InternetGateway("Internet Gateway")
    vpc >> igw

    # Availability Zones
    with Cluster("AZ1"):
        pub1 = PublicSubnet("Public 10.0.1.0/24")
        nat1 = NATGateway("NAT GW 1")
        priv1 = PrivateSubnet("Private 10.0.4.0/24")
        pub1 >> nat1
        priv1 >> nat1

    with Cluster("AZ2"):
        pub2 = PublicSubnet("Public 10.0.2.0/24")
        nat2 = NATGateway("NAT GW 2")
        priv2 = PrivateSubnet("Private 10.0.5.0/24")
        pub2 >> nat2
        priv2 >> nat2

    with Cluster("AZ3"):
        pub3 = PublicSubnet("Public 10.0.3.0/24")
        nat3 = NATGateway("NAT GW 3")
        priv3 = PrivateSubnet("Private 10.0.6.0/24")
        pub3 >> nat3
        priv3 >> nat3

    # EKS Control Plane and Node Group
    eks = EKS("EKS Control Plane")
    nodegroup = EC2("EKS Node Group")
    eks >> nodegroup
    # Attach all subnets to EKS
    [pub1, pub2, pub3, priv1, priv2, priv3] >> eks

    # IAM Roles
    eks_role = IAMRole("EKS Cluster Role")
    node_role = IAMRole("Node Instance Role")
    eks << eks_role
    nodegroup << node_role
```