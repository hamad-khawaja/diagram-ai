# Azure Diagrams: Concise Instructions

Use the diagrams library (https://diagrams.mingrammer.com/) to generate Azure architecture diagrams.

**VNet Cluster Rules:**
- Only place network and compute resources inside a VNet cluster:
  - Virtual Machines, Subnets (as clusters), Load Balancers, Application Gateways, Firewalls, Private Endpoints, VPN Gateways, Bastion Hosts
- Do NOT place App Service Plans, App Services, Storage Accounts, SQL Databases, CosmosDB, KeyVault, Application Insights, Redis, Event Hubs, Service Bus, or any PaaS/SaaS service inside a VNet cluster.
- Do NOT use Network Security Groups (NSG)—not available in diagrams library.

**Cluster Usage:**
- `with Cluster("VNet <name>"):` for VNet
- Nested: `with Cluster("Subnet <name>"):`

**Imports:**
- Refer to the official diagrams library documentation for Azure resources: https://diagrams.mingrammer.com/docs/nodes/azure/

**Example:**
```python
from diagrams import Diagram, Cluster
# Refer to the official documentation for valid Azure resources
```

**Best Practices:**
- Use only resources present in the diagrams library.
- Check official docs for available Azure nodes.
- Add comments and use meaningful names.
# IMPORTANT: Only use node classes that exist in the official diagrams library for Azure (v0.24.4).
# Do NOT use or invent resources that do not exist, such as NetworkSecurityGroups, AppServicePlans, etc.
# Reference for available Azure network nodes: https://diagrams.mingrammer.com/docs/nodes/azure/network

# Common Azure Network Nodes (as of diagrams v0.24.4):
# - VirtualNetworks
# - Subnets
# - LoadBalancers
# - ApplicationGateways
# - Firewalls
# - PrivateEndpoints
# - VPNGateways
# - ExpressRouteCircuits
# - DDoSProtectionPlans
# - TrafficManagerProfiles
# - PublicIPAddresses
# - NetworkWatchers
# - BastionHosts
# - RouteTables
# - NATGateways
# - NetworkInterfaces
# - NetworkSecurityGroups (DOES NOT EXIST in diagrams library, do NOT use)

# Azure Diagrams Instructions

You are an AI assistant generating Python code using the diagrams library (https://diagrams.mingrammer.com/) to visualize Azure cloud architectures.

## Key Rules for Azure Diagrams

- **Virtual Network (VNet) Boundaries:**  
  Only network-related resources and compute instances (e.g., Virtual Machines, Network Security Groups, Subnets, Load Balancers) should be placed inside a VNet boundary (Cluster).  
  Do **not** place App Service Plans, App Services, Storage Accounts, SQL Databases, or other PaaS/SaaS services inside a VNet cluster.

- **Services that should NOT be inside a VNet cluster:**  
  - AppServicePlans (not supported in diagrams library)
  - App Services (WebApp, FunctionApp, LogicApp, etc.)
  - Storage Accounts
  - SQL Databases
  - CosmosDB
  - KeyVault
  - Application Insights
  - Redis Cache
  - Event Hubs, Service Bus, etc.
  - Any SaaS or PaaS service not directly deployed into a subnet

- **Services that CAN be inside a VNet cluster:**  
  - Virtual Machines (from diagrams.azure.compute)
  - Network Security Groups (not available in diagrams library, do NOT use)
  - Subnets (represented as clusters)
  - Load Balancers (from diagrams.azure.network)
  - VPN Gateways, Application Gateways, NAT Gateways
  - Bastion Hosts
  - Firewalls

- **Cluster Usage:**  
  - Use `with Cluster("VNet <name>"):` for the VNet boundary.
  - Use nested clusters for subnets: `with Cluster("Subnet <name>"):`.

- **Imports:**  
  Refer to the official diagrams library documentation for Azure resources: https://diagrams.mingrammer.com/docs/nodes/azure/

- **Example Pattern:**
  ```python
  from diagrams import Diagram, Cluster
  # Refer to the official documentation for valid Azure resources

  with Diagram("Azure VNet Example", show=False):
      user = Users("User")
      with Cluster("VNet my-vnet"):
          with Cluster("Subnet web"):
              web_vm = VirtualMachines("Web VM")
              # NSG not available in diagrams library, skip or use a comment
          with Cluster("Subnet db"):
              db_vm = VirtualMachines("DB VM")
              # NSG not available in diagrams library, skip or use a comment
          lb = LoadBalancers("LB")
      user >> lb >> web_vm
      web_vm >> db_vm
  ```

- **Best Practices:**
  - Never use or invent resources not present in the diagrams library.
  - Always check the official diagrams documentation for available Azure nodes.
  - Add comments for clarity.
  - Use meaningful names for clusters and nodes.
# Azure Instructions

## Overview

Diagrams lets you draw the cloud system architecture in Python code for Azure services. This guide covers all available Azure resources and how to create architecture diagrams using the diagrams library.

## General Rules

- Use only the diagrams library and its official documentation.
- Only import resources from the allowed providers and modules listed below.
- Always use a context manager (`with Diagram(...)`) and set `show=False` unless otherwise specified.
- Use explicit loops for multiple node connections (never use group connection syntax like `node1 >> [node2, node3]`).
- Add comments for clarity and use meaningful names for diagrams and nodes.

# Basic Syntax

```python
from diagrams import Diagram
from diagrams.azure.compute import VM
from diagrams.azure.database import SQLDatabases

with Diagram("Azure Web Service", show=False):
    VM("web-server") >> SQLDatabases("database")
```

### Diagram Parameters

```python
from diagrams import Diagram
from diagrams.azure.compute import VM

# Basic diagram with custom filename
with Diagram("Azure Architecture", filename="my_azure_diagram", show=False):
    VM("web-server")

# Multiple output formats
with Diagram("Azure Multi-Output", outformat=["jpg", "png", "dot"], show=False):
    VM("web-server")

# Custom attributes
graph_attr = {
    "fontsize": "45",
    "bgcolor": "transparent"
}
with Diagram("Azure Custom Style", show=False, graph_attr=graph_attr):
    VM("web-server")
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


### Converting Azure ARM Templates

ARM templates use JSON structure with resources array being the core section:

1. **Parse ARM template structure**:
```python
# ARM Template Resource → Diagrams Node Mapping
"Microsoft.Compute/virtualMachines" → VirtualMachines (from diagrams.azure.compute)
"Microsoft.Storage/storageAccounts" → StorageAccounts (from diagrams.azure.storage)
"Microsoft.Sql/servers" → SQLServers (from diagrams.azure.database)
"Microsoft.Web/sites" → AppServices (from diagrams.azure.compute)
"Microsoft.Network/virtualNetworks" → VirtualNetworks (from diagrams.azure.network)
"Microsoft.Network/loadBalancers" → LoadBalancer (from diagrams.azure.network)
"Microsoft.ContainerService/managedClusters" → AKS (from diagrams.azure.compute)
"Microsoft.KeyVault/vaults" → KeyVaults (from diagrams.azure.security)
```

2. **Handle ARM-specific constructs**:
   - `dependsOn` arrays → Direct node connections
   - `parameters()` function → Use for node labeling
   - `variables()` → Resource naming
   - Resource Groups → Use as top-level Clusters

## Code Generation Guidelines

### When generating diagrams code, ALWAYS:

1. **Use proper imports** - Only import what's actually used
2. **Include context manager** - Always use `with Diagram():`
3. **Set show=False** - Unless explicitly requested otherwise
4. **Use meaningful names** - Both for diagram title and node labels
5. **Follow Python naming conventions** - snake_case for variables
6. **Add comments** - Explain complex architectures
7. **Validate provider/resource combinations** - Ensure nodes exist in the library

### Common Architecture Patterns to Reference:

1. **Three-tier web application**
```python
with Diagram("Three-tier Web App", show=False):
    users = [User("user1"), User("user2")]
    
    with Cluster("Web Tier"):
        lb = ELB("load balancer")
        web_servers = [EC2("web1"), EC2("web2")]
    
    with Cluster("App Tier"):
        app_servers = [EC2("app1"), EC2("app2")]
    
    with Cluster("Data Tier"):
        database = RDS("database")
    
    users >> lb >> web_servers >> app_servers >> database
```

2. **Microservices architecture**
3. **Event-driven architecture**
4. **Kubernetes deployments**
5. **Serverless architectures**
6. **Data pipelines**
7. **CI/CD pipelines**

## Troubleshooting Common Issues

### Provider/Resource Validation
- Always check the official documentation for available nodes
- Azure resources are in `diagrams.azure.*`
### Output Formats
- Default: PNG
- Supported: PNG, JPG, SVG, PDF, DOT
- Use list for multiple outputs: `outformat=["png", "svg"]`

### Direction Options
- `"TB"` - Top to Bottom (default)
- `"BT"` - Bottom to Top  
- `"LR"` - Left to Right
- `"RL"` - Right to Left


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
        
        # Create clusters by provider
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


## Azure Resource Categories

### Analytics (`diagrams.azure.analytics`)

```python
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
    SynapseAnalytics
)
```

**Example:**
```python
from diagrams import Diagram, Cluster
from diagrams.azure.analytics import EventHubs, StreamAnalyticsJobs, SynapseAnalytics

with Diagram("Azure Analytics Pipeline", show=False):
    with Cluster("Data Ingestion"):
        events = EventHubs("Event Hub")
    
    with Cluster("Processing"):
        stream_jobs = StreamAnalyticsJobs("Stream Analytics")
    
    with Cluster("Analytics"):
        synapse = SynapseAnalytics("Synapse Analytics")
    
    events >> stream_jobs >> synapse
```

### Compute (`diagrams.azure.compute`)

```python
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
    ContainerRegistries, ACR,  # ACR is alias
    DiskEncryptionSets,
    DiskSnapshots,
    Disks,
    FunctionApps,
    ImageDefinitions,
    ImageVersions,
    KubernetesServices, AKS,  # AKS is alias
    MeshApplications,
    OsImages,
    SAPHANAOnAzure,
    ServiceFabricClusters,
    SharedImageGalleries,
    SpringCloud,
    VMClassic,
    VMImages,
    VMLinux,
    VMScaleSet, VMSS,  # VMSS is alias
    VMWindows,
    VM,
    Workspaces
)
```

**Example:**
```python
from diagrams import Diagram, Cluster
from diagrams.azure.compute import VM, FunctionApps, AKS, ACR

