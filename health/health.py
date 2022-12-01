from base import Base
from sqlalchemy import Column, Integer, String, DateTime

class Health(Base):
    """ Getting Health Checks """

    __tablename__ = "health"

    id = Column(Integer, primary_key=True)
    receiver = Column(String(250), nullable=False)
    storage = Column(String(250), nullable=False)
    processing = Column(String(250), nullable=False)
    audit_log = Column(String(250), nullable=False)
    last_update = Column(DateTime, nullable=False)

    def __init__(self, receiver, storage, processing, audit_log, last_update):
        """ Initializes a processing statistics objet """
        self.receiver = receiver
        self.storage = storage
        self.processing = processing
        self.audit_log = audit_log
        self.last_update = last_update

    def to_dict(self):
        """ Dictionary Representation of a statistics """
        dict = {}
        dict['receiver'] = self.receiver
        dict['storage'] = self.storage
        dict['processing'] = self.processing
        dict['audit_log'] = self.audit_log
        dict['last_update'] = self.last_update
        return dict