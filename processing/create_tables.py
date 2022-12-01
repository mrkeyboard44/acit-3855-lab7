import sqlite3
def create_tables_now(db_name):
        conn = sqlite3.connect(db_name)

        c = conn.cursor()

        c.execute('''
                CREATE TABLE stats
                (id INTEGER PRIMARY KEY ASC, 
                recording_id VARCHAR(250) NOT NULL,
                total_recordings INTEGER NOT NULL,
                total_reps INTEGER NOT NULL,
                max_heart_rate INTEGER NOT NULL,
                min_heart_rate INTEGER NOT NULL,
                calories_burned INTEGER NOT NULL,
                last_updated VARCHAR(100) NOT NULL)
                ''')

        conn.commit()
        conn.close()

