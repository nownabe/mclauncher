import time

import googleapiclient.discovery
import google.auth

from mclauncher.config import Config

from .instance import Instance


class ComputeEngine:
    def __init__(self, config: Config):
        self.instance_zone = config.instance_zone
        self.instance_name = config.instance_name

        credentials, self.project = google.auth.default()
        self.__compute = googleapiclient.discovery.build(
            'compute', 'v1', credentials=credentials)

    def get_instance(self) -> Instance:
        request = self.__compute.instances().get(
            project=self.project,
            zone=self.instance_zone,
            instance=self.instance_name,
        )
        response = request.execute()

        address = None

        if response['status'] == 'RUNNING':
            address = response['networkInterfaces'][0]['accessConfigs'][0]['natIP']

        return Instance(
            address=address,
            is_running=response['status'] == 'RUNNING'
        )

    def start_instance(self) -> bool:
        request = self.__compute.instances().start(
            project=self.project,
            zone=self.instance_zone,
            instance=self.instance_name,
        )
        result = request.execute()

        while True:
            if result['status'] == 'DONE':
                if 'error' in result:
                    raise Exception(result['error'])
                break

            time.sleep(0.5)
            result = self.__compute.zoneOperations().get(
                project=self.project,
                zone=self.instance_zone,
                operation=result['name'],
            ).execute()

        return True

    def stop_instance(self) -> bool:
        request = self.__compute.instances().stop(
            project=self.project,
            zone=self.instance_zone,
            instance=self.instance_name,
        )
        result = request.execute()

        while True:
            if result['status'] == 'DONE':
                if 'error' in result:
                    raise Exception(result['error'])
                break

            time.sleep(0.5)
            result = self.__compute.zoneOperations().get(
                project=self.project,
                zone=self.instance_zone,
                operation=result['name'],
            ).execute()

        return True
