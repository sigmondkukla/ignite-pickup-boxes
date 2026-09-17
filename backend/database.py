import psycopg2
import random
from typing import Optional, List, Tuple
from datetime import datetime, timezone

STATUS_IN_BOX = 0
STATUS_PICKED_UP = 1
STATUS_ABANDONED = 2
STATUS_AWAITING_PICKUP = 3


class Box:
    def __init__(self, id, print_id, assign_enabled):
        self.id = id
        self.print_id = print_id
        self.assign_enabled = assign_enabled


class Print:
    def __init__(
        self,
        id: int,
        print_number: int,
        email: str,
        code: int,
        box_id: int,
        status: int,
        scan_count: int,
        date_added,
        reminder_sent: bool,
        date_picked_up,
    ) -> None:
        self.id = id
        self.print_number = print_number
        self.email = email
        self.code = code
        self.box_id = box_id
        self.status = status
        self.scan_count = scan_count
        self.date_added = date_added
        self.reminder_sent = reminder_sent
        self.date_picked_up = date_picked_up

    def _days_in_box(self) -> int:
        if not self.date_added:
            return 0

        now = datetime.now(timezone.utc)

        if getattr(self.date_added, "tzinfo", None) is None:
            added = self.date_added.replace(tzinfo=timezone.utc)
        else:
            added = self.date_added.astimezone(timezone.utc)

        delta = now - added
        return max(delta.days, 0)

    def to_dict(self) -> dict:
        days_in_box = self._days_in_box()
        return {
            "id": self.id,
            "print_number": self.print_number,
            "email": self.email,
            "code": self.code,
            "box_id": self.box_id,
            "status": self.status,
            "scan_count": self.scan_count,
            "date_added": self.date_added.isoformat() if self.date_added else None,
            "reminder_sent": self.reminder_sent,
            "date_picked_up": self.date_picked_up.isoformat() if self.date_picked_up else None,
            "days_in_box": days_in_box,
            "dib": f"{days_in_box} DIB",
        }


