import datetime

from sqlalchemy import or_
from sqlalchemy.future import select
from sqlalchemy.orm import Session

from database.models import Event


class EventDAL:
    def __init__(self, session: Session):
        self.session = session

    async def create_new_event(
        self,
        name: str,
        description: str,
        venue: str,
        event_date: datetime.date,
        event_time: str,
        chief_guest: str,
    ):
        new_event = Event(
            name=name,
            description=description,
            venue=venue,
            event_date=event_date,
            event_time=event_time,
            chief_guest=chief_guest,
        )

        self.session.add(new_event)
        await self.session.commit()

        return str(new_event.id)

    async def fetch_all_upcoming_events(self):
        q = await self.session.execute(
            select(Event)
            .where(Event.event_date >= datetime.date.today())
            .order_by(Event.event_date.asc())
        )

        return q.scalars().all()

    async def fetch_all_completed_events(self):
        q = await self.session.execute(
            select(Event)
            .where(Event.event_date < datetime.date.today())
            .order_by(Event.event_date.desc())
        )

        return q.scalars().all()

    async def fetch_specific_event(self, id):
        q = await self.session.execute(select(Event).where(Event.id == id))

        return q.scalars().first()

    async def fetch_completed_events(self, text):
        q = await self.session.execute(
            select(Event).where(
                or_(
                    Event.name.ilike(f"%{text}%"),
                    Event.venue.ilike(f"%{text}%"),
                    Event.chief_guest.ilike(f"%{text}%"),
                ),
                Event.event_date < datetime.date.today(),
            )
        )

        return q.scalars().all()

    async def fetch_upcoming_events(self):
        q = await self.session.execute(
            select(Event).where(
                Event.event_date >= datetime.date.today(),
                Event.event_date < datetime.date.today() + datetime.timedelta(days=7),
            )
        )

        return q.scalars().all()
