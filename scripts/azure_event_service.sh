#!/bin/bash
#
# Author:  Dlo Bagari
# created Date: 11-11-2019
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR" || exit 1
cd ..
python3 ./src/event_service/cli_controller.py "$@"