from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from sqlalchemy import func, extract
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
    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text("INSERT INTO room (room_name) VALUES (:room_name) RETURNING id"),
            {"room_name": new_room.room_name}
        )
        room_id = result.scalar()
    return {"room_id": room_id}


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
    id: int
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

@router.post("/user/{id}")
def set_user(id: int, user: User):
    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text("""UPDATE users SET name = :name, room_id = :room_id, points = :points
                            WHERE id = :user_id"""),
            {"name": user.name, "room_id": user.room_id, "points": user.points, "user_id": user.id}
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

@router.post("/reward")
def get_reward(room_id: int):
    with db.engine.begin() as connection:
        res = connection.execute(
            sqlalchemy.text("SELECT * FROM users WHERE room_id = :room_id"),
            {"room_id": room_id}
        )
        users = []
        for row in res:
            users.append(row.id)

        curmomth = func.extract('month', func.timezone('UTC', func.now()))
        curyear = func.extract('year', func.timezone('UTC', func.now()))

        points = []
        for user in users:
            total = connection.execute(
                sqlalchemy.text("""
                    SELECT SUM(points) FROM chores WHERE assigned_user_id = :user_id
                    and extract('month' created_at) = :month
                    and extract('year' created_at) = :year"""),
                {"user_id": user, "month": curmomth, "year": curyear}
            ).scalar()
            points.append(total)

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
                sqlalchemy.text("INSERT INTO calendar (name) VALUES (:calendar_name)"),
                {"name": "Room " + str(room_id) + "'s Calendar"}
            )
            cal = calid.fetchone()[0]

        connection.execute(
            sqlalchemy.text("INSERT INTO events (calendar_id, name, description, start_time, end_time) VALUES (:calendar_id, :name, :description, :start_time, :end_time)"),
            {"calendar_id": cal, "name": "Reward for " + str(maxname),
             "description": "Reward to be completed by other roommates",
             "start_time": func.timezone('UTC', func.now()), "end_time": func.timezone('UTC', func.now())}
        )

    return {"success": "ok"}