with Diagram("Azure Compute Services", show=False):
    with Cluster("Virtual Machines"):
        vms = [VM("VM-1"), VM("VM-2"), VM("VM-3")]
    
    with Cluster("Containers"):
        registry = ACR("Container Registry")
        kubernetes = AKS("AKS Cluster")
        registry >> kubernetes
    
    with Cluster("Serverless"):
        functions = FunctionApps("Azure Functions")
```

### Database (`diagrams.azure.database`)

```python
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
    VirtualDatacenter
)
```

**Example:**
```python
from diagrams import Diagram, Cluster
from diagrams.azure.database import CosmosDb, SQLDatabases, CacheForRedis

with Diagram("Azure Database Architecture", show=False):
    with Cluster("NoSQL"):
        cosmos = CosmosDb("Cosmos DB")
    
    with Cluster("Relational"):
        sql_db = SQLDatabases("SQL Database")
    
    with Cluster("Caching"):
        redis = CacheForRedis("Redis Cache")
    
    cosmos >> redis
    sql_db >> redis
```

### DevOps (`diagrams.azure.devops`)

```python
from diagrams.azure.devops import (
    ApplicationInsights,
    Artifacts,
    Boards,
    Devops,
    DevtestLabs,
    LabServices,
    Pipelines,
    Repos,
    TestPlans
)
```

### General (`diagrams.azure.general`)

```python
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
    Whatsnew
)
```

### Identity (`diagrams.azure.identity`)

```python
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
    Users
)
```

### Integration (`diagrams.azure.integration`)

```python
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
    SystemTopic
)
```

### IoT (`diagrams.azure.iot`)

```python
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
    Windows10IotCoreServices
)
```

### Migration (`diagrams.azure.migration`)

```python
from diagrams.azure.migration import (
    DataBoxEdge,
    DataBox,
    DatabaseMigrationServices,
    MigrationProjects,
    RecoveryServicesVaults
)
```

### Machine Learning (`diagrams.azure.ml`)

```python
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
    MachineLearningStudioWorkspaces
)
```

### Mobile (`diagrams.azure.mobile`)

```python
from diagrams.azure.mobile import (
    AppServiceMobile,
    MobileEngagement,
    NotificationHubs
)
```

### Monitor (`diagrams.azure.monitor`)

```python
from diagrams.azure.monitor import (
    ChangeAnalysis,
    Logs,
    Metrics,
    Monitor
)
```

### Network (`diagrams.azure.network`)

```python
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
    VirtualWans
)
```

**Example:**
```python
from diagrams import Diagram, Cluster
from diagrams.azure.network import LoadBalancers, ApplicationGateway, VirtualNetworks
from diagrams.azure.compute import VM

