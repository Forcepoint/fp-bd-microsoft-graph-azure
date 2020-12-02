import argparse
from user_cli.user_service import UserService
from user_cli.create_service import CreateService


class CliArgs:
    def __init__(self, pro_name):
        self._pro_name = pro_name
        self._parser = argparse.ArgumentParser(prog=pro_name)
        self._user_service = UserService(self._parser)
        self._create_service = CreateService(self._parser)
        self._build_args()

    def _build_args(self):
        subparsers = self._parser.add_subparsers(title="sub-commands")
        run_cli = subparsers.add_parser("run",
                                        description="Runs the User Service")

        run_cli.add_argument("--config-file", "-c", action="store", dest="config_file",
                             help="REQUIRED: The config file path", required=True)
        run_cli.set_defaults(function=self._user_service)
        service_cli = subparsers.add_parser("service",
                                            description="creates azure_user.service Systemd Service")
        service_cli.add_argument("--start", "-s", action="store_true",
                                 default=False, dest="start", help="Start systemd service"
                                                                   "(azure_user.service)")
        service_cli.add_argument("--name", "-n", action="store",
                                 default="azure_user", dest="name",
                                 help="the service name, default name is 'azure_user'")
        service_cli.add_argument("--config-file", "-c", action="store",
                                 required=True, dest="config_file",
                                 help="the config file path")
        service_cli.set_defaults(function=self._create_service)

    def get_parser(self):
        return self._parser


