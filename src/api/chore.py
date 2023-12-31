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
    assigned_user_id: int = None
    points: int

@router.post("/")
def add_chore(new_chore: NewChore):
    '''Adds a chore to the database'''
    if new_chore.points < 0:
        return "Points cannot be negative. Try Again"
    else :
        try:
            with db.engine.begin() as connection:
                if new_chore.assigned_user_id != None:
                    chore_id = connection.execute(
                        sqlalchemy.text("INSERT INTO chores (chore_name, assigned_user_id, completed, points) VALUES (:name, :assigned_user_id, false, :points) RETURNING id"),
                        {"name": new_chore.chore_name, "assigned_user_id": new_chore.assigned_user_id,
                         "points": new_chore.points}
                    ).scalar()
                else :
                    chore_id = connection.execute(
                        sqlalchemy.text("INSERT INTO chores (chore_name, points) VALUES (:name, :points) RETURNING id"),
                        {"name": new_chore.chore_name, "points": new_chore.points}
                    ).scalar()


            return {"chore_id": chore_id}
        except Exception as error:
            print(f"Error returned: <<{error}>>")
            return ("Couldn't complete endpoint - check assigned user id")


@router.get("/room/{room_id}")
def get_all_chores(room_id: int):
    '''Given a room id, returns all chores in the room'''
    chores = []
    try:
        with db.engine.begin() as connection:
            result = connection.execute(
                sqlalchemy.text("""
                                SELECT chores.id as chore_id, chore_name, completed, name as assigned_user_name, users.id as user_id, chores.points
                                FROM chores
                                JOIN users on users.id = assigned_user_id
                                WHERE users.room_id = :room_id
                                """),
                                {"room_id": room_id}
            )
    except Exception as error:
        print(f"Error returned: <<{error}>>")
        return ("Couldn't complete endpoint")


    for chore in result:
        chores.append({
            "chore_id" : chore.chore_id,
            "chore_name": chore.chore_name,
            "completed": chore.completed,
            "assigned_user_id" : chore.user_id,
            "assigned_user_name": chore.assigned_user_name,
            "points": chore.points
        })

    return chores

@router.get("/room/{room_id}/completed")
def get_completed_chores(room_id: int):
    '''Returns all completed chores in a room'''
    completed_list = []
    try:
        with db.engine.begin() as connection:
            chores = connection.execute(
                sqlalchemy.text("""
                                SELECT chores.id, chore_name, name as assigned_user_name, users.id as user_id, chores.points
                                FROM chores
                                LEFT JOIN users on users.id = assigned_user_id
                                WHERE users.room_id = :room_id AND completed=true
                                """),
                                {"room_id": room_id}
            )

            for chore in chores:
                if chore.assigned_user_name == None:
                    assigned_user_name = "No user assigned"
                else:
                    assigned_user_name = chore.assigned_user_name

                completed_list.append({
                    "id": chore.id,
                    "chore_name": chore.chore_name,
                    "user_id" : chore.user_id,
                    "assigned user": assigned_user_name,
                    "points": chore.points,
                })

        return completed_list
    except Exception as error:
        print(f"Error returned: <<{error}>>")
        return ("Couldn't complete endpoint")


@router.put("/{chore_id}/claim/{user_id}")
def claim_chore(chore_id: int, user_id: int):
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
        return ("Couldn't complete endpoint - check your id")


@router.get("/{id}")
def get_chores_by_user(id: int):
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
        return ("Couldn't complete endpoint - please check user_added id")


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
        return ("Couldn't complete endpoint - please check your input")


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
        return ("Couldn't complete endpoint - please check your id")
