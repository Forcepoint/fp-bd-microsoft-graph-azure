# Author:  Dlo Bagari
# created Date: 11-11-2019

from event_cli.cli_args import CliArgs

if __name__ == "__main__":
    cli_args = CliArgs("azure_events.sh")
    parser = cli_args.get_parser()
    args = parser.parse_args()
    args.function(args)
