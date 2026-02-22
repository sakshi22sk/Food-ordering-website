from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.deps import get_db
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.menu import MenuItem
from app.schemas.order import OrderCreate, OrderResponse
from app.core.security import get_current_user, admin_required
from app.models.user import User

router = APIRouter(prefix="/orders", tags=["Orders"])


# ✅ PLACE ORDER (simple, no response model)
@router.post("/")
def place_order(
    data: OrderCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if not data.items:
        raise HTTPException(400, "Order must contain items")

    order = Order(
        user_id=current_user.user_id,
        time_slot=data.time_slot
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    for item in data.items:
        menu_item = db.query(MenuItem).filter(
            MenuItem.item_id == item.item_id,
            MenuItem.is_available == True
        ).first()

        if not menu_item:
            raise HTTPException(400, "Invalid or unavailable item")

        db.add(OrderItem(
            order_id=order.order_id,
            item_id=item.item_id,
            quantity=item.quantity
        ))

    db.commit()

    return {"message": "Order placed successfully"}


# ✅ GET MY ORDERS (bill-style)
@router.get("/my", response_model=list[OrderResponse])
def my_orders(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    orders = (
    db.query(Order)
    .filter(Order.user_id == current_user.user_id)
    .order_by(Order.created_at.desc())  # 👈 latest first
    .all()
)

    response = []

    for order in orders:
        items = (
            db.query(OrderItem, MenuItem)
            .join(MenuItem, OrderItem.item_id == MenuItem.item_id)
            .filter(OrderItem.order_id == order.order_id)
            .all()
        )

        item_list = []
        total_price = 0

        for order_item, menu_item in items:
            subtotal = menu_item.price * order_item.quantity
            total_price += subtotal

            item_list.append({
                "item_name": menu_item.name,
                "price": menu_item.price,
                "quantity": order_item.quantity,
                "subtotal": subtotal
            })

        response.append({
            "order_id": order.order_id,
            "time_slot": order.time_slot,
            "status": order.status,
            "items": item_list,
            "total_price": total_price
        })

    return response


@router.get("/slot/{slot}")
def orders_by_slot(
    slot: str,
    db: Session = Depends(get_db),
    admin=Depends(admin_required)
):
    # 1️⃣ Validate slot against ENUM
    valid_slots = Order.__table__.c.time_slot.type.enums
    if slot not in valid_slots:
        raise HTTPException(
            status_code=400,
            detail="Invalid time slot"
        )

    # 2️⃣ Fetch orders for slot
    orders = (
        db.query(Order)
        .filter(Order.time_slot == slot)
        .order_by(Order.created_at.asc())
        .all()
    )

    response = []

    for order in orders:
        # 3️⃣ Fetch user
        user = db.query(User).filter(User.user_id == order.user_id).first()

        # 4️⃣ Fetch items with menu details
        items = (
            db.query(OrderItem, MenuItem)
            .join(MenuItem, OrderItem.item_id == MenuItem.item_id)
            .filter(OrderItem.order_id == order.order_id)
            .all()
        )

        item_list = []
        total_price = 0

        for order_item, menu_item in items:
            subtotal = menu_item.price * order_item.quantity
            total_price += subtotal

            item_list.append({
                "item_name": menu_item.name,
                "price": menu_item.price,
                "quantity": order_item.quantity,
                "subtotal": subtotal
            })

        response.append({
            "order_id": order.order_id,
            "time_slot": order.time_slot,
            "status": order.status,
            "created_at": order.created_at,

            "user": {
                "user_id": user.user_id,
                "name": user.name,
                "phone": user.phone
            },

            "items": item_list,
            "total_price": total_price
        })

    return response


from app.schemas.order import OrderStatusUpdate
from fastapi import status as http_status

@router.patch("/{order_id}/status")
def update_order_status(
    order_id: int,
    data: OrderStatusUpdate,
    db: Session = Depends(get_db),
    admin=Depends(admin_required)
):
    order = db.query(Order).filter(Order.order_id == order_id).first()

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    # ✅ VALID STATE TRANSITIONS
    if order.status == "pending" and data.status != "ready":
        raise HTTPException(
            status_code=400,
            detail="Pending order can only be marked as READY"
        )

    if order.status == "ready" and data.status != "picked":
        raise HTTPException(
            status_code=400,
            detail="Ready order can only be marked as PICKED"
        )

    if order.status == "picked":
        raise HTTPException(
            status_code=400,
            detail="Picked order cannot be updated"
        )

    order.status = data.status
    db.commit()
    db.refresh(order)

    return {
        "message": "Order status updated successfully",
        "order_id": order.order_id,
        "new_status": order.status
    }
