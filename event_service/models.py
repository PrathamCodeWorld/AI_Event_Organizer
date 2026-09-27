from event_service.config import Base, engine
from sqlalchemy import String,Integer,Column,Date

class Event(Base):
    __tablename__ = "events"

    id = Column("id",Integer,primary_key=True,index=True)
    title = Column("title",String(100),nullable=False,index=True)
    date = Column("date",Date,nullable=False)
    organizer = Column("organizer",String(100),nullable=False)
    city = Column("city",String(15),nullable=False)
    organizer_email = Column('organizer_email',String(100),nullable=False)

Base.metadata.create_all(bind=engine)





