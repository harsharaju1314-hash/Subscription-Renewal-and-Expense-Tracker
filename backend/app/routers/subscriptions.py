from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models.user import User
from backend.app.models.subscription import SubscriptionStatus
from backend.app.schemas.subscription import (
    SubscriptionCreate,
    SubscriptionUpdate,
    SubscriptionResponse,
    RenewalNoticeResponse,
)
from backend.app.services.subscription_service import SubscriptionService
from backend.app.routers.auth import get_current_user

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])


@router.get("", response_model=List[SubscriptionResponse])
def get_subscriptions(
    status: Optional[SubscriptionStatus] = None,
    category_id: Optional[int] = None,
    search: Optional[str] = None,
    sort_by: Optional[str] = Query(default="renewal_date"),
    order: Optional[str] = Query(default="asc"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve all subscriptions for the authenticated user with optional filtering and sorting."""
    return SubscriptionService.get_subscriptions(
        db=db,
        user_id=current_user.id,
        status=status,
        category_id=category_id,
        search=search,
        sort_by=sort_by,
        order=order,
    )


@router.get("/renewals", response_model=List[RenewalNoticeResponse])
@router.get("/renewals/upcoming", response_model=List[RenewalNoticeResponse])
def get_upcoming_renewals(
    days: int = Query(default=30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve subscriptions renewing within the next N days."""
    return SubscriptionService.get_upcoming_renewals(
        db=db, user_id=current_user.id, days_ahead=days
    )


@router.post("", response_model=SubscriptionResponse, status_code=status.HTTP_201_CREATED)
def create_subscription(
    sub_in: SubscriptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add a new subscription for the authenticated user."""
    return SubscriptionService.create_subscription(
        db=db, sub_in=sub_in, user_id=current_user.id
    )


@router.get("/{subscription_id}", response_model=SubscriptionResponse)
def get_subscription(
    subscription_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get single subscription details. Validates user ownership."""
    sub = SubscriptionService.get_subscription_by_id(
        db=db, sub_id=subscription_id, user_id=current_user.id
    )
    if not sub:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subscription with ID {subscription_id} not found.",
        )
    from backend.app.services.subscription_service import _format_subscription_response
    return _format_subscription_response(sub)


@router.put("/{subscription_id}", response_model=SubscriptionResponse)
def update_subscription(
    subscription_id: int,
    sub_in: SubscriptionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update an existing subscription. Validates user ownership."""
    updated = SubscriptionService.update_subscription(
        db=db, sub_id=subscription_id, sub_in=sub_in, user_id=current_user.id
    )
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subscription with ID {subscription_id} not found or unauthorized.",
        )
    return updated


@router.delete("/{subscription_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_subscription(
    subscription_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a subscription. Validates user ownership."""
    deleted = SubscriptionService.delete_subscription(
        db=db, sub_id=subscription_id, user_id=current_user.id
    )
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subscription with ID {subscription_id} not found or unauthorized.",
        )
    return None
