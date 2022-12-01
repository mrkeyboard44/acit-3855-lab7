from unittest import result
import os
import connexion
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

else:
    print("In Dev Environment")
    app_conf_file = "app_conf.yml"
    log_conf_file = "log_conf.yml"
    
with open(app_conf_file, 'r') as f:
    app_config = yaml.safe_load(f.read())
    # KAFKA_HOSTNAME = app_config['events']['hostname']
    SQLITE_DB_HOST = app_config["datastore"]["filename"]

with open(log_conf_file, 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')


RECEIVER_SERVICE_URL = app_config['end_points']['receiver']['url']
STORAGE_SERVICE_URL = app_config['end_points']['storage']['url']
PROCESSING_SERVICE_URL = app_config['end_points']['processing']['url']
AUDIT_LOG_SERVICE_URL = app_config['end_points']['audit_log']['url']

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
         
def date_to_string(date):
    dt_date = date.strftime("%Y-%m-%d")
    dt_time = '%3A'.join(date.strftime("%H-%M-%S").split('-'))
    dt_mlsec = date.strftime("%f")
    dt_string = f"{dt_date}%20{dt_time}.{dt_mlsec}"
    return dt_string

def get_data():
    """Gets most recent datetime value from Health DB.
    Then requests Storage Service for events since that time."""

    last_dt = get_last_updated_from_db()
    current_time = datetime.datetime.now()

    start_dt_string = date_to_string(last_dt)
    end_dt_string = date_to_string(current_time)
    print(current_time)
    #dt_string example = 2022-10-27%2023%3A56%3A17.575232
    res1 = requests.get(
        f'f{RECEIVER_SERVICE_URL}/audit_log/exerciseData?index=0'
    )
    res2 = requests.get(
        f'f{RECEIVER_SERVICE_URL}/audit_log/exerciseData?index=0'
    )
    res3 = requests.get(
        f'{STORAGE_SERVICE_URL}/exerciseData?start_timestamp={start_dt_string}&end_timestamp={end_dt_string}'
    )
    res4 = requests.get(
        f'{STORAGE_SERVICE_URL}/userParameters?start_timestamp={start_dt_string}&end_timestamp={end_dt_string}'
    )
    res5 = requests.get(
        f'f{PROCESSING_SERVICE_URL}/events/stats'
    )
    res6 = requests.get(
        f'f{AUDIT_LOG_SERVICE_URL}/audit_log/exerciseData?index=0'
    )
    res7 = requests.get(
        f'f{AUDIT_LOG_SERVICE_URL}/audit_log/userParameters?index=0'
    )
    
    if res1.status_code != 200:
        logger.error(f'Request from Storage -> exercise_data returned error: {res1.status_code}')
    if res2.status_code != 200:
        logger.error(f'Request from Storage -> user_parameters returned error: {res2.status_code}')
    
    event_count_res1 = len(res1.json())
    event_count_res2 = len(res2.json())
    
    logger.info(f'Amount of events recieved from Storage service: exercise_data: {event_count_res1} user_parameters: {event_count_res2}')
    
    return {'exercise_data': res1.json(), 'user_parameters': res2.json()}


def populate_health():
    """ Periodically update "health" and saves them to db """

    logger.info("Start Periodic Processing")
    health_check_collection = get_data()
    for health in health_check_collection:
        health_to_db(health)
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

    session = DB_SESSION()
    health = Health(health['receiver'],
        health['storage'],
        health['processing'],
        health['audit_log'],
        health["last_updated"])
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
                        'last_updated': datetime.datetime(1980, 10, 30, 20, 12, 8, 795698)})
    return results_list


def get_last_updated_from_db():
    """Returns most recent datetime value found in DB"""
    current_dt = datetime.datetime.now() 
    
    db_health = health_from_db()
    last_updated_list = []
    
    for health_check in db_health:
        last_updated_list.append(health_check['last_updated'])
    
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
