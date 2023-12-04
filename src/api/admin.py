from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.post("/reset")
def reset():
    """
    Reset the state -- won't implement for now
    """
    return "OK"


@router.get("/shop_info/")
def get_shop_info():
    """ """
    return {
        "site_name": "Roommate App",
        "site_owners": "Joel, Wesley, Ritvik, Krish",
    }

