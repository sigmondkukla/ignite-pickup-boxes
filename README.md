# ignite-pickup-boxes

## Installation

1. `git clone https://github.com/PicoPlanetDev/ignite-pickup-boxes`
2. `cd ignite-pickup-boxes/frontend`
3. `bun install` or `npm install`
4. `sudo apt install screen`
5. `screen -dmS frontend bun dev -- --host`
6. `cd ../backend`
7. `screen -dmS scanner ./start_scanner.sh`
8. `screen -dmS app ./start_app.sh`

## Notes

- When starting up the system, ensure that the solenoid power supply is turned off using the red switch on the back of the boxes
  - Failure to do so may cause some or all boxes to open as the system initializes
