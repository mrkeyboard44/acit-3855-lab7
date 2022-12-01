import sqlite3
def create_tables_now(db_name):
        conn = sqlite3.connect(db_name)

        c = conn.cursor()

        c.execute('''
                CREATE TABLE health
                (id INTEGER PRIMARY KEY ASC, 
                receiver VARCHAR(250) NOT NULL,
                storage VARCHAR(250) NOT NULL,
                processing VARCHAR(250) NOT NULL,
                audit_log VARCHAR(250) NOT NULL,
                last_update VARCHAR(100) NOT NULL)
                ''')

        conn.commit()
        conn.close()

