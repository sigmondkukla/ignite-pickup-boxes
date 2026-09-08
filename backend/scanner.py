import serial
import requests
import argparse
import threading
import time

BACKEND_URL = "http://localhost:5000/api/scan"
VALID_SCANNER_IDS = {"left", "right"}


args = argparse.ArgumentParser()

args.add_argument(
    "--ports",
    nargs="+",
    default=["COM9"],
    help="Serial ports to connect to. Example: --ports /dev/ttyACM0 /dev/ttyACM1"
)

args.add_argument(
    "--scanner-ids",
    nargs="+",
    default=["left"],
    help="Scanner IDs matching ports. Example: --scanner-ids right left"
)

parsed = args.parse_args()
ports = parsed.ports
scanner_ids = parsed.scanner_ids


def get_scanner_id_for_port(index):
    if index < len(scanner_ids):
        scanner_id = scanner_ids[index].strip().lower()
    else:
        scanner_id = "left"

    if scanner_id not in VALID_SCANNER_IDS:
        scanner_id = "left"

    return scanner_id


def scanner_worker(port, scanner_id):
    while True:
        ser = None

        try:
            ser = serial.Serial(port, 9600, 8, "N", 1, timeout=None)
            print(f"[{port}] Connected as scanner_id={scanner_id}", flush=True)

            while True:
                raw_line = ser.readline().decode("utf-8", errors="ignore").strip()

                if not raw_line:
                    continue

                if raw_line.startswith("P01"):
                    code = raw_line[3:]
                elif raw_line.isdigit():
                    code = raw_line
                else:
                    print(f"[{port}] Invalid code: {raw_line}", flush=True)
                    continue

                print(f"[{port}] Scanned code={code} scanner_id={scanner_id}", flush=True)

                try:
                    response = requests.post(
                        BACKEND_URL,
                        json={
                            "code": code,
                            "scanner_id": scanner_id,
                            "source": "serial_scanner",
                            "port": port,
                        },
                        timeout=2,
                    )

                    try:
                        print(f"[{port}] Backend response: {response.json()}", flush=True)
                    except Exception:
                        print(f"[{port}] Backend response text: {response.text}", flush=True)

                except requests.exceptions.RequestException as e:
                    print(f"[{port}] Failed to send scan: {e}", flush=True)

        except serial.SerialException as e:
            print(f"[{port}] Serial error: {e}", flush=True)

        except Exception as e:
            print(f"[{port}] Error: {e}", flush=True)

        finally:
            try:
                if ser and ser.is_open:
                    ser.close()
            except Exception:
                pass

        print(f"[{port}] Reconnecting in 2 seconds...", flush=True)
        time.sleep(2)


threads = []

for index, port in enumerate(ports):
    scanner_id = get_scanner_id_for_port(index)

    thread = threading.Thread(
        target=scanner_worker,
        args=(port, scanner_id),
        daemon=True,
    )

    thread.start()
    threads.append(thread)


try:
    for thread in threads:
        thread.join()

except KeyboardInterrupt:
    print("Exiting scanner...", flush=True)
