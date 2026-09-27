import os
from datetime import date , datetime
from fastapi import FastAPI,HTTPException, Query
import requests


EVENTS_URL = os.getenv('EVENT_SERVICE_URL','http://localhost:8001')

app = FastAPI(title = "assistant service")

##############################################################################
# Checking Health

@app.get('/',tags=['health'])
def health():
    return {"service":"assistant-service","status":"ok"}


#############################################################################
# Setting Event services URLs here

FETCH_URL = f"{EVENTS_URL}/events/"
NE_URL = f'{EVENTS_URL}/events/next'
UE_URL = f'{EVENTS_URL}/events/upcoming'


##############################################################################
# Requesting Event services here

def fetch_events(URL):
    try:
        # request.get method return response object
        response = requests.get(URL,timeout=3)
        response.raise_for_status() #raises requests.exceptions.HTTPError if status_code >= 400
        return response.json()
    except requests.RequestException:
        raise HTTPException(status_code=503,detail="Event service unavailable")


##############################################################################
# post and get methods that accept the user query

@app.post("/assistant")
def assistant_post(q: str = Query(...,description="Ask about events")):
    return _answer(q)

@app.get("/assistant")
def assistant_get(q: str = Query(...,description="Ask about events")):
    return _answer(q)


def _answer(q: str):
    q_low = q.lower().strip()
    events = fetch_events(FETCH_URL)
    if not events:
        return HTTPException(status_code=404,detail="Events not found")
    for e in events:
        if isinstance(e.get("date"),str):
            try:
                e['_date_obj'] = datetime.strptime(e['date'],"%Y-%m-%d").date()
            except ValueError:
                e['_date_obj'] = None
        else:
            e['_date_obj'] = e.get('date')

    today = date.today()

    # next event 
    if 'next event' in q_low or 'first coming' in q_low:
        next_event = fetch_events(NE_URL)
        if next_event:
            return {"answer":f"Next event is {next_event['title']} in {next_event['city']} on {next_event['date']}"
                    }
    
    # upcoming event
    if 'upcoming' in q_low or 'future events' in q_low:
        e = fetch_events(UE_URL)
        if e:
            return {"answer": f"{len(e)} upcoming event(s)",
                    "events": [{"title":ev['title'],"city":ev['city'],"date":ev['date']} for ev in e]
                    }
    
    # events by city
    if 'in' in q_low:
        idx = q_low.rfind(' in ')
        city = q_low[idx+4:].strip().split("?.,")[0]
        by_city = [e for e in events if e['city'].lower() == city.lower()]
        if not by_city:
            return {"message": f"No events found in {city}"}
        
        return {
            "answer": f"Found {len(by_city)} event(s) in {city}",
            "events": [{"title": e["title"], "date": e['date']} for e in by_city]
        }
    
    # Events on a specific date (YYYY-MM-DD)
    import re
    Date = re.search(r'\b(\d{4}-\d{2}-\d{2})\b',q_low)
    if Date:
        dd = Date.group(1)
        on_date = [e for e in events if e.get('date') == dd]
        if not on_date:
            return {"answer":f"No events scheduled on {dd}"}
        return {
            "answer": f"Found {len(on_date)} event(s) on {dd}",
            "events": [{"title":e['title'],'city':e['city']} for e in on_date]
        }
    
    # default
    return {
        "answer": "try queries like: 'what is the next event?, 'show upcoming events','Events in chennai','Events on 2025-12-10' "
    }
