from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = 'sqlite:///events_db'

engine = create_engine(DATABASE_URL, connect_args= {'check_same_thread': False})

session = sessionmaker(bind=engine)

Base = declarative_base()

def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()