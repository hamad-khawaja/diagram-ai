from diagrams import Diagram, Cluster
from diagrams.aws.network import VPC, InternetGateway, NATGateway
from diagrams.aws.compute import EC2

with Diagram("VPC with 3 Public and 3 Private Subnets (Multi-AZ)", show=False, direction="TB"):
    vpc = VPC("VPC")
    igw = InternetGateway("Internet Gateway")
    vpc >> igw

    nat_gateways = []
    public_ec2_list = []
    private_ec2_list = []

    # Represent each AZ
    for i in range(1, 4):
        with Cluster(f"AZ{i}"):
            # Public Subnet
            with Cluster("Public Subnet"):
                pub_ec2 = EC2(f"Public EC2 {i}")
                nat_gw = NATGateway(f"NAT GW {i}")
                pub_ec2 >> nat_gw     # Public EC2 to NAT Gateway for completeness
                nat_gw << igw         # NAT Gateway connected to IGW for outbound traffic

            # Private Subnet
            with Cluster("Private Subnet"):
                priv_ec2 = EC2(f"Private EC2 {i}")
                priv_ec2 >> nat_gw    # Private EC2 uses NAT Gateway for outbound internet

            # Collect for overall connections if needed
            nat_gateways.append(nat_gw)
            public_ec2_list.append(pub_ec2)
            private_ec2_list.append(priv_ec2)

    # Show that all NAT Gateways are inside VPC
    for nat_gw in nat_gateways:
        vpc >> nat_gw