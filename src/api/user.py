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
            id = connection.execute(
                sqlalchemy.text("INSERT INTO users (name, room_id) VALUES (:name, :room_id) RETURNING id"),
                {"name": new_user.name, "room_id": new_user.room_id}
            )

            uid = id.scalar()

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

            connection.execute(
                sqlalchemy.text("""
                                UPDATE users
                                SET calendar_id = :calendar_id
                                WHERE
                                id = :uid
                                """),
                                {"calendar_id": calendar_id,
                                 "uid": uid}
            )

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
    except Exception as error:
        print(f"Error returned: <<{error}>>")
        return ("Couldn't complete endpoint")

@router.put("/{id}")
def set_user(id: int, user: User, calendar_id: int = None):
    '''Updates user data'''
    try:
        with db.engine.begin() as connection:
            if calendar_id == None:
                    rows = connection.execute(
                        sqlalchemy.text("""UPDATE users SET name = :name, room_id = :room_id, points = :points
                                        WHERE id = :user_id RETURNING *"""),
                        {"name": user.name, "room_id": user.room_id, "points": user.points, "user_id": id }
                    )
                    
                    if rows.scalar() == None:
                        return "Not a valid ID"
                    
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
                
                rows = connection.execute(
                    sqlalchemy.text("""UPDATE users SET name = :name, room_id = :room_id, points = :points, calendar_id = :calendar_id
                                    WHERE id = :user_id RETURNING *"""),
                    {"name": user.name, "room_id": user.room_id, "points": user.points, "user_id": id, "calendar_id":calendar_id }
                )

                if rows.scalar() == None:
                    return "Not a valid ID"
          
        return {"success": "ok"}
    except Exception as error:
        print(f"Error returned: <<{error}>>")
        return ("Couldn't complete endpoint")

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
        return {f"No user found of id {id}"}
    return {"deleted_user": deleted.name}
