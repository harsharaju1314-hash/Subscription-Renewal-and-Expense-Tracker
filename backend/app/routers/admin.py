from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.app.core.database import get_db
from backend.app.core.cache import cache
from backend.app.models.user import User
from backend.app.models.role import Role, UserRole
from backend.app.models.subscription import Subscription
from backend.app.models.expense import Expense
from backend.app.routers.auth import get_current_user, require_role, _build_user_response
from backend.app.schemas.auth import UserResponse

router = APIRouter(prefix="/admin", tags=["Administration"])


class RoleUpdateRequest(BaseModel):
    role: str  # "USER", "ANALYST", "ADMIN"


class UserStatusUpdateRequest(BaseModel):
    is_active: bool


@router.get("/users", response_model=List[UserResponse])
def list_users(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role(["ADMIN"])),
):
    """Admin endpoint: Retrieve list of registered application users and roles."""
    users = db.query(User).offset(skip).limit(limit).all()
    return [_build_user_response(u) for u in users]


@router.put("/users/{user_id}/role", response_model=UserResponse)
def update_user_role(
    user_id: int,
    req: RoleUpdateRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role(["ADMIN"])),
):
    """Admin endpoint: Assign or update role for a user."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    target_role = req.role.upper()
    role_obj = db.query(Role).filter(Role.name == target_role).first()
    if not role_obj:
        role_obj = Role(name=target_role, description=f"{target_role} Role")
        db.add(role_obj)
        db.commit()
        db.refresh(role_obj)

    # Check if already assigned
    existing = db.query(UserRole).filter(UserRole.user_id == user.id, UserRole.role_id == role_obj.id).first()
    if not existing:
        db.add(UserRole(user_id=user.id, role_id=role_obj.id))
        db.commit()
        db.refresh(user)

    return _build_user_response(user)


@router.put("/users/{user_id}/status", response_model=UserResponse)
def toggle_user_status(
    user_id: int,
    req: UserStatusUpdateRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role(["ADMIN"])),
):
    """Admin endpoint: Activate or deactivate a user account."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    user.is_active = req.is_active
    db.commit()
    db.refresh(user)
    return _build_user_response(user)


@router.get("/operations")
def get_operations_monitoring(
    db: Session = Depends(get_db),
    admin: User = Depends(require_role(["ADMIN"])),
):
    """Admin endpoint: Operational health, database row counts, cache metrics, and system status."""
    user_count = db.query(func.count(User.id)).scalar()
    sub_count = db.query(func.count(Subscription.id)).scalar()
    expense_count = db.query(func.count(Expense.id)).scalar()

    return {
        "status": "OPERATIONAL",
        "redis_connected": cache.is_redis_connected,
        "database": {
            "status": "connected",
            "total_users": user_count,
            "total_subscriptions": sub_count,
            "total_expense_records": expense_count,
        },
        "cache": {
            "enabled": True,
            "backend": "redis" if cache.is_redis_connected else "in-memory-fallback",
        },
    }
