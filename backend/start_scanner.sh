#!/bin/bash

cd /home/ignite/ignite-pickup-boxes/backend || exit 1
source venv/bin/activate

python3 scanner.py --ports /dev/ttyACM0 /dev/ttyACM1 --scanner-ids right left
