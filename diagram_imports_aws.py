# AWS Imports Template for Diagrams Library
# (Renamed from diagram_imports_template.py)

# AWS Cost Imports
from diagrams.aws.cost import (
    Budgets,
    CostAndUsageReport,
    CostExplorer,
    CostManagement,
    ReservedInstanceReporting,
    SavingsPlans
)

# AWS Database Imports
from diagrams.aws.database import (
    AuroraInstance,
    Aurora,
    DatabaseMigrationServiceDatabaseMigrationWorkflow,
    DatabaseMigrationService,
    Database,
    DocumentdbMongodbCompatibility,
    DynamodbAttribute,
    DynamodbAttributes,
    DynamodbDax,
    DynamodbGlobalSecondaryIndex,
    DynamodbItem,
    DynamodbItems,
    DynamodbStreams,
    DynamodbTable,
    Dynamodb,
    ElasticacheCacheNode,
    ElasticacheForMemcached,
    ElasticacheForRedis,
    Elasticache,
    KeyspacesManagedApacheCassandraService,
    Neptune,
    QuantumLedgerDatabaseQldb,
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

# AWS DevTools Imports
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
    CommandLineInterface,
    DeveloperTools,
    ToolsAndSdks,
    XRay
)

# AWS Enablement Imports
from diagrams.aws.enablement import (
    CustomerEnablement,
    Iq,
    ManagedServices,
    ProfessionalServices,
    Support
)

# AWS End User Imports
from diagrams.aws.enduser import (
    Appstream20,
    DesktopAndAppStreaming,
    Workdocs,
    Worklink,
    Workspaces
)
# AWS AR/VR Imports
from diagrams.aws.ar import ArVr, Sumerian

# AWS Blockchain Imports
from diagrams.aws.blockchain import (
    BlockchainResource,
    Blockchain,
    ManagedBlockchain,
    QuantumLedgerDatabaseQldb
)

# AWS Business Imports
from diagrams.aws.business import (
    AlexaForBusiness,
    BusinessApplications,
    Chime,
    Workmail
)

