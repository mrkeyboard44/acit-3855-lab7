"""checks data types before being formatted for db query"""
from sqlalchemy import Column, Integer, String, Float
from base import Base


class UserParameters(Base):
    """ User Parameters """

    __tablename__ = "user_parameters"

    id = Column(Integer, primary_key=True)
    user_id = Column(String(250), nullable=False)
    age = Column(Integer, nullable=False)
    weight = Column(Integer, nullable=False)
    device_name = Column(String(250), nullable=False)
    exercise = Column(String(100), nullable=False)
    reps = Column(Integer, nullable=False)
    met = Column(Float, nullable=False)
    recording_id = Column(String(250), nullable=False)
    date_created = Column(String(100), nullable=False)
    trace_id = Column(String(250), nullable=False)
    trace_time = Column(String(100), nullable=False)
    

    def __init__(self, user_id, age, weight, device_name, exercise, reps, met, date_created, recording_id, trace_id, trace_time):
        """ Initializes an user parameters reading """
        self.user_id = user_id
        self.age = age
        self.weight = weight
        self.device_name = device_name
        self.exercise = exercise
        self.reps = reps
        self.met = met
        self.recording_id = recording_id
        self.date_created = date_created
        self.trace_id = trace_id
        self.trace_time = trace_time


    def to_dict(self):
        """ Dictionary Representation of an user parameters reading """
        dict = {}
        dict['id'] = self.id
        dict['user_id'] = self.user_id
        dict['age'] = self.age
        dict['weight'] = self.weight
        dict['device_name'] = self.device_name
        dict['exercise'] = self.exercise
        dict['reps'] = self.reps
        dict['met'] = self.met
        dict['recording_id'] = self.recording_id
        dict['date_created'] = self.date_created
        dict['trace_id'] =  self.trace_id
        dict['trace_time'] = self.trace_time


        return dict
