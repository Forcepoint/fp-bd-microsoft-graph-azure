from confluent_kafka import Consumer, KafkaError
from fba_lib.const_values import ConstValues


class LogConsumer:
    def __init__(self, settings):
        self._settings = settings
        self._consumer = self._build_consumer()

    def _build_consumer(self):
        """
        Create a consumer object and return it.
        :return: Consumer
        """
        settings = {
                    'bootstrap.servers': self._settings["kafka_bootstrap_server"],
                    'group.id': self._settings['fba_consumer_group_name'],
                    'client.id': 'client-1',
                    'enable.auto.commit': True,
                    'session.timeout.ms': 6000
        }
        c = Consumer(settings)
        return c

    def subscribe(self, topic=None):
        """
        Subscribe to a topic and process abd read messages
        :return:
        """
        if topic is None:
            topic = self._settings["logs_topic_name"]
            self._consumer.subscribe([topic])
        try:
            while True:
                msg = self._consumer.poll(0.1)
                if msg is None:
                    continue
                elif not msg.error():
                    self._consumer.commit()
                    yield ConstValues.ERROR_CODE_ZERO, "", msg.value()
                elif msg.error().code() == KafkaError._PARTITION_EOF:
                    yield ConstValues.ERROR_CODE_ONE, 'End of partition reached {0}/{1}'.format(msg.topic(),
                                                                                                msg.partition()), {}
                else:
                    yield ConstValues.ERROR_CODE_ONE, 'Error occured: {0}'.format(msg.error().str()), {}

        except KeyboardInterrupt:
            pass

        finally:
            self._consumer.close()
