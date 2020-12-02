#
# Author:  Dlo Bagari
# created Date: 14-11-2019

import json
from confluent_kafka import Producer


class Publisher:
    def __init__(self, settings):
        self._settings = settings

    def publish(self, message, user_org_id, first_name, last_name):
        data = {"user_id": user_org_id, "first_name": first_name,
                "last_name": last_name, "timestamp": message["timestamp"], "risk_level": message["risk_level"]}
        return self._publish(data)

    def _publish(self, json_file):
        try:
            log = json.dumps(json_file)
            p = Producer({'bootstrap.servers': f"{self._settings['kafka_bootstrap_server']}"})
            p.produce(self._settings['risk_level_topic_name'], log)
            p.flush(30)
            return True, ""
        except Exception as e:
            return False, str(e)


