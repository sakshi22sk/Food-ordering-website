
from sqlalchemy import Column, Integer, String, Boolean
from app.database import Base

class MenuItem(Base):
    __tablename__ = "menu_items"

    item_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), unique=True, nullable=False)
    price = Column(Integer, nullable=False)
    is_available = Column(Boolean, default=True)
