from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.models.user import User
from backend.app.routers.auth import get_current_user
from backend.app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/expenses", tags=["Expenses"])


@router.get("/report")
def get_expenses_report(
    format: str = Query(default="json", pattern="^(json|csv)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve comprehensive monthly and yearly financial reports, category breakdowns,
    budget utilization, and redundancy forecasts. Supports both JSON and CSV export formats.
    """
    if format == "csv":
        csv_data = AnalyticsService.export_subscriptions_csv(db=db, user_id=current_user.id)
        return Response(
            content=csv_data,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=subscription_expenses_report.csv"},
        )

    return AnalyticsService.get_comprehensive_report(db=db, user_id=current_user.id)
