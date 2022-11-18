from base import Base
from sqlalchemy import Column, Integer, String, DateTime

class Stats(Base):
    """ Processing Statistics """

    __tablename__ = "stats"

    id = Column(Integer, primary_key=True)
    recording_id = Column(String(250), nullable=False)
    total_recordings = Column(Integer, nullable=False)
    total_reps = Column(Integer, nullable=False)
    max_heart_rate = Column(Integer, nullable=False)
    min_heart_rate = Column(Integer, nullable=False)
    calories_burned = Column(Integer, nullable=False)
    last_updated = Column(DateTime, nullable=False)

    def __init__(self, recording_id, total_recordings, total_reps, max_heart_rate, min_heart_rate, calories_burned, last_updated):
        """ Initializes a processing statistics objet """
        self.recording_id = recording_id
        self.total_recordings = total_recordings
        self.total_reps = total_reps
        self.max_heart_rate = max_heart_rate
        self.min_heart_rate = min_heart_rate
        self.calories_burned = calories_burned
        self.last_updated = last_updated

    def to_dict(self):
        """ Dictionary Representation of a statistics """
        dict = {}
        dict['recording_id'] = self.recording_id
        dict['total_recordings'] = self.total_recordings
        dict['total_reps'] = self.total_reps
        dict['max_heart_rate'] = self.max_heart_rate
        dict['min_heart_rate'] = self.min_heart_rate
        dict['calories_burned'] = self.calories_burned
        dict['last_updated'] = self.last_updated
        return dict