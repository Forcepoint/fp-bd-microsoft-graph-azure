import yaml
from time import sleep
from sys import exit
from fba_lib.logger import Logger
from fba_lib.logs_consumer import LogConsumer
from fba_lib.const_values import ConstValues
from fba_lib.exec_cmd import ExeCmd

class LogsProcess:
    def __init__(self, parser):
        self._parser = parser
        self._settings = None
        self._logger = None
        self._logs_consumer = None
        self._exec_cmd = ExeCmd()

    def __call__(self, args):
        self._args = args
        with open(self._args.config_file) as f:
            self._settings = yaml.load(f, yaml.SafeLoader)
        if self._settings is None:
            self._logger.error(self, "Failed in loading the config file")
            self._parser.error("Failed in loading the config file")
        self._logger = Logger(self._settings["logs_directory"])

        self.process()

    def process(self, rest_time=30):
        """
        Pull messages from kafka bus and send them to fba
        :param rest_time:
        :return:
        """
        try:
            while True:
                self._logs_consumer = LogConsumer(self._settings)
                for error_code, error_message, message in self._logs_consumer.subscribe():
                    if message is None:
                        continue
                    if error_code == ConstValues.ERROR_CODE_ONE:
                        self._logger.error(self, error_message)
                        self._parser.error(error_message)
                    error_code, error_message = self._send_to_fba(message)
                    if error_code != ConstValues.ERROR_CODE_ZERO:
                        self._logger.critical(self, error_message)
                sleep(rest_time)
        except KeyboardInterrupt:
            exit(0)

    def _send_to_fba(self, message):
        message = message.decode()
        url = "https://{}:9000/event".format(self._settings["fba_events_end_point"])

        cmd = 'curl -XPOST -H"Content-Type:application/json"' \
              ' {} -k -d \'{}\''.format(url, message)
        output, error = self._exec_cmd.run(cmd)
        if output is None:
            self._logger.error(self, error.decode())
            return ConstValues.ERROR_CODE_ONE, error.decode()
        if len(output) != 0:
            if "acknowledged" in output:
                if output["acknowledged"] is True:
                    return ConstValues.ERROR_CODE_ZERO, ""
            elif "code" in list(output.keys()) and int(output["code"]) == 400:
                return ConstValues.ERROR_CODE_ONE, output["message"]
            else:
                return ConstValues.ERROR_CODE_ONE, "Failed to sent an event"
