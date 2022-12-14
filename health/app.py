from unittest import result
import os
import connexion
from connexion import NoContent
import yaml
from sqlalchemy import create_engine
from health import Health
from base import Base
from create_tables import create_tables_now
from sqlalchemy.orm import sessionmaker
import requests
import logging.config
import logging
from apscheduler.schedulers.background import BackgroundScheduler
import datetime

from flask_cors import CORS, cross_origin

if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    app_conf_file = "/config/app_conf.yml"
    log_conf_file = "/config/log_conf.yml"
    test = True

else:
    print("In Dev Environment")
    app_conf_file = "app_conf.yml"
    log_conf_file = "log_conf.yml"
    test = False
    
with open(app_conf_file, 'r') as f:
    app_config = yaml.safe_load(f.read())
    # KAFKA_HOSTNAME = app_config['events']['hostname']
    if test:
        SQLITE_DB_HOST = app_config["datastore"]["filename"]["test"]
    else:
        SQLITE_DB_HOST = app_config["datastore"]["filename"]["dev"]

with open(log_conf_file, 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')


RECEIVER_SERVICE_URL = app_config['end_points']['receiver']['url']
STORAGE_SERVICE_URL = app_config['end_points']['storage']['url']
PROCESSING_SERVICE_URL = app_config['end_points']['processing']['url']
AUDIT_LOG_SERVICE_URL = app_config['end_points']['audit_log']['url']

SERVICE_COLLECTION = {'receiver': RECEIVER_SERVICE_URL,
                    'storage': STORAGE_SERVICE_URL,
                    'processing': PROCESSING_SERVICE_URL,
                    'audit_log': AUDIT_LOG_SERVICE_URL}

DB_ENGINE = create_engine("sqlite:///%s" % SQLITE_DB_HOST)

Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)


def get_health_check():
    """GET request function. Returns most recent health checks entry."""
    session = DB_SESSION()

    last_updated_datetime = get_last_updated_from_db()

    readings = session.query(Health).filter(Health.last_update == last_updated_datetime)

    results_list = []

    for reading in readings:
        results_list.append(reading.to_dict())
    session.close()

    if len(results_list) == 0:
        logger.error('Request Failed!')
        return 'Health Checks do not exist :(', 404
    else:
        logger.debug(results_list[0])
        logger.info('Request Success!')
        return results_list[0], 200


def get_data():
    """Gets most recent datetime value from Health DB.
    Then requests Storage Service for events since that time."""

    last_dt = get_last_updated_from_db()
    current_time = datetime.datetime.now()

    print(current_time)

    responses = {}
    for service, url in SERVICE_COLLECTION.items():
        responses[service] = requests.get(
            f'{url}/health'
        )

    status_dict = {}
    for service, response in responses.items():
        if response.status_code == 200:
            status_dict[service] = 'Running'
            logger.info(f'HEALTH CHECK: {service} is reachable')
        else:
            status_dict[service] = 'Unreachable'
            logger.error(f'HEALTH CHECK: {service} is unreachable')
    status_dict['last_update'] = datetime.datetime.now()
    return status_dict


def populate_health():
    """ Periodically update "health" and saves them to db """

    logger.info("Start Periodic Processing")
    health_check_collection = get_data()
    health_to_db(health_check_collection)
    logger.info("Periodic Processing Has Ended")
    

def init_scheduler():
    """Starts a Health Check Proccess on an interval"""

    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_health,
                    'interval',
                    seconds=app_config['scheduler']['period_sec'])
    sched.start()


def health_to_db(health):
    """Saves health check results to DB"""
    logger.info('Saving update to DB')
    session = DB_SESSION()
    health = Health(health['receiver'],
        health['storage'],
        health['processing'],
        health['audit_log'],
        health["last_update"])
    session.add(health)
    session.commit()
    session.close()


def health_from_db():
    """Gets all health checks from table.sqlite and returns them.
    If none are found then default values are returned instead."""

    session = DB_SESSION()
    readings = session.query(Health)
    results_list = []

    try:
        for reading in readings:
            results_list.append(reading.to_dict())
        if len(results_list) == 0:
            logger.error('Table "health" is empty...')
            results_list = get_default_values()
    except:
        logger.error('No table found "health".')
        results_list = get_default_values()
        logger.info('Creating DB...')
        create_tables_now(SQLITE_DB_HOST)
        logger.info('Table "health" Created!')

    session.close()

    return results_list


def get_default_values():
    """Returns Default values if none are found from DB"""
    results_list = []
    logger.info('Using default values instead.')
    results_list.append({'receiver': 'Running',
                        'storage': 'Running',
                        'processing': 'Running',
                        'audit_log': 'Running', 
                        'last_update': datetime.datetime(1980, 10, 30, 20, 12, 8, 795698)})
    return results_list


def get_last_updated_from_db():
    """Returns most recent datetime value found in DB"""
    current_dt = datetime.datetime.now() 
    
    db_health = health_from_db()
    last_updated_list = []
    
    for health_check in db_health:
        last_updated_list.append(health_check['last_update'])
    
    last_dt = max(dt for dt in last_updated_list if dt < current_dt)

    logger.info(f'Last updated scanned is {last_dt}')

    return last_dt




app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml", base_path='/health', strict_validation=True, validate_responses=True)
if "TARGET_ENV" not in os.environ or os.environ["TARGET_ENV"] != "test":
    CORS(app.app)
    app.app.config['CORS_HEADERS'] = 'Content-Type'

if __name__ == "__main__":
    # run our standalone gevent server
    init_scheduler()
    app.run(port=8120, use_reloader=False) 
