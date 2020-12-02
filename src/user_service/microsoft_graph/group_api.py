import urllib.parse
from microsoft_graph.api_request import ApiRequest
from microsoft_graph.user_api import UserApi
from user_lib.const_values import ConstValues

MICROSOFT_GRAPH = "https://graph.microsoft.com/v1.0"


class GroupApi:
    def __init__(self, access_token, logger=None):
        self._api_request = ApiRequest(access_token, logger)
        self._user_api = UserApi(access_token, logger)
        self._groups_name = None
        self._logger = logger

    def filter_group_by_name(self, name):
        query = f"displayName eq '{name}'"
        query = urllib.parse.quote(query)
        endpoint = f"https://graph.microsoft.com/v1.0/groups?$filter={query}"
        error_code, data = self._api_request.api_request(endpoint)
        return error_code, data

    def change_group(self, user_id, group_name, terminate_session=True):
        # find all groups gor the target user
        target_group = None
        current_group = None
        error_code, response = self.filter_group_by_name(group_name)
        if error_code != ConstValues.ERROR_CODE_ZERO:
            return error_code, response
        if len(response["value"]) == 0:
            return ConstValues.ERROR_CODE_ONE, {"message": f"The target group '{group_name}'"
                                                           f" is not exists on azure AB"}
        target_group = response["value"][0]
        error_code, response = self._user_api.get_user_groups(user_id)

        if error_code != ConstValues.ERROR_CODE_ZERO:
            return error_code, response
        groups = response["value"]
        if len(groups) != 0:
            for group in groups:
                if group["displayName"] in set(self._groups_name.values()):
                    group_id = group["id"]
                    current_group = group["displayName"]
                    error_code, response = self.remove_member(group_id, user_id)
                    if error_code != ConstValues.ERROR_CODE_ZERO:
                        return error_code, response
        error_code, data = self.add_member(target_group["id"], user_id)
        if error_code == ConstValues.ERROR_CODE_ZERO:
            self._logger.info(self, f"User:{user_id}:  group changed: {current_group} to {group_name}")
            current_group = 0 if current_group is None else int(current_group[-1])
            target_group = int(group_name[-1])
            if target_group > current_group:
                self._logger.info(self, f"User:{user_id}:  Revoke SignIn Session applied")
                error_code_revoke, data2 = self._user_api.revoke_session(user_id)
        return error_code, data

    def get_groups(self):
        endpoint = f"{MICROSOFT_GRAPH}/groups"
        error_code, data = self._api_request.api_request(endpoint)
        return error_code, data

    def get_group_members(self, group_id):
        endpoint = f"{MICROSOFT_GRAPH}/groups/{group_id}/members"
        error_code, data = self._api_request.api_request(endpoint)
        return error_code, data

    def add_member(self, group_id, user_id):
        endpoint = f"{MICROSOFT_GRAPH}/groups/{group_id}/members/$ref"
        json_file = {"@odata.id": f"{MICROSOFT_GRAPH}/users/{user_id}"}
        error, data = self._api_request.api_request(endpoint, request_type="post", json_file=json_file)
        return error, data

    def remove_member(self, group_id, user_id):
        endpoint = f"{MICROSOFT_GRAPH}/groups/{group_id}/members/{user_id}/$ref"
        error, data = self._api_request.api_request(endpoint, request_type="delete")
        return error, data

    def set_groups_name(self, groups):
        """
        set the risk level groups name
        :param groups:
        :return:
        """
        self._groups_name = groups


