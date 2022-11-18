from unittest import result
import mysql.connector

class SelectTable():

    db_conn = mysql.connector.connect(host="localhost", user="openapi",
    password="password", database="openapi")

    db_cursor = db_conn.cursor()

    def __init__(self, table_type):
        self.table_type = table_type


    def print_result(myresult, table_name):
        print('\n-------------', table_name, '-------------')

        myresult = myresult[::-1]

        if len(myresult) > 10:
            result_length = 10
        else:
            result_length = len(myresult)

        for i in range(result_length):
            print(myresult[i])


    def select_exercise_data(db_cursor):
        db_cursor.execute('''
                        SELECT * FROM exercise_data
                        ''')

        return db_cursor.fetchall()[-1]

        # print_result(myresult, 'exercise_data')

    def select_user_parameters(db_cursor):
        db_cursor.execute('''
                    SELECT * FROM user_parameters
                    ''')

        myresult = db_cursor.fetchall()

        # print_result(myresult, 'user_parameters')

    def select_activity_summary(db_cursor):

        db_cursor.execute('''
                    SELECT * FROM activity_summary
                    ''')

        myresult = db_cursor.fetchall()

        # print_result(myresult, 'activity_summary')


    db_conn.commit()
    db_conn.close()