from google_sheets_service import (
    get_print_details_by_print_number,
    update_dates_by_print_number,
    update_box_status_by_print_number,
)
from flask import Flask, jsonify, request
from flask_cors import CORS

import os
import re
from dotenv import load_dotenv
from pathlib import Path
import threading
import time
from datetime import datetime

import database as db
from boxes import ArduinoBoxes
from emailer import Emailer

NUM_STACK_BOXES = 8
MAX_SCAN_USES = 3

STATUS_IN_BOX = 0
STATUS_PICKED_UP = 1
STATUS_ABANDONED = 2
STATUS_AWAITING_PICKUP = 3

VALID_SCANNER_IDS = {"left", "right"}

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(dotenv_path=BASE_DIR / ".env")

STACK_0_SERIAL_PORT = os.getenv("STACK_0_SERIAL_PORT")
STACK_1_SERIAL_PORT = os.getenv("STACK_1_SERIAL_PORT")
STACK_2_SERIAL_PORT = os.getenv("STACK_2_SERIAL_PORT")
STACK_3_SERIAL_PORT = os.getenv("STACK_3_SERIAL_PORT")

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

latest_scan_events = {
    "left": {
        "event_id": 0,
        "timestamp": 0,
        "status": "idle",
        "title": "",
        "message": "",
        "box_id": None,
    },
    "right": {
        "event_id": 0,
        "timestamp": 0,
        "status": "idle",
        "title": "",
        "message": "",
        "box_id": None,
    },
}

latest_scan_lock = threading.Lock()


def normalize_scanner_id(scanner_id):
    scanner_id = (scanner_id or "left").strip().lower()
    if scanner_id not in VALID_SCANNER_IDS:
        return "left"
    return scanner_id


def update_latest_scan_event(scanner_id, status, title, message, box_id=None):
    scanner_id = normalize_scanner_id(scanner_id)

    with latest_scan_lock:
        event = latest_scan_events[scanner_id]
        event["event_id"] += 1
        event["timestamp"] = int(time.time())
        event["status"] = status
        event["title"] = title
        event["message"] = message
        event["box_id"] = box_id


def extract_google_sheet_id(sheet_url_or_id):
    value = (sheet_url_or_id or "").strip()

    if not value:
        return None

    match = re.search(r"/spreadsheets/d/([a-zA-Z0-9-_]+)", value)
    if match:
        return match.group(1)

    if re.match(r"^[a-zA-Z0-9-_]{20,}$", value):
        return value

    return None


def get_active_spreadsheet_id():
    saved_id = database.get_setting("GSHEET_SPREADSHEET_ID")

    if saved_id:
        return saved_id

    return os.getenv("GSHEET_SPREADSHEET_ID", "")


CORS(
    app,
    resources={
        r"/api/*": {
            "origins": [
                "http://127.0.0.1:5173",
                "http://localhost:5173",
                "http://127.0.0.1:5174",
                "http://localhost:5174",
                "http://ignitepickupboxes.clarkson.edu",
                "https://ignitepickupboxes.clarkson.edu",
            ],
            "supports_credentials": True,
            "allow_headers": ["Content-Type", "Authorization"],
            "methods": ["GET", "HEAD", "POST", "PUT", "DELETE", "OPTIONS"],
        }
    },
)


database = db.Database(
    database=os.getenv("PG_DATABASE"),
    user=os.getenv("PG_USER"),
    password=os.getenv("PG_PASSWORD"),
    host=os.getenv("PG_HOST"),
    port=os.getenv("PG_PORT"),
)

try:
    database.fill_box_table(32)
except Exception as e:
    app.logger.warning(f"[DB] fill_box_table warning: {e}")

