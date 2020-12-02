from cunsumer.consumer_confluent_kafka import KafkaConsumer


class ConsumerHandler:
    def __init__(self, settings,  client_id, timeout, auto_commit):
        self._consumer = KafkaConsumer(settings, client_id, timeout, auto_commit)

    def message_listener(self, topic, timeout):
        """
        listen to new messages and yield them
        :return: error_code, error_message, message_json
        """
        while True:
            for error_code, error_message, message in self._consumer.subscribe(topic, timeout):
                yield error_code, error_message, message
                if error_code == 1:
                    break


