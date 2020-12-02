import urllib.parse
from microsoft_graph.api_request import ApiRequest

MICROSOFT_GRAPH = "https://graph.microsoft.com/v1.0"


class UserApi:
    def __init__(self, access_token, logger=None):
        self._api_request = ApiRequest(access_token, logger)
        self._logger = logger

    def get_user(self, user_id=None):
        if user_id is None:
            endpoint = "https://graph.microsoft.com/v1.0/users"
        else:
            endpoint = f"https://graph.microsoft.com/v1.0/users/{user_id}"
        error_code, data = self._api_request.api_request(endpoint)
        return error_code, data

    def find_user_by_name(self, first_name, last_name):
        query = f"displayName eq '{first_name} {last_name}'"
        query = urllib.parse.quote(query)
        endpoint = f"https://graph.microsoft.com/v1.0/users?$filter={query}"
        error_code, data = self._api_request.api_request(endpoint)
        return error_code, data

    def get_user_groups(self, user_id):
        """
         return all groups the user is a nested member of.
        :param user_id:user_id or user's email address
        :return:error_code, groups
        """
        endpoint = f"{MICROSOFT_GRAPH}/users/{user_id}/memberOf"
        error_code, data = self._api_request.api_request(endpoint)
        return error_code, data

    def revoke_session(self, user_id):
        """
        prevents access to the organization's data through applications on the device by requiring the user to sign in
         again to all applications that they have previously consented to, independent of device
        :param user_id: the user's ID
        :return:
        """
        endpoint = f"{MICROSOFT_GRAPH}/users/{user_id}/revokeSignInSessions"
        error_code, data = self._api_request.api_request(endpoint, request_type="post")
        return error_code, data

