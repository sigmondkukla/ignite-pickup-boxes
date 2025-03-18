from flask import Flask, send_file, jsonify, request
from flask_cors import CORS
import os
from dotenv import load_dotenv
import database as db
from boxes import Boxes, GPIOBoxes, ArduinoBoxes
from emailer import Emailer

NUM_STACK_BOXES = 8 # Number of boxes in each stack

# GPIO boxes (stack 0)
# GPIO_BOX_PINS = [29, 31, 33, 35, 37, 36, 38, 40]

load_dotenv()

# Arduino boxes
STACK_0_SERIAL_PORT = os.getenv("STACK_0_SERIAL_PORT")
STACK_1_SERIAL_PORT = os.getenv("STACK_1_SERIAL_PORT")
STACK_2_SERIAL_PORT = os.getenv("STACK_2_SERIAL_PORT")
STACK_3_SERIAL_PORT = os.getenv("STACK_3_SERIAL_PORT")

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

database = db.Database(database=os.getenv("PG_DATABASE"),
                       user=os.getenv("PG_USER"),
                       password=os.getenv("PG_PASSWORD"),
                       host=os.getenv("PG_HOST"),
                       port=os.getenv("PG_PORT"))

# stack_0 = GPIOBoxes(NUM_BOXES, GPIO_BOX_PINS) # GPIO-controlled boxes (stack 0)
stack_0 = ArduinoBoxes(NUM_STACK_BOXES, STACK_0_SERIAL_PORT) # Arduino-controlled boxes (stack 0)
stack_1 = ArduinoBoxes(NUM_STACK_BOXES, STACK_1_SERIAL_PORT) # Arduino-controlled boxes (stack 1)
stack_2 = ArduinoBoxes(NUM_STACK_BOXES, STACK_2_SERIAL_PORT) # Arduino-controlled boxes (stack 2)
stack_3 = ArduinoBoxes(NUM_STACK_BOXES, STACK_3_SERIAL_PORT) # Arduino-controlled boxes (stack 3)

stacks = [stack_0, stack_1, stack_2, stack_3]

emailer = Emailer(email_user=os.getenv("EMAIL_USER"),
                  email_password=os.getenv("EMAIL_PASSWORD"))

@app.route("/api", methods=["GET"])
def api():
    return f"Hello, world!"

@app.route("/api/prints", methods=["GET", "POST", "PUT", "DELETE"])
def prints():
    if request.method == "GET": # return all prints
        return jsonify([print.to_dict() for print in database.get_prints()])
    
    elif request.method == "POST": # create a new print
        data = request.json
        database.create_print(data["print_number"], data["email"], data["box_id"]) # add print to db with random code
        new_print = database.get_print_by_number(data["print_number"]) # get the new print so we know the code
        emailer.send_pickup_email(new_print.email, new_print.code) # send email to user with code
        return jsonify({"status": "success"})
    
    elif request.method == "PUT": # modify an existing print
        data = request.json
        database.update_print(data)
        return jsonify({"status": "success"})
    
    elif request.method == "DELETE":
        data = request.json
        try: # attempt to delete multiple items, if the ids key is present it will not fail
            database.delete_prints(data["ids"])
        except KeyError: # the ids key was not present, so we catch and assume we are deleting a single item
            database.delete_print(data["id"])
        return jsonify({"status": "success"})
    
@app.route("/api/prints/unlock", methods=["POST"])
def unlock_print():
    data = request.json
    print_data = database.get_print(data["id"])
    if print_data is None:
        return jsonify({"status": "error", "message": "Print not found"})
    
    # Determine and open the box
    stack_index = print_data.box_id // NUM_STACK_BOXES # Determine which stack the box is in
    box_index = print_data.box_id % NUM_STACK_BOXES # Determine which box in the stack to open
    stacks[stack_index].open_box(box_index) # Open the offset box in the stack

    return jsonify({"status": "success"})
    
@app.route("/api/get_next_available_box", methods=["GET"])
def get_next_available_box():
    box = database.get_next_available_box()
    return jsonify(box.id)
    
@app.route("/api/scan", methods=["POST"])
def scan():
    data = request.json
    # print("Incoming scan:", data["code"])
    print_data = database.get_print_by_code(data["code"])
    # print(print_data)
    if print_data is None: # Print not found
        print("Print not found")
        return jsonify({"status": "error", "message": "Print not found"})
    if print_data.status == 1:
        print("Print already picked up")
        return jsonify({"status": "error", "message": "Print already picked up"})
    
    # Determine and open the box
    stack_index = print_data.box_id // NUM_STACK_BOXES # Determine which stack the box is in
    box_index = print_data.box_id % NUM_STACK_BOXES # Determine which box in the stack to open
    stacks[stack_index].open_box(box_index) # Open the offset box in the stack
    
    # box = database.get_box(print_data.box_id)
    database.set_box_print_id(print_data.box_id, -1) # Make the box available again
    database.set_print_status(print_data.id, 1) # Update print status to picked up
    return jsonify({"status": "success"})


