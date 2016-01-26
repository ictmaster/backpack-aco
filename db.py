import sqlite3
import sys

db_name = 'aco_i.db'

def get_edge_by_id(id):
    con = sqlite3.connect(db_name)
    c = con.cursor()
    c.execute("select * from edges where id=?", (id,))
    edge = c.fetchone()
    con.commit()
    con.close()
    return edge
def create_db():
    con = sqlite3.connect(db_name)
    c = con.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS nodes
    (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data TEXT
    );
    """)
    c.execute("""
    CREATE TABLE IF NOT EXISTS edges
    (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        from_node INTEGER,
        to_node INTEGER,
        cost TEXT,
        pheromones REAL
    );
    """)
    con.commit()
    con.close()


def drop_db():
    con = sqlite3.connect(db_name)
    c = con.cursor()
    c.execute("DROP TABLE nodes")
    c.execute("DROP TABLE edges")
    con.commit()
    con.close()

if __name__ == '__main__':
    if 'redo' in sys.argv:
        try:
            drop_db()
        except sqlite3.OperationalError:
            pass
        create_db()
    else:
        create_db()
