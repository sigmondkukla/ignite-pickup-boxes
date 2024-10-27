from flask import Flask, send_file, jsonify, request
from flask_cors import CORS
import os
from dotenv import load_dotenv
import database as db
from boxes import Boxes
from emailer import Emailer

NUM_BOXES = 8 # Number of boxes in the system
BOX_PINS = [29, 31, 33, 35, 37, 36, 38, 40]

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

database = db.Database(database=os.getenv("PG_DATABASE"),
                       user=os.getenv("PG_USER"),
                       password=os.getenv("PG_PASSWORD"),
                       host=os.getenv("PG_HOST"),
                       port=os.getenv("PG_PORT"))

boxes = Boxes(NUM_BOXES, BOX_PINS)

emailer = Emailer(email_user=os.getenv("EMAIL_USER"),
                  email_password=os.getenv("EMAIL_PASSWORD"))

@app.route("/api", methods=["GET"])
def api():
    return f"Hello, world!"

@app.route("/api/prints", methods=["GET", "POST", "PUT", "DELETE"])
def prints():
    if request.method == "GET":
        return jsonify([print.to_dict() for print in database.get_prints()])
    elif request.method == "POST":
        data = request.json
        database.create_print(data["print_number"], data["email"], data["box_id"])
        new_print = database.get_print_by_number(data["print_number"])
        emailer.send_pickup_email(new_print.email, new_print.code)
        return jsonify({"status": "success"})
    elif request.method == "PUT":
        data = request.json
        database.update_print(data)
        return jsonify({"status": "success"})
    elif request.method == "DELETE":
        data = request.json
        try: # attempt to delete multuple items, if the ids key is present it will not fail
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
    boxes.open_box(print_data.box_id)
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
    if print_data.print_status == 1:
        print("Print already picked up")
        return jsonify({"status": "error", "message": "Print already picked up"})
    
    boxes.open_box(print_data.box_id) # Open the box
    
    # box = database.get_box(print_data.box_id)
    database.set_box_print_id(print_data.box_id, -1) # Make the box available again
    database.set_print_status(print_data.id, 1) # Update print status to picked up
    return jsonify({"status": "success"})


