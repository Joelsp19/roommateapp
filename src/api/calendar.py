from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
from datetime import datetime, timezone
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/calendar",
    tags=["calendar"],
    dependencies=[Depends(auth.get_api_key)],
)

class NewCalendar(BaseModel):
    calendar_name: str

@router.post("/")
def add_calendar(new_calendar: NewCalendar):
    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text("INSERT INTO calendar (name) VALUES (:name) RETURNING id"),
            {"name": new_calendar.calendar_name}
        )
    calendar_id = result.scalar()
    return {"calendar_id": calendar_id}

#returns all the calendar information
@router.get("/")
def get_calendars():
    cal_list = []
    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text(
                """            
                SELECT *
                FROM calendar 
                """)
        )
    for calendar in result:
        cal_list.append(
            {
                "id": calendar.id,
                "name": calendar.name
            }
        )
    if len(cal_list) == 0:
        return "No calendars available"
    return cal_list

#updates the calendar information based on calendar
@router.put("/{calendar_id}")
def update_calendar(new_calendar: NewCalendar, calendar_id: int):
    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text(
                """            
                UPDATE calendar
                SET name = :name
                WHERE id = :calendar_id
                """),
            {"name": new_calendar.calendar_name,"calendar_id": calendar_id}
        )
   
    return {"success": "ok"}

#returns all the calendar information for a given calendar
@router.get("/{calendar_id}")
def get_calendar(calendar_id:int):
    cal_list = []
    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text(
                """            
                SELECT *
                FROM calendar
                WHERE id = calendar_id 
                """),
            {"calendar_id": calendar_id}
        )
    for calendar in result:
        cal_list.append(
            {
                "id": calendar.id,
                "name": calendar.name
            }
        )
    if len(cal_list) == 0:
        return "No calendars available"
    return cal_list




class NewEvent(BaseModel):
    name: str
    description: str
    start: datetime = datetime.now(timezone.utc)
    end: datetime = datetime.now(timezone.utc)


#returns all the events for a specific calendar
@router.get("/{calendar_id}/event")
def get_events(calendar_id: int):
    events = []
    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text(
                """
                SELECT *
                FROM event
                WHERE calendar_id = :calendar_id

                """),
                {"calendar_id": calendar_id})
        
    for event in result:
        events.append({
            "id": event.id,
            "name": event.name,
            "description": event.description,
            "start": event.start_time,
            "end": event.end_time,
            "calendar_id": event.calendar_id
        })

    return events


#adds an event to the calendar
@router.post("/{calendar_id}/event")
def add_event(new_event: NewEvent, calendar_id: int):
    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO event (name, description, start_time, end_time, calendar_id)
                VALUES (:name, :description, TIMESTAMP :start, TIMESTAMP :end, :calendar_id)
                """
            ),
            {
                "name": new_event.name,
                "description" : new_event.description,
                "start": new_event.start.strftime("%Y-%m-%d %H:%M:%S"),
                "end": new_event.end.strftime("%Y-%m-%d %H:%M:%S"),
                "calendar_id": calendar_id,
            },
        )

    return {"success": "ok"}

#updates an event in the calendar
@router.put("/{calendar_id}/event/{event_id}")
def update_event(new_event: NewEvent, calendar_id: int, event_id: int):
    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text(
                """
               UPDATE event
               SET name=:name, description=:description, start_time=TIMESTAMP :start, end_time=TIMESTAMP :end, calendar_id=:calendar_id
               WHERE id = :event_id
                """),
            {"name": new_event.name, "description": new_event.description, "start": new_event.start.strftime("%Y-%m-%d %H:%M:%S"),
                "end": new_event.end.strftime("%Y-%m-%d %H:%M:%S"), "event_id": event_id, "calendar_id": calendar_id}
        )

    return {"success": "ok"}

#returns a specific event for a specific calendar
@router.get("/{calendar_id}/event/{event_id}")
def get_event(calendar_id: int, event_id: int):
    events = []
    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text(
                """
                SELECT *
                FROM event
                WHERE calendar_id = :calendar_id and id=:event_id
                """),
                {"calendar_id": calendar_id, "event_id": event_id})
        
    for event in result:
        events.append({
            "id": event.id,
            "name": event.name,
            "description": event.description,
            "start": event.start_time,
            "end": event.end_time,
            "calendar_id": event.calendar_id
        })

    return events

@router.delete("/{calendar_id}/event/{event_id}")
def delete_event(calendar_id: int, event_id: int):
    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text(
                """
                DELETE FROM event
                WHERE calendar_id = :calendar_id and id=:event_id
                """),
                {"calendar_id": calendar_id, "event_id": event_id})
        
    return {"success": "ok"}



