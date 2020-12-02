# Author:  Dlo Bagari
# created Date: 11-11-2019

from user_cli.cli_args import CliArgs
from sys import exit

if __name__ == "__main__":
    cli_args = CliArgs("user_service.sh")
    try:
        parser = cli_args.get_parser()
        args = parser.parse_args()
        args.function(args)
    except KeyboardInterrupt:
        print()
        exit()
