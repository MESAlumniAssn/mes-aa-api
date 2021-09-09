import datetime
import os
import uuid
from typing import Optional

import requests_async as requests
from fastapi import Depends
from fastapi import Header
from fastapi import HTTPException
from fastapi import status
from pydantic import BaseModel
from sentry_sdk import capture_exception

from . import get_event_dal
from . import router
from database.data_access.eventDAL import EventDAL
from helpers.imagekit_init import initialize_imagekit_prod
from helpers.token_decoder import decode_auth_token


class EventBase(BaseModel):
    name: str
    description: str
    venue: str
    event_date: datetime.date
    event_time: str
    chief_guest: Optional[str] = None

    class Config:
        orm_mode = True


@router.post("/events", status_code=status.HTTP_201_CREATED)
async def post_new_event(
    event: EventBase,
    authorization: Optional[str] = Header(None),
    eventDAL: EventDAL = Depends(get_event_dal),
):
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Uh uh uh... You didn't say the magic word",
        )

    valid_token = decode_auth_token(authorization)

    if not valid_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Uh uh uh... You didn't say the magic word",
        )

    try:
        record = await eventDAL.create_new_event(
            event.name,
            event.description,
            event.venue,
            event.event_date,
            event.event_time.upper(),
            event.chief_guest,
        )

        formatted_name = event.name.split(" ")
        formatted_name = ("-").join(formatted_name)

        await requests.post(
            "https://api.imagekit.io/v1/folder/",
            auth=(os.getenv("IMAGEKIT_PRIVATE_KEY_PROD") + ":", " "),
            data={"folderName": formatted_name, "parentFolderPath": "MES-AA/Events"},
        )

        if not record:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Event creation failed",
            )

        return {
            "id": record,
            "name": event.name,
            "description": event.description,
            "venue": event.venue,
            "date": event.event_date,
            "time": event.event_time,
            "chief_guest": event.chief_guest,
        }

    except Exception as e:
        capture_exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create an event",
        )


@router.get("/events/{status}", status_code=status.HTTP_200_OK)
async def get_all_events(status: str, eventDAL: EventDAL = Depends(get_event_dal)):
    events = []
    event_obj = {}

    try:
        if status == "upcoming":
            records = await eventDAL.fetch_all_upcoming_events()

        if status == "completed":
            records = await eventDAL.fetch_all_completed_events()

        for record in records:
            event_obj["event_id"] = record.id
            event_obj["name"] = record.name
            event_obj["description"] = record.description
            event_obj["date"] = record.event_date.strftime("%d-%b-%Y")
            event_obj["time"] = record.event_time
            event_obj["venue"] = record.venue
            event_obj["chief_guest"] = record.chief_guest

            events.append(event_obj.copy())

        return events

    except Exception as e:
        capture_exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not fetch events",
        )


@router.get("/event/{id}", status_code=status.HTTP_200_OK)
async def get_event(id: uuid.UUID, eventDAL: EventDAL = Depends(get_event_dal)):

    try:
        record = await eventDAL.fetch_specific_event(id)

        imagekit = initialize_imagekit_prod()

        formatted_name = record.name.split(" ")
        formatted_name = ("-").join(formatted_name)

        files = imagekit.list_files(
            {"path": f"MES-AA/Events/{formatted_name}", "limit": 100}
        )

        return {
            "name": record.name,
            "description": record.description,
            "date": record.event_date,
            "time": record.event_time,
            "venue": record.venue,
            "chief_guest": record.chief_guest,
            "images": files["response"],
        }
    except Exception as e:
        capture_exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not fetch event",
        )


@router.get("/events/search/{search_text}", status_code=status.HTTP_200_OK)
async def search_events(search_text: str, eventDAL: EventDAL = Depends(get_event_dal)):
    events = []
    event_obj = {}

    try:
        records = await eventDAL.fetch_completed_events(search_text)

        for record in records:
            event_obj["event_id"] = record.id
            event_obj["name"] = record.name
            event_obj["description"] = record.description
            event_obj["date"] = record.event_date
            event_obj["time"] = record.event_time
            event_obj["venue"] = record.venue
            event_obj["chief_guest"] = record.chief_guest

            events.append(event_obj.copy())

        return events

    except Exception as e:
        capture_exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not fetch events",
        )


@router.get("/events/upcoming/current_week", status_code=status.HTTP_200_OK)
async def upcoming_events(eventDAL: EventDAL = Depends(get_event_dal)):
    events = []
    event_obj = {}

    try:
        records = await eventDAL.fetch_upcoming_events()

        for record in records:
            date_of_event = (
                record.event_date.strftime("%d-%b-%Y")
                if record.event_date > datetime.date.today()
                else "today"
            )

            event_obj["event_id"] = record.id
            event_obj["name"] = record.name
            event_obj["date"] = date_of_event

            events.append(event_obj.copy())

        return events

    except Exception as e:
        capture_exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not fetch events",
        )
