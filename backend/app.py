from flask import Flask, send_file, jsonify, request
from flask_cors import CORS
import os
from dotenv import load_dotenv
import database as db
from boxes import Boxes

SER_PIN = 11 # GPIO board pin connected to serial data of shift register
SRCLK_PIN = 13 # GPIO board pin connected to the shift register clock pin
RCLK_PIN = 15 # GPIO board pin connected to the storage register clock pin (latch pin)
NUM_BOXES = 8 # Number of boxes in the system

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

database = db.Database()
boxes = Boxes(NUM_BOXES, SER_PIN, SRCLK_PIN, RCLK_PIN)

@app.route("/api", methods=["GET"])
def api():
    return f"Hello, world!"

@app.route("/api/prints", methods=["GET", "POST", "PUT", "DELETE"])
def prints():
    if request.method == "GET":
        return jsonify([print.to_dict() for print in database.get_prints()])
    elif request.method == "POST":
        data = request.json
        database.create_print(data["print_number"], data["email"], data["code"], data["box_id"])
        return jsonify({"success": True})
    elif request.method == "PUT":
        data = request.json
        database.set_print_status(data["print_id"], data["status"])
        return jsonify({"success": True})
    elif request.method == "DELETE":
        data = request.json
        database.delete_print(data["print_id"])
        return jsonify({"success": True})
    
@app.route("/api/scan", methods=["POST"])
def scan():
    data = request.json
    print("Incoming scan:", data["code"])
    print_data = database.get_print_by_code(data["code"])
    print(print_data)
    if print_data is None:
        print("Code not found")
        return jsonify({"success": False})
    # Open the box
    boxes.open_box(print_data.box_id)
    # Make the box available
    box = database.get_box(print_data.box_id)
    database.set_box_print_id(box.id, -1)
