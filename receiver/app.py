from datetime import datetime
import json
import uuid
from connexion import NoContent
import connexion    
import os
import yaml
import logging
import logging.config
import datetime
from pykafka import KafkaClient 

MAX_EVENTS = 10
EVENT_FILE = 'events.json'

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())
    KAFKA_HOSTNAME = app_config['events']['hostname']
    KAFKA_PORT = app_config['events']['port']
    KAFKA_TOPIC = app_config['events']['topic']

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

logger.info(f"Connecting to Kafka. Hostname:{KAFKA_HOSTNAME}, Port:{KAFKA_PORT}")

def report_exercise_data(body):
    client = KafkaClient(hosts=f'{KAFKA_HOSTNAME}:{KAFKA_PORT}')
    topic = client.topics[str.encode(KAFKA_TOPIC)]
    producer = topic.get_sync_producer()

    date_created = str(datetime.datetime.now())

    
    trace_time = str(datetime.datetime.now())
    trace_id = str(uuid.uuid1())
   
    payload = {'user_id':body['user_id'],
            'device_name': body['device_name'], 
            'heart_rate': body['heart_rate'],
            'date_created': date_created,
            'recording_id': body['recording_id'],
            'trace_time': trace_time,
            'trace_id': trace_id}

    #write_to_json(payload)
    # res = requests.post('http://localhost:8090/exerciseData', json=payload)

    msg = { "type": "exercise_data",
        "datetime" : datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "payload": payload }
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))
    
    return NoContent, 201


def report_user_parameters(body):
    client = KafkaClient(hosts=f'{KAFKA_HOSTNAME}:{KAFKA_PORT}')
    topic = client.topics[str.encode(KAFKA_TOPIC)]
    producer = topic.get_sync_producer()

    date_created = str(datetime.datetime.now())
    trace_time = str(datetime.datetime.now())
    trace_id = str(uuid.uuid1())

    payload = {'user_id':body['user_id'],
        'age':body['age'],
        'weight': body['weight'],
        'device_name': body['device_name'],
        'exercise':body['exercise'],
        'reps':body['reps'],
        'met':body['met'],
        'date_created': date_created,
        'recording_id': body['recording_id'],
        'trace_time': trace_time,
        'trace_id': trace_id}

    msg = { "type": "user_parameters",
        "datetime" : datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "payload": payload }
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))

    return NoContent, 201


def request_check_success(vars, body):
    for var in body:
        if var not in vars:
            return False
    return True


def write_to_json(payload):

    if EVENT_FILE  not in os.listdir():
        with open(EVENT_FILE, 'w') as f:
            f.close()
    
    readings = []
    with open(EVENT_FILE) as file:
        try:
            readings = json.load(file)
        except:
            readings = []

    with open(EVENT_FILE, 'w') as file:
        if len(readings) > 10:
            readings.pop(0)
        readings.append({"received_timestamp":str(datetime.now()), "request_data":payload})
        json.dump(readings, file, indent=2)



options = {"swagger_ui_config": True}
app = connexion.FlaskApp(__name__, specification_dir='', options=options)
app.add_api("openapi.yml", strict_validation=True, validate_responses=True) 

if __name__ == "__main__":
    app.run(port=8070)