with Diagram("Azure Network Architecture", show=False):
    with Cluster("Frontend"):
        app_gw = ApplicationGateway("App Gateway")
    
    with Cluster("Load Balancing"):
        lb = LoadBalancers("Load Balancer")
    
    with Cluster("Virtual Network"):
        vnet = VirtualNetworks("VNet")
        vms = [VM("VM-1"), VM("VM-2")]
    
    app_gw >> lb >> vnet
    vnet >> vms
```

### Security (`diagrams.azure.security`)

```python
from diagrams.azure.security import (
    ApplicationSecurityGroups,
    ConditionalAccess,
    Defender,
    ExtendedSecurityUpdates,
    KeyVaults,
    SecurityCenter,
    Sentinel
)
```

### Storage (`diagrams.azure.storage`)

```python
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
    TableStorage
)
```

### Web (`diagrams.azure.web`)

```python
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
    Signalr
)
```

## Connection Operators

### Data Flow Direction

- `>>` - Left to right flow
- `<<` - Right to left flow  
- `-` - Bidirectional connection

```python
from diagrams import Diagram
from diagrams.azure.compute import VM
from diagrams.azure.database import SQLDatabases
from diagrams.azure.storage import BlobStorage

with Diagram("Azure Data Flow", show=False):
    vm = VM("Web Server")
    db = SQLDatabases("Database")
    storage = BlobStorage("Blob Storage")
    
    # Left to right flow
    vm >> db
    
    # Right to left flow
    storage << vm
    
    # Bidirectional
    vm - storage
