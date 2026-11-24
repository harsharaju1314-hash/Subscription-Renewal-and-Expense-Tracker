from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models.user import User
from backend.app.schemas.optimization import OptimizationRequest, OptimizationResponse
from backend.app.services.optimization_service import OptimizationService
from backend.app.routers.auth import get_current_user

router = APIRouter(prefix="/optimization", tags=["Budget Optimization"])


@router.post("/solve", response_model=OptimizationResponse)
def solve_budget_optimization(
    request: OptimizationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Solve the 0-1 Knapsack Mixed-Integer Linear Program to recommend optimal subscription cuts."""
    return OptimizationService.solve_budget_optimization(
        db=db, user_id=current_user.id, request=request
    )
