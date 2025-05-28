from diagrams import Diagram, Cluster, Edge
from diagrams.aws.network import APIGateway
from diagrams.aws.compute import Lambda
from diagrams.aws.database import Dynamodb
from diagrams.aws.storage import S3
from diagrams.aws.management import Cloudwatch
from diagrams.aws.security import IAMRole

with Diagram("AWS Serverless Web Backend", show=False, direction="LR", outformat=["png", "svg", "pdf", "dot", "jpg"]):
    # API Gateway as entrypoint
    api = APIGateway("API Gateway")

    # Lambda function (backend logic)
    with Cluster("Serverless Compute"):
        lambda_func = Lambda("Lambda Function")
        lambda_role = IAMRole("Lambda IAM Role")
        lambda_func << Edge(style="dashed", label="assume role") << lambda_role

    # DynamoDB for data storage
    db = Dynamodb("DynamoDB Table")

    # S3 for static assets or file uploads
    s3 = S3("S3 Bucket")

    # CloudWatch for logs/monitoring
    cw = Cloudwatch("CloudWatch Logs")

    # Data flow
    api >> Edge(label="Invoke") >> lambda_func
    lambda_func >> Edge(label="Read/Write") >> db
    lambda_func >> Edge(label="Store/Retrieve") >> s3
    lambda_func >> Edge(label="Logs") >> cw