stack_0 = ArduinoBoxes(NUM_STACK_BOXES, STACK_0_SERIAL_PORT)
stack_1 = ArduinoBoxes(NUM_STACK_BOXES, STACK_1_SERIAL_PORT)
stack_2 = ArduinoBoxes(NUM_STACK_BOXES, STACK_2_SERIAL_PORT)
stack_3 = ArduinoBoxes(NUM_STACK_BOXES, STACK_3_SERIAL_PORT)
stacks = [stack_0, stack_1, stack_2, stack_3]

emailer = Emailer(
    email_user=os.getenv("EMAIL_USER"),
    smtp_host=os.getenv("SMTP_HOST", "intmx.clarkson.edu"),
    smtp_port=int(os.getenv("SMTP_PORT", "25")),
)

if not emailer.email_user:
    raise RuntimeError(
        "EMAIL_USER not set. "
        "Make sure /home/ignite/ignite-pickup-boxes/backend/.env exists and contains EMAIL_USER."
    )


@app.route("/api/settings/google-sheet", methods=["GET"])
def get_google_sheet_setting():
    sheet_id = database.get_setting(
        "GSHEET_SPREADSHEET_ID",
        os.getenv("GSHEET_SPREADSHEET_ID", "")
    )

    return jsonify({
        "status": "success",
        "sheet_id": sheet_id,
        "sheet_url": f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit" if sheet_id else ""
    })


@app.route("/api/settings/google-sheet", methods=["POST"])
def update_google_sheet_setting():
    data = request.get_json(silent=True) or {}

    sheet_input = (
        data.get("sheet_url")
        or data.get("sheet_id")
        or ""
    ).strip()

    sheet_id = extract_google_sheet_id(sheet_input)

    if not sheet_id:
        return jsonify({
            "status": "error",
            "message": "Invalid Google Sheet link or ID"
        }), 400

    database.set_setting("GSHEET_SPREADSHEET_ID", sheet_id)

    return jsonify({
        "status": "success",
        "message": "Google Sheet updated successfully",
        "sheet_id": sheet_id,
        "sheet_url": f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit"
    })


DISALLOWED_BOXES = {31, 32}
MIN_BOX_ID = 1
MAX_BOX_ID = 32

LOGICAL_TO_PHYSICAL_BOX = {
    1: 24,
    2: 25,
    3: 16,
    4: 17,
    5: 8,
    6: 9,
    7: 0,
    8: 1,
    9: 26,
    10: 18,
    11: 19,
    12: 10,
    13: 11,
    14: 2,
    15: 28,
    16: 29,
    17: 20,
    18: 21,
    19: 12,
    20: 13,
    21: 4,
    22: 5,
    23: 30,
    24: 31,
    25: 22,
    26: 23,
    27: 14,
    28: 15,
    29: 6,
    30: 7,
    31: 27,
    32: 3,
}


def disabled_box_message(box_id: int) -> str:
    return f"Box {box_id} is disabled, Please enter another valid box number"


def scanner_box_message(box_id: int) -> str:
    return f"Box {box_id} is reserved for scanner use, Please enter another valid box number"


def unavailable_box_message(box_id: int) -> str:
    return f"Box {box_id} is unavailable, Please enter another valid box number"


def validate_box_id(raw_box_id):
    try:
        box_id = int(raw_box_id)
    except (TypeError, ValueError):
        return None, (
            jsonify({"status": "error", "message": "Box number must be an integer."}),
            400,
        )

    if box_id < MIN_BOX_ID or box_id > MAX_BOX_ID:
        return None, (
            jsonify(
                {
                    "status": "error",
                    "message": f"Box number must be between {MIN_BOX_ID} and {MAX_BOX_ID}.",
                }
            ),
            400,
        )

    if box_id in DISALLOWED_BOXES:
        return None, (
            jsonify({"status": "error", "message": scanner_box_message(box_id)}),
            400,
        )

    return box_id, None


def logical_to_physical_box_id(logical_box_id: int):
    physical_box_id = LOGICAL_TO_PHYSICAL_BOX.get(logical_box_id)
    if physical_box_id is None:
        return None, f"No physical mapping defined for logical box {logical_box_id}"
    return physical_box_id, None


