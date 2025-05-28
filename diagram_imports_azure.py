# Azure Analytics Imports
from diagrams.azure.analytics import (
    AnalysisServices,
    DataExplorerClusters,
    DataFactories,
    DataLakeAnalytics,
    DataLakeStoreGen1,
    Databricks,
    EventHubClusters,
    EventHubs,
    Hdinsightclusters,
    LogAnalyticsWorkspaces,
    StreamAnalyticsJobs,
    SynapseAnalytics,
)

# Azure Compute Imports
from diagrams.azure.compute import (
    AppServices,
    AutomanagedVM,
    AvailabilitySets,
    BatchAccounts,
    CitrixVirtualDesktopsEssentials,
    CloudServicesClassic,
    CloudServices,
    CloudsimpleVirtualMachines,
    ContainerApps,
    ContainerInstances,
    ContainerRegistries,  # ACR (alias)
    DiskEncryptionSets,
    DiskSnapshots,
    Disks,
    FunctionApps,
    ImageDefinitions,
    ImageVersions,
    KubernetesServices,  # AKS (alias)
    MeshApplications,
    OsImages,
    SAPHANAOnAzure,
    ServiceFabricClusters,
    SharedImageGalleries,
    SpringCloud,
    VMClassic,
    VMImages,
    VMLinux,
    VMScaleSet,  # VMSS (alias)
    VMWindows,
    VM,
    Workspaces,
)

# Azure Database Imports
from diagrams.azure.database import (
    BlobStorage,
    CacheForRedis,
    CosmosDb,
    DataExplorerClusters,
    DataFactory,
    DataLake,
    DatabaseForMariadbServers,
    DatabaseForMysqlServers,
    DatabaseForPostgresqlServers,
    ElasticDatabasePools,
    ElasticJobAgents,
    InstancePools,
    ManagedDatabases,
    SQLDatabases,
    SQLDatawarehouse,
    SQLManagedInstances,
    SQLServerStretchDatabases,
    SQLServers,
    SQLVM,
    SQL,
    SsisLiftAndShiftIr,
    SynapseAnalytics,
    VirtualClusters,
    VirtualDatacenter,
)

# Azure DevOps Imports
from diagrams.azure.devops import (
    ApplicationInsights,
    Artifacts,
    Boards,
    Devops,
    DevtestLabs,
    LabServices,
    Pipelines,
    Repos,
    TestPlans,
)

# Azure General Imports
from diagrams.azure.general import (
    Allresources,
    Azurehome,
    Developertools,
    Helpsupport,
    Information,
    Managementgroups,
    Marketplace,
    Quickstartcenter,
    Recent,
    Reservations,
    Resource,
    Resourcegroups,
    Servicehealth,
    Shareddashboard,
    Subscriptions,
    Support,
    Supportrequests,
    Tag,
    Tags,
    Templates,
    Twousericon,
    Userhealthicon,
    Usericon,
    Userprivacy,
    Userresource,
    Whatsnew,
)

# Azure Identity Imports
from diagrams.azure.identity import (
    AccessReview,
    ActiveDirectoryConnectHealth,
    ActiveDirectory,
    ADB2C,
    ADDomainServices,
    ADIdentityProtection,
    ADPrivilegedIdentityManagement,
    AppRegistrations,
    ConditionalAccess,
    EnterpriseApplications,
    Groups,
    IdentityGovernance,
    InformationProtection,
    ManagedIdentities,
    Users,
)

# Azure Integration Imports
from diagrams.azure.integration import (
    APIForFhir,
    APIManagement,
    AppConfiguration,
    DataCatalog,
    EventGridDomains,
    EventGridSubscriptions,
    EventGridTopics,
    IntegrationAccounts,
    IntegrationServiceEnvironments,
    LogicAppsCustomConnector,
    LogicApps,
    PartnerTopic,
    SendgridAccounts,
    ServiceBusRelays,
    ServiceBus,
    ServiceCatalogManagedApplicationDefinitions,
    SoftwareAsAService,
    StorsimpleDeviceManagers,
    SystemTopic,
)

# Azure IoT Imports
from diagrams.azure.iot import (
    DeviceProvisioningServices,
    DigitalTwins,
    IotCentralApplications,
    IotHubSecurity,
    IotHub,
    Maps,
    Sphere,
    TimeSeriesInsightsEnvironments,
    TimeSeriesInsightsEventsSources,
    Windows10IotCoreServices,
)

# Azure Migration Imports
from diagrams.azure.migration import (
    DataBoxEdge,
    DataBox,
    DatabaseMigrationServices,
    MigrationProjects,
    RecoveryServicesVaults,
)

# Azure ML Imports
from diagrams.azure.ml import (
    AzureOpenAI,
    AzureSpeedToText,
    BatchAI,
    BotServices,
    CognitiveServices,
    GenomicsAccounts,
    MachineLearningServiceWorkspaces,
    MachineLearningStudioWebServicePlans,
    MachineLearningStudioWebServices,
    MachineLearningStudioWorkspaces,
)

# Azure Mobile Imports
from diagrams.azure.mobile import (
    AppServiceMobile,
    MobileEngagement,
    NotificationHubs,
)

# Azure Monitor Imports
from diagrams.azure.monitor import (
    ChangeAnalysis,
    Logs,
    Metrics,
    Monitor,
)

# Azure Network Imports
from diagrams.azure.network import (
    ApplicationGateway,
    ApplicationSecurityGroups,
    CDNProfiles,
    Connections,
    DDOSProtectionPlans,
    DNSPrivateZones,
    DNSZones,
    ExpressrouteCircuits,
    Firewall,
    FrontDoors,
    LoadBalancers,
    LocalNetworkGateways,
    NetworkInterfaces,
    NetworkSecurityGroupsClassic,
    NetworkWatcher,
    OnPremisesDataGateways,
    PrivateEndpoint,
    PublicIpAddresses,
    ReservedIpAddressesClassic,
    RouteFilters,
    RouteTables,
    ServiceEndpointPolicies,
    Subnets,
    TrafficManagerProfiles,
    VirtualNetworkClassic,
    VirtualNetworkGateways,
    VirtualNetworks,
    VirtualWans,
)

# Azure Security Imports
from diagrams.azure.security import (
    ApplicationSecurityGroups,
    ConditionalAccess,
    Defender,
    ExtendedSecurityUpdates,
    KeyVaults,
    SecurityCenter,
    Sentinel,
)

# Azure Storage Imports
from diagrams.azure.storage import (
    ArchiveStorage,
    Azurefxtedgefiler,
    BlobStorage,
    DataBoxEdgeDataBoxGateway,
    DataBox,
    DataLakeStorage,
    GeneralStorage,
    NetappFiles,
    QueuesStorage,
    StorageAccountsClassic,
    StorageAccounts,
    StorageExplorer,
    StorageSyncServices,
    StorsimpleDataManagers,
    StorsimpleDeviceManagers,
    TableStorage,
)

# Azure Web Imports
from diagrams.azure.web import (
    APIConnections,
    AppServiceCertificates,
    AppServiceDomains,
    AppServiceEnvironments,
    AppServicePlans,
    AppServices,
    MediaServices,
    NotificationHubNamespaces,
    Search,
    Signalr,
)
