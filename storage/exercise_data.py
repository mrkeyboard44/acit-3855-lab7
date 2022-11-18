from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime


class ExerciseData(Base):
    """ Exercise Data """

    __tablename__ = "exercise_data"

    id = Column(Integer, primary_key=True)
    user_id = Column(String(250), nullable=False)
    device_name = Column(String(250), nullable=False)
    heart_rate = Column(Integer, nullable=False)
    date_created = Column(DateTime(), nullable=False)
    recording_id = Column(String(250), nullable=False)
    trace_id = Column(String(250), nullable=False)
    trace_time = Column(String(100), nullable=False)
    
    def __init__(self, user_id, device_name, heart_rate, date_created, recording_id, trace_id, trace_time):
        """ Initializes an exercise data reading """
        self.user_id = user_id
        self.device_name = device_name
        self.heart_rate = heart_rate
        self.date_created = date_created
        self.recording_id = recording_id
        self.trace_id = trace_id
        self.trace_time = trace_time
        
    def to_dict(self):
        """ Dictionary Representation of an exercise data reading """
        dict = {}
        dict['id'] = self.id
        dict['user_id'] = self.user_id
        dict['device_name'] = self.device_name
        dict['heart_rate'] = self.heart_rate
        dict['recording_id'] = self.recording_id
        dict['date_created'] = self.date_created
        dict['trace_id'] =  self.trace_id
        dict['trace_time'] = self.trace_time

        return dict
