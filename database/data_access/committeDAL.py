from typing import List

from sqlalchemy.future import select
from sqlalchemy.orm import Session

from database.models import Committee


class CommitteeDAL:
    def __init__(self, session: Session):
        self.session = session

    async def fetch_all_committe_members(self) -> List[Committee]:
        q = await self.session.execute(select(Committee).order_by(Committee.id))
        return q.scalars().all()