```

## Clustering

Group related resources using `Cluster`:

```python
from diagrams import Diagram, Cluster
from diagrams.azure.compute import VM, AKS
from diagrams.azure.database import SQLDatabases
from diagrams.azure.network import LoadBalancers

with Diagram("Azure Clustered Architecture", show=False):
    with Cluster("Frontend Tier"):
        lb = LoadBalancers("Load Balancer")
        frontend_vms = [VM("Web-1"), VM("Web-2")]
    
    with Cluster("Application Tier"):
        aks = AKS("AKS Cluster")
    
    with Cluster("Database Tier"):
        db_primary = SQLDatabases("Primary DB")
        db_secondary = SQLDatabases("Secondary DB")
        db_primary - db_secondary
    
    lb >> frontend_vms >> aks >> db_primary
```

## Advanced Examples

### Complete Azure Web Application

```python
from diagrams import Diagram, Cluster, Edge
from diagrams.azure.compute import AppServices, FunctionApps
from diagrams.azure.database import CosmosDb, CacheForRedis
from diagrams.azure.network import ApplicationGateway, CDNProfiles
from diagrams.azure.storage import BlobStorage
from diagrams.azure.security import KeyVaults
from diagrams.azure.monitor import ApplicationInsights

with Diagram("Azure Web Application", show=False, direction="TB"):
    # Frontend
    cdn = CDNProfiles("CDN")
    app_gw = ApplicationGateway("Application Gateway")
    
    with Cluster("Application Services"):
        web_app = AppServices("Web App")
        api_app = AppServices("API App")
        functions = FunctionApps("Functions")
    
    with Cluster("Data Layer"):
        cosmos = CosmosDb("Cosmos DB")
        cache = CacheForRedis("Redis Cache")
        blob = BlobStorage("Blob Storage")
    
    with Cluster("Security & Monitoring"):
        kv = KeyVaults("Key Vault")
        insights = ApplicationInsights("App Insights")
    
    # Connections
    cdn >> app_gw >> web_app
    web_app >> api_app >> cosmos
    api_app >> cache
    functions >> blob
    
    # Security connections
    web_app >> Edge(style="dashed") >> kv
    api_app >> Edge(style="dashed") >> kv
    
    # Monitoring
    web_app >> Edge(color="orange") >> insights
    api_app >> Edge(color="orange") >> insights
