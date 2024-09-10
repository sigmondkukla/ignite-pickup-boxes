import psycopg2
import dotenv
import os

class Database:
    def __init__(self):
        dotenv.load_dotenv()
        self.conn = psycopg2.connect(database="ignite-pickup-boxes",
                                     host="128.153.181.158",
                                     user="ignite-pickup-boxes",
                                     password=os.getenv("POSTGRES_PASSWORD"),
                                     port="5432")
        self.cur = self.conn.cursor()

        self.ensure_tables()

    def ensure_tables(self):
        self.ensure_print_table()
        self.ensure_box_table()

    def ensure_print_table(self):
        self.cur.execute("""CREATE TABLE IF NOT EXISTS print (
                         id SERIAL PRIMARY KEY, 
                         print_number INTEGER, 
                         email TEXT, 
                         code INTEGER, 
                         box_id INTEGER,
                         status INTEGER);""")
        self.conn.commit()

    def ensure_box_table(self):
        self.cur.execute("""CREATE TABLE IF NOT EXISTS box (
                         id INTEGER PRIMARY KEY, 
                         print_id INTEGER, 
                         assign_enabled INTEGER);""")
        self.conn.commit()

    def fill_box_table(self, num_boxes):
        for i in range(num_boxes):
            self.cur.execute("INSERT INTO box (id, print_id, assign_enabled) VALUES (%s, -1, %s);", (i, 1))
        self.conn.commit()

    def get_available_boxes(self):
        self.cur.execute("SELECT * FROM box WHERE print_id = -1 AND assign_enabled = 1;")
        return [Box(*row) for row in self.cur.fetchall()]
    
    def get_next_available_box(self):
        self.cur.execute("SELECT * FROM box WHERE print_id = -1 AND assign_enabled = 1 LIMIT 1;")
        return Box(*self.cur.fetchone())
    
    def create_print(self, print_number, email, code, box_id):
        self.cur.execute("INSERT INTO print (print_number, email, code, box_id, status) VALUES (%s, %s, %s, %s, %s);", (print_number, email, code, box_id, 0))
        self.conn.commit()

    def set_print_status(self, print_id, status):
        self.cur.execute("UPDATE print SET status = %s WHERE id = %s;", (status, print_id))
        self.conn.commit()

    def get_print(self, print_id):
        self.cur.execute("SELECT * FROM print WHERE id = %s;", (print_id,))
        return Print(*self.cur.fetchone())
    
    def get_prints(self):
        self.cur.execute("SELECT * FROM print;")
        return [Print(*row) for row in self.cur.fetchall()]

class Box:
    def __init__(self, id, print_id, assign_enabled):
        self.id = id
        self.print_id = print_id
        self.assign_enabled = assign_enabled
    
    # def available(self) -> bool:
    #     """Checks if the box is empty and allowed to be assigned
        
    #     Returns:
    #         bool: if the system may automatically assign this box
    #     """
    #     return self.assign_enabled == 1 and self.print_id == -1
    
class Print:
    def __init__(self, id: int, print_number: int, email: str, code: int, box_id: int, status: int) -> None:
        self.id = id
        self.print_number = print_number
        self.email = email
        self.code = code
        self.box_id = box_id
        self.status = status 

if __name__ == "__main__":
    db = Database()
    db.fill_box_table(8)
    db.conn.close()