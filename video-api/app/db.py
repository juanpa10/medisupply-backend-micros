from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

DB_URL = os.getenv("DATABASE_URL") 

if not DB_URL:
    host = os.getenv("DB_HOST")
    if host:  
        user = os.getenv("POSTGRES_USER")
        password = os.getenv("POSTGRES_PASSWORD")
        name = os.getenv("POSTGRES_DB")
        port = os.getenv("DB_PORT", "5432")
        if all([user, password, name]):
            DB_URL = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{name}"

if not DB_URL:
    DB_URL = "sqlite:///evidence.db"  
    
engine = create_engine(DB_URL, echo=False, future=True)
#DATABASE_URL = "sqlite:///./evidence.db"

#engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)
Base = declarative_base()
