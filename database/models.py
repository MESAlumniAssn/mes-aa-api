import datetime
import uuid

from sqlalchemy import BigInteger
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import Date
from sqlalchemy import Float
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID

from database.db import Base


class Committee(Base):

    __tablename__ = "committee"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    role = Column(String(50), nullable=False)
    designation = Column(String(50), nullable=False)
    image_url = Column(String(500), nullable=True)

    def __repr__(self):
        return f"Committee({self.id}, {self.name})"


class Testimonial(Base):
    __tablename__ = "testimonials"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    batch = Column(String(10), nullable=False)
    message = Column(String(1000), nullable=False)
    approved = Column(Boolean, default=False)
    verification_hash = Column(String(100))

    def __repr__(self):
        return f"Testimonial({self.name}, {self.batch})"


class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    prefix = Column(String(10), nullable=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(50), nullable=False, index=True)
    mobile = Column(String(15), nullable=False)
    birthday = Column(Date, nullable=False)
    address1 = Column(String(100), nullable=False)
    address2 = Column(String(100))
    city = Column(String(50), nullable=False)
    state = Column(String(50), nullable=False)
    pincode = Column(String(15), nullable=False)
    country = Column(String(50), nullable=False)
    duration_start = Column(Integer)
    duration_end = Column(Integer, index=True)
    course_puc = Column(String(50))
    course_degree = Column(String(50))
    course_pg = Column(String(50))
    course_others = Column(String(50))
    vision = Column(String(1000))
    profession = Column(String(100))
    other_interests = Column(String(1000))
    membership_type = Column(String(10), index=True)
    payment_status = Column(Boolean, default=False)
    payment_amount = Column(Float, default=0.0, index=True)
    date_created = Column(Date, default=datetime.date.today)
    membership_valid_upto = Column(Date)
    membership_expired = Column(Boolean, default=False)
    date_renewed = Column(Date)
    alt_user_id = Column(String(50))
    profile_url = Column(String(500))
    id_card_url = Column(String(500))
    membership_certificate_url = Column(String(500))
    payment_mode = Column(String(1), default="O")
    manual_payment_notification = Column(Boolean, default=False)
    email_subscription_status = Column(Boolean, default=True)

    def __repr__(self):
        return f"User({self.id}, {self.email}, {self.country})"


class FamousAlumni(Base):
    __tablename__ = "famous_alumni"

    id = Column(BigInteger, primary_key=True, autoincrement=True, index=True)
    name = Column(String(100))
    award = Column(String(100))
    year = Column(String(4))
    category = Column(String(100), index=True)
    description = Column(String(200))
    batch = Column(String(4))

    def __repr__(self):
        return f"FamousAlumni({self.id}, {self.name})"


class Admin(Base):
    __tablename__ = "admin"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(50), unique=True)
    password = Column(String(500))

    def __repr__(self) -> str:
        return f"Admin({self.id}, {self.email})"
