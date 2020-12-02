import yaml
import json
from time import sleep
from risk_level_lib.logger import Logger
from risk_level_lib.risk_level_consumer import RiskLevelConsumer
from risk_level_lib.const_values import ConstValues
from risk_level_lib.user_api import UserApi

REST_TIME = 10


class RiskProcess:
    def __init__(self, parser):
        self._parser = parser
        self._args = None
        self._consumer = None
        self._risk_level_groups = {}
        self._user_api = None

    def __call__(self, args):
        self._args = args
        with open(self._args.config_file) as f:
            self._settings = yaml.load(f, yaml.SafeLoader)
        if self._settings is None:
            self._logger.error(self, "Failed in loading the config file")
            self._parser.error("Failed in loading the config file")
        self._logger = Logger(self._settings["logs_directory"])
        self._user_api = UserApi(self._settings, self._logger)
        self._get_risk_level_groups_name()
        error_code, error_message = self._is_risk_level_groups_exist()
        if error_code != ConstValues.ERROR_CODE_ZERO:
            self._logger.critical(self, error_message)
            self._parser.error(error_message)
        self._consumer = RiskLevelConsumer(self._settings)
        self._risk_level_listener()

    def _risk_level_listener(self):
        """
        Listen to the kafka bus, pull new risk levels objects and send them to the user service
        :return:
        """
        try:
            while True:
                for error_code, error_message, message in self._consumer.subscribe():
                    if message is None:
                        continue
                    if error_code == ConstValues.ERROR_CODE_ONE:
                        self._logger.error(self, error_message)
                        self._parser.error(error_message)
                    message = message.decode()
                    message = json.loads(message)
                    error_code, error_message = self._send_to_user_service(message)
                    if error_code != ConstValues.ERROR_CODE_ZERO:
                        self._logger.critical(self, error_message)
                sleep(REST_TIME)
        except KeyboardInterrupt:
            exit(0)

    def _send_to_user_service(self, message):
        """
        submit a change user group request to user service
        :param message: json file contain risk level info related to a user.
        :return:
        """
        risk_level = int(message["risk_level"])
        risk_level_group_name = self._risk_level_groups[risk_level]
        status_code, response = self._user_api.change_user_group(message["user_id"], risk_level_group_name)
        return ConstValues.ERROR_CODE_ZERO, ""

    def _get_risk_level_groups_name(self):
        """
        extract risk level groups name from settings
        :return: None
        """
        self._risk_level_groups[1] = self._settings["risk_level_groups_name"]["risk_level_one"]
        self._risk_level_groups[2] = self._settings["risk_level_groups_name"]["risk_level_two"]
        self._risk_level_groups[3] = self._settings["risk_level_groups_name"]["risk_level_three"]
        self._risk_level_groups[4] = self._settings["risk_level_groups_name"]["risk_level_four"]
        self._risk_level_groups[5] = self._settings["risk_level_groups_name"]["risk_level_five"]

    def _is_risk_level_groups_exist(self):
        """
        ensure the given group name is exists in azure AD
        :return: result, error_code, error_message
        """
        for group in self._risk_level_groups:
            status_code, response = self._user_api.find_group_by_name(self._risk_level_groups[group])
            if status_code != 200:
                return ConstValues.ERROR_CODE_ONE, response["error"]
            else:
                if len(response["value"]) != 0 and response["value"][0]["displayName"] != self._risk_level_groups[group]:
                    return ConstValues.ERROR_CODE_ONE, f"The group '{ self._risk_level_groups[group]}'"
        return ConstValues.ERROR_CODE_ZERO, ""
