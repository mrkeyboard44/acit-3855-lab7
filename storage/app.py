"""storage module receives events from reciever and stores in db"""
import json
import os
import logging
import logging.config
from threading import Thread
import datetime
import yaml
from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker
from pykafka import KafkaClient
from pykafka.common import OffsetType
import connexion
from connexion import NoContent
from exercise_data import ExerciseData
from user_parameters import UserParameters
from base import Base

if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    app_conf_file = "/config/app_conf.yml"
    log_conf_file = "/config/log_conf.yml"
    
else:
    print("In Dev Environment")
    app_conf_file = "app_conf.yml"
    log_conf_file = "log_conf.yml"
    
with open(app_conf_file, 'r') as f:
    app_config = yaml.safe_load(f.read())
    DB_USER = app_config['datastore']['user']
    DB_PW = app_config['datastore']['password']
    DB_HNAME = app_config['datastore']['hostname']
    DB_PORT = app_config['datastore']['port']
    DB_NAME = app_config['datastore']['db']

    KAFKA_HOSTNAME = app_config['events']['hostname']
    KAFKA_PORT = app_config['events']['port']
    KAFKA_TOPIC = app_config['events']['topic']

# External Logging Configuration
with open(log_conf_file, 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)
    logger = logging.getLogger('basicLogger')
    logger.info("App Conf File: %s" % app_conf_file)
    logger.info("Log Conf File: %s" % log_conf_file)

logger = logging.getLogger('basicLogger')

logger.info(f"Connecting to DB. Hostname:{DB_HNAME}, Port:{DB_PORT}")

logger.info(f"Connecting to Kafka. Hostname:{KAFKA_HOSTNAME}, Port:{KAFKA_PORT}")


DB_ENGINE = create_engine(f'mysql+pymysql://{DB_USER}:{DB_PW}@{DB_HNAME}:{DB_PORT}/{DB_NAME}', pool_pre_ping=True)

# DB_ENGINE = create_engine("sqlite:///readings.sqlite")
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)




def report_exercise_data(body):
    """ Receives exercise data """
    session = DB_SESSION()
    print(body['user_id'],
        body['device_name'],
        body['heart_rate'],
        body['date_created'],
        body['recording_id'],
        body['trace_id'],
        body['trace_time'])
    ed = ExerciseData(body['user_id'],
        body['device_name'],
        body['heart_rate'],
        body['date_created'],
        body['recording_id'],
        body['trace_id'],
        body['trace_time'])


    session.add(ed)

    session.commit()
    session.close()

    trace_id = body['trace_id']
    logger.debug(f'Stored event exerciseData request with a trace id of { trace_id}')
    

    return NoContent, 201

def get_exercise_data(start_timestamp, end_timestamp):
    session = DB_SESSION()

    start_timestamp_datetime = datetime.datetime.strptime(start_timestamp, "%Y-%m-%d %H:%M:%S.%f")
    end_timestamp_datetime = datetime.datetime.strptime(end_timestamp, "%Y-%m-%d %H:%M:%S.%f")

    readings = session.query(ExerciseData).filter(
        and_(ExerciseData.date_created >= start_timestamp_datetime,
            ExerciseData.date_created < end_timestamp_datetime))

    results_list = []

    for reading in readings:
        results_list.append(reading.to_dict())
    session.close()

    logger.info("Query for Exercise Data from %s to %s returns %d results" % (start_timestamp, end_timestamp, len(results_list)))

    return results_list, 200


def report_user_parameters(body):
    """ Receives a heart rate (pulse) reading """

    session = DB_SESSION()
    up = UserParameters(body['user_id'],
                   body['age'],
                   body['weight'],
                   body['device_name'],
                   body['exercise'],
                   body['reps'],
                   body['met'],
                   body['date_created'],
                   body['recording_id'],
                   body['trace_id'],
                   body['trace_time'])

    session.add(up)

    session.commit()
    session.close()

    trace_id = body['trace_id']
    print('hello')
    logger.debug(f'Stored event userParameters request with a trace id of { trace_id}')

    return NoContent, 201

def get_user_parameters(start_timestamp, end_timestamp):
    session = DB_SESSION()

    start_timestamp_datetime = datetime.datetime.strptime(start_timestamp, "%Y-%m-%d %H:%M:%S.%f")
    end_timestamp_datetime = datetime.datetime.strptime(end_timestamp, "%Y-%m-%d %H:%M:%S.%f")

    readings = session.query(UserParameters).filter(
        and_(UserParameters.date_created >= start_timestamp_datetime,
            UserParameters.date_created < end_timestamp_datetime))

    results_list = []

    for reading in readings:
        results_list.append(reading.to_dict())
    session.close()

    logger.info("Query for User Parameters from %s to %s returns %d results" % (start_timestamp, end_timestamp, len(results_list)))

    return results_list, 200


    
def process_messages():
    """ Process event messages """
    hostname = "%s:%d" % (KAFKA_HOSTNAME, KAFKA_PORT)
    client = KafkaClient(hosts=hostname)
    print('client', client)
    topic = client.topics[str.encode(KAFKA_TOPIC)]
    print('topic', topic)
    # Create a consume on a consumer group, that only reads new messages
    # (uncommitted messages) when the service re-starts (i.e., it doesn't
    # read all the old messages from the history in the message queue).
    consumer = topic.get_simple_consumer(consumer_group=b'event_group', \
                                        reset_offset_on_start=False,\
                                        auto_offset_reset=OffsetType.LATEST)
    disconnected = True
    while disconnected:
        try:
            consumer.consume()
            disconnected = False
            logger.info('Connected to Kafka!')
        except:
            consumer = topic.get_simple_consumer()
            # use either the above method or the following:
            consumer.stop()
            consumer.start()
            disconnected = True
            logger.error("Couldn't connect to Kafka. Trying again...")

    # print('consumer', consumer)
    # This is blocking - it will wait for a new message
    for msg in consumer:
        print('recieved!')
        msg_str = msg.value.decode('utf-8')
        msg = json.loads(msg_str)
        logger.info("Message: %s" % msg)
        payload = msg["payload"]
        if msg["type"] == "exercise_data": # Change this to your event type
            # Store the event1 (i.e., the payload) to the DB
            report_exercise_data(payload)

        elif msg["type"] == "user_parameters": # Change this to your event type
            # Store the event2 (i.e., the payload) to the DB
            report_user_parameters(payload)

            # Commit the new message as being read
        

        consumer.commit_offsets()





app = connexion.FlaskApp(__name__, specification_dir='/storage')
app.add_api("/storage/openapi.yml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    t1 = Thread(target=process_messages)
    t1.setDaemon(True)
    t1.start()
    app.run(port=8090)
