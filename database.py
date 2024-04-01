from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import DIALECT, USER, PASSWORD, SERVER, PORT, DB_NAME

SQLALCHEMY_DATABASE_URL = f"{DIALECT}://{USER}:{PASSWORD}@{SERVER}:{PORT}/{DB_NAME}"
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=False)

SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()
