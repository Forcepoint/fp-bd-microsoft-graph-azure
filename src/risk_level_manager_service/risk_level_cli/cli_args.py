#
# Author:  Dlo Bagari
# created Date: 11-11-2019


import argparse
from risk_level_cli.risk_process import RiskProcess
from risk_level_cli.create_service import CreateService


class CliArgs:
    def __init__(self, name):
        self._parser = argparse.ArgumentParser(prog=name)
        self._logs_process = RiskProcess(self._parser)
        self._create_service = CreateService(self._parser)
        self._build_args()

    def _build_args(self):
        subparsers = self._parser.add_subparsers(title="sub-commands")
        run_cli = subparsers.add_parser("run",
                                        description="Runs the risk level manager service")
        service_cli = subparsers.add_parser("service", description="create Systemd Service for azure_"
                                                                   "risk_level.service")

        run_cli.add_argument("--config-file", "-c", action="store", dest="config_file",
                             help="the config file path", required=True)
        run_cli.set_defaults(function=self._logs_process)

        service_cli.add_argument("--start", "-s", action="store_true",
                                 default=False, dest="start", help="Start systemd service(azure_risk_level.service)")
        service_cli.add_argument("--name", "-n", action="store",
                                 default="azure_risk_level", dest="name", help="the service name, "
                                                                  "default name is 'azure_risk_level'")
        service_cli.add_argument("--config-file", "-c", action="store", dest="config_file",
                                 help="the config file path", required=True)
        service_cli.set_defaults(function=self._create_service)

    def get_parser(self):
        return self._parser
