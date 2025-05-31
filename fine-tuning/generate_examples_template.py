import jsonlines

EXAMPLES = [
    {
        "prompt": "Generate a simple AWS web application architecture with an Application Load Balancer, two EC2 instances, and an RDS database.",
        "completion": """from diagrams import Diagram, Cluster\nfrom diagrams.aws.network import ALB\nfrom diagrams.aws.compute import EC2\nfrom diagrams.aws.database import RDS\nfrom diagrams.generic.blank import Blank\n\nwith Diagram(\n    'Simple AWS Web App',\n    show=False,\n    outformat=['png', 'svg', 'pdf', 'dot', 'jpg']\n):\n    summary = Blank('This diagram shows a simple AWS web application with an Application Load Balancer, two EC2 instances, and an RDS database.')\n    alb = ALB('ALB')\n    with Cluster('Web Tier'):\n        web_servers = [EC2('Web1'), EC2('Web2')]\n    db = RDS('UserDB')\n    alb >> web_servers >> db\n"""
    },
    {
        "prompt": "Create a multi-region Azure architecture with Traffic Manager, Application Gateways, VM Scale Sets, and SQL Databases.",
        "completion": """from diagrams import Diagram, Cluster\nfrom diagrams.azure.network import TrafficManagerProfiles, ApplicationGateway\nfrom diagrams.azure.compute import VMScaleSet\nfrom diagrams.azure.database import SQLDatabases\nfrom diagrams.generic.blank import Blank\n\nwith Diagram(\n    'Azure Multi-Region Web App',\n    show=False,\n    outformat=['png', 'svg', 'pdf', 'dot', 'jpg']\n):\n    summary = Blank('This diagram shows a multi-region Azure web application using Traffic Manager, Application Gateways, VM Scale Sets, and SQL Databases.')\n    tm = TrafficManagerProfiles('Traffic Manager')\n    with Cluster('East US'):\n        appgw_east = ApplicationGateway('App Gateway')\n        vmss_east = VMScaleSet('VM Scale Set')\n        sql_east = SQLDatabases('SQL DB')\n        appgw_east >> vmss_east >> sql_east\n    # ... (other regions) ...\n"""
    },
    {
        "prompt": "Show a GCP architecture with a Load Balancer, two GCE instances, and a Cloud SQL database.",
        "completion": """from diagrams import Diagram, Cluster\nfrom diagrams.gcp.network import LoadBalancing\nfrom diagrams.gcp.compute import GCE\nfrom diagrams.gcp.database import SQL\nfrom diagrams.generic.blank import Blank\n\nwith Diagram(\n    'GCP Web App',\n    show=False,\n    outformat=['png', 'svg', 'pdf', 'dot', 'jpg']\n):\n    summary = Blank('This diagram shows a GCP web application with a Load Balancer, two GCE instances, and a Cloud SQL database.')\n    lb = LoadBalancing('Load Balancer')\n    with Cluster('Web Tier'):\n        gce1 = GCE('GCE1')\n        gce2 = GCE('GCE2')\n    db = SQL('Cloud SQL')\n    lb >> [gce1, gce2] >> db\n"""
    },
    {
        "prompt": "Create a multi-region Azure architecture with Traffic Manager, Application Gateways, VM Scale Sets, and SQL Databases.",
        "completion": """from diagrams import Diagram, Cluster\nfrom diagrams.azure.network import TrafficManagerProfiles, ApplicationGateway\nfrom diagrams.azure.compute import VMScaleSet\nfrom diagrams.azure.database import SQLDatabases\nfrom diagrams.generic.blank import Blank\n\nwith Diagram(\n    'Azure Multi-Region Web App',\n    show=False,\n    outformat=['png', 'svg', 'pdf', 'dot', 'jpg']\n):\n    summary = Blank('This diagram shows a multi-region Azure web application using Traffic Manager, Application Gateways, VM Scale Sets, and SQL Databases.')\n    tm = TrafficManagerProfiles('Traffic Manager')\n    with Cluster('East US'):\n        appgw_east = ApplicationGateway('App Gateway')\n        vmss_east = VMScaleSet('VM Scale Set')\n        sql_east = SQLDatabases('SQL DB')\n        appgw_east >> vmss_east >> sql_east\n    # ... (other regions) ...\n"""
    },
    {
        "prompt": "Show a GCP architecture with a Load Balancer, two GCE instances, and a Cloud SQL database.",
        "completion": """from diagrams import Diagram, Cluster\nfrom diagrams.gcp.network import LoadBalancing\nfrom diagrams.gcp.compute import GCE\nfrom diagrams.gcp.database import SQL\nfrom diagrams.generic.blank import Blank\n\nwith Diagram(\n    'GCP Web App',\n    show=False,\n    outformat=['png', 'svg', 'pdf', 'dot', 'jpg']\n):\n    summary = Blank('This diagram shows a GCP web application with a Load Balancer, two GCE instances, and a Cloud SQL database.')\n    lb = LoadBalancing('Load Balancer')\n    with Cluster('Web Tier'):\n        gce1 = GCE('GCE1')\n        gce2 = GCE('GCE2')\n    db = SQL('Cloud SQL')\n    lb >> [gce1, gce2] >> db\n"""
    },
    {
        "prompt": "Generate a multi-region AWS architecture with Route 53, ALB, EC2 instances, and Aurora Global Database.",
        "completion": """from diagrams import Diagram, Cluster\nfrom diagrams.aws.network import Route53, ALB\nfrom diagrams.aws.compute import EC2\nfrom diagrams.aws.database import Aurora\nfrom diagrams.aws.storage import S3\nfrom diagrams.generic.blank import Blank\n\nwith Diagram(\n    'Multi-Region AWS Architecture',\n    show=False,\n    outformat=['png', 'svg', 'pdf', 'dot', 'jpg']\n):\n    summary = Blank('This diagram shows a multi-region AWS architecture with Route 53 for global DNS, Aurora Global Database for cross-region replication, and S3 for cross-region storage.')\n    dns = Route53('Route 53')\n    with Cluster('US East (N. Virginia)'):\n        alb_east = ALB('ALB')\n        app_east = [EC2('App 1'), EC2('App 2')]\n        aurora_east_primary = Aurora('Aurora Writer (Primary)')\n        aurora_east_replicas = [Aurora('Aurora Reader 1'), Aurora('Aurora Reader 2')]\n        s3_east = S3('S3 (us-east-1)')\n        alb_east >> app_east >> aurora_east_primary\n        for app in app_east:\n            app >> aurora_east_replicas\n            app >> s3_east\n    # ... (other regions) ...\n"""
    },
    {
        "prompt": "Create a multi-region Azure architecture with Traffic Manager, Application Gateways, VM Scale Sets, and SQL Databases.",
        "completion": """from diagrams import Diagram, Cluster\nfrom diagrams.azure.network import TrafficManagerProfiles, ApplicationGateway\nfrom diagrams.azure.compute import VMScaleSet\nfrom diagrams.azure.database import SQLDatabases\nfrom diagrams.generic.blank import Blank\n\nwith Diagram(\n    'Azure Multi-Region Web App',\n    show=False,\n    outformat=['png', 'svg', 'pdf', 'dot', 'jpg']\n):\n    summary = Blank('This diagram shows a multi-region Azure web application using Traffic Manager, Application Gateways, VM Scale Sets, and SQL Databases.')\n    tm = TrafficManagerProfiles('Traffic Manager')\n    with Cluster('East US'):\n        appgw_east = ApplicationGateway('App Gateway')\n        vmss_east = VMScaleSet('VM Scale Set')\n        sql_east = SQLDatabases('SQL DB')\n        appgw_east >> vmss_east >> sql_east\n    # ... (other regions) ...\n"""
    },
    {
        "prompt": "Create a multi region Arora architecture with Route 53, ALB, EC2 instances, and Aurora Global Database.",
        "completion": """from diagrams import Diagram, Cluster\nfrom diagrams.aws.network import Route53, ALB\nfrom diagrams.aws.compute import EC2\nfrom diagrams.aws.database import Aurora\nfrom diagrams.aws.storage import S3\nfrom diagrams.generic.blank import Blank\n\nwith Diagram(\n    'Multi-Region AWS Architecture',\n    show=False,\n    outformat=['png', 'svg', 'pdf', 'dot', 'jpg']\n):\n    summary = Blank('This diagram shows a multi-region AWS architecture with Route 53 for global DNS, Aurora Global Database for cross-region replication, and S3 for cross-region storage.')\n    dns = Route53('Route 53')\n    with Cluster('US East (N. Virginia)'):\n        alb_east = ALB('ALB')\n        app_east = [EC2('App 1'), EC2('App 2')]\n        aurora_east_primary = Aurora('Aurora Writer (Primary)')\n        aurora_east_replicas = [Aurora('Aurora Reader 1'), Aurora('Aurora Reader 2')]\n        s3_east = S3('S3 (us-east-1)')\n        alb_east >> app_east >> aurora_east_primary\n        for app in app_east:\n            app >> aurora_east_replicas\n            app >> s3_east\n    # ... (other regions) ...\n"""
    },
    {
        "prompt": "Generate a diagram for Deploy SQL Server FCIs on Amazon EC2 and Amazon FSx for Windows File Server.",
        "completion": """from diagrams import Diagram, Cluster\nfrom diagrams.aws.compute import EC2\nfrom diagrams.aws.storage import FSx\nfrom diagrams.aws.database import RDS\nfrom diagrams.generic.blank import Blank\n\nwith Diagram(\n    'SQL Server FCI on EC2 and FSx',\n    show=False,\n    outformat=['png', 'svg', 'pdf', 'dot', 'jpg']\n):\n    summary = Blank('This diagram shows a SQL Server Failover Cluster Instance (FCI) deployed on Amazon EC2 instances with Amazon FSx for Windows File Server as shared storage.')\n    with Cluster('SQL Server FCI'):\n        sql_fci = [EC2('SQL Node 1'), EC2('SQL Node 2')]\n    fsx = FSx('FSx for Windows File Server')\n    sql_fci >> fsx\n"""
    } 
]

SYSTEM_PROMPT = "You are a helpful assistant that generates diagrams code. Always follow best practices and only use supported nodes."

with jsonlines.open('custom_examples.jsonl', mode='w') as writer:
    for ex in EXAMPLES:
        writer.write({
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": ex["prompt"]},
                {"role": "assistant", "content": ex["completion"]}
            ]
        })

print("custom_examples.jsonl created with sample prompt-completion pairs.")
