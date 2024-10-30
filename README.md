# ignite-pickup-boxes

## Requirements

### Hardware

If you only have a single stack of boxes, only this first list is needed.
However, if you have more stacks of boxes to control, you'll need some additional (cheaper) hardware for each.

#### For the single/master stack of boxes

- Raspberry Pi (or equivalent)
  - 5V 3A power supply reccomended
- 8 channel optoisolated relay board
- 12V switching power supply
- Speaker wire
- Female-female jumper wires

#### (Optional) For multiple stacks of boxes

The master box additionally requires a USB hub with at least one port for each additional slave stack.

**Each additional slave stack:**

- Arduino Nano
- 8 channel optoisolated relay board
- Speaker wire
- Female-female jumper wires
- (Optional) USB extender for additional scanner

### Internet

A DHCP reserved address with DNS hostname set up would allow for an ideal user experience. However, a mesh VPN such as Tailscale would provide similar functionality if necessary.

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
  - Failure to do so may cause some or all boxes to open before the system pulls the box pins low

## Database

This project requires a SQL-like database to store information about the boxes and prints.
I'm using Postgres right now, hosted in a Docker container on the Raspberry Pi running the master box.

There are two tables in the database, with a preview of each below:

### box

| id | print_id | assign_enabled |
|----|----------|----------------|
| 0  | 123      | 1              |
| 1  | -1       | 1              |
| 2  | -1       | 0              |

The box table contains ids (an index of each box based on the relay associated with it), the print_id currently in the box (or -1 if the box is empty), and an integer boolean representing if the box can be automatically assigned to or not.

### print

| id | print_number | email                 | code   | box_id | status |
|----|--------------|-----------------------|--------|--------|--------|
| 0  | 42           | recipient@example.com | 123456 | 0      | 0      |

The print table contains the following columns:

- `id`: not exposed to frontend, internal print id guaranteed unique
- `print_number`: exposed to frontend, not guaranteed unique because of user input
- `email`: the email of the print recipient
- `code`: the numeric code emailed as a QR code to the recipient
- `status`: an enum for the status of the pickup
  - `0`: in box
  - `1`: picked up
  - `2`: abandoned
