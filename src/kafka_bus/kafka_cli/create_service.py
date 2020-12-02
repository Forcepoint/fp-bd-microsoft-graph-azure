import subprocess
from subprocess import Popen
from os import system, path
import yaml


class CreateService:
    def __init__(self, parser):
        self._args = None
        self._parser = parser
        self._settings = None

    def __call__(self, args):
        self._args = args
        with open(self._args.config_file) as f:
            self._settings = yaml.load(f, yaml.SafeLoader)
        if self.is_service_exists() is False:
            self._create_service()
        else:
            self._parser.error("The service is already exists")

    @staticmethod
    def execute_cmd(cmd):
        process = Popen([cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        output, errors = process.communicate()
        return output.decode(), errors

    def is_service_exists(self):
        zookeeper_service_path = "/etc/systemd/system/{}.service".format("zookeeper")
        kafka_service_path = "/etc/systemd/system/{}.service".format("kafka")
        return path.isfile(zookeeper_service_path) and path.isfile(kafka_service_path)

    def _create_service(self):
        result = self._install_kafka()
        if result is False:
            self._parser.error("Failed in installing Apache Kafka")

        # create zookeeper service
        zookeeper_service_location = "/etc/systemd/system/zookeeper.service"
        zookeeper_service = """
[Unit]
Description=Starts the zookeeper Service
Wants=network-online.target
Requires=network.target remote-fs.target
After=network.target remote-fs.target

[Service]
Type=simple
ExecStart=/bin/sh -c '{0}/bin/zookeeper-server-start.sh {0}/config/zookeeper.properties > {0}/kafka.log 2>&1'
ExecStop={0}/bin/zookeeper-server-stop.sh
Restart=on-abnormal

[Install]
WantedBy=multi-user.target
""".format(self._settings["kafka_directory"])
        with open(zookeeper_service_location, 'w') as f:
            f.write(zookeeper_service)
        system("chmod 644 {}".format(zookeeper_service_location))

        # create kafka-server service
        server_service_location = "/etc/systemd/system/kafka.service"
        server_service = """
[Unit]
Description=Starts the kafka server Service
Requires=zookeeper.service
After=zookeeper.service

[Service]
Type=simple
ExecStartPre=/bin/sleep 5
ExecStart={0}/bin/kafka-server-start.sh {0}/config/server.properties
ExecStop={0}/bin/kafka-server-stop.sh
Restart=always

[Install]
WantedBy=multi-user.target
""".format(self._settings["kafka_directory"])
        with open(server_service_location, 'w') as f:
            f.write(server_service)
        system("chmod 644 {}".format(server_service_location))

    def _install_kafka(self):
        cmd = f"{self._settings['application_directory']}/scripts/kafka_installer.sh"
        system("chmod +x {}".format(cmd))
        cmd = cmd + " " + self._settings['kafka_directory']
        output, error = self.execute_cmd(cmd)
        return True



