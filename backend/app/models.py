from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id = Column(Integer, primary_key=True, index=True)
    candidate_name = Column(String(100), nullable=False)
    current_topic = Column(String(100), nullable=True)
    current_question_index = Column(Integer, default=-1)
    is_finished = Column(Boolean, default=False)
    total_score = Column(Float, default=0)
    question_order = Column(Text, nullable=True)
    max_questions = Column(Integer, default=3)

    messages = relationship(
        "InterviewMessage",
        back_populates="session",
        cascade="all, delete-orphan",
    )


class InterviewMessage(Base):
    __tablename__ = "interview_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("interview_sessions.id"))
    sender = Column(String(20), nullable=False)
    message = Column(Text, nullable=False)
    topic = Column(String(100), nullable=True)
    score = Column(Float, nullable=True)

    session = relationship(
        "InterviewSession",
        back_populates="messages",
    )