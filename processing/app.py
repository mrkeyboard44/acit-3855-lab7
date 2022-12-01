from unittest import result
import os
import connexion
import yaml
from sqlalchemy import create_engine
from stats import Stats
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


STORAGE_SERVICE_URL = app_config['eventstore']['url']
try:
    DB_ENGINE = create_engine("sqlite:///%s" % SQLITE_DB_HOST)
except:
    create_tables_now(SQLITE_DB_HOST)
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)


def get_stats():
    """GET request function. Returns most recent statistics entry."""
    session = DB_SESSION()

    last_updated_datetime = get_last_updated_from_db()

    readings = session.query(Stats).filter(Stats.last_updated == last_updated_datetime)

    results_list = []

    for reading in readings:
        results_list.append(reading.to_dict())
    session.close()

    if len(results_list) == 0:
        logger.error('Request Failed!')
        return 'Statistics do not exist :(', 404
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
    """Gets most recent datetime value from Stats DB.
    Then requests Storage Service for events since that time."""

    last_dt = get_last_updated_from_db()
    current_time = datetime.datetime.now()

    start_dt_string = date_to_string(last_dt)
    end_dt_string = date_to_string(current_time)
    print(current_time)
    #dt_string example = 2022-10-27%2023%3A56%3A17.575232

    res1 = requests.get(
        f'{STORAGE_SERVICE_URL}/exerciseData?start_timestamp={start_dt_string}&end_timestamp={end_dt_string}'
    )
        
    res2 = requests.get(
        f'{STORAGE_SERVICE_URL}/userParameters?start_timestamp={start_dt_string}&end_timestamp={end_dt_string}'
    )
    
    if res1.status_code != 200:
        logger.error(f'Request from Storage -> exercise_data returned error: {res1.status_code}')
    if res2.status_code != 200:
        logger.error(f'Request from Storage -> user_parameters returned error: {res2.status_code}')
    
    event_count_res1 = len(res1.json())
    event_count_res2 = len(res2.json())
    
    logger.info(f'Amount of events recieved from Storage service: exercise_data: {event_count_res1} user_parameters: {event_count_res2}')
    
    return {'exercise_data': res1.json(), 'user_parameters': res2.json()}


def create_stats():
    """Calculates Stats and returns them."""
    logger.info('TESTING --------------------------------------------------------')
    data = get_data()

    recordings = {}

    recording_paramerters = {}
    
    #Organize Exercise Data into a Dict called 'recordings'
    if data['exercise_data'] != []:
        for event in data['exercise_data']:
            print('event', event)
            if 'trace_id' in event:
                trace_id = event['trace_id']
                logger.debug(f'Stored event exerciseData request with a trace id of {trace_id}')

            if event['recording_id'] not in recordings.keys():
                recordings[event['recording_id']] = {'heart_rate': [event['heart_rate']]}
            else:
                recordings[event['recording_id']]['heart_rate'].append(event['heart_rate'])

    #Organize User Paramters into a Dict called 'recording paramters'
    if data['user_parameters'] != []:
        for event in data['user_parameters']:
            if 'trace_id' in event:
                trace_id = event['trace_id']
                logger.debug(f'Stored event userParameters request with a trace id of {trace_id}')

            if event['recording_id'] not in recording_paramerters.keys():
                recording_paramerters[event['recording_id']] = {'reps': [event['reps']], 'met': [event['met']], 'weight': [event['weight']]}
            else:
                recording_paramerters[event['recording_id']]['reps'].append(event['reps'])
                recording_paramerters[event['recording_id']]['met'].append(event['met'])
                recording_paramerters[event['recording_id']]['weight'].append(event['weight'])

    hr_stats = {}
    activity_stats = {}

    #Calculates the stats from exercise data -> min hr, max hr, total_recordings
    if len(recordings.keys()) != 0:
        for recording in recordings.keys():
            total_recordings = len(recordings[recording]['heart_rate'])
            max_heart_rate = max(recordings[recording]['heart_rate'])
            min_heart_rate = min(recordings[recording]['heart_rate'])
            
            

            hr_stats[recording] = {'total_hr_recordings': total_recordings,
                            'max_heart_rate': max_heart_rate,
                            'min_heart_rate': min_heart_rate}
    
    #Calculates the stats from user parameters -> total reps, calories burned, total recordings.
    if len(recording_paramerters.keys()) != 0:
        for recording in recording_paramerters.keys():
            rec_params = recording_paramerters[recording]
            total_reps = sum(rec_params['reps'])
            total_recordings = len(rec_params['reps'])
            #calorie_rate_per_rep = MET * weight * 7 / 44000 
            # MET (metabolic equivalent) of jump rope is 11.8
            caloric_rate = ( float(rec_params['met'][0]) * float(rec_params['weight'][0]) * 7 ) / 44000
            calories_burned = int(round(float(total_reps) * caloric_rate))

            activity_stats[recording] = {'total_cal_rep_recordings': total_recordings,
                            'total_reps': total_reps,
                            'calories_burned': calories_burned}

    combined_stats = {}

    #Adds the exercise data stats to dict to be combined with the user paramters stats.
    for stat in hr_stats.keys():
        combined_stats[stat] = {'recording_id': stat,
                    'total_recordings': hr_stats[stat]['total_hr_recordings'],
                    'max_heart_rate': hr_stats[stat]['max_heart_rate'],
                    'min_heart_rate': hr_stats[stat]['min_heart_rate'],
                    'total_reps': 'N/A',
                    'calories_burned': 'N/A'}

    #Adds the user parameters stats to the dict if it has the same recording id.
    #Total recordings are combined with the exercise parameters if it exists.
    for stat in activity_stats.keys():
        if stat in combined_stats.keys():
            combined_stats[stat]['total_recordings'] = activity_stats[stat]['total_cal_rep_recordings']
            combined_stats[stat]['total_reps'] = activity_stats[stat]['total_reps']
            combined_stats[stat]['calories_burned'] = activity_stats[stat]['calories_burned']
        else:
            combined_stats[stat] = {'recording_id': stat,
                    'total_recordings': activity_stats[stat]['total_cal_rep_recordings'],
                    'max_heart_rate': 'N/A',
                    'min_heart_rate': 'N/A',
                    'total_reps': activity_stats[stat]['total_reps'],
                    'calories_burned': activity_stats[stat]['calories_burned']}

    #Results are converted to a neat object to be added to the db.
    results = []
    for stat in combined_stats.keys():
        combined_stats[stat]['last_updated'] = datetime.datetime.now()
        results.append(combined_stats[stat])

    for stat in results:
        logger.debug(f'updated statistics values {stat}')

    return results


