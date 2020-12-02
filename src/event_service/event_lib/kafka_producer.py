from confluent_kafka import Producer
import json


class KafkaProducer:
    def __init__(self, settings):
        self._settings = settings

    def publish(self, json_file):
        try:
            log = json.dumps(json_file)
            p = Producer({'bootstrap.servers': f"{self._settings['kafka_bootstrap_server']}"})
            p.produce(self._settings['logs_topic_name'], log)
            p.flush(30)
            return True, ""
        except Exception as e:
            return False, str(e)

