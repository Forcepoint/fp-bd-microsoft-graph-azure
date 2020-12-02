import json
import requests
from user_lib.const_values import ConstValues


class ApiRequest:
    def __init__(self, assess_token, logger=None):
        self._access_token = assess_token
        self.logger = logger

    def api_request(self, endpoint, q_param=None, request_type="get", json_file=None):
        """
        create and send an API request to Microsoft Graph
        :param endpoint: API endpoint
        :param q_param: requests parameters
        :param request_type: the request type
        :param json_file: request body
        :return: error_code, response
        """
        token = self._access_token.access_token()
        headers = {'Content-Type': 'application/json',
                   'Authorization': 'Bearer {0}'.format(token['accessToken'])}
        if request_type == "delete":
            response = requests.delete(endpoint, headers=headers)
        elif request_type == "post":
            response = requests.post(endpoint, headers=headers, json=json_file)
        else:
            if q_param is not None:
                response = requests.get(endpoint, headers=headers, params=q_param)
            else:
                response = requests.get(endpoint, headers=headers)
        if response.status_code == 200:
            json_data = json.loads(response.text)
            if '@odata.nextLink' in json_data.keys():
                record = self.api_request(json_data['@odata.nextLink'])
                entries = len(record['value'])
                count = 0
                while count < entries:
                    json_data['value'].append(record['value'][count])
                    count += 1
            return ConstValues.ERROR_CODE_ZERO, json_data
        elif response.status_code == 204:
            return ConstValues.ERROR_CODE_ZERO, {}
        else:
            return ConstValues.ERROR_CODE_ONE, response.json()["error"]