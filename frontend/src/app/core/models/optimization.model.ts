export interface OptimizedItem {
  id: number;
  name: string;
  category_name: string;
  monthly_cost: number;
  annual_cost: number;
  utility_score: number;
  is_essential: boolean;
  action: 'KEEP' | 'CANCEL';
  reason: string;
}

export interface OptimizationResponse {
  baseline_monthly_spend: number;
  target_monthly_budget: number;
  optimized_monthly_spend: number;
  total_monthly_savings: number;
  savings_percentage: number;
  budget_headroom_remaining: number;
  is_budget_met: boolean;
  essential_spend_total: number;
  retained_subscriptions: OptimizedItem[];
  cancelled_subscriptions: OptimizedItem[];
  optimization_status: string;
  solver_method: string;
  summary_message: string;
}

export interface OptimizationRequest {
  target_monthly_budget?: number;
  custom_utility_overrides?: Record<number, number>;
  custom_essential_overrides?: Record<number, boolean>;
}
