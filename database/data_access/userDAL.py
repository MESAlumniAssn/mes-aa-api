import datetime
from typing import List
from typing import Optional

from sqlalchemy import and_
from sqlalchemy import update
from sqlalchemy.future import select
from sqlalchemy.orm import Session

from database.models import User


class UserDAL:
    def __init__(self, session: Session):
        self.session = session

    async def get_all_users(self):
        q = await self.session.execute(select(User).order_by(User.id))
        return q.scalars().all()

    async def create_user(
        self,
        prefix: str,
        first_name: str,
        last_name: str,
        email: str,
        mobile: Optional[str],
        birthday: datetime.date,
        address1: str,
        address2: str,
        city: str,
        state: str,
        pincode: str,
        country: str,
        duration_start: int,
        duration_end: int,
        course_puc: str,
        course_degree: str,
        course_pg: str,
        course_others: str,
        vision: str,
        profession: str,
        other_interests: str,
        membership_type: str,
        payment_mode: str,
        alt_user_id: str,
        membership_valid_upto: datetime.date,
        profile_url: str,
        id_card_url: str,
        membership_certificate_url: str,
        paid_amount: float,
    ):
        new_user = User(
            prefix=prefix,
            first_name=first_name,
            last_name=last_name,
            email=email,
            mobile=mobile or None,
            birthday=birthday,
            address1=address1,
            address2=address2 or None,
            city=city,
            state=state,
            pincode=pincode,
            country=country,
            duration_start=duration_start,
            duration_end=duration_end,
            course_puc=course_puc,
            course_degree=course_degree,
            course_pg=course_pg,
            course_others=course_others,
            vision=vision,
            profession=profession,
            other_interests=other_interests,
            membership_type=membership_type,
            payment_mode=payment_mode,
            alt_user_id=alt_user_id,
            membership_valid_upto=membership_valid_upto,
            profile_url=profile_url,
            id_card_url=id_card_url,
            membership_certificate_url=membership_certificate_url,
            payment_amount=paid_amount,
        )

        self.session.add(new_user)
        await self.session.commit()

    async def check_if_email_exists(self, email: str):
        q = await self.session.execute(select(User).where(User.email == email))
        return q.scalars().first()

    async def lastser_details_for_alt_id(self, alt_user_id: str) -> List[User]:
        q = await self.session.execute(
            select(User).where(User.alt_user_id == alt_user_id)
        )
        return q.scalars().first()

    async def get_user_details_for_id(self, user_id: int) -> List[User]:
        q = await self.session.execute(select(User).where(User.id == user_id))
        return q.scalars().first()

    async def update_payment_status(self, user_id: int) -> None:
        q = update(User).where(User.id == user_id)
        q = q.values(payment_status=True)

        await self.session.execute(q)

    async def get_registered_members(self, member_type: str, payment) -> List[User]:
        q = await self.session.execute(
            select(User).where(
                User.membership_type == member_type,
                User.payment_status == bool(payment),
            )
        )
        return q.scalars().all()

    async def search_alumni(
        self,
        first_name: Optional[str],
        last_name: Optional[str],
        profession: Optional[str],
    ):

        q = await self.session.execute(
            select(User).where(
                and_(
                    User.first_name.ilike(f"%{first_name}%"),
                    User.last_name.ilike(f"%{last_name}%"),
                    User.profession.ilike(f"%{profession}%"),
                )
            )
        )

        return q.scalars().all()

    # async def update_user_details(
    #     self,
    #     user_id: int,
    #     duration_start: Optional[int],
    #     duration_end: Optional[int],
    #     courses: Optional[str],
    #     vision: Optional[str],
    #     profession: Optional[str],
    #     other_interests: Optional[str],
    # ):
    #     q = update(User).where(User.id == user_id)

    #     if duration_start:
    #         q = q.values(duration_start=duration_start)

    #     if duration_end:
    #         q = q.values(duration_end=duration_end)

    #     if courses:
    #         q = q.values(courses=courses)

    #     if vision:
    #         q = q.values(vision=vision)

    #     if profession:
    #         q = q.values(profession=profession)

    #     if other_interests:
    #         q = q.values(other_interests=other_interests)

    #     q.execution_options(synchronize_session="fetch")

    #     await self.session.execute(q)

    #     return status.HTTP_201_CREATED
