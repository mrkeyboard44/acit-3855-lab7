from pykafka import KafkaClient 
import os
from threading import Thread 
import logging
import logging.config
import yaml
import json
import connexion
from flask_cors import CORS, cross_origin

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

logger.info(f"Connecting to Kafka. Hostname:{KAFKA_HOSTNAME}, Port:{KAFKA_PORT}")

def get_exercise_data(index):
    """ Get Exercise Data in History """
    hostname = "%s:%d" % (KAFKA_HOSTNAME, KAFKA_PORT)
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(KAFKA_TOPIC)]

    consumer = topic.get_simple_consumer(reset_offset_on_start=True,
    consumer_timeout_ms=1000)
    logger.info("Retrieving exercise data at index %d" % index)

    try:
        count = 0
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            logger.info("Message: %s" % msg)
            payload = msg["payload"]
            if msg["type"] == "exercise_data":
                if count == index:
                    logger.info("Message: %s" % msg)
                    return payload, 200
                else:
                    count += 1

    except:
        logger.error("No more messages found")
        logger.error("Could not find exercise data at index %d" % index)
    return { "message": "Not Found"}, 404


def get_user_parameters(index):
    """ Get User Parameters Reading in History """
    hostname = "%s:%d" % (KAFKA_HOSTNAME, KAFKA_PORT)
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(KAFKA_TOPIC)]

    consumer = topic.get_simple_consumer(reset_offset_on_start=True,
    consumer_timeout_ms=1000)
    logger.info("Retrieving user parameters at index %d" % index)

    try:
        count = 0
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            payload = msg["payload"]
            
            if msg["type"] == "user_parameters":
                if count == index:
                    logger.info("Message: %s" % msg)
                    return payload, 200
                else:
                    count += 1
    except:
        logger.error("No more messages found")
        logger.error("Could not find user parameters at index %d" % index)
    
    return { "message": "Not Found"}, 404

app = connexion.FlaskApp(__name__, specification_dir='/audit_log')
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'

if __name__ == "__main__":
    t1 = Thread(target=get_exercise_data)
    t1.setDaemon(True)
    t1.start()
    t2 = Thread(target=get_user_parameters)
    t2.setDaemon(True)
    t2.start()
    app.run(port=8110)  