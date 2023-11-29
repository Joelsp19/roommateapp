from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
from datetime import date
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/room",
    tags=["room"],
    dependencies=[Depends(auth.get_api_key)],
)

class NewRoom(BaseModel):
    room_name: str

@router.post("/")
def add_room(new_room: NewRoom):
    #every time you add a room then you want to create a room calendar
    #code from add_calendar
    calendar_name = new_room.room_name + "calendar"
    with db.engine.begin() as connection:
        calendar_id = connection.execute(
            sqlalchemy.text("INSERT INTO calendar (name) VALUES (:name) RETURNING id"),
            {"name": calendar_name}
        )
        calendar_id = calendar_id.scalar()

        result = connection.execute(
            sqlalchemy.text("INSERT INTO room (room_name, calendar_id) VALUES (:room_name, :calendar_id) RETURNING id"),
            {"room_name": new_room.room_name, "calendar_id": calendar_id}
        )
        room_id = result.scalar()
    return {"room_id": room_id}
    
#update room info
@router.put("/{room_id}")
def update_room(new_room: NewRoom, room_id: int, calendar_id: int = None):
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

#get the room details
@router.get("/{room_id}")
def get_room():
    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text(
            """
            SELECT room_name, name as calendar_name
            FROM room
            JOIN calendar on calendar_id = calendar.id
            WHERE id = :room_id
            """)
        )
        room = result.scalars()

    return {
        "room_name":room.room_name,
        "calendar_id": room.calendar_name
    }


class NewUser(BaseModel):
    room_id: int
    name: str

@router.post("/user")
def add_user(new_user: NewUser):
    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text("INSERT INTO users (name, room_id) VALUES (:name, :room_id) RETURNING id"),
            {"name": new_user.name, "room_id": new_user.room_id}
        )
    return {"success": "ok"}


class User(BaseModel):
    name: str
    room_id: int
    points: int

@router.get("/user/{id}")
def get_user(id: int):
    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text("SELECT * FROM users WHERE id = :user_id"),
            {"user_id": id}
        )
    user = result.first()
    user_dict = {
        "id": user.id,
        "name": user.name,
        "room_id": user.room_id,
        "points": user.points
    }
    return user_dict

@router.put("/user/{id}")
def set_user(id: int, user: User, calendar_id: int = None):
    with db.engine.begin() as connection:
        
        if calendar_id == None:
            result = connection.execute(
                sqlalchemy.text("""UPDATE users SET name = :name, room_id = :room_id, points = :points
                                WHERE id = :user_id"""),
                {"name": user.name, "room_id": user.room_id, "points": user.points, "user_id": id }
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
                sqlalchemy.text("""UPDATE users SET name = :name, room_id = :room_id, points = :points, calendar_id = :calendar_id
                                WHERE id = :user_id"""),
                {"name": user.name, "room_id": user.room_id, "points": user.points, "user_id": id, "calendar_id":calendar_id }
            )

    return {"success": "ok"}

@router.delete("/user/{id}")
def delete_user(id: int):
    with db.engine.begin() as connection:
        connection.execute(
            sqlalchemy.text("""DELETE FROM users
                            WHERE id = :id"""),
                            {"id": id}
        )
    
    return {"success": "ok"}

@router.get("/{room_id}/free_time")
def free_time(room_id: int, date_wanted: date):
    # grab all calendarids associated with user under the room and the room
    # grab all events with these calendarids
    #choose all the rows that the date is between start and end date
    # 4 cases: 
        #if start date before date_wanted then add '00:00:00' as a time
        #if end date after date_wanted: then add '23:59:59' as a time
        #both are not the date_wanted: then add '00:00:00' as a time and '23:59:59' as a time (no free time)
        #both are the date watned: then add the corresponding time from database
    # return all the free times 
    
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
        )

    #use a stack
    #each index will appear twice in the hash table
    #on the second appearance, remove the existing elem
    #if the list is empty then we have free time until the next available time

    list_times = times.all()
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
def get_reward(id: int):
    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text("SELECT * FROM rewards WHERE id = :reward_id"),
            {"reward_id": id}
        )
