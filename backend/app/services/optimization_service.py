from typing import List, Dict, Optional, Tuple
import numpy as np
from sqlalchemy.orm import Session

try:
    from scipy.optimize import milp, LinearConstraint, Bounds
    SCIPY_MILP_AVAILABLE = True
except ImportError:
    SCIPY_MILP_AVAILABLE = False

from backend.app.models.subscription import Subscription, SubscriptionStatus
from backend.app.models.budget import Budget
from backend.app.schemas.optimization import (
    OptimizationRequest,
    OptimizedItem,
    OptimizationResponse,
)


class OptimizationService:

    @staticmethod
    def solve_budget_optimization(
        db: Session, user_id: int, request: OptimizationRequest
    ) -> OptimizationResponse:
        # Retrieve user active subscriptions
        active_subs = (
            db.query(Subscription)
            .filter(
                Subscription.user_id == user_id,
                Subscription.status == SubscriptionStatus.ACTIVE,
            )
            .all()
        )

        # Baseline budget
        if request.target_monthly_budget is not None:
            target_budget = float(request.target_monthly_budget)
        else:
            budget_obj = db.query(Budget).filter(Budget.user_id == user_id).first()
            target_budget = float(budget_obj.monthly_limit) if budget_obj else 200.00

        if not active_subs:
            return OptimizationResponse(
                baseline_monthly_spend=0.0,
                target_monthly_budget=target_budget,
                optimized_monthly_spend=0.0,
                total_monthly_savings=0.0,
                savings_percentage=0.0,
                budget_headroom_remaining=target_budget,
                is_budget_met=True,
                essential_spend_total=0.0,
                retained_subscriptions=[],
                cancelled_subscriptions=[],
                optimization_status="optimal",
                solver_method="No subscriptions to optimize",
                summary_message="No active subscriptions found for this account.",
            )

        # Apply custom overrides if provided in request
        utility_map = request.custom_utility_overrides or {}
        essential_map = request.custom_essential_overrides or {}

        items_data = []
        for s in active_subs:
            cost = round(s.monthly_equivalent_cost, 2)
            utility = utility_map.get(s.id, s.utility_score)
            is_ess = essential_map.get(s.id, s.is_essential)
            cat_name = s.category.name if s.category else "General"
            items_data.append({
                "sub": s,
                "id": s.id,
                "name": s.name,
                "category_name": cat_name,
                "cost": cost,
                "annual_cost": round(cost * 12.0, 2),
                "utility": utility,
                "is_essential": is_ess,
            })

        baseline_spend = sum(item["cost"] for item in items_data)

        # Partition into Essential and Optional sets
        essential_items = [it for it in items_data if it["is_essential"]]
        optional_items = [it for it in items_data if not it["is_essential"]]

        essential_spend = sum(it["cost"] for it in essential_items)
        retained_items: List[OptimizedItem] = []
        cancelled_items: List[OptimizedItem] = []

        # 1. Add all essentials to retained list
        for it in essential_items:
            retained_items.append(
                OptimizedItem(
                    id=it["id"],
                    name=it["name"],
                    category_name=it["category_name"],
                    monthly_cost=it["cost"],
                    annual_cost=it["annual_cost"],
                    utility_score=it["utility"],
                    is_essential=True,
                    action="KEEP",
                    reason="Essential subscription explicitly protected from cancellation.",
                )
            )

        remaining_budget = target_budget - essential_spend

        solver_method = "Mixed-Integer Linear Programming (scipy.optimize.milp)"
        status_str = "optimal"

        if remaining_budget <= 0:
            # Essential spend alone exceeds or meets budget
            # All optionals must be cancelled
            for it in optional_items:
                cancelled_items.append(
                    OptimizedItem(
                        id=it["id"],
                        name=it["name"],
                        category_name=it["category_name"],
                        monthly_cost=it["cost"],
                        annual_cost=it["annual_cost"],
                        utility_score=it["utility"],
                        is_essential=False,
                        action="CANCEL",
                        reason=f"Budget deficit: Essential subscriptions (${essential_spend:.2f}) exceed the target limit (${target_budget:.2f}).",
                    )
                )
            status_str = "budget_deficit"
        elif not optional_items:
            status_str = "optimal"
        else:
            # Solve 0-1 Knapsack using MILP or Greedy Knapsack fallback
            m = len(optional_items)
            costs = np.array([it["cost"] for it in optional_items], dtype=float)
            utilities = np.array([it["utility"] for it in optional_items], dtype=float)

            selection = [0] * m

            if SCIPY_MILP_AVAILABLE and m > 0:
                try:
                    # Objective: maximize sum(u_i * x_i) => minimize sum(-u_i * x_i)
                    c = -utilities
                    # Constraint: sum(c_i * x_i) <= remaining_budget
                    A = costs.reshape(1, -1)
                    constraints = LinearConstraint(A, 0, remaining_budget)
                    # Integrality: 1 for integer (binary 0 or 1)
                    integrality = np.ones(m)
                    bounds = Bounds(0, 1)

                    res = milp(c=c, integrality=integrality, bounds=bounds, constraints=constraints)
                    if res.success:
                        # Extract binary decisions
                        selection = [int(round(val)) for val in res.x]
                        status_str = "optimal"
                    else:
                        selection = OptimizationService._greedy_knapsack(costs, utilities, remaining_budget)
                        status_str = "heuristic_feasible"
                        solver_method = "Greedy Utility-Density Heuristic"
                except Exception:
                    selection = OptimizationService._greedy_knapsack(costs, utilities, remaining_budget)
                    status_str = "heuristic_feasible"
                    solver_method = "Greedy Utility-Density Heuristic"
            else:
                selection = OptimizationService._greedy_knapsack(costs, utilities, remaining_budget)
                status_str = "heuristic_feasible"
                solver_method = "Greedy Utility-Density Heuristic"

            for idx, it in enumerate(optional_items):
                if selection[idx] == 1:
                    retained_items.append(
                        OptimizedItem(
                            id=it["id"],
                            name=it["name"],
                            category_name=it["category_name"],
                            monthly_cost=it["cost"],
                            annual_cost=it["annual_cost"],
                            utility_score=it["utility"],
                            is_essential=False,
                            action="KEEP",
                            reason=f"High utility score ({it['utility']}/10) selected within ${remaining_budget:.2f} discretionary budget.",
                        )
                    )
                else:
                    cancelled_items.append(
                        OptimizedItem(
                            id=it["id"],
                            name=it["name"],
                            category_name=it["category_name"],
                            monthly_cost=it["cost"],
                            annual_cost=it["annual_cost"],
                            utility_score=it["utility"],
                            is_essential=False,
                            action="CANCEL",
                            reason=f"Recommended cut: saves ${it['cost']:.2f}/mo (utility score: {it['utility']}/10).",
                        )
                    )

        optimized_spend = sum(it.monthly_cost for it in retained_items)
        savings = max(0.0, baseline_spend - optimized_spend)
        savings_pct = (savings / baseline_spend * 100.0) if baseline_spend > 0 else 0.0
        headroom = max(0.0, target_budget - optimized_spend)
        is_met = optimized_spend <= target_budget

        msg = (
            f"Optimized spending to ${optimized_spend:.2f}/mo from baseline ${baseline_spend:.2f}/mo, "
            f"saving ${savings:.2f}/mo ({savings_pct:.1f}% reduction). "
            f"Kept {len(retained_items)} subscriptions, recommended cancelling {len(cancelled_items)}."
        )

        return OptimizationResponse(
            baseline_monthly_spend=round(baseline_spend, 2),
            target_monthly_budget=round(target_budget, 2),
            optimized_monthly_spend=round(optimized_spend, 2),
            total_monthly_savings=round(savings, 2),
            savings_percentage=round(savings_pct, 1),
            budget_headroom_remaining=round(headroom, 2),
            is_budget_met=is_met,
            essential_spend_total=round(essential_spend, 2),
            retained_subscriptions=retained_items,
            cancelled_subscriptions=cancelled_items,
            optimization_status=status_str,
            solver_method=solver_method,
            summary_message=msg,
        )

    @staticmethod
    def _greedy_knapsack(costs: np.ndarray, utilities: np.ndarray, budget: float) -> List[int]:
        """Greedy 0-1 Knapsack approximation based on utility-to-cost ratio."""
        n = len(costs)
        # Ratio of utility to cost
        ratios = [utilities[i] / max(costs[i], 0.01) for i in range(n)]
        sorted_indices = sorted(range(n), key=lambda i: ratios[i], reverse=True)

        selection = [0] * n
        spent = 0.0
        for idx in sorted_indices:
            if spent + costs[idx] <= budget + 1e-5:
                selection[idx] = 1
                spent += costs[idx]

        return selection
