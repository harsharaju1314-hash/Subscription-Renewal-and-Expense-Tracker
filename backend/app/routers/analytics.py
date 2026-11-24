from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models.user import User
from backend.app.schemas.analytics import (
    ExpenseSummaryResponse,
    CategorySpendingResponse,
    TrendsResponse,
    BudgetUtilizationResponse,
)
from backend.app.services.analytics_service import AnalyticsService
from backend.app.routers.auth import get_current_user

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/summary", response_model=ExpenseSummaryResponse)
def get_expense_summary(
    bypass_cache: bool = Query(default=False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve comprehensive monthly and annual expense analytics and KPI metrics."""
    return AnalyticsService.get_expense_summary(
        db=db, user_id=current_user.id, use_cache=not bypass_cache
    )


@router.get("/categories", response_model=CategorySpendingResponse)
def get_category_spending(
    bypass_cache: bool = Query(default=False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve subscription expenditure breakdown grouped by category."""
    return AnalyticsService.get_category_spending(
        db=db, user_id=current_user.id, use_cache=not bypass_cache
    )


@router.get("/trends", response_model=TrendsResponse)
def get_spending_trends(
    months: int = Query(default=6, ge=1, le=24),
    bypass_cache: bool = Query(default=False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve historical monthly spending trends over the requested time horizon."""
    return AnalyticsService.get_monthly_spending_trends(
        db=db, user_id=current_user.id, months=months, use_cache=not bypass_cache
    )


@router.get("/budget", response_model=BudgetUtilizationResponse)
def get_budget_utilization(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve current subscription spend against monthly budget limit."""
    return AnalyticsService.get_budget_utilization(db=db, user_id=current_user.id)
