from fastapi import FastAPI, exceptions
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from src.api import room, chore, split, calendar
import json
import logging
import sys

description = """
The Roommate App is the premier site for all your roommate planning and tracking needs.
"""

app = FastAPI(
    title="Roommate App",
    description=description,
    version="0.0.1",
    terms_of_service="http://example.com/terms/",
    contact={
        "name": "Joel Puthankalam",
        "email": "jputhank@calpoly.edu",
    },
)

app.include_router(room.router)
app.include_router(chore.router)
app.include_router(split.router)
app.include_router(calendar.router)

@app.exception_handler(exceptions.RequestValidationError)
@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc):
    logging.error(f"The client sent invalid data!: {exc}")
    exc_json = json.loads(exc.json())
    response = {"message": [], "data": None}
    for error in exc_json:
        response['message'].append(f"{error['loc']}: {error['msg']}")

    return JSONResponse(response, status_code=422)

@app.get("/")
async def root():
    return {"message": "Welcome to the Roommate App."}
