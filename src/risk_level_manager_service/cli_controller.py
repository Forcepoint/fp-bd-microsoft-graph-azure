#
# Author:  Dlo Bagari
# created Date: 15-11-2019

from risk_level_cli.cli_args import CliArgs

if __name__ == "__main__":
    cli_args = CliArgs("risk_level_manager.sh")
    parser = cli_args.get_parser()
    args = parser.parse_args()
    args.function(args)