def populate_stats():
    """ Periodically update stats and saves them to db """

    logger.info("Start Periodic Processing")
    stat_collection = create_stats()
    for stats in stat_collection:
        stats_to_db(stats)
    logger.info("Periodic Processing Has Ended")
    

def init_scheduler():
    """Starts a Statistics Proccess on an interval"""

    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats,
                    'interval',
                    seconds=app_config['scheduler']['period_sec'])
    sched.start()


def stats_to_db(stats):
    """Saves Stats results to DB"""

    session = DB_SESSION()
    stats = Stats(stats['recording_id'],
        stats['total_recordings'],
        stats['total_reps'],
        stats['max_heart_rate'],
        stats['min_heart_rate'],
        stats['calories_burned'],
        stats["last_updated"])
    session.add(stats)
    session.commit()
    session.close()


def stats_from_db():
    """Gets all Stats from table.sqlite and returns them.
    If none are found then default values are returned instead."""

    session = DB_SESSION()
    readings = session.query(Stats)
    results_list = []

    try:
        for reading in readings:
            results_list.append(reading.to_dict())
        if len(results_list) == 0:
            logger.error('Table "stats" is empty...')
            results_list = get_default_values()
    except:
        logger.error('No table found "stats".')
        results_list = get_default_values()
        logger.info('Creating DB...')
        create_tables_now()
        logger.info('Table DB Created!')

    session.close()

    return results_list


def get_default_values():
    """Returns Default values if none are found from DB"""
    results_list = []
    logger.info('Using default values instead.')
    results_list.append({'recording_id': 'c21665a2-230c-4ad8-9d32-3d7f0eb0b3b6', 
                        'total_recordings': 5, 
                        'total_reps': 305, 
                        'max_heart_rate': 180, 
                        'min_heart_rate': 180, 
                        'calories_burned': 100, 
                        'last_updated': datetime.datetime(1980, 10, 30, 20, 12, 8, 795698)})
    return results_list


def get_last_updated_from_db():
    """Returns most recent datetime value found in DB"""
    current_dt = datetime.datetime.now() 
    
    db_stats = stats_from_db()
    last_updated_list = []
    
    for stat in db_stats:
        last_updated_list.append(stat['last_updated'])
    
    last_dt = max(dt for dt in last_updated_list if dt < current_dt)

    logger.info(f'Last updated scanned is {last_dt}')

    return last_dt




app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml", strict_validation=True, validate_responses=True)
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'

if __name__ == "__main__":
    # run our standalone gevent server
    init_scheduler()
    app.run(port=8100, use_reloader=False) 
