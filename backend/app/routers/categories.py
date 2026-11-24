from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models.category import Category
from backend.app.schemas.category import CategoryCreate, CategoryResponse
from backend.app.routers.auth import get_current_user
from backend.app.models.user import User

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("", response_model=List[CategoryResponse])
def list_categories(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    return db.query(Category).order_by(Category.name.asc()).all()


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    cat_in: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = db.query(Category).filter(Category.name.ilike(cat_in.name)).first()
    if existing:
        return existing

    cat = Category(
        name=cat_in.name,
        description=cat_in.description,
        icon=cat_in.icon or "category",
        color=cat_in.color or "#4f46e5",
    )
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat
