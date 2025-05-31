from diagrams import Diagram, Cluster
from diagrams.aws.network import VPC
from diagrams.aws.compute import EC2

with Diagram(
    "This diagram shows a single AWS VPC containing two EC2 instances for compute workloads.",
    outformat=["png", "svg", "pdf", "dot", "jpg"],
    show=False,
    direction="TB"
):
    with Cluster("VPC"):
        ec2_1 = EC2("EC2 Instance 1")
        ec2_2 = EC2("EC2 Instance 2")
        ec2_1 - ec2_2  # Bidirectional connection to indicate they are in the same VPC