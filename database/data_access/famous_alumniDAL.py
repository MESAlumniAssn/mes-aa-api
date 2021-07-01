from typing import List

from sqlalchemy.future import select
from sqlalchemy.orm import Session

from database.models import FamousAlumni


class FamousAlumniDAL:
    def __init__(self, session: Session):
        self.session = session

    async def fetch_all_famous_alumni(self) -> List[FamousAlumni]:
        q = await self.session.execute(select(FamousAlumni).order_by(FamousAlumni.name))
        return q.scalars().all()
