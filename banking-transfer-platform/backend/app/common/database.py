from sqlalchemy import create_engine, Column, String, DateTime, func, Numeric, Integer, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
Base = declarative_base()
engine = create_engine("sqlite:///banking_transfer.db")
SessionLocal = sessionmaker(bind=engine)
async def init_db():
    Base.metadata.create_all(bind=engine)
async def check_db_connection():
    pass