class Database:
    def __init__(self, database: str, host: str, user: str, password: str, port: str) -> None:
        self.database = database
        self.host = host
        self.user = user
        self.password = password
        self.port = port

        self.conn = psycopg2.connect(
            database=database, host=host, user=user, password=password, port=port
        )
        self.cur = self.conn.cursor()

        self.ensure_tables()

    def ensure_cursor(self) -> None:
        if self.conn.closed:
            self.conn = psycopg2.connect(
                database=self.database,
                host=self.host,
                user=self.user,
                password=self.password,
                port=self.port,
            )
            self.cur = self.conn.cursor()
        elif self.cur.closed:
            self.cur = self.conn.cursor()

    def ensure_tables(self) -> None:
        self.ensure_cursor()
        self.ensure_print_table()
        self.ensure_box_table()
        self.ensure_disabled_boxes_table()
        self.ensure_app_settings_table()

    def ensure_app_settings_table(self) -> None:
        self.ensure_cursor()
        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS app_settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT NOW()
            );
            """
        )
        self.conn.commit()

    def get_setting(self, key: str, default=None):
        self.ensure_cursor()
        self.cur.execute(
            "SELECT value FROM app_settings WHERE key = %s;",
            (key,),
        )
        row = self.cur.fetchone()
        return row[0] if row else default

    def set_setting(self, key: str, value: str) -> bool:
        self.ensure_cursor()
        self.cur.execute(
            """
            INSERT INTO app_settings (key, value, updated_at)
            VALUES (%s, %s, NOW())
            ON CONFLICT (key)
            DO UPDATE SET value = EXCLUDED.value,
                          updated_at = NOW();
            """,
            (key, value),
        )
        self.conn.commit()
        return True

    def ensure_print_table(self) -> None:
        self.ensure_cursor()
        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS print (
                id SERIAL PRIMARY KEY,
                print_number INTEGER,
                email TEXT,
                code INTEGER,
                box_id INTEGER,
                status INTEGER,
                scan_count INTEGER NOT NULL DEFAULT 0,
                date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reminder_sent BOOLEAN NOT NULL DEFAULT FALSE,
                date_picked_up TIMESTAMP
            );
            """
        )
        self.conn.commit()

        self.cur.execute(
            """
            ALTER TABLE print
            ADD COLUMN IF NOT EXISTS scan_count INTEGER NOT NULL DEFAULT 0;
            """
        )
        self.conn.commit()

        self.cur.execute(
            """
            ALTER TABLE print
            ADD COLUMN IF NOT EXISTS date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
            """
        )
        self.conn.commit()

        self.cur.execute(
            """
            ALTER TABLE print
            ADD COLUMN IF NOT EXISTS reminder_sent BOOLEAN NOT NULL DEFAULT FALSE;
            """
        )
        self.conn.commit()

        self.cur.execute(
            """
            ALTER TABLE print
            ADD COLUMN IF NOT EXISTS date_picked_up TIMESTAMP;
            """
        )
        self.conn.commit()

        self.cur.execute(
            """
            UPDATE print
            SET date_added = CURRENT_TIMESTAMP
            WHERE date_added IS NULL;
            """
        )
        self.conn.commit()

        self.cur.execute(
            """
            UPDATE print
            SET reminder_sent = FALSE
            WHERE reminder_sent IS NULL;
            """
        )
        self.conn.commit()

    def ensure_box_table(self) -> None:
        self.ensure_cursor()
        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS box (
                id INTEGER PRIMARY KEY,
                print_id INTEGER,
                assign_enabled INTEGER
            );
            """
        )
        self.conn.commit()

    def ensure_disabled_boxes_table(self) -> None:
        self.ensure_cursor()
        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS disabled_boxes (
                id SERIAL PRIMARY KEY,
                box_id INTEGER UNIQUE NOT NULL,
                reason TEXT,
                created_at TIMESTAMP DEFAULT NOW()
            );
            """
        )
        self.conn.commit()

    def fill_box_table(self, num_boxes: int) -> None:
        self.ensure_cursor()
        for i in range(1, num_boxes + 1):
            self.cur.execute(
                """
                INSERT INTO box (id, print_id, assign_enabled)
                VALUES (%s, -1, 1)
                ON CONFLICT (id) DO NOTHING;
                """,
                (i,),
            )
        self.conn.commit()

    def list_disabled_boxes(self) -> List[Tuple[int, Optional[str]]]:
        self.ensure_cursor()
        self.cur.execute(
            "SELECT box_id, reason FROM disabled_boxes ORDER BY box_id ASC;"
        )
        return [(row[0], row[1]) for row in self.cur.fetchall()]

    def is_box_disabled(self, box_id: int) -> bool:
        self.ensure_cursor()
        self.cur.execute(
            "SELECT 1 FROM disabled_boxes WHERE box_id = %s LIMIT 1;",
            (box_id,),
        )
        return self.cur.fetchone() is not None

    def disable_box(self, box_id: int, reason: Optional[str] = None) -> None:
        self.ensure_cursor()
        self.cur.execute(
            """
            INSERT INTO disabled_boxes (box_id, reason)
            VALUES (%s, %s)
            ON CONFLICT (box_id)
            DO UPDATE SET reason = EXCLUDED.reason;
            """,
            (box_id, reason),
        )
        self.conn.commit()

    def enable_box(self, box_id: int) -> None:
        self.ensure_cursor()
        self.cur.execute("DELETE FROM disabled_boxes WHERE box_id = %s;", (box_id,))
        self.conn.commit()

    def validate_box_not_disabled(self, box_id: int) -> None:
        if self.is_box_disabled(box_id):
            raise ValueError(f"Box {box_id} is disabled")

    def get_available_boxes(self) -> List[Box]:
        self.ensure_cursor()
        self.cur.execute(
            """
            SELECT b.id, b.print_id, b.assign_enabled
            FROM box b
            WHERE b.print_id = -1
              AND b.assign_enabled = 1
              AND NOT EXISTS (
                SELECT 1 FROM disabled_boxes d WHERE d.box_id = b.id
              )
            ORDER BY b.id;
            """
        )
        return [Box(*row) for row in self.cur.fetchall()]

    def get_next_available_box(self) -> Optional[Box]:
        self.ensure_cursor()
        self.cur.execute(
            """
            SELECT b.id, b.print_id, b.assign_enabled
            FROM box b
            WHERE b.print_id = -1
              AND b.assign_enabled = 1
              AND NOT EXISTS (
                SELECT 1 FROM disabled_boxes d WHERE d.box_id = b.id
              )
            ORDER BY b.id
            LIMIT 1;
            """
        )
        row = self.cur.fetchone()
        if row is None:
            return None
        return Box(*row)

    def get_box(self, box_id) -> Optional[Box]:
        self.ensure_cursor()
        self.cur.execute(
            "SELECT id, print_id, assign_enabled FROM box WHERE id = %s;",
            (box_id,),
        )
        row = self.cur.fetchone()
        if row is None:
            return None
        return Box(*row)

    def set_box_print_id(self, box_id, print_id):
        self.validate_box_not_disabled(int(box_id))

        self.ensure_cursor()
        self.cur.execute(
            "UPDATE box SET print_id = %s WHERE id = %s;",
            (print_id, box_id),
        )
        self.conn.commit()

    def create_print(self, print_number: int, email: str, box_id: int):
        self.validate_box_not_disabled(int(box_id))

        self.ensure_cursor()
        code = random.randint(100000, 999999)

        self.cur.execute(
            """
            INSERT INTO print (
                print_number, email, code, box_id, status, scan_count, date_added, reminder_sent, date_picked_up
            )
            VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, FALSE, NULL)
            RETURNING id, code;
            """,
            (print_number, email, code, box_id, STATUS_IN_BOX, 0),
        )
        row = self.cur.fetchone()
        print_id = row[0]

        self.cur.execute(
            "UPDATE box SET print_id = %s WHERE id = %s;",
            (print_id, box_id),
        )
        self.conn.commit()

        return print_id, code

    def set_print_status(self, print_id: int, status: int):
        self.ensure_cursor()

        if status == STATUS_PICKED_UP:
            self.cur.execute(
                """
                UPDATE print
                SET status = %s,
                    date_picked_up = CURRENT_TIMESTAMP
                WHERE id = %s;
                """,
                (status, print_id),
            )
            self.cur.execute(
                "UPDATE box SET print_id = -1 WHERE print_id = %s;",
                (print_id,),
            )

        elif status == STATUS_ABANDONED:
            self.cur.execute(
                """
                UPDATE print
                SET status = %s
                WHERE id = %s;
                """,
                (status, print_id),
            )
            self.cur.execute(
                "UPDATE box SET print_id = -1 WHERE print_id = %s;",
                (print_id,),
            )

        elif status in (STATUS_IN_BOX, STATUS_AWAITING_PICKUP):
            self.cur.execute(
                """
                UPDATE print
                SET status = %s
                WHERE id = %s;
                """,
                (status, print_id),
            )

        else:
            raise ValueError(f"Invalid status: {status}")

        self.conn.commit()

    def set_print_scan_count(self, print_id: int, scan_count: int):
        self.ensure_cursor()
        self.cur.execute(
            "UPDATE print SET scan_count = %s WHERE id = %s;",
            (scan_count, print_id),
        )
        self.conn.commit()

    def rotate_print_code(self, print_id: int) -> int:
        self.ensure_cursor()

        while True:
            new_code = random.randint(100000, 999999)
            self.cur.execute(
                "SELECT 1 FROM print WHERE code = %s LIMIT 1;",
                (new_code,),
            )
            if self.cur.fetchone() is None:
                break

        self.cur.execute(
            "UPDATE print SET code = %s WHERE id = %s;",
            (new_code, print_id),
        )
        self.conn.commit()
        return new_code

    def get_print(self, print_id) -> Optional[Print]:
        self.ensure_cursor()
        self.cur.execute(
            """
            SELECT id, print_number, email, code, box_id, status, scan_count, date_added, reminder_sent, date_picked_up
            FROM print
            WHERE id = %s;
            """,
            (print_id,),
        )
        row = self.cur.fetchone()
        if row is None:
            return None
        return Print(*row)

    def get_prints(self) -> List[Print]:
        self.ensure_cursor()
        self.cur.execute(
            """
            SELECT id, print_number, email, code, box_id, status, scan_count, date_added, reminder_sent, date_picked_up
            FROM print
            ORDER BY id DESC;
            """
        )
        return [Print(*row) for row in self.cur.fetchall()]

    def get_print_by_code(self, code) -> Optional[Print]:
        self.ensure_cursor()
        self.cur.execute(
            """
            SELECT id, print_number, email, code, box_id, status, scan_count, date_added, reminder_sent, date_picked_up
            FROM print
            WHERE code = %s;
            """,
            (code,),
        )
        row = self.cur.fetchone()
        if row is None:
            return None
        return Print(*row)

    def get_print_by_number(self, print_number) -> Optional[Print]:
        self.ensure_cursor()
        self.cur.execute(
            """
            SELECT id, print_number, email, code, box_id, status, scan_count, date_added, reminder_sent, date_picked_up
            FROM print
            WHERE print_number = %s
            ORDER BY id DESC
            LIMIT 1;
            """,
            (print_number,),
        )
        row = self.cur.fetchone()
        if row is None:
            return None
        return Print(*row)

    def get_prints_for_7_day_reminder(self):
        self.ensure_cursor()
        self.cur.execute(
            """
            SELECT id, print_number, email, code, box_id, status, scan_count, date_added, reminder_sent, date_picked_up
            FROM print
            WHERE status = %s
              AND reminder_sent = FALSE
              AND date_added <= (CURRENT_TIMESTAMP - INTERVAL '7 days')
            ORDER BY date_added ASC;
            """,
            (STATUS_IN_BOX,),
        )
        return [Print(*row) for row in self.cur.fetchall()]

    def get_prints_for_15_day_abandon(self):
        self.ensure_cursor()
        self.cur.execute(
            """
            SELECT id, print_number, email, code, box_id, status, scan_count, date_added, reminder_sent, date_picked_up
            FROM print
            WHERE status = %s
              AND date_added <= (CURRENT_TIMESTAMP - INTERVAL '15 days')
            ORDER BY date_added ASC;
            """,
            (STATUS_AWAITING_PICKUP,),
        )
        return [Print(*row) for row in self.cur.fetchall()]

    def mark_reminder_sent(self, print_id: int):
        self.ensure_cursor()
        self.cur.execute(
            "UPDATE print SET reminder_sent = TRUE WHERE id = %s;",
            (print_id,),
        )
        self.conn.commit()

    def delete_print(self, print_id):
        self.ensure_cursor()

        self.cur.execute(
            "UPDATE box SET print_id = -1 WHERE print_id = %s;",
            (print_id,),
        )
        self.cur.execute("DELETE FROM print WHERE id = %s;", (print_id,))
        self.conn.commit()

    def delete_prints(self, print_ids):
        self.ensure_cursor()
        ids_tuple = tuple(print_ids)
        if not ids_tuple:
            return

        self.cur.execute(
            "UPDATE box SET print_id = -1 WHERE print_id IN %s;",
            (ids_tuple,),
        )
        self.cur.execute("DELETE FROM print WHERE id IN %s;", (ids_tuple,))
        self.conn.commit()

    def update_print(self, data):
        self.ensure_cursor()

        current = self.get_print(data["id"])
        if current is None:
            raise ValueError(f"Print {data['id']} not found")

        new_box_id = data.get("box_id")
        old_box_id = current.box_id

        if new_box_id is not None:
            self.validate_box_not_disabled(int(new_box_id))

        next_status = data["status"]
        date_picked_up = data.get("date_picked_up", current.date_picked_up)

        if next_status == STATUS_PICKED_UP and current.date_picked_up is None:
            self.cur.execute(
                """
                UPDATE print
                SET print_number = %s,
                    email = %s,
                    code = %s,
                    box_id = %s,
                    status = %s,
                    scan_count = %s,
                    reminder_sent = %s,
                    date_picked_up = CURRENT_TIMESTAMP
                WHERE id = %s;
                """,
                (
                    data["print_number"],
                    data["email"],
                    data["code"],
                    data["box_id"],
                    next_status,
                    data.get("scan_count", current.scan_count),
                    data.get("reminder_sent", current.reminder_sent),
                    data["id"],
                ),
            )
        else:
            self.cur.execute(
                """
                UPDATE print
                SET print_number = %s,
                    email = %s,
                    code = %s,
                    box_id = %s,
                    status = %s,
                    scan_count = %s,
                    reminder_sent = %s,
                    date_picked_up = %s
                WHERE id = %s;
                """,
                (
                    data["print_number"],
                    data["email"],
                    data["code"],
                    data["box_id"],
                    next_status,
                    data.get("scan_count", current.scan_count),
                    data.get("reminder_sent", current.reminder_sent),
                    date_picked_up,
                    data["id"],
                ),
            )

        if new_box_id is not None and int(new_box_id) != int(old_box_id):
            self.cur.execute(
                "UPDATE box SET print_id = -1 WHERE id = %s;",
                (old_box_id,),
            )
            self.cur.execute(
                "UPDATE box SET print_id = %s WHERE id = %s;",
                (data["id"], new_box_id),
            )

        if next_status in (STATUS_PICKED_UP, STATUS_ABANDONED):
            self.cur.execute(
                "UPDATE box SET print_id = -1 WHERE print_id = %s;",
                (data["id"],),
            )
        elif next_status in (STATUS_IN_BOX, STATUS_AWAITING_PICKUP) and new_box_id is not None:
            self.cur.execute(
                "UPDATE box SET print_id = %s WHERE id = %s;",
                (data["id"], new_box_id),
            )

        self.conn.commit()


if __name__ == "__main__":
    pass
