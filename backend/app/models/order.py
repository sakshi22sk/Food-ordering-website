from sqlalchemy import Column, Integer, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Order(Base):
    __tablename__ = "orders"

    order_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)

    time_slot = Column(
        Enum(
            "10:00-10:15",
            "10:15-10:30",
            "10:30-10:45",
            "10:45-11:00",

            "11:00-11:15",
            "11:15-11:30",
            "11:30-11:45",
            "11:45-12:00",

            "12:00-12:15",
            "12:15-12:30",
            "12:30-12:45",
            "12:45-13:00",

            "13:00-13:15",
            "13:15-13:30",
            "13:30-13:45",
            "13:45-14:00",

            "14:00-14:15",
            "14:15-14:30",
            "14:30-14:45",
            "14:45-15:00",

            "15:00-15:15",
            "15:15-15:30",
            "15:30-15:45",
            "15:45-16:00",

            "16:00-16:15",
            "16:15-16:30",
            "16:30-16:45",
            "16:45-17:00",
            "17:00-17:15",
            "17:15-17:30",
            "17:30-17:45",
            "17:45-18:00",
            "18:15-18:30",
            "18:30-18:45",
            "18:45-19:00",
            "19:00-19:15",

            name="time_slots"
        ),
        nullable=False
    )

    status = Column(
        Enum("pending", "ready", "picked", name="order_status"),
        default="pending",
        nullable=False
    )

    created_at = Column(DateTime, default=datetime.utcnow)

    items = relationship("OrderItem", back_populates="order")
