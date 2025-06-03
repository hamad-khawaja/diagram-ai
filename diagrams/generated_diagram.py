from diagrams import Diagram, Cluster, Edge
from diagrams.aws.network import VPC, PublicSubnet, PrivateSubnet, ALB
from diagrams.aws.compute import EC2
from diagrams.aws.database import RDS
from diagrams.aws.storage import S3

with Diagram(
    "AWS 3-Tier Web Architecture",
    outformat=["png", "svg"],
    show=False,
    direction="TB",
    graph_attr={"fontsize": "20"},
):
    # Architecture summary label
    summary = Edge(label="This diagram shows a classic AWS 3-tier architecture: ALB in a public subnet, EC2 web/app servers in private subnets, and RDS SQL database in a secure data tier.", style="invis")

    # VPC
    with Cluster("VPC"):
        # Public Subnet (Web Tier)
        with Cluster("Public Subnet\n(Web Tier)"):
            alb = ALB("Application Load Balancer")

        # Private Subnet (App Tier)
        with Cluster("Private Subnet\n(App Tier)"):
            app_servers = [EC2("App Server 1"), EC2("App Server 2")]

        # Private Subnet (Data Tier)
        with Cluster("Private Subnet\n(Data Tier)"):
            db = RDS("RDS\nSQL Database")

    # S3 for static assets (outside VPC)
    s3 = S3("S3\nStatic Assets")

    # Connections
    alb >> app_servers
    for app in app_servers:
        app >> db
        app >> s3

    # Place summary at the top
    summary >> alb