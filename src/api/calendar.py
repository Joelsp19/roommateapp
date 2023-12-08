from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
from datetime import datetime, timezone
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/calendars",
    tags=["calendars"],
    dependencies=[Depends(auth.get_api_key)],
)

class NewCalendar(BaseModel):
    calendar_name: str

# @router.post("/")
# def add_calendar(new_calendar: NewCalendar):
#     '''Add a calendar to the database'''
#     try:
#         with db.engine.begin() as connection:
#             calendar_id = connection.execute(
#                 sqlalchemy.text("INSERT INTO calendar (name) VALUES (:name) RETURNING id"),
#                 {"name": new_calendar.calendar_name}
#             ).scalar()

#         return {"calendar_id": calendar_id}
#     except Exception as error:
#         print(f"Error returned: <<{error}>>")
#         return ("Couldn't complete endpoint")

@router.get("/room/{room_id}")
def get_calendars(room_id: int):
    '''Given a room id, returns all the calendars in the room'''
    cal_list = []
    try:
        with db.engine.begin() as connection:
            calendars = connection.execute(
                sqlalchemy.text(
                    """            
                    SELECT calendar.id, calendar.name
                    FROM calendar
                    LEFT JOIN users ON users.calendar_id = calendar.id
                    LEFT JOIN room ON room.calendar_id = calendar.id
                    WHERE users.room_id = :room_id OR room.id = :room_id
                    """),
                    {"room_id": room_id}
            ).all()
        print(calendars)
        for calendar in calendars:
            cal_list.append(
                {
                    "id": calendar.id,
                    "calendar_name": calendar.name
                }
            )
        if len(cal_list) == 0:
            return "No calendars available"
        return cal_list
    except Exception as error:
        print(f"Error returned: <<{error}>>")
        return ("Couldn't complete endpoint")

@router.put("/{calendar_id}")
def update_calendar(new_calendar: NewCalendar, calendar_id: int):
    '''Updates the calendar information based on calendar'''
    try:
        with db.engine.begin() as connection:
            rows = connection.execute(
                sqlalchemy.text(
                    """            
                    UPDATE calendar
                    SET name = :name
                    WHERE id = :calendar_id
                    RETURNING *
                    """),
                {"name": new_calendar.calendar_name,"calendar_id": calendar_id}
            )
            if rows.scalar() == None:
                return "Not a valid ID"
          
    
        return {"success": "ok"}
    except Exception as error:
        print(f"Error returned: <<{error}>>")
        return ("Couldn't complete endpoint")

@router.get("/{calendar_id}")
def get_calendar(calendar_id:int):
    '''Returns all the calendar information for a given calendar'''
    cal_list = []
    try:
        with db.engine.begin() as connection:
            calendars = connection.execute(
                sqlalchemy.text(
                    """            
                    SELECT id, name
                    FROM calendar
                    WHERE id = :calendar_id 
                    """),
                {"calendar_id": calendar_id}
            )
        for calendar in calendars:
            cal_list.append(
                {
                    "id": calendar.id,
                    "name": calendar.name
                }
            )
        if len(cal_list) == 0:
            return "No calendars available"
        return cal_list
    except Exception as error:
        print(f"Error returned: <<{error}>>")
        return ("Couldn't complete endpoint")

@router.delete("/{calendar_id}")
def delete_calendar(calendar_id: int):
    '''Deletes a calendar fron the database'''
    try:
        with db.engine.begin() as connection:
            connection.execute(
                sqlalchemy.text(
                    """
                    DELETE FROM calendar
                    WHERE id = :calendar_id
                    """),
                    {"calendar_id": calendar_id}
            )
        return {"success": "ok"}
    except Exception as error:
        print(f"Error returned: <<{error}>>")
        return ("Couldn't complete endpoint")

class NewEvent(BaseModel):
    name: str
    description: str
    start: datetime = datetime.now(timezone.utc)
    end: datetime = datetime.now(timezone.utc)


@router.get("/{calendar_id}/event")
def get_events(calendar_id: int):
    '''Returns all the events for a specific calendar'''
    events = []
    try:
        with db.engine.begin() as connection:
            events_list = connection.execute(
                sqlalchemy.text(
                    """
                    SELECT *
                    FROM event
                    WHERE calendar_id = :calendar_id

                    """),
                    {"calendar_id": calendar_id})
            
        for event in events_list:
            events.append({
                "id": event.id,
                "name": event.name,
                "description": event.description,
                "start": event.start_time,
                "end": event.end_time,
                "calendar_id": event.calendar_id
            })

        return events
    except Exception as error:
        print(f"Error returned: <<{error}>>")
        return ("Couldn't complete endpoint")


@router.post("/{calendar_id}/event")
def add_event(new_event: NewEvent, calendar_id: int):
    '''Adds an event to the calendar'''
    if new_event.start.strftime("%Y-%m-%d %H:%M:%S") > new_event.end.strftime("%Y-%m-%d %H:%M:%S"):
        return "The end time is earlier than the start time. Please try again"
    try:
        with db.engine.begin() as connection:
            connection.execute(
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
    except Exception as error:
        print(f"Error returned: <<{error}>>")
        return ("Couldn't complete endpoint")

@router.put("/{calendar_id}/event/{event_id}")
def update_event(new_event: NewEvent, calendar_id: int, event_id: int):
    '''Updates an event in the calendar'''
    try:
        with db.engine.begin() as connection:
            rows = connection.execute(
                sqlalchemy.text(
                    """
                UPDATE event
                SET name=:name, description=:description, start_time=TIMESTAMP :start, end_time=TIMESTAMP :end, calendar_id=:calendar_id
                WHERE id = :event_id
                RETURNING *
                    """),
                {"name": new_event.name, "description": new_event.description, "start": new_event.start.strftime("%Y-%m-%d %H:%M:%S"),
                    "end": new_event.end.strftime("%Y-%m-%d %H:%M:%S"), "event_id": event_id, "calendar_id": calendar_id}
            )
            if rows.scalar() == None:
                return "Not a valid ID"
          

        return {"success": "ok"}
    except Exception as error:
        print(f"Error returned: <<{error}>>")
        return ("Couldn't complete endpoint")

@router.get("/{calendar_id}/event/{event_id}")
def get_event(calendar_id: int, event_id: int):
    '''Returns a specific event for a specific calendar'''
    events = []
    try:
        with db.engine.begin() as connection:
            events = connection.execute(
                sqlalchemy.text(
                    """
                    SELECT *
                    FROM event
                    WHERE calendar_id = :calendar_id and id=:event_id
                    """),
                    {"calendar_id": calendar_id, "event_id": event_id})

        specific_event = [] 
        for event in events:
            specific_event.append({
                "id": event.id,
                "name": event.name,
                "description": event.description,
                "start": event.start_time,
                "end": event.end_time,
                "calendar_id": event.calendar_id
            })

        return specific_event
    except Exception as error:
        print(f"Error returned: <<{error}>>")
        return ("Couldn't complete endpoint")

@router.delete("/{calendar_id}/event/{event_id}")
def delete_event(calendar_id: int, event_id: int):
    '''Deletes an event based on calendar and event ids'''
    try:
        with db.engine.begin() as connection:
            deleted = connection.execute(
                sqlalchemy.text(
                    """
                    DELETE FROM event
                    WHERE calendar_id = :calendar_id and id=:event_id
                    RETURNING *
                    """),
                    {"calendar_id": calendar_id, "event_id": event_id}).first()
            
            
        return {"deleted_event": deleted.name}
    except Exception as error:
        print(f"Error returned: <<{error}>>")
        return ("Couldn't complete endpoint")
