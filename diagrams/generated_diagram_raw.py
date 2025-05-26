from diagrams import Diagram, Cluster
from diagrams.azure.network import VirtualNetworks, Subnets, PrivateEndpoint
from diagrams.azure.database import SQLDatabases
from diagrams.azure.web import AppServices

with Diagram("Azure VNet with Integration and Database Subnets", show=False):
    # App Service (PaaS) - should NOT be inside VNet cluster
    app_service = AppServices("App Service")

    with Cluster("VNet my-vnet"):
        # Integration Subnet for App Service integration
        with Cluster("Subnet integration-subnet"):
            integration_subnet = Subnets("Integration Subnet")
            # App Service connects to this subnet via VNet Integration

        # Database Subnet with SQL DB and Private Endpoint
        with Cluster("Subnet db-subnet"):
            db_subnet = Subnets("DB Subnet")
            sql_db = SQLDatabases("SQL Database")
            pe_sql = PrivateEndpoint("Private Endpoint\n(SQL DB)")
            sql_db >> pe_sql

    # Connections
    app_service >> integration_subnet  # VNet Integration
    pe_sql >> db_subnet  # Private Endpoint is in DB Subnet