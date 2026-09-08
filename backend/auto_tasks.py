import os
from dotenv import load_dotenv
from database import Database
from emailer import Emailer
from google_sheets_service import (
    get_print_details_by_print_number,
    update_box_status_by_print_number,
)

load_dotenv()

STATUS_IN_BOX = 0
STATUS_PICKED_UP = 1
STATUS_ABANDONED = 2
STATUS_AWAITING_PICKUP = 3


def get_recipient_name(print_obj):
    fallback_name = print_obj.email.split("@")[0]

    try:
        details = get_print_details_by_print_number(print_obj.print_number)
        if details and details.get("name"):
            return str(details["name"]).strip()
    except Exception as e:
        print(
            f"[WARN] Could not fetch name from sheets for "
            f"print_number={print_obj.print_number}: {e}"
        )

    return fallback_name


def send_reminder_email(emailer, print_obj):
    name = get_recipient_name(print_obj)

    print(
        f"[REMINDER] Sending current code "
        f"print_id={print_obj.id}, "
        f"print_number={print_obj.print_number}, "
        f"email={print_obj.email}, "
        f"code={print_obj.code}"
    )

    try:
        emailer.send_reminder_email(
            to=print_obj.email,
            code=print_obj.code,
            name=name,
        )
        print(f"[EMAIL] Reminder sent to {print_obj.email} ({name})")
    except Exception as e:
        raise RuntimeError(f"Email failed: {e}") from e


def main():
    db = Database(
        database=os.getenv("PG_DATABASE"),
        host=os.getenv("PG_HOST"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        port=os.getenv("PG_PORT"),
    )

    emailer = Emailer(
        email_user=os.getenv("EMAIL_USER", "makerspace@clarkson.edu"),
        smtp_host=os.getenv("SMTP_HOST", "intmx.clarkson.edu"),
        smtp_port=int(os.getenv("SMTP_PORT", "25")),
    )

    print("[AUTO] Running daily tasks...")

    reminders = db.get_prints_for_7_day_reminder()
    print(f"[AUTO] {len(reminders)} reminders")

    for item in reminders:
        try:
            send_reminder_email(emailer, item)
            db.mark_reminder_sent(item.id)
            db.set_print_status(item.id, STATUS_AWAITING_PICKUP)

            try:
                update_box_status_by_print_number(
                    item.print_number,
                    STATUS_AWAITING_PICKUP
                )
                print(f"[GSHEET] Updated status to Awaiting Pickup for print {item.print_number}")
            except Exception as sheet_err:
                print(
                    f"[WARN] Failed to update sheet status for print "
                    f"{item.print_number}: {sheet_err}"
                )

        except Exception as e:
            print(f"[ERROR] Reminder failed for print_id={item.id}: {e}")

    old_items = db.get_prints_for_15_day_abandon()
    print(f"[AUTO] {len(old_items)} to abandon")

    for item in old_items:
        try:
            db.set_print_status(item.id, STATUS_ABANDONED)

            try:
                update_box_status_by_print_number(
                    item.print_number,
                    STATUS_ABANDONED
                )
                print(f"[GSHEET] Updated status to Abandoned for print {item.print_number}")
            except Exception as sheet_err:
                print(
                    f"[WARN] Failed to update sheet status for print "
                    f"{item.print_number}: {sheet_err}"
                )

            print(f"[AUTO] Abandoned {item.id}")
        except Exception as e:
            print(f"[ERROR] Abandon failed for print_id={item.id}: {e}")

    print("[AUTO] Done")


if __name__ == "__main__":
    main()
