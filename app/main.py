from dotenv import load_dotenv

load_dotenv()

import os
from fastapi import FastAPI
from database.db import engine, Base
from routers import (
    index,
    committee,
    testimonial,
    users,
    famous_alumni,
    dashboard,
    gallery,
    admin,
    payments,
    email_messages,
)
from starlette.middleware.cors import CORSMiddleware

app = FastAPI(docs_url=None, redoc_url=None)

origins = [os.getenv("CORS_ORIGIN_SERVER")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


app.include_router(committee.router)
app.include_router(testimonial.router)
app.include_router(users.router)
app.include_router(famous_alumni.router)
app.include_router(dashboard.router)
app.include_router(gallery.router)
app.include_router(admin.router)
app.include_router(payments.router)
app.include_router(email_messages.router)
app.include_router(index.router)
