from diagrams import Diagram, Cluster
from diagrams.aws.network import VPC, ALB, Nacl
from diagrams.aws.compute import EC2
from diagrams.aws.database import RDS
from diagrams.aws.security import IAM
with Diagram("3-Tier AWS Architecture", outformat=["png", "svg"], direction="TB"):
    # VPC Configuration
    with Cluster("VPC (us-east-1)"):
        # Security
        nacl = Nacl("Network ACL")
        iam = IAM("IAM Roles")
        # Web Tier
        with Cluster("Public Subnets"):
            alb = ALB("Application Load Balancer")
            web_instances = [EC2("Web Server 1"),
                             EC2("Web Server 2")]
        # Application Tier
        with Cluster("Private Subnets"):
            app_instances = [EC2("App Server 1"),
                             EC2("App Server 2")]
        # Database Tier
        with Cluster("Database Subnets"):
            aurora = RDS("Amazon Aurora")
    # Connections
    alb >> web_instances
    for web in web_instances:
        web >> app_instances
    for app in app_instances:
        app >> aurora
    # Security Connections
    nacl >> web_instances
    nacl >> app_instances
    nacl >> aurora
    iam >> web_instances
    iam >> app_instances
    iam >> aurora