def open_box_by_box_id(box_id: int):
    physical_box_id, err = logical_to_physical_box_id(box_id)
    if err:
        return False, err

    total_boxes = len(stacks) * NUM_STACK_BOXES
    if physical_box_id < 0 or physical_box_id >= total_boxes:
        return False, f"Invalid physical box_id {physical_box_id} (expected 0-{total_boxes - 1})"

    stack_index = physical_box_id // NUM_STACK_BOXES
    box_index = physical_box_id % NUM_STACK_BOXES

    try:
        stacks[stack_index].open_box(box_index)
        return True, None
    except Exception as e:
        return False, str(e)


@app.route("/api", methods=["GET"])
def api():
    return "Hello, world!"


@app.route("/api/get_next_available_box", methods=["GET"])
def get_next_available_box():
    try:
        box = database.get_next_available_box()
        if box is None:
            return jsonify({"status": "error", "message": "No available boxes"}), 404
        return jsonify(box.id)
    except Exception as e:
        app.logger.exception(f"[BOXES] get_next_available_box failed: {e}")
        return jsonify({"status": "error", "message": "Failed to get next available box"}), 500


@app.route("/api/print-email/<print_number>", methods=["GET"])
def get_print_email(print_number):
    try:
        details = get_print_details_by_print_number(print_number)

        if not details or not details.get("email"):
            return jsonify({"status": "error", "message": "Print number not found"}), 404

        return jsonify(
            {
                "status": "success",
                "print_number": str(print_number),
                "email": details["email"],
                "name": details.get("name", "Maker"),
            }
        ), 200

    except Exception as e:
        app.logger.exception(f"[GSHEET] lookup failed for print_number={print_number}: {e}")
        return jsonify(
            {
                "status": "error",
                "message": "Failed to fetch print details from Google Sheet",
            }
        ), 500


