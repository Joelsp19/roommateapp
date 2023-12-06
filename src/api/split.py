from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/splits",
    tags=["splits"],
    dependencies=[Depends(auth.get_api_key)],
)

class NewSplit(BaseModel):
    name: str
    price: float
    quantity: int
    user_added: int     # Temp for testing

@router.post("/")
def add_split(new_split: NewSplit):
    '''Add a split in the database'''
    try:
        with db.engine.begin() as connection:
            result = connection.execute(
                sqlalchemy.text("""
                                INSERT INTO split (name, price, quantity, user_added) 
                                VALUES (:name, :price, :quantity, :user_added) 
                                RETURNING id
                                """) ,
                                {"name": new_split.name,
                                "price": new_split.price,
                                "quantity": new_split.quantity,
                                "user_added": new_split.user_added}
            )
            split_id = result.scalar()
        return {"split_id": split_id}
    except Exception as error:
        print(f"Error returned: <<{error}>>")
        return ("Couldn't complete endpoint")


@router.put("/{split_id}/update/")
def update_split(split_id: int, name: str, price: float, quantity: int):
    '''Update a split given a split_id'''
    try:
        with db.engine.begin() as connection:
            rows = connection.execute(
                sqlalchemy.text("""
                                UPDATE split
                                SET
                                    name = :name,
                                    price = :price,
                                    quantity = :quantity
                                WHERE id = :split_id
                                RETURNING *
                                """),
                                {"split_id": split_id,
                                "name": name,
                                "price": price,
                                "quantity": quantity}
            )
            if rows.scalar() == None:
                return "Not a valid ID"
          
        return {"success": "ok"}
    except Exception as error:
        print(f"Error returned: <<{error}>>")
        return ("Couldn't complete endpoint")


@router.get("/{split_id}")
def get_split(split_id: int):
    '''Returns a split given a split id'''
    try:
        with db.engine.begin() as connection:
            split = connection.execute(
                sqlalchemy.text("""
                                SELECT id, name, price, quantity, user_added
                                FROM split
                                WHERE id = :split_id
                                """),
                                {"split_id": split_id}
        ).first()
        
        if split == None:
            return {"success": f"Error: No split found with split id {split_id}"}
        return {"id": split.id,
                "name": split.name,
                "price": split.price,
                "quantity": split.quantity,
                "user_added": split.user_added}
    except Exception as error:
        print(f"Error returned: <<{error}>>")
        return ("Couldn't complete endpoint")


@router.get("/{user_id}/")
def get_split_by_user(user_id: int):
    '''Returns all splits created by a certain user'''
    try:
        with db.engine.begin() as connection:
            user_splits = connection.execute(
                sqlalchemy.text("""
                                SELECT id, name, price, quantity, user_added
                                FROM split
                                WHERE user_added = :user_added
                                """),
                                {"user_added": user_id}
            ).all()
    
        user_splits_list = []
        for split in user_splits:
            user_splits_list.append({
                "id": split.id,
                "name": split.name,
                "price": split.price,
                "quantity": split.quantity,
                "user_added": split.user_added
            })
        return user_splits_list
    except Exception as error:
        print(f"Error returned: <<{error}>>")
        return ("Couldn't complete endpoint")


@router.get("/{user_id}/pay/")
def pay_splits(user_id: int):
    '''Given a user id, return how much they have to pay and to whom'''
    try:
        with db.engine.begin() as connection:
            room_id = connection.execute(
                sqlalchemy.text("""
                                SELECT users.room_id
                                FROM users
                                WHERE users.id = :user_id"""),
                                {"user_id": user_id}
            )
            room_id = room_id.scalar()

            num_roommates = connection.execute(
                sqlalchemy.text("""
                                SELECT COUNT(*)
                                FROM users
                                WHERE users.room_id = :room_id
                                """),
                                {"room_id": room_id}
            )
            num_roommates = num_roommates.scalar()

            room_splits = connection.execute(
                sqlalchemy.text("""
                                SELECT
                                    split.id,
                                    price,
                                    quantity,
                                    user_added
                                FROM split
                                JOIN users ON users.id = split.user_added
                                WHERE 
                                    room_id = :room_id AND
                                    user_added != :user_id
                                """),
                                {"user_id": user_id,
                                "room_id": room_id}
            ).all()
        
        user_splits_list = []
        for split in room_splits:
            print(split)
            name = split[0]
            price = split[1]
            quantity = split[2]
            user_added = split[3]
            user_splits_list.append({
                "Item": name,
                "Price you pay": price / num_roommates,
                "Who you pay": user_added
            })
        return user_splits_list
    except Exception as error:
        print(f"Error returned: <<{error}>>")
        return ("Couldn't complete endpoint")

@router.delete("/{split_id}/delete/")
def delete_split(split_id: int):
    '''Delete a split given a split_id'''
    try:
        with db.engine.begin() as connection:
            result = connection.execute(
                sqlalchemy.text("""
                                DELETE
                                FROM split
                                WHERE id = :split_id
                                RETURNING *
                                """),
                                {"split_id": split_id}
            ).first()

        if result == None:
            return {"success": f"Error: No split with id {split_id}"}
        return {"deleted_item": result.name}
    except Exception as error:
        print(f"Error returned: <<{error}>>")
        return ("Couldn't complete endpoint")