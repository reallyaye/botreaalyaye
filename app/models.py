import datetime
from sqlalchemy import Table, Column, Integer, String, DateTime
from app.services.db import metadata

users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("email", String, unique=True, index=True, nullable=False),
    Column("hashed_password", String, nullable=False),
    Column("created_at", DateTime, default=datetime.datetime.utcnow),
)
