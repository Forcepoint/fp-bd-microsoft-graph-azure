from os import system, path
from kafka_cli.create_service import CreateService
import yaml
from time import sleep


class RunKafka:
    def __init__(self, parser):
        self._parser = parser
        self._setting = None
        self._args = None

    def __call__(self, args):
        self._args = args
        # make sure kafka service are exists
        with open(self._args.config_file) as f:
            self._settings = yaml.load(f, yaml.SafeLoader)
        zookeeper_service_path = "/etc/systemd/system/{}.service".format("zookeeper")
        kafka_service_path = "/etc/systemd/system/{}.service".format("kafka")
        if (path.isfile(zookeeper_service_path) and path.isfile(kafka_service_path)) is False:
            self._parser.error("the required systemd services are not found, "
                               "please create these service. use service -h for more info")
        # make sure service are running
        zookeeper_running, error = self.is_service_running("zookeeper")
        kafka_running, error = self.is_service_running("zookeeper")
        if (zookeeper_running and kafka_running) is False:
            # servers are not running, run them
            system("systemctl daemon-reload")
            sleep(4)
            system("systemctl start {}.service".format('zookeeper'))
            sleep(10)
            system("systemctl start {}.service".format('kafka'))
            sleep(10)

        # make sure the required topic is exists
        cmd = f"{self._settings['kafka_directory']}/bin/kafka-topics.sh --list --zookeeper localhost:2181"
        output, error = CreateService.execute_cmd(cmd)
        output = str(output).strip().strip('\n')
        required_topic = {self._settings["logs_topic_name"], self._settings["risk_level_topic_name"]}
        if len(output) != 0:
            for topic in required_topic:
                if topic not in output:
                    cmd = f"{self._settings['kafka_directory']}/bin/kafka-topics.sh --create --zookeeper" \
                          f" localhost:2181 --replication-factor 1 --partitions 1" \
                          f" --topic {topic}"
                    output, error = CreateService.execute_cmd(cmd)
                    if f"Created topic \"{topic}\"" not in output:
                        self._parser.error(f"Failed in creating the topic {topic}")
                    sleep(5)

    def is_service_running(self, name):
        cmd = "systemctl list-units"
        output, errors = CreateService.execute_cmd(cmd)
        output = output.strip()
        if len(output) != 0:
            output = str(output).split("\n")
            for line in output:
                if line.strip().startswith("{}.service ".format(name)):
                    return True, 0
            return False, 0
        return False, 1