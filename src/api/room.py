from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
from datetime import date
import sqlalchemy
from sqlalchemy import func, extract
from src import database as db
from datetime import datetime

router = APIRouter(
    prefix="/rooms",
    tags=["rooms"],
    dependencies=[Depends(auth.get_api_key)],
)

class NewRoom(BaseModel):
    room_name: str

@router.post("/")
def add_room(new_room: NewRoom):
    '''Adds a room to the database'''
    #every time you add a room then you want to create a room calendar
    #code from add_calendar
    calendar_name = new_room.room_name + "calendar"
    with db.engine.begin() as connection:
        calendar_id = connection.execute(
            sqlalchemy.text("INSERT INTO calendar (name) VALUES (:name) RETURNING id"),
            {"name": calendar_name}
        )
        calendar_id = calendar_id.scalar()

        room_id = connection.execute(
            sqlalchemy.text("INSERT INTO room (room_name, calendar_id) VALUES (:room_name, :calendar_id) RETURNING id"),
            {"room_name": new_room.room_name, "calendar_id": calendar_id}
        ).scalar()
       
    return {"room_id": room_id}

@router.put("/{room_id}")
def update_room(new_room: NewRoom, room_id: int, calendar_id: int = None):
    '''Update room data given a room_id'''
    #check if the given calendar_id is a valid calendar_id
    #update the roomname and calendar if it is

    with db.engine.begin() as connection:

        if calendar_id == None:
            result = connection.execute(
                sqlalchemy.text(
                """
                UPDATE room
                SET room_name = :room_name
                WHERE id = :room_id
                """),
                {"room_name": new_room.room_name, "room_id": room_id}
            )
        else:
            valid_calendar_id= connection.execute(
                sqlalchemy.text(
                """
                SELECT id
                FROM calendar
                WHERE id = :calendar_id
                """),
                {"calendar_id": calendar_id}
            )

            if valid_calendar_id.scalar() == None:
                return "Not a valid calendar id"

            result = connection.execute(
                sqlalchemy.text(
                """
                UPDATE room
                SET room_name = :room_name, calendar_id = :calendar_id
                WHERE id = :room_id
                """),
                {"room_name": new_room.room_name, "calendar_id": calendar_id, "room_id": room_id}
            )


    if result != None:
        return {"success": "ok"}
    else:
        return {"success": "not_ok"}

@router.get("/{room_id}")
def get_room(room_id: int):
    '''Returns specific room data given a room_id'''
    with db.engine.begin() as connection:
        room = connection.execute(
            sqlalchemy.text(
            """
            SELECT room_name, name as calendar_name
            FROM room
            LEFT JOIN calendar on calendar_id = calendar.id
            WHERE room.id = :room_id
            """),  {"room_id": room_id}
        ).first()

    return {
        "room_name":room.room_name if room.room_name != None else "No associated room name",
        "calendar_id":  room.calendar_name if room.calendar_name != None else "No associated calendar"
    }

@router.get("/{room_id}/users")
def get_roommmates(room_id: int):
    '''Given a room_id, returns a list of user ids living in the room'''
    with db.engine.begin() as connection:
        roommates = connection.execute(
            sqlalchemy.text(
                """
                SELECT id
                FROM users
                WHERE room_id = :room_id
                """
            ),
            {"room_id": room_id}
        ).all()
    
    roommate_list = [roommate[0] for roommate in roommates]
    return roommate_list

