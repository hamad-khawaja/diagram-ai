from diagrams import Diagram, Cluster, Edge
from diagrams.gcp.network import LoadBalancing, VPC
from diagrams.gcp.compute import GCE
from diagrams.gcp.database import SQL
from diagrams.gcp.storage import GCS

with Diagram(
    "GCP Three-Tier Web Architecture\nGlobal Load Balancer routes traffic to Compute Engine VMs in a VPC, with Cloud SQL and Cloud Storage for data.",
    outformat=["png", "svg", "pdf", "dot", "jpg"],
    show=False,
    direction="TB"
):
    # Presentation Tier
    lb = LoadBalancing("HTTP(S) Load Balancer")

    # Application Tier (inside VPC)
    with Cluster("VPC web-vpc"):
        with Cluster("Subnet web-subnet"):
            app_vms = [GCE("App VM 1"), GCE("App VM 2")]

    # Data Tier (outside VPC cluster)
    db = SQL("Cloud SQL")
    storage = GCS("Cloud Storage")

    # Connections
    lb >> app_vms
    for vm in app_vms:
        vm >> db
        vm >> storage