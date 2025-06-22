from diagrams import Diagram, Cluster
from diagrams.aws.network import VPC, ALB, Route53, Nacl
from diagrams.aws.compute import EC2
from diagrams.aws.database import RDS
from diagrams.aws.security import IAM
# Create the diagram with both PNG and SVG outputs
with Diagram("3-Tier AWS Architecture", outformat=["png", "svg"], direction="TB", show=False):
    # Networking and Security
    dns = Route53("DNS")
    nacl = Nacl("Network ACL")
    iam = IAM("IAM Roles")
    # VPC Configuration
    with Cluster("VPC (us-east-1)"):
        # Public Subnets
        with Cluster("Public Subnets"):
            alb = ALB("Application Load Balancer")
            web_instances = [EC2("Web Server 1"),
                             EC2("Web Server 2")]
        # Private Subnets
        with Cluster("Private Subnets"):
            app_instances = [EC2("App Server 1"),
                             EC2("App Server 2")]
            db = RDS("Amazon Aurora")
    # Connections
    dns >> alb
    nacl >> alb
    iam >> web_instances
    iam >> app_instances
    iam >> db
    # Connect web servers to ALB
    for web in web_instances:
        alb >> web
    # Connect app servers to web servers
    for web in web_instances:
        for app in app_instances:
            web >> app
    # Connect app servers to the database
    for app in app_instances:
        app >> db