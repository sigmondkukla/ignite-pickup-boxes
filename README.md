# ignite-pickup-boxes

## Installation

1. Clone the repository: `git clone https://github.com/PicoPlanetDev/ignite-pickup-boxes`
2. Change to the frontend directory: `cd ignite-pickup-boxes/frontend`
3. Install NPM dependencies: `bun install` or `npm install`
4. Install GNU Screen for background running: `sudo apt install screen`
5. Start the frontend dev server: `screen -dmS frontend bun dev -- --host`
6. Change to the backend directory: `cd ../backend`
7. Create a virtual environment: `python3 -m venv venv`
8. Activate the virtual environment: `source venv/bin/activate`
9. Install Python dependencies: `pip3 install -r requirements.txt`
10. Start the scanner listener: `screen -dmS scanner ./start_scanner.sh`
11. Start the backend Flask app: `screen -dmS app ./start_app.sh`

## Notes

- When starting up the system, ensure that the solenoid power supply is turned off using the red switch on the back of the boxes
  - Failure to do so may cause some or all boxes to open as the system initializes
