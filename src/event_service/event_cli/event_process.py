# Author:  Dlo Bagari
# created Date: 11-11-2019

import yaml
from os import path
from datetime import datetime, timezone, timedelta
import dateutil.parser
from time import sleep
import json
from event_lib.logger import Logger
from event_lib.access_token import AccessToken
from event_lib.event_puller import EventPuller
from event_lib.field_mapper import FieldMapper
from event_lib.kafka_producer import KafkaProducer
from event_lib.const_values import ConstValues

LISTENER_SLEEP_TIME = 30


class EventProcess:
    def __init__(self, parser):
        self._args = None
        self._settings = None
        self._logger = None
        self._token = None
        self._event_puller = None
        self._mapper = None
        self._parser = parser
        self._producer = None
        self._timestamp = None

    def __call__(self, args):
        self._args = args
        with open(self._args.config_file) as f:
            self._settings = yaml.load(f, yaml.SafeLoader)
        self._logger = Logger(self._settings["logs_directory"])
        self._token = AccessToken(self._logger, self._settings)
        self._event_puller = EventPuller(self._token, self._settings)
        self._mapper = FieldMapper(self._settings)
        self._producer = KafkaProducer(self._settings)
        timestamp_file = f'{self._settings["application_directory"]}/timestamp'
        self._listen_to_logs(timestamp_file)

    def _get_logs(self, timestamp_file):
        if path.exists(timestamp_file):
            with open(timestamp_file) as f:
                self._timestamp = f.read().strip()
        else:
            now = datetime.now() - timedelta(days=27)
            self._timestamp = now.isoformat().split('T')[0]
        error_code, logs = self._event_puller.logs_request(self._timestamp)
        if error_code != 1:
            for log in logs['value']:
                json_file = self._mapper.map(log)
                result, error_message = self._producer.publish(json_file)
                if result is False:
                    self._logger.critical(self, "Failed in publishing a message: " + error_message)
                else:
                    timestamp = json_file["timestamp"]
                    self.update_timestamp(timestamp_file, timestamp)
        else:
            error_message = "{}: {}".format(logs["code"], logs["message"])
            self._logger.error(self, error_message)
            self._parser.error(error_message)

    def update_timestamp(self, timestamp_file, timestamp):
        new_timestamp = None
        previous_timestamp = None
        if path.exists(timestamp_file):
            with open(timestamp_file) as f:
                previous_timestamp = f.read().strip()
            previous_datetime = dateutil.parser.parse(previous_timestamp)
            previous_datetime = previous_datetime.astimezone(tz=timezone.utc)
            log_datetime = dateutil.parser.parse(timestamp)
            log_datetime = log_datetime.astimezone(tz=timezone.utc)
            if log_datetime > previous_datetime:
                new_timestamp = timestamp
        else:
            new_timestamp = timestamp
        if new_timestamp is not None:
            with open(timestamp_file, 'w') as f:
                new_timestamp = self._add_one_second(new_timestamp)
                f.write(new_timestamp)
                self._timestamp = new_timestamp
        else:
            self._timestamp = timestamp

    def _listen_to_logs(self, timestamp_file):
        try:
            while True:
                self._get_logs(timestamp_file)
                sleep(LISTENER_SLEEP_TIME)
        except KeyboardInterrupt:
            exit(0)

    def _add_one_second(self, new_timestamp):
        timestamp = dateutil.parser.parse(new_timestamp[:-1])
        timestamp = timestamp + timedelta(milliseconds=1)
        timestamp_iso = timestamp.isoformat()
        timestamp = timestamp_iso.split("+")[0] + "Z"
        return timestamp

