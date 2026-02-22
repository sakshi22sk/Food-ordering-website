from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.deps import get_db
from app.models.menu import MenuItem
from app.schemas.menu import MenuCreate, MenuUpdate, MenuResponse
from app.core.security import admin_required, get_current_user

router = APIRouter(prefix="/menu", tags=["Menu"])

# 🔹 Student + Admin: view available menu
@router.get("/", response_model=list[MenuResponse])
def get_menu(db: Session = Depends(get_db)):
    return db.query(MenuItem).all()

# 🔹 Admin only: create item
@router.post("/", response_model=MenuResponse)
def create_menu(
    data: MenuCreate,
    db: Session = Depends(get_db),
    admin=Depends(admin_required)
):
    if db.query(MenuItem).filter(MenuItem.name == data.name).first():
        raise HTTPException(400, "Item already exists")

    item = MenuItem(name=data.name, price=data.price)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

# 🔹 Admin only: update item
@router.put("/{item_id}", response_model=MenuResponse)
def update_menu(
    item_id: int,
    data: MenuUpdate,
    db: Session = Depends(get_db),
    admin=Depends(admin_required)
):
    item = db.query(MenuItem).filter(MenuItem.item_id == item_id).first()
    if not item:
        raise HTTPException(404, "Item not found")

    if data.name is not None:
        item.name = data.name
    if data.price is not None:
        item.price = data.price
    if data.is_available is not None:
        item.is_available = data.is_available

    db.commit()
    db.refresh(item)
    return item
