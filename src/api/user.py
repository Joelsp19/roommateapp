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
    try:
        with db.engine.begin() as connection:
            # Create a new calendar
            calendar_id = connection.execute(
                sqlalchemy.text("""
                                INSERT INTO calendar
                                (created_at, name)
                                VALUES
                                (:created_at, :name)
                                RETURNING id"""),
                                {"created_at": datetime.now(),
                                 "name": f"{new_user.name}'s calendar"}
            ).scalar()

            # Create user
            uid = connection.execute(
                sqlalchemy.text("""
                                INSERT INTO users
                                (name, room_id, calendar_id)
                                VALUES
                                (:name, :room_id, :calendar_id)
                                RETURNING id
                                """),
                                {"calendar_id": calendar_id,
                                 "name": new_user.name,
                                 "room_id": new_user.room_id}
            ).scalar()

        return {"user_id": uid, "calendar_id": calendar_id}
    except Exception as error:
        print(f"Error returned: <<{error}>>")
        return ("Couldn't complete endpoint")

class User(BaseModel):
    name: str
    room_id: int
    points: int

@router.get("/{id}")
def get_user(id: int):
    '''Returns a user given a user_id'''
    try:
        with db.engine.begin() as connection:
            user = connection.execute(
                sqlalchemy.text("SELECT id, name, room_id, points, calendar_id FROM users WHERE id = :user_id"),
                {"user_id": id}
            ).first()
    
        if user != None:
            user_dict = {
                "id": user.id,
                "calendar_id": user.calendar_id if user.calendar_id != None else "User doesn't have a calendar",
                "name": user.name,
                "room_id": user.room_id,
                "points": user.points,
            }
            return user_dict
        else :
            return {"User not found"}
    except Exception as error:
        print(f"Error returned: <<{error}>>")
        return ("Couldn't complete endpoint")

@router.put("/{id}")
def set_user(id: int, name: str | None = None, room_id: int | None = None):
    '''Updates user data'''
    try:
        with db.engine.begin() as connection:
            if(name != None and room_id != None):
                rows = connection.execute(
                    sqlalchemy.text("""UPDATE users SET name = :name, room_id = :room_id
                                    WHERE id = :user_id RETURNING *"""),
                    {"name": name, "room_id": room_id,  "user_id": id }
                )
            elif (name == None and room_id!=None):
                rows = connection.execute(
                    sqlalchemy.text("""UPDATE users SET room_id = :room_id
                                    WHERE id = :user_id RETURNING *"""),
                    {"room_id": room_id,  "user_id": id }
                )
            elif (name != None and room_id == None):
                rows = connection.execute(
                    sqlalchemy.text("""UPDATE users SET name = :name
                                    WHERE id = :user_id RETURNING *"""),
                    {"name": name,  "user_id": id }
                )
            else:
                return "Please pass in some params to update"
              
            if rows.scalar() == None:
                return "Not a valid user ID"
                    
            return {"success": "updated user"}
    except Exception as error:
        print(f"Error returned: <<{error}>>")
        return ("Couldn't complete endpoint - check your room ID")

@router.delete("/{user_id}")
def delete_user(user_id: int):
    '''Deletes a user from the database given a user_id'''
    with db.engine.begin() as connection:
        # Check if user has any remaining splits to pay
        room_id = connection.execute(
                sqlalchemy.text("""
                                SELECT users.room_id
                                FROM users
                                WHERE users.id = :user_id"""),
                                {"user_id": user_id}
        ).scalar()

        splits = connection.execute(
            sqlalchemy.text("""
                            SELECT *
                            FROM split
                            JOIN users ON users.id = split.user_added
                            JOIN room ON room.id = users.room_id
                            WHERE room.id = :room_id
                            """),
                            {"room_id": room_id}
        ).all()
        if splits != []:
            return "You still have some unhandled splits!"

        deleted = connection.execute(
            sqlalchemy.text("""DELETE FROM users
                            WHERE id = :id
                            RETURNING name
                            """),
                            {"id": user_id}
        ).first()
    if deleted == None:
        return {f"No user found of id {user_id}"}
    return {"deleted_user": deleted.name}