# AWS Compute Imports
from diagrams.aws.compute import (
    AppRunner,
    ApplicationAutoScaling,
    Batch,
    ComputeOptimizer,
    Compute,
    EC2Ami,
    EC2AutoScaling,
    EC2ContainerRegistryImage,
    EC2ContainerRegistryRegistry,
    EC2ContainerRegistry,
    EC2ElasticIpAddress,
    EC2ImageBuilder,
    EC2Instance,
    EC2Instances,
    EC2Rescue,
    EC2SpotInstance,
    EC2,
    ElasticBeanstalkApplication,
    ElasticBeanstalkDeployment,
    ElasticBeanstalk,
    ElasticContainerServiceContainer,
    ElasticContainerServiceService,
    ElasticContainerService,
    ElasticKubernetesService,
    Fargate,
    LambdaFunction,
    Lambda,
    Lightsail,
    LocalZones,
    Outposts,
    ServerlessApplicationRepository,
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
# AWS Analytics Imports
from diagrams.aws.analytics import (
    AmazonOpensearchService,
    Analytics,
    Athena,
    CloudsearchSearchDocuments,
    Cloudsearch,
    DataLakeResource,
    DataPipeline,
    ElasticsearchService,
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

# AWS Engagement Imports
from diagrams.aws.engagement import (
    Connect,
    CustomerEngagement,
    Pinpoint,
    SimpleEmailServiceSesEmail,
    SimpleEmailServiceSes,  # SES (alias)
)

# AWS Game Tech Imports
from diagrams.aws.game import (
    GameTech,
    Gamelift,
)

# AWS General Imports
from diagrams.aws.general import (
    Client,
    Disk,
    Forums,
    General,
    GenericDatabase,
    GenericFirewall,
    GenericOfficeBuilding,  # OfficeBuilding (alias)
    GenericSamlToken,
    GenericSDK,
    InternetAlt1,
    InternetAlt2,
    InternetGateway,
    Marketplace,
    MobileClient,
    Multimedia,
    OfficeBuilding,
    SamlToken,
    SDK,
    SslPadlock,
    TapeStorage,
    Toolkit,
    TraditionalServer,
    User,
    Users,
)

# AWS Integration Imports
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
    SimpleNotificationServiceSns,  # SNS (alias)
    SimpleQueueServiceSqsMessage,
    SimpleQueueServiceSqsQueue,
    SimpleQueueServiceSqs,  # SQS (alias)
    StepFunctions,  # SF (alias)
)

# AWS IoT Imports
from diagrams.aws.iot import (
    Freertos,  # FreeRTOS (alias)
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
    IotHardwareBoard,  # IotBoard (alias)
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
    IotWindfarm,
)

# AWS Management Imports
from diagrams.aws.management import (
    AmazonDevopsGuru,
    AmazonManagedGrafana,
    AmazonManagedPrometheus,
    AmazonManagedWorkflowsApacheAirflow,
    AutoScaling,
    Chatbot,
    CloudformationChangeSet,
    CloudformationStack,
    CloudformationTemplate,
    Cloudformation,
    Cloudtrail,
    CloudwatchAlarm,
    CloudwatchEventEventBased,
    CloudwatchEventTimeBased,
    CloudwatchLogs,
    CloudwatchRule,
    Cloudwatch,
    Codeguru,
    CommandLineInterface,
    Config,
    ControlTower,
    LicenseManager,
    ManagedServices,
    ManagementAndGovernance,
    ManagementConsole,
    OpsworksApps,
    OpsworksDeployments,
    OpsworksInstances,
    OpsworksLayers,
    OpsworksMonitoring,
    OpsworksPermissions,
    OpsworksResources,
    OpsworksStack,
    Opsworks,
    OrganizationsAccount,
    OrganizationsOrganizationalUnit,
    Organizations,
    PersonalHealthDashboard,
    Proton,
    ServiceCatalog,
    SystemsManagerAppConfig,
    SystemsManagerAutomation,
    SystemsManagerDocuments,
    SystemsManagerInventory,
    SystemsManagerMaintenanceWindows,
    SystemsManagerOpscenter,
    SystemsManagerParameterStore,  # ParameterStore (alias)
    SystemsManagerPatchManager,
    SystemsManagerRunCommand,
    SystemsManagerStateManager,
    SystemsManager,  # SSM (alias)
    TrustedAdvisorChecklistCost,
    TrustedAdvisorChecklistFaultTolerant,
    TrustedAdvisorChecklistPerformance,
    TrustedAdvisorChecklistSecurity,
    TrustedAdvisorChecklist,
    TrustedAdvisor,
    WellArchitectedTool,
)

# AWS Media Imports
from diagrams.aws.media import (
    ElasticTranscoder,
    ElementalConductor,
    ElementalDelta,
    ElementalLive,
    ElementalMediaconnect,
    ElementalMediaconvert,
    ElementalMedialive,
    ElementalMediapackage,
    ElementalMediastore,
    ElementalMediatailor,
    ElementalServer,
    KinesisVideoStreams,
    MediaServices,
)

# AWS Migration Imports
from diagrams.aws.migration import (
    ApplicationDiscoveryService,  # ADS (alias)
    CloudendureMigration,  # CEM (alias)
    DatabaseMigrationService,  # DMS (alias)
    DatasyncAgent,
    Datasync,
    MigrationAndTransfer,  # MAT (alias)
    MigrationHub,
    ServerMigrationService,  # SMS (alias)
    SnowballEdge,
    Snowball,
    Snowmobile,
    TransferForSftp,
)

# AWS ML Imports
from diagrams.aws.ml import (
    ApacheMxnetOnAWS,
    AugmentedAi,
    Bedrock,
    Comprehend,
    DeepLearningAmis,
    DeepLearningContainers,  # DLC (alias)
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
    Translate,
)

# AWS Mobile Imports
from diagrams.aws.mobile import (
    Amplify,
    APIGatewayEndpoint,
    APIGateway,
    Appsync,
    DeviceFarm,
    Mobile,
    Pinpoint,
)

# AWS Network Imports
from diagrams.aws.network import (
    APIGatewayEndpoint,
    APIGateway,
    AppMesh,
    ClientVpn,
    CloudMap,
    CloudFrontDownloadDistribution,
    CloudFrontEdgeLocation,
    CloudFrontStreamingDistribution,
    CloudFront,  # CF (alias)
    DirectConnect,
    ElasticLoadBalancing,  # ELB (alias)
    ElbApplicationLoadBalancer,  # ALB (alias)
    ElbClassicLoadBalancer,  # CLB (alias)
    ElbNetworkLoadBalancer,  # NLB (alias)
    Endpoint,
    GlobalAccelerator,  # GAX (alias)
    InternetGateway,  # IGW (alias)
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
    TransitGatewayAttachment,  # TGWAttach (alias)
    TransitGateway,  # TGW (alias)
    VPCCustomerGateway,
    VPCElasticNetworkAdapter,
    VPCElasticNetworkInterface,
    VPCFlowLogs,
    VPCPeering,
    VPCRouter,
    VPCTrafficMirroring,
    VPC,
    VpnConnection,
    VpnGateway,
)

# AWS Quantum Imports
from diagrams.aws.quantum import (
    Braket,
    QuantumTechnologies,
)

# AWS Robotics Imports
from diagrams.aws.robotics import (
    RobomakerCloudExtensionRos,
    RobomakerDevelopmentEnvironment,
    RobomakerFleetManagement,
    RobomakerSimulator,
    Robomaker,
    Robotics,
)

# AWS Satellite Imports
from diagrams.aws.satellite import (
    GroundStation,
    Satellite,
)

# AWS Security Imports
from diagrams.aws.security import (
    AdConnector,
    Artifact,
    CertificateAuthority,
    CertificateManager,  # ACM (alias)
    CloudDirectory,
    Cloudhsm,  # CloudHSM (alias)
    Cognito,
    Detective,
    DirectoryService,  # DS (alias)
    FirewallManager,  # FMS (alias)
    Guardduty,
    IdentityAndAccessManagementIamAccessAnalyzer,  # IAMAccessAnalyzer (alias)
    IdentityAndAccessManagementIamAddOn,
    IdentityAndAccessManagementIamAWSStsAlternate,
    IdentityAndAccessManagementIamAWSSts,  # IAMAWSSts (alias)
    IdentityAndAccessManagementIamDataEncryptionKey,
    IdentityAndAccessManagementIamEncryptedData,
    IdentityAndAccessManagementIamLongTermSecurityCredential,
    IdentityAndAccessManagementIamMfaToken,
    IdentityAndAccessManagementIamPermissions,  # IAMPermissions (alias)
    IdentityAndAccessManagementIamRole,  # IAMRole (alias)
    IdentityAndAccessManagementIamTemporarySecurityCredential,
    IdentityAndAccessManagementIam,  # IAM (alias)
    InspectorAgent,
    Inspector,
    KeyManagementService,  # KMS (alias)
    Macie,
    ManagedMicrosoftAd,
    ResourceAccessManager,  # RAM (alias)
    SecretsManager,
    SecurityHubFinding,
    SecurityHub,
    SecurityIdentityAndCompliance,
    ShieldAdvanced,
    Shield,
    SimpleAd,
    SingleSignOn,
    WAFFilteringRule,
    WAF,
)

# AWS Storage Imports
from diagrams.aws.storage import (
    Backup,
    CloudendureDisasterRecovery,  # CDR (alias)
    EFSInfrequentaccessPrimaryBg,
    EFSStandardPrimaryBg,
    ElasticBlockStoreEBSSnapshot,
    ElasticBlockStoreEBSVolume,
    ElasticBlockStoreEBS,  # EBS (alias)
    ElasticFileSystemEFSFileSystem,
    ElasticFileSystemEFS,  # EFS (alias)
    FsxForLustre,
    FsxForWindowsFileServer,
    Fsx,  # FSx (alias)
    MultipleVolumesResource,
    S3AccessPoints,
    S3GlacierArchive,
    S3GlacierVault,
    S3Glacier,
    S3ObjectLambdaAccessPoints,
    SimpleStorageServiceS3BucketWithObjects,
    SimpleStorageServiceS3Bucket,
    SimpleStorageServiceS3Object,
    SimpleStorageServiceS3,  # S3 (alias)
    SnowFamilySnowballImportExport,
    SnowballEdge,
    Snowball,
    Snowmobile,
    StorageGatewayCachedVolume,
    StorageGatewayNonCachedVolume,
    StorageGatewayVirtualTapeLibrary,
    StorageGateway,
    Storage,
)
