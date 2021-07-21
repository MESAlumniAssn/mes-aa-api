from typing import List

from sqlalchemy import update
from sqlalchemy.future import select
from sqlalchemy.orm import Session

from database.models import Testimonial


class TestimonialDAL:
    def __init__(self, session: Session):
        self.session = session

    async def fetch_all_testimonials(self) -> List[Testimonial]:
        q = await self.session.execute(
            select(Testimonial)
            .where(Testimonial.approved)
            .order_by(Testimonial.id.desc())
        )
        return q.scalars().all()

    async def create_testimonial(self, name, batch, message, approved, hash):
        new_testimonial = Testimonial(
            name=name,
            batch=batch,
            message=message,
            approved=approved,
            verification_hash=hash,
        )

        self.session.add(new_testimonial)
        await self.session.commit()

        return {"id": new_testimonial.id, "hash": new_testimonial.verification_hash}

    async def verify_if_testimonial_exists(self, verification_hash, id):
        q = await self.session.execute(
            select(Testimonial).where(
                Testimonial.id == id, Testimonial.verification_hash == verification_hash
            )
        )
        return q.scalars().first()

    async def update_testimonial_verification_status(self, verification_hash):
        q = update(Testimonial).where(
            Testimonial.verification_hash == verification_hash
        )
        q = q.values(approved=True)

        await self.session.execute(q)
