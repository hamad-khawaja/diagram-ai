from diagrams import Diagram, Cluster, Edge
from diagrams.azure.network import ApplicationGateway, TrafficManagerProfiles, VirtualNetworks
from diagrams.azure.compute import VMScaleSet
from diagrams.azure.database import SQLDatabases
from diagrams.azure.storage import BlobStorage

with Diagram("Azure Multi-Region Application Architecture", show=False, direction="TB"):
    # Global DNS-based routing
    traffic_manager = TrafficManagerProfiles("Azure Traffic Manager\n(DNS-based Routing)")

    # East US Region (Primary)
    with Cluster("East US (Primary Region)"):
        vnet_east = VirtualNetworks("VNet East US")
        appgw_east = ApplicationGateway("App Gateway")
        with Cluster("App Tier"):
            vmss_east = VMScaleSet("VM Scale Set")
        sql_east = SQLDatabases("SQL DB\nPrimary\nZone-Redundant")
        blob_east = BlobStorage("Blob Storage\nRA-GRS")
        # Regional flow
        vnet_east >> appgw_east >> vmss_east
        vmss_east >> sql_east
        vmss_east >> blob_east

    # West Europe Region (Secondary)
    with Cluster("West Europe (Secondary Region)"):
        vnet_eu = VirtualNetworks("VNet West Europe")
        appgw_eu = ApplicationGateway("App Gateway")
        with Cluster("App Tier"):
            vmss_eu = VMScaleSet("VM Scale Set")
        sql_eu = SQLDatabases("SQL DB\nSecondary\nZone-Redundant")
        blob_eu = BlobStorage("Blob Storage\nRA-GRS")
        vnet_eu >> appgw_eu >> vmss_eu
        vmss_eu >> sql_eu
        vmss_eu >> blob_eu

    # Southeast Asia Region (Secondary)
    with Cluster("Southeast Asia (Secondary Region)"):
        vnet_sea = VirtualNetworks("VNet SE Asia")
        appgw_sea = ApplicationGateway("App Gateway")
        with Cluster("App Tier"):
            vmss_sea = VMScaleSet("VM Scale Set")
        sql_sea = SQLDatabases("SQL DB\nSecondary\nZone-Redundant")
        blob_sea = BlobStorage("Blob Storage\nRA-GRS")
        vnet_sea >> appgw_sea >> vmss_sea
        vmss_sea >> sql_sea
        vmss_sea >> blob_sea

    # Traffic Manager routes users to the closest region's App Gateway
    traffic_manager >> [appgw_east, appgw_eu, appgw_sea]

    # SQL Database geo-replication (primary to secondaries)
    sql_east >> Edge(label="Active Geo-Replication", style="dashed", color="blue") >> sql_eu
    sql_east >> Edge(label="Active Geo-Replication", style="dashed", color="blue") >> sql_sea

    # Blob Storage cross-region replication (RA-GRS)
    blob_east >> Edge(label="RA-GRS Replication", style="dotted", color="purple") >> blob_eu
    blob_east >> Edge(label="RA-GRS Replication", style="dotted", color="purple") >> blob_sea

    # Failover: SQL secondary can become new primary (conceptual)
    sql_eu >> Edge(label="Failover Promotion", style="dashed", color="red") >> sql_east
    sql_sea >> Edge(label="Failover Promotion", style="dashed", color="red") >> sql_east

    # Users connect to Traffic Manager (not shown: you can add a generic "User" node if desired)