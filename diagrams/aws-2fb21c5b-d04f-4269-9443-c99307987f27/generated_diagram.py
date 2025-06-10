from diagrams import Diagram, Cluster
from diagrams.aws.network import VPC, ALB, Nacl
from diagrams.aws.compute import EC2
from diagrams.aws.database import RDS
from diagrams.aws.security import IAM
with Diagram("3-Tier AWS Architecture", outformat=["png", "svg"], direction="TB", show=False):
    # VPC Configuration
    with Cluster("VPC (us-east-1)"):
        # Presentation Tier
        with Cluster("Public Subnet"):
            alb = ALB("Load Balancer")
            web_servers = [EC2("Web Server 1"),
                           EC2("Web Server 2")]
        # Application Tier
        with Cluster("Private Subnet"):
            app_servers = [EC2("App Server 1"),
                           EC2("App Server 2")]
        # Database Tier
        with Cluster("Database Subnet"):
            db_primary = RDS("Aurora Primary")
            db_replica = RDS("Aurora Replica")
        # Security
        nacl = Nacl("Network ACL")
        iam = IAM("IAM Roles")
    # Connections
    alb >> web_servers
    for web_server in web_servers:
        web_server >> app_servers
    for app_server in app_servers:
        app_server >> [db_primary, db_replica]
    # Security connections
    nacl >> web_servers
    nacl >> app_servers
    nacl >> [db_primary, db_replica]
    iam >> web_servers
    iam >> app_servers
    iam >> [db_primary, db_replica]