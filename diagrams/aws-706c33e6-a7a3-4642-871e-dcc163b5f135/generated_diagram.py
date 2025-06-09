from diagrams import Diagram, Cluster
from diagrams.aws.compute import EC2
from diagrams.aws.database import Aurora
from diagrams.aws.network import VPC, InternetGateway, ALB
from diagrams.aws.network import PrivateSubnet, PublicSubnet
# URL for the diagrams library documentation
# https://diagrams.mingrammer.com/docs/nodes/aws
with Diagram("Three-Tier Architecture", outformat=["png", "svg"], direction="TB", show=False):
    # Define the VPC
    with Cluster("VPC"):
        # Define the public subnet for the presentation layer
        with Cluster("Public Subnet"):
            # Internet Gateway for external access
            igw = InternetGateway("Internet Gateway")
            # Load Balancer for distributing traffic
            alb = ALB("Load Balancer")
            # EC2 instances for the presentation layer
            ec2_instances = [EC2("Web Server 1"),
                             EC2("Web Server 2")]
        # Define the private subnet for the data layer
        with Cluster("Private Subnet"):
            # Aurora database for the data layer
            aurora_db = Aurora("Aurora Database")
    # Connectivity
    igw >> alb  # Internet traffic to Load Balancer
    alb >> ec2_instances  # Load Balancer to EC2 instances
    for ec2 in ec2_instances:
        ec2 >> aurora_db  # EC2 instances to Aurora database