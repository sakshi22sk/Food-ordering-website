from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.deps import get_db
from app.models.user import User
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from app.core.security import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])
@router.post("/register", response_model=TokenResponse)
def register(data: RegisterRequest, db: Session = Depends(get_db)):

    # check phone uniqueness
    if db.query(User).filter(User.phone == data.phone).first():
        raise HTTPException(
            status_code=400,
            detail="Phone already registered"
        )

    # check email uniqueness (if provided)
    if data.email:
        if db.query(User).filter(User.email == data.email).first():
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )

    user = User(
        name=data.name,
        phone=data.phone,
        email=data.email,
        password=hash_password(data.password),
        role="student"
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({
        "sub": str(user.user_id),
        "role": user.role
    })

    # ✅ RETURN ALL REQUIRED FIELDS
    return {
        "access_token": token,
        "name": user.name,
        "role": user.role
    }


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    if "@" in data.identifier:
        user = db.query(User).filter(
            User.email == data.identifier
        ).first()
    else:
        user = db.query(User).filter(
            User.phone == data.identifier
        ).first()
    
    if not user or not verify_password(data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    token = create_access_token({
        "sub": str(user.user_id),
        "role": user.role
    })
    # print(user.role)
    return {
        "access_token": token,
        "role": user.role,
        "name": user.name,
    }
