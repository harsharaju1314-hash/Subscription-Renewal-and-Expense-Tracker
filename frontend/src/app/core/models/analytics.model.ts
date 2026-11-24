export interface MostExpensiveItem {
  id: number;
  name: string;
  cost: number;
  billing_cycle: string;
  monthly_equivalent: number;
  category_name: string;
}

export interface ExpenseSummary {
  total_monthly_spend: number;
  total_annual_spend: number;
  active_subscriptions_count: number;
  total_subscriptions_count: number;
  upcoming_renewals_7d_count: number;
  upcoming_renewals_30d_count: number;
  monthly_budget: number;
  budget_utilization_pct: number;
  potential_monthly_savings: number;
  most_expensive_subscription?: MostExpensiveItem;
  cached: boolean;
}

export interface CategorySpendingItem {
  category_id: number;
  category_name: string;
  total_monthly_spend: number;
  count: number;
  percentage: number;
  color: string;
  icon: string;
}

export interface CategorySpendingResponse {
  items: CategorySpendingItem[];
  total_monthly: number;
  cached: boolean;
}

export interface MonthlySpendingTrendItem {
  month_label: string;
  year: number;
  month: number;
  total_spend: number;
  active_subscriptions_count: number;
}

export interface TrendsResponse {
  trends: MonthlySpendingTrendItem[];
  cached: boolean;
}

export interface BudgetUtilization {
  monthly_budget: number;
  current_monthly_spend: number;
  remaining_budget: number;
  utilization_percentage: number;
  is_over_budget: boolean;
  status_label: string;
}
