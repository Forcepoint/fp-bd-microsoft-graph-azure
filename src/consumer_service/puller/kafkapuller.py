#
# Author:  Dlo Bagari
# created Date: 14-11-2019
from time import sleep
from sys import exit
from cunsumer.consumerhandler import ConsumerHandler
from message_handler.messagehandler import MessageHandler
from publisher.publisher import Publisher

PAUSE = 5


class KafkaPuller:
    def __init__(self, settings, client_id, timeout, auto_commit, logger):
        self._settings = settings
        self._logger = logger
        self._consumer = ConsumerHandler(self._settings, client_id, timeout, auto_commit)
        self._database_handler = MessageHandler(self._settings, self._logger)
        self._publisher = Publisher(self._settings)

    def listener(self, topic, timeout):
        """
        Listen to new messages and notify the the DataBaseManager about it.
        :param topic: the topic name
        :param timeout: Maximum time to block waiting for message, event or callback
        :return: error_code, error_message
        """
        try:
            while True:
                for error_code, error_message, message in self._consumer.message_listener(topic, float(timeout)):
                    if error_code != 0:
                        self._logger(self, error_message)
                    else:
                        self._database_handler.handle_message(message, self._publisher)
                sleep(PAUSE)
        except KeyboardInterrupt:
            print()
            exit(0)


