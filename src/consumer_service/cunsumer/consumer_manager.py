import yaml
import requests
from puller.kafkapuller import KafkaPuller
from lib_consumer.logger import Logger


class ConsumerManager:
    def __init__(self):
        self._args = None
        self._kafka_puller = None
        self._settings = None

    def __call__(self, args):
        self._args = args
        with open(self._args.config_file) as f:
            self._settings = yaml.load(f, yaml.SafeLoader)
        self._logger = Logger(self._settings["logs_directory"])
        # TODO: if user API is not available
        try:
            self._kafka_puller = KafkaPuller(self._settings,
                                             self._args.client_id, self._args.session_timeout,
                                             True, self._logger)
            self._kafka_puller.listener(self._settings["fba_kafka_topic_name"], "0.1")
        except requests.exceptions.ConnectionError as e:
            print(e)