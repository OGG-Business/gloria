from sqlalchemy import create_engine, Column, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
Base = declarative_base()
engine = create_engine('sqlite:///test.db')
SessionLocal = sessionmaker(bind=engine)
async def init_db(): pass
async def check_db_connection(): pass
