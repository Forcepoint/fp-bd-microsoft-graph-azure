
import yaml
import sys
import json
from multiprocessing import Process
from time import sleep
from service_api.flask_api import *
from user_lib.log_consumer import LogConsumer


class FlaskProcess(Process):
    def __init__(self, flask_app, ip_address, port):
        super().__init__()
        self._flask_app = flask_app
        self._ip_address = ip_address
        self._port = port

    def run(self):
        try:
            self._flask_app.run(port=int(self._port), debug=False, host=self._ip_address)
        except KeyboardInterrupt:
            self.terminate()

    def join(self, timeout=None):
        try:
            super().join(timeout)
        except KeyboardInterrupt:
            print()
            self.terminate()


class UserService:
    def __init__(self, parser):
        self._args = None
        self._parser = parser
        self._settings = None
        self._consumer = None
        self._flask_process = None

    def __call__(self, args):
        try:
            self._args = args
            with open(self._args.config_file) as f:
                self._settings = yaml.load(f, yaml.SafeLoader)
            if self._settings is None:
                self._parser.error("Failed in loading the settings.yml file")
            self._logger = logger
            self._logger.set_log_directory(self._settings["logs_directory"])
            entity.set_settings(self._settings)
            access_token.set_settings(self._settings)
            access_token.set_logger(logger)
            self._consumer = LogConsumer(self._settings)
            risk_level_groups_name = self._get_risk_level_groups_name()
            group_api.set_groups_name(risk_level_groups_name)
            ip_address, port = self._settings["user_service_ip"], self._settings["user_service_port"]
            flask_process = FlaskProcess(app, ip_address, port)
            flask_process.start()
            self._flask_process = flask_process
            self._listen_to_new_logs()
        except KeyboardInterrupt:
            sys.exit()

    def _listen_to_new_logs(self, rest_time=30):
        """
        :param rest_time: time for pausing the listener
        pull logs from kafka bus and create entity and monitor them it required
        :return:
        """
        try:
            while True:
                self._consumer = LogConsumer(self._settings)
                for error_code, error_message, message in self._consumer.subscribe():
                    if message is None:
                        continue
                    if error_code == ConstValues.ERROR_CODE_ONE:
                        self._logger.error(self, error_message)
                        self._parser.error(error_message)
                    error_code, error_message = self._process_log(message)
                    if error_code != ConstValues.ERROR_CODE_ZERO:
                        self._logger.critical(self, error_message)
                sleep(rest_time)
        except KeyboardInterrupt:
            exit(0)

    def _process_log(self, message):
        message = message.decode()
        message = json.loads(message)
        user_name = None
        email_address = None
        for role in message["entities"]:
            if role["role"] == "User":
                user_name = role["entities"][0]
            elif role["role"] == "Email":
                email_address = role["entities"][0]
        if user_name is not None and email_address is not None:
            name_parts = user_name.split()
            if len(name_parts) > 1:
                entity_data = {"first_name": name_parts[0], "last_name": name_parts[1],
                               "email_address": email_address}
                error_code, result, entity_id = entity.handle_notification(entity_data)

        return 0, ""

    def _get_risk_level_groups_name(self):
        """
        extract risk level groups name from settings
        :return: None
        """
        return {1: self._settings["risk_level_groups_name"]["risk_level_one"],
                2: self._settings["risk_level_groups_name"]["risk_level_two"],
                3: self._settings["risk_level_groups_name"]["risk_level_three"],
                4: self._settings["risk_level_groups_name"]["risk_level_four"],
                5: self._settings["risk_level_groups_name"]["risk_level_five"]}


