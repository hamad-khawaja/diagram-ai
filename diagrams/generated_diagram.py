from diagrams import Diagram, Cluster
from diagrams.aws.network import VPC, PublicSubnet, PrivateSubnet, InternetGateway
from diagrams.aws.compute import EC2
from diagrams.aws.database import RDS

with Diagram("AWS VPC with Public/Private Subnets", show=False, direction="TB"):
    vpc = VPC("VPC")
    igw = InternetGateway("Internet Gateway")
    vpc >> igw

    with Cluster("Public Subnet"):
        pub_subnet = PublicSubnet("Public Subnet")
        ec2_public = EC2("EC2 Public")

    with Cluster("Private Subnet"):
        priv_subnet = PrivateSubnet("Private Subnet")
        ec2_private = EC2("EC2 Private")
        rds = RDS("RDS DB")

    # Connections
    vpc >> pub_subnet
    vpc >> priv_subnet

    pub_subnet >> ec2_public
    priv_subnet >> ec2_private
    priv_subnet >> rds

    # Public EC2 can access Private EC2 and RDS (e.g., via bastion or app logic)
    ec2_public >> ec2_private
    ec2_private >> rds