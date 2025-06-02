from diagrams import Diagram, Cluster, Edge
from diagrams.aws.network import Route53, ALB, VPC, InternetGateway, PublicSubnet, PrivateSubnet
from diagrams.aws.compute import EC2
from diagrams.aws.database import RDS
from diagrams.aws.storage import S3

with Diagram(
    "Simple AWS Web Application Architecture",
    outformat=["png", "svg", "pdf", "dot", "jpg"],
    show=False,
    direction="TB",
    graph_attr={"fontsize": "20"},
):
    # Architecture summary label
    summary = "A basic AWS web app: Route 53 DNS, ALB, EC2 in private subnet, RDS, and S3 for static assets."

    # Global DNS
    dns = Route53("Route 53")

    with Cluster("VPC"):
        igw = InternetGateway("Internet Gateway")

        with Cluster("Public Subnet"):
            alb = ALB("Application Load Balancer")
            alb >> igw

        with Cluster("Private Subnet"):
            web = EC2("Web App EC2")
            db = RDS("RDS MySQL")
            web >> db

        # ALB forwards traffic to EC2
        alb >> web

    # S3 for static assets
    s3 = S3("S3 Static Assets")

    # Connections
    dns >> alb
    web >> s3

    # Architecture summary label at the bottom
    summary_node = Edge(label=summary, style="invis")
    s3 >> summary_node