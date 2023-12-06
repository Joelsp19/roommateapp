from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db
from datetime import datetime

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
    '''Adds a chore to the database'''
    try:
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
    except Exception as error:
        print(f"Error returned: <<{error}>>")
        return ("Couldn't complete endpoint")


@router.get("/")
def get_all_chores():
    '''Returns all chores in the database'''
    chores = []
    try:
        with db.engine.begin() as connection:
            result = connection.execute(
                sqlalchemy.text("""SELECT chore_name, completed, name as assigned_user_name, chores.points
                                FROM chores
                                JOIN users on users.id = assigned_user_id
                                """)
            )
    except Exception as error:
        print(f"Error returned: <<{error}>>")
        return ("Couldn't complete endpoint")


    for chore in result:
        chores.append({
            "chore_name": chore.chore_name,
            "completed": chore.completed,
            "assigned_user_id": chore.assigned_user_name,
            "points": chore.points
        })

    return chores

@router.get("/completed")
def get_completed_chores():
    '''Returns all completed chores in the database'''
    completed_list = []
    try:
        with db.engine.begin() as connection:
            chores = connection.execute(
                sqlalchemy.text("""
                                SELECT chores.id, chore_name, completed, name as assigned_user_name, chores.points
                                FROM chores
                                LEFT JOIN users on users.id = assigned_user_id
                                WHERE completed=true
                                """),
            )

            for chore in chores:
                if chore.assigned_user_name == None:
                    assigned_user_name = "No user assigned"
                else:
                    assigned_user_name = chore.assigned_user_name

                completed_list.append({
                    "id": chore.id,
                    "chore_name": chore.chore_name,
                    "assigned user": assigned_user_name,
                    "completed": chore.completed,
                    "points": chore.points,
                })

        return completed_list
    except Exception as error:
        print(f"Error returned: <<{error}>>")
        return ("Couldn't complete endpoint")


@router.put("/{chore_id}/claim/{user_id}")
def set_user(chore_id: int, user_id: int):
    '''Adds a user to a chore for them to complete'''
    try:
        with db.engine.begin() as connection:
            rows = connection.execute(
                sqlalchemy.text("""UPDATE chores
                                SET assigned_user_id = :user_id
                                WHERE id = :chore_id
                                RETURNING *"""),
                                {"user_id": user_id, "chore_id": chore_id})
            if rows.scalar() == None:
                return "Not a valid ID"
          
        return {"success": "ok"}
    except Exception as error:
        print(f"Error returned: <<{error}>>")
        return ("Couldn't complete endpoint")


@router.get("/{id}")
def get_chores_by_uid(id: int):
    '''Returns all chores assigned to user'''
    list = []
    try:
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
    except Exception as error:
        print(f"Error returned: <<{error}>>")
        return ("Couldn't complete endpoint")


@router.get("/{chore_id}/duration")
def get_chore_duration(chore_id: int):
    '''Returns how long a chore has been uncompleted for'''
    try:
        with db.engine.begin() as connection:
            result = connection.execute(
                sqlalchemy.text(
                    """
                    SELECT created_at, completed_at
                    FROM chores
                    WHERE id = :chore_id
                    """
                ),
                {"chore_id": chore_id}
            ).all()

        if result == []:
            return {"duration": f"Error: No chore found with chore id {chore_id}"}

        created_time, completed_time = result[0]
        if completed_time == None:
            date_diff = datetime.now(tz=created_time.tzinfo) - created_time
        else:
            date_diff = completed_time - created_time
        days = date_diff.days
        hours = date_diff.seconds // 3600
        return {"duration": f"{days} days and {hours} hours"}
    except Exception as error:
        print(f"Error returned: <<{error}>>")
        return ("Couldn't complete endpoint")


@router.put("/{chore_id}/completed")
def update_completed(chore_id: int):
    '''Completes a chore and awards the user points'''
    try:
        with db.engine.begin() as connection:
            result = connection.execute(
                sqlalchemy.text(
                    """
                    SELECT completed, created_at
                    FROM chores
                    WHERE id = :chore_id"""
                ),
                {"chore_id": chore_id}
            ).all()

            if result == []:
                return {"success": f"Error: No chore found with chore id {chore_id}"}
            completed, created_at = result[0]
            if completed == True:
                # Chore is already completed
                return {"success": f"Chore is already completed"}

            rows = connection.execute(
                sqlalchemy.text(
                    """
                    UPDATE chores
                    SET completed = :true, completed_at = :completed_at
                    WHERE id = :choreid
                    RETURNING *
                    """),
                {"choreid": chore_id,
                "true": True,
                "completed_at": datetime.now(tz=created_at.tzinfo)}
            )
            if rows.scalar() == None:
                return "Not a valid ID"
          
            rows2 = connection.execute(
                sqlalchemy.text(
                    """
                    UPDATE users
                    SET points = points + (SELECT points FROM chores WHERE id = :choreid)
                    WHERE id = (SELECT assigned_user_id FROM chores WHERE id = :choreid)
                    RETURNING *
                    """),
                {"choreid": chore_id}
            )

            if rows2.scalar() == None:
                return "Not a valid ID"
          
        return {"success" : "ok"}
    except Exception as error:
        print(f"Error returned: <<{error}>>")
        return ("Couldn't complete endpoint")