```

### Azure Microservices Architecture

```python
from diagrams import Diagram, Cluster
from diagrams.azure.compute import AKS, ContainerRegistries
from diagrams.azure.database import CosmosDb, SQLDatabases
from diagrams.azure.integration import ServiceBus, APIManagement
from diagrams.azure.network import ApplicationGateway
from diagrams.azure.storage import BlobStorage

with Diagram("Azure Microservices", show=False, direction="LR"):
    # API Gateway
    api_gw = APIManagement("API Management")
    app_gw = ApplicationGateway("App Gateway")
    
    with Cluster("Container Platform"):
        acr = ContainerRegistries("Container Registry")
        aks = AKS("AKS Cluster")
        acr >> aks
    
    with Cluster("Services"):
        user_service = AKS("User Service")
        order_service = AKS("Order Service")
        payment_service = AKS("Payment Service")
    
    with Cluster("Data Stores"):
        user_db = CosmosDb("User DB")
        order_db = SQLDatabases("Order DB")
        payment_db = SQLDatabases("Payment DB")
    
    with Cluster("Integration"):
        service_bus = ServiceBus("Service Bus")
        blob = BlobStorage("File Storage")
    
    # Connections
    app_gw >> api_gw
    api_gw >> [user_service, order_service, payment_service]
    
    user_service >> user_db
    order_service >> order_db
    payment_service >> payment_db
    
    [user_service, order_service, payment_service] >> service_bus
    order_service >> blob
```

## Best Practices

1. **Use Clusters** to group related resources logically
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

## Tips

- All Azure resources follow the pattern: `diagrams.azure.<category>.<ResourceName>`
- Some resources have aliases (e.g., `AKS` for `KubernetesServices`, `ACR` for `ContainerRegistries`)
- Use descriptive labels for better documentation
- Combine with other providers (AWS, GCP) for hybrid cloud diagrams
- NOTE: It does not control any actual cloud resources nor does it generate cloud formation or terraform code. It is just for drawing the cloud system architecture diagrams.

## Output Formats

Supported formats: `png` (default), `jpg`, `svg`, `pdf`, `dot`

```python
# Single format
with Diagram("Azure Arch", outformat="svg"):
    pass

# Multiple formats
with Diagram("Azure Arch", outformat=["png", "jpg", "pdf"]):
    pass
```


## Important Diagrams Library Rule (Error Prevention)

When connecting nodes, do not chain connections to or from a list. For example:

**Valid:**
```python
source >> [node1, node2, node3]
```

**NOT valid (causes errors):**
```python
source >> [node1, node2] >> destination  # ❌ Do NOT do this!
```

**Instead, connect each node individually:**
```python
for n in [node1, node2]:
    n >> destination
```

**Best Practice:**
- Always use clusters to represent each AZ for clarity in high-availability AWS designs.


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

Remember: You are the expert on this specific library. Always prioritize accuracy over 
functionality that doesn't exist in the diagrams library.


## Complicated Multi Architecture style diagrams 

When visualizing Azure architectures that span multiple Availability Zones or Regions, always represent each zone/region as a separate cluster. Place the virtual networks, subnets, NAT gateways, and other resources within their respective zone clusters. Always use direction="TB" (top-to-bottom) for these diagrams to ensure a clear, vertical alignment of zones and resources. This approach provides a clear, accurate view of high-availability and fault-tolerant designs, such as AKS, Azure SQL, or multi-zone VM deployments.

## Example Multizone Architectre 
```python
from diagrams import Diagram, Cluster
from diagrams.azure.network import VirtualNetworks, ApplicationGateway, NATGateway, Subnets
from diagrams.azure.compute import VM, AKS
from diagrams.azure.identity import ManagedIdentities