@app.route("/api/prints", methods=["GET", "HEAD", "POST", "PUT", "DELETE", "OPTIONS"])
def prints():
    if request.method in ("GET", "HEAD"):
        return jsonify([p.to_dict() for p in database.get_prints()])

    elif request.method == "POST":
        data = request.get_json(force=True)

        if not data.get("print_number"):
            return jsonify({"status": "error", "message": "Print number is required"}), 400

        if not data.get("email") or not data.get("name"):
            try:
                details = get_print_details_by_print_number(data["print_number"])
            except Exception as e:
                app.logger.exception(f"[GSHEET] lookup failed for print_number={data['print_number']}: {e}")
                return jsonify({"status": "error", "message": "Failed to fetch print details from Google Sheet"}), 500

            if not details or not details.get("email"):
                return jsonify({"status": "error", "message": "No email found for that print number"}), 404

            if not data.get("email"):
                data["email"] = details["email"]

            if not data.get("name"):
                data["name"] = details.get("name", "Maker")

        box_id, err = validate_box_id(data.get("box_id"))
        if err:
            return err

        try:
            print_id, code = database.create_print(data["print_number"], data["email"], box_id)

            try:
                update_dates_by_print_number(
                    data["print_number"],
                    date_added=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                )
            except Exception as sheet_err:
                app.logger.warning(
                    f"[GSHEET] Failed to update Date Added for print {data['print_number']}: {sheet_err}"
                )

            try:
                update_box_status_by_print_number(data["print_number"], STATUS_IN_BOX)
            except Exception as sheet_err:
                app.logger.warning(
                    f"[GSHEET] Failed to update Status for print {data['print_number']}: {sheet_err}"
                )

        except ValueError:
            return jsonify({"status": "error", "message": unavailable_box_message(box_id)}), 400
        except Exception as e:
            app.logger.exception(f"[PRINTS] create_print failed: {e}")
            return jsonify({"status": "error", "message": "Failed to create print"}), 500

        try:
            recipient_name = data.get("name", "").strip() or "Maker"
            app.logger.warning(f"[EMAIL] sending to={data['email']} code={code} name={recipient_name}")
            emailer.send_pickup_email(data["email"], code, recipient_name)
            app.logger.warning(f"[EMAIL] sent OK to={data['email']}")
            return jsonify({"status": "success", "email_sent": True, "id": print_id, "code": code})
        except Exception as e:
            app.logger.exception(f"[EMAIL] FAILED to send to={data['email']}: {e}")
            return jsonify(
                {
                    "status": "error",
                    "message": "Print created but email failed to send.",
                    "email_sent": False,
                    "error": str(e),
                    "id": print_id,
                }
            ), 500

    elif request.method == "PUT":
        data = request.get_json(force=True)

        if "box_id" in data:
            box_id, err = validate_box_id(data.get("box_id"))
            if err:
                return err
            data["box_id"] = box_id

        try:
            database.update_print(data)

            try:
                update_box_status_by_print_number(data["print_number"], data["status"])
            except Exception as sheet_err:
                app.logger.warning(
                    f"[GSHEET] Failed to update Status for print {data['print_number']}: {sheet_err}"
                )

            if data["status"] == STATUS_PICKED_UP:
                try:
                    update_dates_by_print_number(
                        data["print_number"],
                        date_picked_up=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    )
                except Exception as sheet_err:
                    app.logger.warning(
                        f"[GSHEET] Failed to update Date Picked Up for print {data['print_number']}: {sheet_err}"
                    )

        except ValueError:
            if "box_id" in data:
                box_id = int(data["box_id"])
                if box_id in DISALLOWED_BOXES:
                    return jsonify({"status": "error", "message": scanner_box_message(box_id)}), 400
                return jsonify({"status": "error", "message": unavailable_box_message(box_id)}), 400

            return jsonify({"status": "error", "message": "Target box is unavailable"}), 400
        except Exception as e:
            app.logger.exception(f"[PRINTS] update_print failed: {e}")
            return jsonify({"status": "error", "message": "Failed to update print"}), 500

        return jsonify({"status": "success"})

    elif request.method == "DELETE":
        data = request.get_json(force=True)
        try:
            database.delete_prints(data["ids"])
        except KeyError:
            database.delete_print(data["id"])
        return jsonify({"status": "success"})

    return jsonify({"status": "error", "message": "Method not allowed"}), 405


@app.route("/api/disabled_boxes", methods=["GET"])
def get_disabled_boxes():
    try:
        rows = database.list_disabled_boxes()
        return jsonify([{"box_id": b, "reason": r} for (b, r) in rows])
    except Exception as e:
        app.logger.exception(f"[DISABLED_BOXES] list failed: {e}")
        return jsonify({"status": "error", "message": "Failed to fetch disabled boxes"}), 500


@app.route("/api/disabled_boxes", methods=["POST"])
def disable_box():
    data = request.get_json(force=True) or {}

    box_id, err = validate_box_id(data.get("box_id"))
    if err:
        return err

    reason = (data.get("reason") or "").strip()

    try:
        box = database.get_box(box_id)
        if box is not None and int(box.print_id) != -1:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": f"Box {box_id} is currently occupied. Remove the print first before disabling it.",
                    }
                ),
                409,
            )
    except Exception as e:
        app.logger.exception(f"[DISABLED_BOXES] occupancy check failed: {e}")
        return jsonify({"status": "error", "message": "Failed to validate box occupancy"}), 500

    try:
        database.disable_box(box_id, reason)
        return jsonify({"status": "success", "box_id": box_id, "disabled": True})
    except Exception as e:
        app.logger.exception(f"[DISABLED_BOXES] disable failed: {e}")
        return jsonify({"status": "error", "message": "Failed to disable box"}), 500


