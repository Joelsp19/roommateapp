from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
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
def get_reward(id: int):
    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text("SELECT * FROM rewards WHERE id = :reward_id"),
            {"reward_id": id}
        )