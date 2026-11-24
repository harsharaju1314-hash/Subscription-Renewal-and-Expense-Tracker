from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.models.user import User
from backend.app.schemas.subscription import RenewalNoticeResponse
from backend.app.services.subscription_service import SubscriptionService
from backend.app.routers.auth import get_current_user

router = APIRouter(prefix="/renewals", tags=["Renewals"])


@router.get("/upcoming", response_model=List[RenewalNoticeResponse])
def get_upcoming_renewals(
    days: int = Query(default=30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve subscriptions renewing within the next N days with priority flags
    and proactive renewal alerts.
    """
    return SubscriptionService.get_upcoming_renewals(
        db=db, user_id=current_user.id, days_ahead=days
    )
