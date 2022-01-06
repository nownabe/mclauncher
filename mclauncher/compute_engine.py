import time
from os import environ
from pprint import pprint

import googleapiclient.discovery
import google.auth

from .instance import Instance

credentials, project = google.auth.default()
compute = googleapiclient.discovery.build(
    'compute', 'v1', credentials=credentials)

zone = environ['INSTANCE_ZONE']
name = environ['INSTANCE_NAME']


def get_instance() -> Instance:
    request = compute.instances().get(
        project=project,
        zone=zone,
        instance=name,
    )
    response = request.execute()

    address = None

    if response['status'] == 'RUNNING':
        address = response['networkInterfaces'][0]['accessConfigs'][0]['natIP']

    return Instance(
        address=address,
        is_running=response['status'] == 'RUNNING'
    )