from sqlalchemy import Column, Integer, Text, DateTime, Numeric

from app.db import Base

class Car(Base):
    __tablename__ = "cars_info"

    id = Column(Integer, primary_key=True)
    name = Column(Text)
    description = Column(Text)
    model = Column(Integer)
    posted_at = Column(DateTime)
    image_url = Column(Text)
    price = Column(Numeric)
    status = Column(Text)
    mileage = Column(Integer)
    location = Column(Text)
    country = Column(Text)