@app.route("/api/disabled_boxes/<int:box_id>", methods=["DELETE"])
def enable_box(box_id: int):
    try:
        box_id = int(box_id)
    except (TypeError, ValueError):
        return jsonify({"status": "error", "message": "Box number must be an integer."}), 400

    if box_id < MIN_BOX_ID or box_id > MAX_BOX_ID:
        return jsonify(
            {
                "status": "error",
                "message": f"Box number must be between {MIN_BOX_ID} and {MAX_BOX_ID}.",
            }
        ), 400

    if box_id in DISALLOWED_BOXES:
        return jsonify({"status": "error", "message": scanner_box_message(box_id)}), 400

    try:
        database.enable_box(box_id)
        return jsonify({"status": "success", "box_id": box_id, "disabled": False})
    except Exception as e:
        app.logger.exception(f"[DISABLED_BOXES] enable failed: {e}")
        return jsonify({"status": "error", "message": "Failed to enable box"}), 500


@app.route("/api/prints/unlock", methods=["POST"])
def unlock_print():
    data = request.get_json(force=True)
    print_data = database.get_print(data["id"])
    if print_data is None:
        return jsonify({"status": "error", "message": "Print not found"}), 404

    if print_data.status in (STATUS_PICKED_UP, STATUS_ABANDONED):
        return jsonify({"status": "error", "message": "Print is not available for unlock"}), 409

    ok, err = open_box_by_box_id(print_data.box_id)
    if not ok:
        return jsonify({"status": "error", "message": f"Failed to open box: {err}"}), 500

    return jsonify({"status": "success"})


@app.route("/api/kiosk/latest-scan", methods=["GET"])
def kiosk_latest_scan():
    screen = normalize_scanner_id(request.args.get("screen"))

    with latest_scan_lock:
        return jsonify(latest_scan_events[screen].copy())


