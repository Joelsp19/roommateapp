from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
from datetime import date
import sqlalchemy
from sqlalchemy import func, extract
from src import database as db
from datetime import datetime

router = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[Depends(auth.get_api_key)],
)

class NewUser(BaseModel):
    room_id: int
    name: str

@router.post("/")
def add_user(new_user: NewUser):
    '''Add a user to the database'''
    with db.engine.begin() as connection:
        id = connection.execute(
            sqlalchemy.text("INSERT INTO users (name, room_id) VALUES (:name, :room_id) RETURNING id"),
            {"name": new_user.name, "room_id": new_user.room_id}
        )

    uid = id.scalar()
    return {"user_id": uid}


class User(BaseModel):
    name: str
    room_id: int
    points: int

@router.get("/{id}")
def get_user(id: int):
    '''Returns a user given a user_id'''
    with db.engine.begin() as connection:
        user = connection.execute(
            sqlalchemy.text("SELECT id, name, room_id, points FROM users WHERE id = :user_id"),
            {"user_id": id}
        ).first()
   
    if user != None:
        user_dict = {
            "id": user.id,
            "name": user.name,
            "room_id": user.room_id,
            "points": user.points
        }
        return user_dict
    else :
        return {"User not found"}
    

@router.put("/{id}")
def set_user(id: int, user: User, calendar_id: int = None):
    '''Updates user data'''
    with db.engine.begin() as connection:
        if calendar_id == None:
            connection.execute(
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

            connection.execute(
                sqlalchemy.text("""UPDATE users SET name = :name, room_id = :room_id, points = :points, calendar_id = :calendar_id
                                WHERE id = :user_id"""),
                {"name": user.name, "room_id": user.room_id, "points": user.points, "user_id": id, "calendar_id":calendar_id }
            )

    return {"success": "ok"}

@router.delete("/{id}")
def delete_user(id: int):
    '''Deletes a user from the database given a user_id'''
    with db.engine.begin() as connection:
        deleted = connection.execute(
            sqlalchemy.text("""DELETE FROM users
                            WHERE id = :id
                            RETURNING name
                            """),
                            {"id": id}
        ).first()
    if deleted == None:
        return {"deleted_user": f"No user found of id {id}"}
    return {"deleted_user": deleted.name}
