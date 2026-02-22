from fastapi import APIRouter, Depends
from app.core.security import get_current_user

router = APIRouter(prefix="/test", tags=["Test"])

@router.get("/me")
def my_profile(current_user=Depends(get_current_user)):
    return {
        "user_id": current_user.user_id,
        "name": current_user.name,
        "role": current_user.role
    }


from app.core.security import admin_required

@router.get("/admin")
def admin_area(admin=Depends(admin_required)):
    return {"message": "Welcome Admin"}
