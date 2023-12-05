from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/chore",
    tags=["chore"],
    dependencies=[Depends(auth.get_api_key)],
)

class NewChore(BaseModel):
    chore_name: str
    completed: bool
    assigned_user_id: int = None
    points: int

@router.post("/")
def add_chore(new_chore: NewChore):
    '''Adds a chore to the database'''
    with db.engine.begin() as connection:
        if new_chore.assigned_user_id != None:
            chore_id = connection.execute(
                sqlalchemy.text("INSERT INTO chores (chore_name, assigned_user_id, completed, points) VALUES (:name, :assigned_user_id, :completed, :points) RETURNING id"),
                {"name": new_chore.chore_name, "assigned_user_id": new_chore.assigned_user_id,
                 "completed": new_chore.completed, "points": new_chore.points}
            ).scalar()
        else :
            chore_id = connection.execute(
                sqlalchemy.text("INSERT INTO chores (chore_name, points) VALUES (:name, :points) RETURNING id"),
                {"name": new_chore.chore_name, "points": new_chore.points}
            ).scalar()


    return {"chore_id": chore_id}

@router.get("/")
def get_all_chores():
    '''Returns all chores in the database'''
    with db.engine.begin() as connection:
        chores = connection.execute(
            sqlalchemy.text("SELECT id, chore_name, completed, assigned_user_id, points FROM chores ")
        )

    chore_list = []
    for chore in chores:
        chore_list.append({
            "id": chore.id,
            "name": chore.chore_name,
            "completed": chore.completed,
            "assigned": chore.assigned_user_id,
            "points": chore.points
        })
    return chore_list


@router.get("/all")
def get_completed_chores():
    '''Returns all completed chores in the database'''
    completed_list = []
    with db.engine.begin() as connection:
        chores = connection.execute(
            sqlalchemy.text("SELECT id, chore_name, assigned_user_id, points FROM chores WHERE completed = true"),
        )

        for chore in chores:
            chore_id: int = chore[0]
            chore_time_created = chore[1]       # datetime format
            chore_name: str = chore[2]
            assigned_user_id = chore[3]
            if assigned_user_id != None:
                assigned_user_name: str = connection.execute(
                    sqlalchemy.text("SELECT name FROM users WHERE id = :uid"),
                    {"uid": assigned_user_id}
                ).first()[0]
            else:
                assigned_user_name: str = "No user assigned"
            completed: bool = chore[4]
            points: int = chore[5]
            completed_list.append({
                "id": chore_id,
                "chore_name": chore_name,
                "assigned user": assigned_user_name,
                "completed": completed,
                "points": points,
            })

    return completed_list

@router.post("/{chore_id}/claim/{user_id}")
def set_user(chore_id: int, user_id: int):
    '''Adds a user to a chore for them to complete'''
    with db.engine.begin() as connection:
        connection.execute(
            sqlalchemy.text("""UPDATE chores
                            SET assigned_user_id = :user_id
                            WHERE id = :chore_id"""),
                            {"user_id": user_id, "chore_id": chore_id})

    return {"success": "ok"}

@router.get("/{id}")
def get_chores_by_id(id: int):
    '''Returns a chore given a chore_id'''
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
        return "Take a break! No chores to be completed."

    return list

@router.post("/{choreid}/completed")
def update_completed(choreid: int):
    '''Completes a chore and awards the user points'''
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
