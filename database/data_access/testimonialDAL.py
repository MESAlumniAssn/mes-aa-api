from typing import List

from sqlalchemy.future import select
from sqlalchemy.orm import Session

from database.models import Testimonial


class TestimonialDAL:
    def __init__(self, session: Session):
        self.session = session

    async def fetch_all_testimonials(self) -> List[Testimonial]:
        q = await self.session.execute(
            select(Testimonial).order_by(Testimonial.id.desc())
        )
        return q.scalars().all()
