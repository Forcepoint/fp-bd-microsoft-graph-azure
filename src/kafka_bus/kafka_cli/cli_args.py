# Author:  Dlo Bagari
# created Date: 11-11-2019

import argparse
from kafka_cli.run_kafka import RunKafka
from kafka_cli.create_service import CreateService


class CliArgs:
    def __init__(self, name):
        self._parser = argparse.ArgumentParser(prog=name)
        self._run_kafka = RunKafka(self._parser)
        self._create_service = CreateService(self._parser)
        self._build_args()

    def _build_args(self):
        subparsers = self._parser.add_subparsers(title="sub-commands")
        run_cli = subparsers.add_parser("run",
                                        description="Runs the kafka_bus service")
        run_cli.add_argument("--config-file", "-c", action="store", dest="config_file",
                             help="The config file path", required=True)
        run_cli.set_defaults(function=self._run_kafka)
        service_cli = subparsers.add_parser("service", description="create Systemd Service for kafka_bus.service")

        service_cli.add_argument("--config-file", "-c", action="store", dest="config_file",
                                 help="the config file path", required=True)
        service_cli.set_defaults(function=self._create_service)

    def get_parser(self):
        return self._parser
