# This list should be updated if you upgrade diagrams or want to support more resources
# Only allow imports from these modules/classes
ALLOWED_IMPORTS = [
    # Core diagrams
    'from diagrams import Diagram',
    'from diagrams import Cluster',
    'from diagrams import Node',
    'from diagrams import Edge',
    'from diagrams.custom import Custom',

    # AWS (all major categories)
    'from diagrams.aws.compute import',
    'from diagrams.aws.database import',
    'from diagrams.aws.network import',
    'from diagrams.aws.storage import',
    'from diagrams.aws.integration import',
    'from diagrams.aws.analytics import',
    'from diagrams.aws.management import',
    'from diagrams.aws.security import',
    'from diagrams.aws.migration import',
    'from diagrams.aws.devtools import',
    'from diagrams.aws.iot import',
    'from diagrams.aws.ml import',
    'from diagrams.aws.media import',
    'from diagrams.aws.mobile import',
    'from diagrams.aws.arvr import',
    'from diagrams.aws.blockchain import',
    'from diagrams.aws.business import',
    'from diagrams.aws.enduser import',
    'from diagrams.aws.game import',
    'from diagrams.aws.general import',
    'from diagrams.aws.quantum import',
    'from diagrams.aws.robomaker import',
    'from diagrams.aws.satellite import',
    'from diagrams.aws.savingsplans import',
    'from diagrams.aws.sso import',
    'from diagrams.aws.vr import',

    # Azure (all major categories)
    'from diagrams.azure.compute import',
    'from diagrams.azure.database import',
    'from diagrams.azure.network import',
    'from diagrams.azure.storage import',
    'from diagrams.azure.analytics import',
    'from diagrams.azure.devops import',
    'from diagrams.azure.identity import',
    'from diagrams.azure.integration import',
    'from diagrams.azure.iot import',
    'from diagrams.azure.management import',
    'from diagrams.azure.media import',
    'from diagrams.azure.migrate import',
    'from diagrams.azure.ml import',
    'from diagrams.azure.security import',
    'from diagrams.azure.web import',

    # GCP (all major categories)
    'from diagrams.gcp.analytics import',
    'from diagrams.gcp.compute import',
    'from diagrams.gcp.database import',
    'from diagrams.gcp.devtools import',
    'from diagrams.gcp.iot import',
    'from diagrams.gcp.ml import',
    'from diagrams.gcp.network import',
    'from diagrams.gcp.security import',
    'from diagrams.gcp.storage import',
    'from diagrams.gcp.migration import',
    'from diagrams.gcp.management import',
    'from diagrams.gcp.media import',
    'from diagrams.gcp.identity import',
    'from diagrams.gcp.integration import',

    # Other (keep existing)
    'from diagrams.k8s.compute import',
    'from diagrams.k8s.network import',
    'from diagrams.k8s.storage import',
    'from diagrams.onprem.compute import',
    'from diagrams.onprem.database import',
    'from diagrams.onprem.network import',
    'from diagrams.onprem.monitoring import',
    'from diagrams.onprem.queue import',
    'from diagrams.programming.language import',
    'from diagrams.programming.framework import',
    'from diagrams.generic.blank import',
    'from diagrams.generic.compute import',
    'from diagrams.generic.database import',
    'from diagrams.generic.network import',
    'from diagrams.c4 import',
]

def is_code_whitelisted(code):
    import re
    for line in code.splitlines():
        if line.strip().startswith('from diagrams'):
            allowed = any(line.strip().startswith(imp) for imp in ALLOWED_IMPORTS)
            if not allowed:
                return False, line.strip()
    return True, None
