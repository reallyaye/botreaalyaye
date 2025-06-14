from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    telegram_id = Column(String, unique=True, nullable=True)
    password = Column(String)
    name = Column(String)
    last_name = Column(String)
    age = Column(Integer)
    height = Column(Float)
    weight = Column(Float)
    goal = Column(String)
    activity_level = Column(String)
    workout_types = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    workouts = relationship("Workout", back_populates="user")
    goals = relationship("Goal", back_populates="user")

class Workout(Base):
    __tablename__ = "workouts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    workout_type = Column(String)
    duration = Column(Integer)  # в минутах
    calories = Column(Float)
    date = Column(DateTime(timezone=True), server_default=func.now())
    notes = Column(Text, nullable=True)

    user = relationship("User", back_populates="workouts")

class Goal(Base):
    __tablename__ = "goals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    goal_type = Column(String)  # calories, workouts, duration
    target_value = Column(Float)
    current_value = Column(Float, default=0)
    deadline = Column(DateTime(timezone=True), nullable=True)
    is_achieved = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="goals") 