from sqlalchemy import Column, Integer, String, DateTime, Enum
from datetime import datetime
from app.database import Base

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)

    name = Column(String(100), nullable=False)

    email = Column(String(255), unique=True, index=True, nullable=True)

    phone = Column(String(15), unique=True, index=True, nullable=False)

    password = Column(String(255), nullable=False)

    role = Column(
        Enum("student", "admin", name="user_roles"),
        default="student",
        nullable=False
    )

    created_at = Column(DateTime, default=datetime.utcnow)
