import mysql.connector

db_conn = mysql.connector.connect(host="https://acit-3855-matt-kafka.westus3.cloudapp.azure.com", user="user",
password="password", database="events")
db_cursor = db_conn.cursor()

db_cursor.execute('''
                    DROP TABLE user_parameters , exercise_data
                    ''')
db_conn.commit()
db_conn.close()
