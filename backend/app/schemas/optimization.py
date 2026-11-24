from typing import List, Optional, Dict
from pydantic import BaseModel, Field


class OptimizationRequest(BaseModel):
    target_monthly_budget: Optional[float] = Field(None, gt=0)
    custom_utility_overrides: Optional[Dict[int, int]] = None
    custom_essential_overrides: Optional[Dict[int, bool]] = None


class OptimizedItem(BaseModel):
    id: int
    name: str
    category_name: str
    monthly_cost: float
    annual_cost: float
    utility_score: int
    is_essential: bool
    action: str  # "KEEP" | "CANCEL"
    reason: str


class OptimizationResponse(BaseModel):
    baseline_monthly_spend: float
    target_monthly_budget: float
    optimized_monthly_spend: float
    total_monthly_savings: float
    savings_percentage: float
    budget_headroom_remaining: float
    is_budget_met: bool
    essential_spend_total: float
    retained_subscriptions: List[OptimizedItem]
    cancelled_subscriptions: List[OptimizedItem]
    optimization_status: str
    solver_method: str
    summary_message: str
