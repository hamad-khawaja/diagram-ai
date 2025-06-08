
# AWS Lambda Python 3.9 base image
FROM public.ecr.aws/lambda/python:3.9

# Install system dependencies
RUN yum install -y graphviz && yum clean all

WORKDIR /var/task

COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy application code
COPY . .

# Lambda handler
CMD ["lambda_handler.handler"]
