from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/chores",
    tags=["chores"],
    dependencies=[Depends(auth.get_api_key)],
)

class NewChore(BaseModel):
    chore_name: str
    completed: bool
    assigned_user_id: int = None
    points: int

@router.post("/")
def add_chore(new_chore: NewChore):
    with db.engine.begin() as connection:
        if new_chore.assigned_user_id != None:
            result = connection.execute(
                sqlalchemy.text("INSERT INTO chores (chore_name, assigned_user_id, completed, points) VALUES (:name, :assigned_user_id, :completed, :points) RETURNING id"),
                {"name": new_chore.chore_name, "assigned_user_id": new_chore.assigned_user_id,
                 "completed": new_chore.completed, "points": new_chore.points}
            )
        else :
            result = connection.execute(
                sqlalchemy.text("INSERT INTO chores (chore_name, points) VALUES (:name, :points) RETURNING id"),
                {"name": new_chore.chore_name, "points": new_chore.points}
            )

    chore_id = result.scalar()
    return {"chore_id": chore_id}

@router.get("/")
def get_chore():
    chores = []
    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text("""SELECT chore_name, completed, name as assigned_user_name, points 
                            FROM chores
                            JOIN users on users.id = assigned_user_id
                            """)
        )

    for chore in result:
        chores.append({
            "chore_id" : chore.id,
            "chore_name": chore.name,
            "completed": chore.completed,
            "assigned_user_id": chore.assigned_user_name,
            "points": chore.points
        })

    return chores

@router.get("/completed")
def get_chores_completed():
    chores = []
    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text("""SELECT chore_name, completed, name as assigned_user_name, points 
                            FROM chores
                            JOIN users on users.id = assigned_user_id
                            WHERE completed=true
                            """),
        )
    for chore in result:
        chores.append({
            "chore_id" : chore.id,
            "chore_name": chore.name,
            "assigned_user_id": chore.assigned_user_name,
            "points": chore.points
        })
    return chores

@router.post("/{chore_id}/claim/{user_id}")
def set_user(chore_id: int, user_id: int):
    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text("""UPDATE chores
                            SET assigned_user_id = :user_id
                            WHERE id = :chore_id"""),
                            {"user_id": user_id, "chore_id": chore_id})

    return {"success": "ok"}

@router.get("/{id}")
def get_chores_by_id(id: int):
    list = []
    with db.engine.begin() as connection:
        tab = connection.execute(
            sqlalchemy.text(
                """
                SELECT id,chore_name,completed
                FROM chores
                WHERE assigned_user_id = :id
                ORDER BY completed
                """),
                {"id": id}
        )

    for row in tab:
        list.append(
            {
            "id": row.id,
            "chore_name": row.chore_name,
            "completed": row.completed
            }
        )
    if list == []:
        print("Take a break! No chores to be completed.")
        return []

    return list


@router.post("/{choreid}/completed")
def update_completed(choreid: int):
    with db.engine.begin() as connection:
        connection.execute(
            sqlalchemy.text(
                """
                UPDATE chores
                SET completed = :true
                WHERE id = :choreid
                """)
            ,{"choreid": choreid, "true": True}
        )
        connection.execute(sqlalchemy.text(
            """UPDATE users
            SET points = points + (SELECT points FROM chores WHERE id = :choreid)
            WHERE id = (SELECT assigned_user_id FROM chores WHERE id = :choreid)"""),
            {"choreid": choreid}
        )
    return {"success" : "ok"}

