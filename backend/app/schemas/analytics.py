from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class MostExpensiveItem(BaseModel):
    id: int
    name: str
    cost: float
    billing_cycle: str
    monthly_equivalent: float
    category_name: str


class ExpenseSummaryResponse(BaseModel):
    total_monthly_spend: float
    total_annual_spend: float
    active_subscriptions_count: int
    total_subscriptions_count: int
    upcoming_renewals_7d_count: int
    upcoming_renewals_30d_count: int
    monthly_budget: float
    budget_utilization_pct: float
    potential_monthly_savings: float
    most_expensive_subscription: Optional[MostExpensiveItem] = None
    cached: bool = False


class CategorySpendingItem(BaseModel):
    category_id: int
    category_name: str
    total_monthly_spend: float
    count: int
    percentage: float
    color: str
    icon: str


class CategorySpendingResponse(BaseModel):
    items: List[CategorySpendingItem]
    total_monthly: float
    cached: bool = False


class MonthlySpendingTrendItem(BaseModel):
    month_label: str
    year: int
    month: int
    total_spend: float
    active_subscriptions_count: int


class TrendsResponse(BaseModel):
    trends: List[MonthlySpendingTrendItem]
    cached: bool = False


class BudgetUtilizationResponse(BaseModel):
    monthly_budget: float
    current_monthly_spend: float
    remaining_budget: float
    utilization_percentage: float
    is_over_budget: bool
    status_label: str
