# Author:  Dlo Bagari
# created Date: 11-11-2019

from adal import AuthenticationContext
import datetime
from datetime import timedelta


class AccessToken:
    def __init__(self):
        self._logger = None
        self._settings = None
        self._token = None

    def set_logger(self, logger):
        self._logger = logger

    def set_settings(self, settings):
        self._settings = settings
        self._get_token()

    def _get_token(self):
        """request a valid access token from azure active directory
        """
        auth_context = AuthenticationContext(f"{self._settings['microsoft_login']}/{self._settings['tenant_name']}")
        token = auth_context.acquire_token_with_client_credentials(resource=self._settings["resource"],
                                                                   client_id=self._settings["app_id"],
                                                                   client_secret=self._settings["app_secret"])
        self._token = token

    def is_expired(self):
        """checks if the exist access token is expired or not
        :return: boolean
        """
        date_time_str = self._token["expiresOn"]
        expiry_date = datetime.datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S.%f')
        expiry_date = expiry_date - timedelta(minutes=5)
        time_to_compare = datetime.datetime.now()
        return time_to_compare >= expiry_date

    def refresh_token(self):
        """
        refresh the expired token
        :return:
        """
        self._get_token()

    def access_token(self):
        """
        return a valid token
        :return:token
        """
        if self.is_expired() is True:
            self.refresh_token()
        return self._token






