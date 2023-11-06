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

@router.post("/")
def add_chore(new_chore: NewChore):
    with db.engine.begin() as connection:
        if new_chore.assigned_user_id != None:
            result = connection.execute(
                sqlalchemy.text("INSERT INTO chores (chore_name, assigned_user_id) VALUES (:name, :assigned_user_id) RETURNING id"),
                {"name": new_chore.chore_name, "assigned_user_id": new_chore.assigned_user_id}
            )
        else :
            result = connection.execute(
                sqlalchemy.text("INSERT INTO chores (chore_name) VALUES (:name) RETURNING id"),
                {"name": new_chore.chore_name}
            )

    chore_id = result.scalar()
    return {"chore_id": chore_id}

@router.get("/")
def get_chore():
    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text("SELECT * FROM chores ")
        ) 
    
    for chore in result:
        print(chore)
         
    return {"success": "ok"}

@router.get("/all")
def get_all_chore():
    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text("SELECT * FROM chores WHERE completed = true"),
        ) 

    for chore in result:
        print(chore)

    return {"success": "ok"}

@router.post("/{chore_id}/claim/{user_id}")
def set_user(chore_id: int, user_id: int):
    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text("""UPDATE chores 
                            SET assigned_user_id = :user_id
                            WHERE id = :chore_id"""),
                            {"user_id": user_id, "chore_id": chore_id})
        
    return {"success": "ok"}

@router.get("/chore/{id}")
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
        return "Take a break! No chores to be completed."

    return list


@router.post("/chore/{choreid}/completed")
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
    return {"success" : "ok"}