from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Construct DATABASE_URL if not provided explicitly. In Kubernetes
# we typically expose DB_USER/DB_PASSWORD/DB_HOST/DB_PORT/DB_NAME via
# secrets/config and not a single DATABASE_URL variable. Previously
# the app fell back to sqlite when DATABASE_URL was missing, which
# caused the service to run against an empty sqlite DB in-cluster.
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
	db_user = os.getenv('DB_USER')
	db_password = os.getenv('DB_PASSWORD')
	db_host = os.getenv('DB_HOST', 'localhost')
	db_port = os.getenv('DB_PORT', '5432')
	db_name = os.getenv('DB_NAME')
	if db_user and db_password and db_name:
		# use psycopg2 dialect for Postgres
		DATABASE_URL = f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
	else:
		DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///reports_test.db')

engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()