@app.route("/api/scan", methods=["POST", "GET"])
def scan():
    data = {}
    if request.method == "POST":
        data = request.get_json(silent=True) or {}

    scanner_id = normalize_scanner_id(
        data.get("scanner_id") or request.args.get("scanner_id")
    )

    code = (data.get("code") or request.args.get("code") or "").strip()
    if not code:
        update_latest_scan_event(
            scanner_id,
            "error",
            "Invalid Code",
            "There has been an error. Ask a Maker Mentor for help.",
            None,
        )
        return jsonify({"status": "error", "message": "Missing code", "scanner_id": scanner_id}), 400

    try:
        code_int = int(code)
    except ValueError:
        update_latest_scan_event(
            scanner_id,
            "error",
            "Invalid Code",
            "There has been an error. Ask a Maker Mentor for help.",
            None,
        )
        return jsonify({"status": "error", "message": "Invalid code format", "scanner_id": scanner_id}), 400

    try:
        print_data = database.get_print_by_code(code_int)
    except Exception as e:
        app.logger.exception(f"[SCAN] DB lookup failed: {e}")
        update_latest_scan_event(
            scanner_id,
            "error",
            "System Error",
            "There has been an error. Ask a Maker Mentor for help.",
            None,
        )
        return jsonify({"status": "error", "message": "Scan lookup failed", "scanner_id": scanner_id}), 500

    if print_data is None:
        update_latest_scan_event(
            scanner_id,
            "error",
            "Invalid Code",
            "There has been an error. Ask a Maker Mentor for help.",
            None,
        )
        return jsonify({"status": "error", "message": "Invalid code or print not found", "scanner_id": scanner_id}), 404

    if getattr(print_data, "status", STATUS_IN_BOX) == STATUS_PICKED_UP:
        update_latest_scan_event(
            scanner_id,
            "error",
            "Already Picked Up",
            "This item has already been picked up.",
            None,
        )
        return jsonify({"status": "error", "message": "Print already picked up", "scanner_id": scanner_id}), 409

    if getattr(print_data, "status", STATUS_IN_BOX) == STATUS_ABANDONED:
        update_latest_scan_event(
            scanner_id,
            "error",
            "Item Unavailable",
            "This item is no longer available for pickup. Ask a Maker Mentor for help.",
            None,
        )
        return jsonify({"status": "error", "message": "Print is abandoned", "scanner_id": scanner_id}), 409

    scan_count = getattr(print_data, "scan_count", 0)

    if scan_count >= MAX_SCAN_USES:
        update_latest_scan_event(
            scanner_id,
            "error",
            "Code Use Limit Reached",
            "There has been an error. Ask a Maker Mentor for help.",
            None,
        )
        return jsonify({"status": "error", "message": "Code usage limit reached", "scanner_id": scanner_id}), 409

    ok, err = open_box_by_box_id(print_data.box_id)
    if not ok:
        update_latest_scan_event(
            scanner_id,
            "error",
            "System Error",
            "There has been an error. Ask a Maker Mentor for help.",
            None,
        )
        return jsonify({"status": "error", "message": f"Failed to open box: {err}", "scanner_id": scanner_id}), 500

    try:
        new_scan_count = scan_count + 1
        database.set_print_scan_count(print_data.id, new_scan_count)

        if scan_count == 0:
            database.set_print_status(print_data.id, STATUS_PICKED_UP)

            try:
                update_dates_by_print_number(
                    print_data.print_number,
                    date_picked_up=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                )
            except Exception as sheet_err:
                app.logger.warning(
                    f"[GSHEET] Failed to update Date Picked Up for print {print_data.print_number}: {sheet_err}"
                )

            try:
                update_box_status_by_print_number(
                    print_data.print_number,
                    STATUS_PICKED_UP
                )
            except Exception as sheet_err:
                app.logger.warning(
                    f"[GSHEET] Failed to update Status for print {print_data.print_number}: {sheet_err}"
                )

        if new_scan_count >= MAX_SCAN_USES:
            database.rotate_print_code(print_data.id)

    except Exception as e:
        app.logger.exception(f"[SCAN] post-unlock update failed: {e}")
        update_latest_scan_event(
            scanner_id,
            "error",
            "System Error",
            "There has been an error. Ask a Maker Mentor for help.",
            None,
        )
        return jsonify({
            "status": "error",
            "message": "Box opened but failed to update status",
            "scanner_id": scanner_id,
        }), 500

    update_latest_scan_event(
        scanner_id,
        "success",
        "Access Granted",
        f"Your Print is in BOX {print_data.box_id}",
        print_data.box_id,
    )

    return jsonify(
        {
            "status": "success",
            "scanner_id": scanner_id,
            "print_id": print_data.id,
            "box_id": print_data.box_id,
            "scan_count": new_scan_count,
            "remaining_uses": MAX_SCAN_USES - new_scan_count,
            "picked_up": True,
        }
    )


@app.route("/api/prints/<int:print_id>/send_email", methods=["POST"])
def send_email_for_print(print_id: int):
    print_data = database.get_print(print_id)
    if print_data is None:
        return jsonify({"status": "error", "message": "Print not found"}), 404

    if getattr(print_data, "status", STATUS_IN_BOX) == STATUS_PICKED_UP:
        return jsonify({"status": "error", "message": "Print already picked up"}), 400

    try:
        recipient_name = getattr(print_data, "name", "") or "Maker"
        app.logger.warning(
            f"[EMAIL] UI resend to={print_data.email} code={print_data.code} print_id={print_id} name={recipient_name}"
        )
        emailer.send_pickup_email(print_data.email, print_data.code, recipient_name)
        app.logger.warning(f"[EMAIL] UI resend OK to={print_data.email} print_id={print_id}")
        return jsonify({"status": "success", "email_sent": True})
    except Exception as e:
        app.logger.exception(f"[EMAIL] UI resend FAILED to={print_data.email} print_id={print_id}: {e}")
        return jsonify(
            {
                "status": "error",
                "message": "Email failed to send.",
                "email_sent": False,
                "error": str(e),
            }
        ), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
