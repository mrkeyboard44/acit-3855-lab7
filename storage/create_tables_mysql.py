import mysql.connector
import yaml

with open('app_conf.yaml', 'r') as f:
    app_config = yaml.safe_load(f.read())
    DB_USER = app_config['datastore']['user']
    DB_PW = app_config['datastore']['password']
    DB_HNAME = app_config['datastore']['hostname']
    DB_PORT = app_config['datastore']['port']
    DB_NAME = app_config['datastore']['db']


db_conn = mysql.connector.connect(host=DB_HNAME, user=DB_USER,
password=DB_PW, database=DB_NAME)

db_cursor = db_conn.cursor()

db_cursor.execute('''
                CREATE TABLE exercise_data
                (id INT NOT NULL AUTO_INCREMENT,
                user_id VARCHAR(250) NOT NULL,
                device_name VARCHAR(250) NOT NULL,
                heart_rate INTEGER NOT NULL,
                date_created VARCHAR(100) NOT NULL,
                recording_id VARCHAR(250) NOT NULL,
                trace_time VARCHAR(100) NOT NULL,
                trace_id VARCHAR(250) NOT NULL,
                CONSTRAINT exercise_data_pk PRIMARY KEY (id))
                ''')

db_cursor.execute('''
                CREATE TABLE user_parameters
                (id INT NOT NULL AUTO_INCREMENT, 
                user_id VARCHAR(250) NOT NULL,
                age INTEGER NOT NULL,
                weight INTEGER NOT NULL,
                device_name VARCHAR(250) NOT NULL,
                exercise VARCHAR(100) NOT NULL,
                reps INTEGER NOT NULL,
                met FLOAT NOT NULL,
                date_created VARCHAR(100) NOT NULL,
                recording_id VARCHAR(250) NOT NULL,
                trace_time VARCHAR(100) NOT NULL,
                trace_id VARCHAR(250) NOT NULL,
                CONSTRAINT user_parameters_pk PRIMARY KEY (id))
                ''')


db_conn.commit()
db_conn.close()
