import openai
import json
import os

# Get your OpenAI API key from the environment variable
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise EnvironmentError("OPENAI_API_KEY environment variable not set.")

# Use the new OpenAI API client (openai>=1.0.0)
client = openai.OpenAI(api_key=OPENAI_API_KEY)

prompts = [
    "Generate a diagrams-python code example for a hybrid AWS and Azure architecture where AWS hosts the frontend and Azure hosts the backend database. Include a technical summary and use only supported nodes. Output should be ready for OpenAI fine-tuning and include all output formats.",
    "Generate a diagrams-python code example for a serverless microservices architecture using AWS Lambda, API Gateway, DynamoDB, and S3. Include a technical summary and use only supported nodes. Output should be ready for OpenAI fine-tuning and include all output formats.",
    "Create a diagrams-python code example for a multi-cloud architecture that integrates Google Cloud Platform (GCP) with Microsoft Azure, showcasing data flow between GCP BigQuery and Azure SQL Database. Include a technical summary and use only supported nodes. Output should be ready for OpenAI fine-tuning and include all output formats.",
    "Generate a diagrams-python code example for a high-availability architecture using AWS Route 53, Application Load Balancer, and multiple EC2 instances across two regions. Include a technical summary and use only supported nodes. Output should be ready for OpenAI fine-tuning and include all output formats.",
    "Create a diagrams-python code example for a secure data pipeline architecture using AWS Kinesis, Lambda, and S3, with encryption at rest and in transit. Include a technical summary and use only supported nodes. Output should be ready for OpenAI fine-tuning and include all output formats.",
    "Generate a diagrams-python code example for a real-time analytics architecture using Apache Kafka, Spark Streaming, and a NoSQL database. Include a technical summary and use only supported nodes. Output should be ready for OpenAI fine-tuning and include all output formats.",
    "Create a diagrams-python code example for a disaster recovery architecture using AWS Backup, S3 Glacier, and cross-region replication. Include a technical summary and use only supported nodes. Output should be ready for OpenAI fine-tuning and include all output formats.",
    "Generate a diagrams-python code example for a containerized application architecture using Docker, Kubernetes, and AWS EKS. Include a technical summary and use only supported nodes. Output should be ready for OpenAI fine-tuning and include all output formats.",
    "Create a diagrams-python code example for a data lake architecture using AWS Lake Formation, Glue, and Athena. Include a technical summary and use only supported nodes. Output should be ready for OpenAI fine-tuning and include all output formats.",
    "Generate a diagrams-python code example for a machine learning architecture using AWS SageMaker, S3, and Lambda for data preprocessing. Include a technical summary and use only supported nodes. Output should be ready for OpenAI fine-tuning and include all output formats."
   ]

output_file = "advanced_examples.jsonl"

with open(output_file, "w") as f:
    for prompt in prompts:
        response = client.chat.completions.create(
            model="gpt-4o",  # or "gpt-4-turbo" or your preferred model
            messages=[
                {"role": "system", "content": "You are an expert in cloud architecture and diagrams-python. Follow best practices, use only supported nodes, and always include a technical summary."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1200
        )
        completion = response.choices[0].message.content
        # Save in OpenAI fine-tuning .jsonl format
        f.write(json.dumps({"prompt": prompt, "completion": completion}) + "\n")

print(f"Saved {len(prompts)} advanced examples to {output_file}")
