import psycopg2

class Box:
    def __init__(self, id, print_id, assign_enabled):
        self.id = id
        self.print_id = print_id
        self.assign_enabled = assign_enabled
    
class Print:
    def __init__(self, id: int, print_number: int, email: str, code: int, box_id: int, status: int) -> None:
        self.id = id
        self.print_number = print_number
        self.email = email
        self.code = code
        self.box_id = box_id
        self.status = status 

class Database:
    def __init__(self, database: str, host: str, user: str, password: str, port: str) -> None:
        self.conn = psycopg2.connect(database=database, host=host, user=user, password=password, port=port)
        self.cur = self.conn.cursor()

        self.ensure_tables()

    def ensure_tables(self) -> None:
        self.ensure_print_table()
        self.ensure_box_table()

    def ensure_print_table(self) -> None:
        self.cur.execute("""CREATE TABLE IF NOT EXISTS print (
                         id SERIAL PRIMARY KEY, 
                         print_number INTEGER, 
                         email TEXT, 
                         code INTEGER, 
                         box_id INTEGER,
                         status INTEGER);""")
        self.conn.commit()

    def ensure_box_table(self) -> None:
        self.cur.execute("""CREATE TABLE IF NOT EXISTS box (
                         id INTEGER PRIMARY KEY, 
                         print_id INTEGER, 
                         assign_enabled INTEGER);""")
        self.conn.commit()

    def fill_box_table(self, num_boxes: int) -> None:
        for i in range(num_boxes):
            self.cur.execute("INSERT INTO box (id, print_id, assign_enabled) VALUES (%s, -1, %s);", (i, 1))
        self.conn.commit()

    def get_available_boxes(self) -> list[Box]:
        self.cur.execute("SELECT * FROM box WHERE print_id = -1 AND assign_enabled = 1;")
        return [Box(*row) for row in self.cur.fetchall()]
    
    def get_next_available_box(self) -> Box:
        self.cur.execute("SELECT * FROM box WHERE print_id = -1 AND assign_enabled = 1 LIMIT 1;")
        return Box(*self.cur.fetchone())
    
    def create_print(self, print_number: int, email: str, code: int, box_id: int):
        self.cur.execute("INSERT INTO print (print_number, email, code, box_id, status) VALUES (%s, %s, %s, %s, %s);", (print_number, email, code, box_id, 0))
        self.conn.commit()

    def set_print_status(self, print_id: int, status: int):
        self.cur.execute("UPDATE print SET status = %s WHERE id = %s;", (status, print_id))
        self.conn.commit()

    def get_print(self, print_id) -> Print:
        self.cur.execute("SELECT * FROM print WHERE id = %s;", (print_id,))
        return Print(*self.cur.fetchone())
    
    def get_prints(self) -> list[Print]:
        self.cur.execute("SELECT * FROM print;")
        return [Print(*row) for row in self.cur.fetchall()]
    
    def get_print_by_code(self, code) -> Print:
        self.cur.execute("SELECT * FROM print WHERE code = %s;", (code,))
        return Print(*self.cur.fetchone())
    
    def get_box(self, box_id) -> Box:
        self.cur.execute("SELECT * FROM box WHERE id = %s;", (box_id,))
        return Box(*self.cur.fetchone())
    
    def set_box_print_id(self, box_id, print_id):
        self.cur.execute("UPDATE box SET print_id = %s WHERE id = %s;", (print_id, box_id))
        self.conn.commit()

if __name__ == "__main__":
    db = Database()
    db.fill_box_table(8)
    db.conn.close()