@router.get("/{room_id}/free_time")
def get_free_times(room_id: int, date_wanted: date):
    '''
    Grab all calendar ids associated with user under the room and the room
    Grab all events with these calendar ids
    Choose all the rows that the date is between start and end date
    4 cases:
        If start date before date_wanted: then add '00:00:00' as a time
        If end date after date_wanted: then add '23:59:59' as a time
        If both are not the date_wanted: then add '00:00:00' as a time and '23:59:59' as a time (no free time)
        If both are the date_wanted: then add the corresponding time from database
    Return all the free times
    '''

    with db.engine.begin() as connection:
        list = []
        times = connection.execute(
            sqlalchemy.text(
            """
            WITH calendars as
            (
                SELECT calendar_id
                FROM(
                SELECT calendar_id
                FROM room
                WHERE id = :room_id
                union
                SELECT calendar_id
                FROM users
                WHERE room_id = :room_id
            ) as sub
            )
            SELECT *
            FROM(
            SELECT calendar_id || ' ' || id AS id,
            CASE
                WHEN DATE(start_time) != :date THEN '00:00:00'
                ELSE TO_CHAR(start_time, 'HH24:MI:SS')
            END as time
            FROM event
            WHERE calendar_id in (
                SELECT calendar_id
                FROM calendars
            ) and :date BETWEEN DATE(start_time) and DATE(end_time)
            union
            SELECT calendar_id || ' ' || id AS id,
            CASE
                WHEN DATE(end_time) != :date THEN '23:59:59'
                ELSE TO_CHAR(end_time, 'HH24:MI:SS')
            END as time
            FROM event
            WHERE calendar_id in (
                SELECT calendar_id
                FROM calendars
            ) and :date BETWEEN DATE(start_time) and DATE(end_time)
            ) as sub
            ORDER BY time
            """),
            {"room_id": room_id, "date": date_wanted.strftime("%Y/%m/%d")}
        ).all()

    #use a stack
    #each index will appear twice in the hash table
    #on the second appearance, remove the existing elem
    #if the list is empty then we have free time until the next available time

    list_times = times
    print(list_times)
    ih = []
    if len(list_times)>1:
        if(list_times[0].time != '00:00:00'):
            list.append(('00:00:00',list_times[0].time))
        ih.append(list_times[0].id)

    for i in range(1,len(list_times)):
        if list_times[i].id not in ih:
            ih.append(list_times[i].id)
        else:
            ih.remove(list_times[i].id)
        if len(ih) == 0:
            if (i == len(list_times)-1):
                if list_times[i].time!='23:59:59':
                    list.append((list_times[i].time,'23:59:59'))
            else:
                list.append((list_times[i].time,list_times[i+1].time))

    if len(list) == 0:
        return "You have no free time today :("
    return list

@router.post("/reward")
def get_reward(room_id: int):
    '''Adds reward event to user's calendar for user with the most points
    at the end of the month'''
    with db.engine.begin() as connection:
        res = connection.execute(
            sqlalchemy.text("SELECT * FROM users WHERE room_id = :room_id"),
            {"room_id": room_id}
        )
        users = []
        for row in res:
            users.append(row.id)

        currentMonth = datetime.now().month
        currentYear = datetime.now().year


        points = []
        for user in users:
            total = connection.execute(
                sqlalchemy.text("""
                    SELECT COALESCE(SUM(points), 0) FROM chores WHERE assigned_user_id = :user_id
                    and extract(MONTH FROM created_at) = :month
                    and extract(YEAR FROM  created_at) = :year"""),
                {"user_id": user, "month": currentMonth, "year": currentYear}
            ).scalar()
            print("total", total)
            points.append(total)

        print("test")
        print(points)
        max_user = users[points.index(max(points))]

        maxname = connection.execute(
            sqlalchemy.text("SELECT name FROM users WHERE id = :user_id"),
            {"user_id": max_user}
        ).scalar()

        cal = connection.execute(
            sqlalchemy.text("SELECT calendar_id FROM room WHERE id = :room_id"),
            {"room_id": room_id}
        ).scalar()
        if cal is None:
            calid = connection.execute(
                sqlalchemy.text("INSERT INTO calendar (name) VALUES (:calendar_name) RETURNING id"),
                {"calendar_name": "Room " + str(room_id) + "'s Calendar"}
            )
            cal = calid.fetchone()[0]

        connection.execute(
            sqlalchemy.text("INSERT INTO event (calendar_id, name, description, start_time, end_time) VALUES (:calendar_id, :name, :description, :start_time, :end_time)"),
            {"calendar_id": cal, "name": "Reward for " + str(maxname),
             "description": "Reward to be completed by other roommates",
             "start_time": datetime.now(), "end_time": datetime.now()}
        )

    return {"success": "ok"}
