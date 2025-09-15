from sqlalchemy import Column, String, DateTime
from database import Base
import datetime

class Session(Base):
    __tablename__ = "sessions"
    user_id = Column(String, primary_key=True)
    device_id = Column(String, primary_key=True)
    device_name = Column(String)
    platform = Column(String)
    ip_address = Column(String)
    last_used = Column(DateTime, default=datetime.datetime.utcnow)
