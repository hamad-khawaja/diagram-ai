from diagrams import Diagram, Cluster, Edge
from diagrams.aws.compute import Lambda
from diagrams.aws.security import IAMRole
from diagrams.aws.storage import S3
from diagrams.aws.database import Dynamodb
from diagrams.aws.analytics import Kinesis

env_name = "dev"  # Replace with your EnvName parameter if desired

with Diagram(f"AWS Lambda Sample ({env_name})", show=False, direction="TB"):
    with Cluster(f"Lambda Environment: {env_name}"):
        lambda_role = IAMRole("LambdaRole")
        lambda_func = Lambda("LambdaFunction")
        lambda_func << Edge(label="assume role") << lambda_role

        # External AWS services Lambda can access
        s3 = S3("S3 (Full Access)")
        ddb = Dynamodb("DynamoDB (Full Access)")
        kinesis = Kinesis("Kinesis (Full Access)")

        lambda_func >> [s3, ddb, kinesis]