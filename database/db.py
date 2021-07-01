import dotenv

dotenv.load_dotenv()

import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker

engine = create_async_engine(
    os.getenv("SQLALCHEMY_DATABASE_URI"), future=True, echo=True
)
async_session = sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)
Base = declarative_base()
