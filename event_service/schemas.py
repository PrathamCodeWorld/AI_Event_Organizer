from pydantic import BaseModel, Field, EmailStr, field_validator, ConfigDict
from datetime import date

class EventCreate(BaseModel):
    title : str = Field(min_length=1, max_length=200)
    city : str | None = None
    date : date
    organizer : str | None = None
    organizer_email : EmailStr | None = None

   
    @field_validator('title')
    @classmethod
    def title_not_empty(cls,val):
        if not val.strip():
            raise ValueError("Title cannot be empty")
        return val
    
    @field_validator("date")
    @classmethod
    def check_date(cls,val):
        if val < date.today():
            raise ValueError("Date can't be less than today")
        return val
    
class EventUpdate(BaseModel):
    title : str | None = None
    city :  str | None = None
    date : date
    organizer : str | None = None
    organizer_email : EmailStr | None = None

class EventOut(EventCreate):
    id : int
    class Config:
        from_attribute = True # by defauld FastAPI read as dict
                              # it tells Fast API to try obj.key too
    
    # Override the EventCreate method

    @field_validator("date")
    @classmethod
    def check_date(cls, val):
        return val
