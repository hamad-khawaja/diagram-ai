from diagrams import Diagram, Cluster, Edge
from diagrams.aws.network import VPC, PublicSubnet, PrivateSubnet, InternetGateway, NATGateway, Route53, ALB
from diagrams.aws.compute import EC2, Lambda, EKS
from diagrams.aws.ml import Sagemaker, Comprehend
from diagrams.aws.storage import S3
from diagrams.aws.database import Dynamodb
from diagrams.aws.integration import SQS
from diagrams.aws.security import IAMRole, KMS
from diagrams.aws.management import Cloudwatch

with Diagram(
    "AWS AI/ML Application Architecture\nThis architecture uses S3 for data storage, SageMaker for model training/inference, EKS for scalable app serving, and integrates security, monitoring, and queueing for a robust AI pipeline.",
    show=False,
    direction="TB",
    outformat=["png", "svg", "pdf", "dot", "jpg"]
):
    # Global DNS
    dns = Route53("Route 53")

    # VPC and Networking
    with Cluster("VPC"):
        igw = InternetGateway("Internet Gateway")
        nat = NATGateway("NAT Gateway")
        with Cluster("Public Subnet"):
            alb = ALB("App Load Balancer")
        with Cluster("Private Subnet"):
            with Cluster("App Layer"):
                eks = EKS("EKS\nModel API")
                lambda_func = Lambda("Pre/Post Processing")
            with Cluster("ML Services"):
                sagemaker = Sagemaker("SageMaker\nTrain/Inference")
                comprehend = Comprehend("Comprehend\nNLP")
            with Cluster("Data Layer"):
                s3 = S3("S3\nData Lake")
                ddb = Dynamodb("DynamoDB\nMetadata")
            queue = SQS("SQS\nAsync Jobs")

    # Security & Monitoring
    with Cluster("Security & Monitoring"):
        iam = IAMRole("IAM Roles")
        kms = KMS("KMS")
        cw = Cloudwatch("CloudWatch")

    # Connections
    dns >> alb
    alb >> eks
    eks >> lambda_func
    lambda_func >> Edge(label="Invoke") >> sagemaker
    lambda_func >> Edge(label="NLP") >> comprehend
    eks >> Edge(label="Async Task") >> queue
    queue >> lambda_func

    # Data flow
    eks >> s3
    sagemaker >> s3
    comprehend >> s3
    eks >> ddb
    lambda_func >> ddb

    # Security
    for node in [eks, lambda_func, sagemaker, comprehend, ddb, s3]:
        node >> Edge(style="dashed", color="brown", label="IAM") >> iam
        node >> Edge(style="dashed", color="purple", label="KMS") >> kms

    # Monitoring
    for node in [eks, lambda_func, sagemaker, comprehend]:
        node >> Edge(style="dotted", color="orange", label="Metrics/Logs") >> cw