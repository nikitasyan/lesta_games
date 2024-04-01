from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


class AllWords(Base):
    __tablename__ = "all_words"

    id = Column(Integer, primary_key=True)
    word = Column(String(250), nullable=False, unique=True)
    count_files_with_word = Column(Integer)

    current_file = relationship(argument="CurrentFile",
                                back_populates="all_words",
                                cascade="all, delete-orphan")


class CurrentFile(Base):
    __tablename__ = "current_file"

    id = Column(Integer, primary_key=True)
    word_count = Column(Integer)
    word_id = Column(Integer, ForeignKey("all_words.id", ondelete="CASCADE"))

    all_words = relationship(argument="AllWords",
                             back_populates="current_file")