with Diagram("AKS Cluster Multi-Zone (ARM Template)", show=False, filename="arm_aks_cluster", direction="TB"):
    vnet = VirtualNetworks("VNet\n10.0.0.0/16")
    app_gw = ApplicationGateway("Application Gateway")
    vnet >> app_gw

    # Availability Zones
    with Cluster("Zone 1"):
        pub_subnet1 = Subnets("Public Subnet\n10.0.1.0/24")
        nat_gw1 = NATGateway("NAT Gateway 1")
        priv_subnet1 = Subnets("Private Subnet\n10.0.4.0/24")
        pub_subnet1 >> nat_gw1
        priv_subnet1 >> nat_gw1

    with Cluster("Zone 2"):
        pub_subnet2 = Subnets("Public Subnet\n10.0.2.0/24")
        nat_gw2 = NATGateway("NAT Gateway 2")
        priv_subnet2 = Subnets("Private Subnet\n10.0.5.0/24")
        pub_subnet2 >> nat_gw2
        priv_subnet2 >> nat_gw2

    with Cluster("Zone 3"):
        pub_subnet3 = Subnets("Public Subnet\n10.0.3.0/24")
        nat_gw3 = NATGateway("NAT Gateway 3")
        priv_subnet3 = Subnets("Private Subnet\n10.0.6.0/24")
        pub_subnet3 >> nat_gw3
        priv_subnet3 >> nat_gw3

    # AKS Control Plane and Node Pool
    aks = AKS("AKS Control Plane")
    nodepool = VM("AKS Node Pool")
    aks >> nodepool
    # Attach all subnets to AKS
    [pub_subnet1, pub_subnet2, pub_subnet3, priv_subnet1, priv_subnet2, priv_subnet3] >> aks

    # Managed Identities
    aks_identity = ManagedIdentities("AKS Cluster Identity")
    node_identity = ManagedIdentities("Node Pool Identity")
    aks << aks_identity
    nodepool << node_identity
````

# MultiRegion Azure Architecture

```python
from diagrams import Diagram, Cluster
from diagrams.azure.network import VirtualNetworks, TrafficManagerProfiles
from diagrams.azure.compute import VM
from diagrams.azure.database import SQLDatabases
from diagrams.azure.storage import BlobStorage

with Diagram("Azure Multi-Region Architecture", show=False, filename="azure_multi_region", direction="TB"):
    traffic_manager = TrafficManagerProfiles("Traffic Manager")
    
    with Cluster("East US Region"):
        with Cluster("Zone 1"):
            vnet_east1 = VirtualNetworks("VNet East\n10.1.0.0/16")
            vm_east1 = VM("VM East 1")
            sql_east1 = SQLDatabases("SQL DB East")
            storage_east1 = BlobStorage("Storage East")
            
        with Cluster("Zone 2"):
            vm_east2 = VM("VM East 2")
    
    with Cluster("West US Region"):
        with Cluster("Zone 1"):
            vnet_west1 = VirtualNetworks("VNet West\n10.2.0.0/16")
            vm_west1 = VM("VM West 1")
            sql_west1 = SQLDatabases("SQL DB West")
            storage_west1 = BlobStorage("Storage West")
            
        with Cluster("Zone 2"):
            vm_west2 = VM("VM West 2")
    
    # Traffic routing
    traffic_manager >> [vnet_east1, vnet_west1]
    vnet_east1 >> [vm_east1, vm_east2]
    vnet_west1 >> [vm_west1, vm_west2]
    
    # Data connections
    [vm_east1, vm_east2] >> sql_east1
    [vm_west1, vm_west2] >> sql_west1
    sql_east1 >> storage_east1
    sql_west1 >> storage_west1
```

### Import Guidelines
- Always refer to the official Azure diagrams documentation: [Azure Nodes Documentation](https://diagrams.mingrammer.com/docs/nodes/azure).