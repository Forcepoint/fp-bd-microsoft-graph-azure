#
# Author:  Dlo Bagari
# created Date: 14-11-2019
from .userutils import UserUtils


class MessageHandler:
    def __init__(self, settings, logger):
        self._settings = settings
        self._log = logger
        self._user_utils = UserUtils(self._settings, self._log)

    def handle_message(self, message, publisher):
        """
        validate user, create risk level object and send it to the kafka bus
        :param message:
        :param publisher: the publisher object
        :return: boolean,
        """
        user_id = message.get("user_id", None)
        if user_id is None:
            self._log.critical(self, "User ID is not exist in the received message")
            return False
        result, first_name, last_name = self._get_user_name(user_id)
        if result is False:
            self._log.error(self, "Failed in parsing the user name")
            return result
        result, user_object = self.is_valid_user(first_name, last_name)
        if result is True:
            user_org_id = user_object["id"]
            result, error_message = publisher.publish(message, user_org_id, first_name, last_name)
            if result is False:
                self._log(self, error_message)
                return False
        else:
            self._log.error(self, f"Not a valid user {first_name} {last_name}")
            return False

    def _get_user_name(self, user_identifier):
        """
        extract user first name and last name from the user identifier
        :param user_identifier: the user's identifier
        :return: fist_name, last_name
        """
        user_name = user_identifier.strip().split('@')[0]
        delimiter = " "
        if "." in user_name:
            delimiter = "."
        if "," in user_name:
            delimiter = ','
        parts = user_name.split(delimiter)
        if len(parts) == 2:
            return True, parts[0], parts[1]
        else:
            return False, "", ""

    def is_valid_user(self, first_name, last_name):
        """
        check if a user is exists in the database
        :param first_name:
        :param last_name:
        :return:boolean
        """
        response_code, user = self._user_utils.find_user_by_name(first_name, last_name)
        if response_code == 200:
            value = user.get("value", None)
            if value is not None and len(value) != 0:
                return True, value[0]
        return False, {}

