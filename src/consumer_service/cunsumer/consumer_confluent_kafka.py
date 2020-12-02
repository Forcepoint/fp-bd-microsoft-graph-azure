from sys import exit
import json
from time import sleep
from confluent_kafka import Consumer, KafkaError


ERROR_CODE_ZERO = 0
ERROR_CODE_ONE = 1
EMPTY_ERROR_MESSAGE = ""
PAUSE = 3


class KafkaConsumer:
    def __init__(self, settings, client_id, timeout, auto_commit):
        self._settings = settings
        self._timeout = timeout
        self._auto_commit = auto_commit
        self._client_id = client_id
        self._consumer = self._build_consumer()

    def subscribe(self, topic_name, timeout):
        """
        Subscribe for topic and listen to new messages until the timeout of
         Kafka consumer occurs which will end the session
        :param topic_name: the topic name
        :param timeout: Maximum time to block waiting for message, event or callback
        :return: error_code, error, message
        """
        self._consumer.subscribe([topic_name])
        try:
            while True:
                msg = self._consumer.poll(timeout)
                if msg is None:
                    continue
                elif not msg.error():
                    yield ERROR_CODE_ZERO, EMPTY_ERROR_MESSAGE, json.loads(msg.value())
                elif msg.error().code() == KafkaError._PARTITION_EOF:
                    yield ERROR_CODE_ONE, 'End of partition reached {0}/{1}'.format(msg.topic(), msg.partition()), None
                else:
                    yield ERROR_CODE_ONE, 'Error occured: {0}'.format(msg.error().str()), None
                sleep(PAUSE)
        except KeyboardInterrupt:
            exit(0)
        finally:
            self._consumer.close()

    def _build_consumer(self):
        """
        Creates kafka consumer object.
        :return:
        """
        settings = {
            'bootstrap.servers': self._settings["fba_kafka_bootstrap_server"],
            'group.id': self._settings["fba_kafka_consumer_group_name"],
            'client.id': self._client_id,
            'enable.auto.commit': self._auto_commit,
            'session.timeout.ms': self._timeout,
            'security.protocol': 'SSL',
            'ssl.ca.location': self._settings["ssl_ca_location"],
            'ssl.certificate.location': self._settings["ssl_certificate_location"],
            'ssl.key.location': self._settings["ssl_key_location"],
            'ssl.key.password': self._settings["key_store_pass"],
            #'auto.offset.reset': 'smallest'
        }
        try:
            cons = Consumer(settings)
            return cons
        except Exception as e:
            print("Error in creating the Consumer: ", e)
            #exit(1)

