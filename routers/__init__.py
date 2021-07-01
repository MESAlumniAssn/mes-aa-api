from fastapi import APIRouter

from database.data_access.adminDAL import AdminDAL
from database.data_access.committeDAL import CommitteeDAL
from database.data_access.famous_alumniDAL import FamousAlumniDAL
from database.data_access.testimonialDAL import TestimonialDAL
from database.data_access.userDAL import UserDAL
from database.db import async_session


router = APIRouter()


async def get_committee_dal():
    async with async_session() as session:
        async with session.begin():
            yield CommitteeDAL(session)


async def get_testimonial_dal():
    async with async_session() as session:
        async with session.begin():
            yield TestimonialDAL(session)


async def get_user_dal():
    async with async_session() as session:
        async with session.begin():
            yield UserDAL(session)


async def get_famous_alumni_dal():
    async with async_session() as session:
        async with session.begin():
            yield FamousAlumniDAL(session)


async def get_admin_dal():
    async with async_session() as session:
        async with session.begin():
            yield AdminDAL(session)
