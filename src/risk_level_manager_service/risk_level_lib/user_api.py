#
# Author:  Dlo Bagari
# created Date: 15-11-2019
import requests


class UserApi:
    def __init__(self, settings, logger):
        self._settings = settings
        self._logger = logger
        self._user_api_url = f'http://{self._settings["user_service_ip"]}:{self._settings["user_service_port"]}'
        self._request_header = {"Accept": "application/json", "Content-Type": "application/json"}

    def find_group_by_name(self, group_name):
        """
        send request to User service in order to get a group object.
        :param group_name: group name
        :return: status_code, group
        """
        try:
            params = {"name": group_name}
            url = self._user_api_url + "/group/filter"
            response = requests.get(url, headers=self._request_header, params=params)
            return response.status_code, response.json()
        except KeyboardInterrupt:
            print()
            exit(0)

    def change_user_group(self, user_id, group_name):
        """
        send request to user Service in order to change a user's group
        :param user_id:
        :param group_name:
        :return:
        """
        try:
            params = {"user_id": user_id, "group_name": group_name}
            url = self._user_api_url + "/group/change"
            response = requests.post(url, headers=self._request_header, params=params)
            return response.status_code, response.json()
        except KeyboardInterrupt:
            print()
            exit(0)