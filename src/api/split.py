from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    tags=["split"],
    dependencies=[Depends(auth.get_api_key)],
)

class NewSplit(BaseModel):
    name: str
    price: float
    quantity: int
    user_added: int     # Temp for testing

@router.post("/split/")
def add_split(new_split: NewSplit):
    with db.engine.begin() as connection:
        connection.execute(
            sqlalchemy.text("""
                            INSERT INTO split (name, price, quantity, user_added) 
                            VALUES (:name, :price, :quantity, :user_added) 
                            """),
                            {"name": new_split.name,
                             "price": new_split.price,
                             "quantity": new_split.quantity,
                             "user_added": new_split.user_added}
        )
    return {"success": "ok"}


# TODO: Implement split updating
# @router.put("/split/{split_id}/update/")


@router.get("/split/{split_id}")
def get_split(split_id: int):
    with db.engine.begin() as connection:
        split_db = connection.execute(
            sqlalchemy.text("""
                            SELECT id, name, price, quantity, user_added
                            FROM split
                            WHERE id = :split_id
                            """), {"split_id": split_id}).all()
    split_list = []
    for split in split_db:
        split_list.append({
            "id": split.id,
            "name": split.name,
            "price": split.price,
            "quantity": split.quantity,
            "user_added": split.user_added
        })
    return split_list


@router.get("/split/{user_id}/")
def get_split_user(user_id: int):
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


@router.get("/split/{user_id}/pay/")
def pay_split_by_user(user_id: int):
    with db.engine.begin() as connection:
        user_splits = connection.execute(
            sqlalchemy.text("""
                            SELECT id, name, price, quantity, user_added
                            FROM split
                            WHERE user_added != :user_added
                            """),
                            {"user_added": user_id}
        ).all()

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

    
    user_splits_list = []
    for split in user_splits:
        user_splits_list.append({
            "id": split.id,
            "name": split.name,
            "price": split.price / num_roommates,
            "quantity": split.quantity,
            "user_added": split.user_added
        })
    return user_splits_list


# TODO: Implement /split/{user_id}/pay/complete/
# @router.post("/split/{user_id}/pay/complete/")


@router.delete("/split/{split_id}/delete/")
def delete_split(split_id: int):
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


    return {"deleted_item": result.name}