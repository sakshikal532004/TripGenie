from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text

from backend.database.database import Base


class User(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False)


class Trip(Base):

    __tablename__ = "trips"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    destination = Column(String(100), nullable=False)
    duration_days = Column(Integer, nullable=False)
    travelers = Column(Integer, nullable=False)
    budget = Column(Float, nullable=False)


class Activity(Base):

    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)

    trip_id = Column(
        Integer,
        ForeignKey("trips.id"),
        nullable=False
    )

    day = Column(Integer, nullable=False)
    time = Column(String(50), nullable=False)
    activity = Column(Text, nullable=False)
    estimated_cost = Column(Float, nullable=False)