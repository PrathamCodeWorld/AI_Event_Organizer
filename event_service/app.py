import os
from datetime import datetime, timedelta, date
import requests
from fastapi import FastAPI, HTTPException, Depends
from event_service.config import session, get_db
from event_service.models import Event
from event_service.schemas import EventCreate, EventOut, EventUpdate

app = FastAPI(title='Event Service')

NOTIFY_URL = os.getenv('NOTIFICATION_SERVICE_URL','http://localhost:8004')


##############################################################################
# Checking Health

@app.get('/',tags=['health'])
async def health():
    return {"service":"event service","status":"ok"}


##############################################################################
# Create

@app.post('/events/',response_model=EventOut)
async def create_event(event: EventCreate, db: session = Depends(get_db)):
    new_event = Event(
                title = event.title,
                date = event.date,
                organizer = event.organizer,
                city = event.city,
                organizer_email = event.organizer_email
                )
    
    db.add(new_event)
    db.commit()
    db.refresh(new_event)

    # Fire and forget nofity (ignore failures)
    try:
        requests.post(f"{NOTIFY_URL}/notify/event-created",json={
            "id": new_event.id,
            "title": event.title,
            "city": new_event.city,
            "date": new_event.date,
            "organizer": new_event.organizer,
            "organizer_email": new_event.organizer_email
        }, timeout=2)
    except Exception:
        pass

    return new_event

##############################################################################
# Upcoming events

@app.get('/events/upcoming',response_model=list[EventOut])
async def upcoming_events(db:session = Depends(get_db)):
    today_date = date.today()
    events = db.query(Event).filter(Event.date >= today_date).order_by(Event.date).all()
    if not events:
        raise HTTPException(status_code=204,detail="no upcoming events")
    return events

##############################################################################
# Next Event

@app.get('/events/next',response_model=EventOut)
async def next_event(db:session = Depends(get_db)):
    today_date = date.today()
    events = db.query(Event).filter(Event.date >= today_date).order_by(Event.date.asc()).first()
    if not events:
        raise HTTPException(status_code=404,detail="no upcoming events")
    return events


##############################################################################
# Today events

@app.get('/events/today',response_model=list[EventOut])
async def today_events(db:session = Depends(get_db)):
    today_date = date.today()
    events = db.query(Event).filter(Event.date == today_date).order_by(Event.date.asc()).all()
    if not events:
        raise HTTPException(status_code=404,detail="no events planned today")
    return events


##############################################################################
# Read

# Read all
@app.get('/events/',response_model=list[EventOut])
async def list_events(db: session = Depends(get_db)):
    events = db.query(Event).order_by(Event.date).all() # give data in ascending order
    return events


# Read one
@app.get('/events/{event_id}',response_model=EventOut)
async def get_event(event_id : int, db: session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404,detail="Event not found")
    return event


##############################################################################
# Update

@app.put('/events/change/{event_id}',response_model=EventOut)
async def udpate_events(event_id: int , event: EventUpdate, db: session = Depends(get_db)):
    oldevent = db.query(Event).filter(Event.id == event_id).first()
    if not oldevent:
        raise HTTPException(status_code=404,detail="Event not found")

    if event.title:
        oldevent.title = event.title
    elif event.city:
        oldevent.city = event.city
    elif event.date:
        oldevent.date = event.date
    elif event.organizer:
        oldevent.organizer = event.organizer
    elif event.organizer_email:
        oldevent.organizer_email = event.organizer_email

    db.commit()
    db.refresh(oldevent)
    return oldevent


##############################################################################
# Delete

@app.delete('/events/cancel/{event_id}')
async def delete_events(event_id : int, db:session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404,detail="Event not found")
    db.delete(event)
    db.commit()
    return {"message":f"Event {event_id} deleted"}




