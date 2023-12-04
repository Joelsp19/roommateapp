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
    '''Create a split'''
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


@router.put("/{split_id}/update/")
def update_split(split_id: int, name: str, price: float, quantity: int):
    '''Update a split'''
    with db.engine.begin() as connection:
        connection.execute(
            sqlalchemy.text("""
                            UPDATE split
                            SET
                                name = :name,
                                price = :price,
                                quantity = :quantity
                            WHERE id = :split_id
                            """),
                            {"split_id": split_id,
                             "name": name,
                             "price": price,
                             "quantity": quantity}
        )
    return {"success": "ok"}


@router.get("/{split_id}")
def get_split(split_id: int):
    '''Get split given a split id'''
    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text("""
                            SELECT * 
                            FROM split
                            WHERE id = :split_id
                            """),
                            {"split_id": split_id}
    )
    split = result.first()
    return {"id": split.id,
            "name": split.name,
            "price": split.price,
            "quantity": split.quantity,
            "user_added": split.user_added}


@router.get("/{user_id}/")
def get_split_user(user_id: int):
    '''Get splits created by a certain user'''
    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text("""
                            SELECT *
                            FROM split
                            WHERE user_added = :user_added
                            """),
                            {"user_added": user_id}
        )
    user_splits = result.all()
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


@router.get("/{user_id}/pay/")
def pay_split(user_id: int):
    '''Given a user id, return how much they have to pay and to whom'''
    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text("""
                            SELECT *
                            FROM split
                            WHERE user_added != :user_added
                            """),
                            {"user_added": user_id}
        )

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

    user_splits = result.all()
    user_splits_list = []
    for split in user_splits:
        user_splits_list.append({
            "Item": split.name,
            "Price you pay": split.price / num_roommates,
            "Who you pay": split.user_added
        })
    return user_splits_list


@router.delete("/{split_id}/delete/")
def delete_split(split_id: int):
    '''Delete a split'''
    with db.engine.begin() as connection:
        connection.execute(
            sqlalchemy.text("""
                            DELETE
                            FROM split
                            WHERE id = :split_id
                            """),
                            {"split_id": split_id}
        )
    return {"success": "ok"}