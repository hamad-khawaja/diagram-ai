from diagrams import Diagram, Cluster
from diagrams.aws.network import VPC, ALB, CloudFront, Route53, Nacl
from diagrams.aws.compute import EC2, Lambda
from diagrams.aws.database import RDS, Dynamodb
from diagrams.aws.storage import S3
from diagrams.aws.security import IAM
from diagrams.aws.media import ElasticTranscoder
from diagrams.aws.analytics import Kinesis
with Diagram("TikTok-like Application Architecture", outformat=["png", "svg"], show=False):
    # VPC Configuration
    with Cluster("VPC (us-east-1)"):
        # Public Subnet
        with Cluster("Public Subnet"):
            alb = ALB("Load Balancer")
            ec2_instances = [EC2("Web Server 1"), EC2("Web Server 2")]
        # Private Subnet
        with Cluster("Private Subnet"):
            rds = RDS("User Profiles DB")
            dynamodb = Dynamodb("Likes & Comments DB")
            lambda_function = Lambda("Content Processing")
    # Storage
    s3 = S3("Video & Static Assets")
    # Content Delivery and DNS
    cloudfront = CloudFront("CDN")
    route53 = Route53("DNS")
    # Media Processing
    transcoder = ElasticTranscoder("Video Transcoder")
    # Analytics
    kinesis = Kinesis("Real-time Analytics")
    # Security and Access Management
    nacl = Nacl("Network ACL")
    iam = IAM("IAM Roles & Policies")
    # Connections
    route53 >> alb
    alb >> ec2_instances
    ec2_instances >> rds
    ec2_instances >> dynamodb
    ec2_instances >> lambda_function
    lambda_function >> s3
    s3 >> cloudfront
    cloudfront >> transcoder
    transcoder >> s3
    ec2_instances >> kinesis
    # Security connections
    for resource in [ec2_instances, rds, dynamodb, s3, transcoder, kinesis]:
        nacl >> resource
        iam >> resource