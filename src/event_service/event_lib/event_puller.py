# Author:  Dlo Bagari
# created Date: 11-11-2019

import requests
import json

ERROR_CODE_ZERO = 0
ERROR_CODE_1 = 1


class EventPuller:
    def __init__(self, token_object, settings):
        self._token_object = token_object
        self._settings = settings

    def api_request(self, endpoint, q_param=None):
        """
        create and send an API request to Microsoft Graph
        :param endpoint: API endpoint
        :param q_param: requests parameters
        :return:
        """
        token = self._token_object.access_token()
        headers = {'Content-Type': 'application/json',
                   'Authorization': 'Bearer {0}'.format(token['accessToken'])}
        if q_param is not None:
            response = requests.get(endpoint, headers=headers, params=q_param)
        else:
            response = requests.get(endpoint, headers=headers)

        if response.status_code == 200:
            json_data = json.loads(response.text)
            if '@odata.nextLink' in json_data.keys():
                error_code, record = self.api_request(json_data['@odata.nextLink'])
                entries = len(record['value'])
                count = 0
                while count < entries:
                    json_data['value'].append(record['value'][count])
                    count += 1
            return ERROR_CODE_ZERO, json_data
        else:
            return ERROR_CODE_1, response.json()["error"]

    def logs_request(self, timestamp):
        q_param = {
            "$filter": "createdDateTime gt {}".format(timestamp)
        }
        return self.api_request(self._settings["logs_endpoint"], q_param=q_param)