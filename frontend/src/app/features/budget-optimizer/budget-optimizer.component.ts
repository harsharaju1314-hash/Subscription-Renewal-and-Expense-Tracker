import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { OptimizationService } from '../../core/services/optimization.service';
import { SubscriptionService } from '../../core/services/subscription.service';
import { Subscription } from '../../core/models/subscription.model';
import {
  OptimizationResponse,
  OptimizationRequest,
} from '../../core/models/optimization.model';
import { NavbarComponent } from '../../shared/navbar/navbar.component';

@Component({
  selector: 'app-budget-optimizer',
  standalone: true,
  imports: [CommonModule, FormsModule, NavbarComponent],
  template: `
    <div class="optimizer-layout">
      <app-navbar title="Mathematical Budget Optimizer (MILP)"></app-navbar>

      <main class="page-content">
        <!-- Configuration Card -->
        <div class="saas-card config-card">
          <div class="config-header">
            <div>
              <h3>Linear Programming 0-1 Knapsack Solver</h3>
              <p>Configure your target monthly budget and adjust utility scores. The optimizer finds the optimal subset that maximizes total utility within your budget.</p>
            </div>
            <button class="btn-primary solve-btn" (click)="runOptimization()" [disabled]="solving">
              <span class="material-icons">auto_awesome</span>
              <span>{{ solving ? 'Solving MILP...' : 'Run Budget Optimization' }}</span>
            </button>
          </div>

          <div class="budget-slider-row">
            <div class="slider-left">
              <label for="budgetSlider">Target Monthly Budget Limit:</label>
              <div class="budget-input-wrap">
                <span class="currency-symbol">$</span>
                <input
                  id="budgetSlider"
                  type="number"
                  [(ngModel)]="targetBudget"
                  class="budget-num-input"
                  min="10"
                  max="2000"
                  step="5"
                />
                <span class="per-month">/ month</span>
              </div>
            </div>
            <input
              type="range"
              [(ngModel)]="targetBudget"
              min="20"
              max="500"
              step="5"
              class="budget-range-bar"
            />
          </div>
        </div>

        <!-- Optimization Results Showcase -->
        <div class="results-container" *ngIf="optimizationResult">
          <!-- Summary Metrics Banner -->
          <div class="metrics-banner saas-card">
            <div class="metric-col">
              <span class="m-label">Current Spend (Baseline)</span>
              <span class="m-val baseline-val">\${{ optimizationResult.baseline_monthly_spend.toFixed(2) }}/mo</span>
            </div>

            <div class="arrow-col">
              <span class="material-icons">trending_flat</span>
            </div>

            <div class="metric-col">
              <span class="m-label">Optimized Spend</span>
              <span class="m-val opt-val">\${{ optimizationResult.optimized_monthly_spend.toFixed(2) }}/mo</span>
            </div>

            <div class="metric-col highlight-col">
              <span class="m-label">Verified Monthly Savings</span>
              <span class="m-val savings-val">\${{ optimizationResult.total_monthly_savings.toFixed(2) }}/mo</span>
              <span class="savings-sub">
                \${{ (optimizationResult.total_monthly_savings * 12).toFixed(2) }}/year ({{ optimizationResult.savings_percentage.toFixed(1) }}% reduction)
              </span>
            </div>

            <div class="metric-col">
              <span class="m-label">Remaining Headroom</span>
              <span class="m-val">\${{ optimizationResult.budget_headroom_remaining.toFixed(2) }}</span>
              <span class="headroom-sub">{{ optimizationResult.is_budget_met ? 'Within Budget' : 'Exceeds Target' }}</span>
            </div>
          </div>

          <!-- Optimization Recommendation Lists Grid -->
          <div class="recommendations-grid">
            <!-- Retained Subscriptions -->
            <div class="saas-card list-card retain-card">
              <div class="list-card-header">
                <div class="header-title">
                  <span class="material-icons check-icon">check_circle</span>
                  <h4>Keep Subscriptions ({{ optimizationResult.retained_subscriptions.length }})</h4>
                </div>
                <span class="spend-pill">\${{ optimizationResult.optimized_monthly_spend.toFixed(2) }}/mo</span>
              </div>

              <div class="items-list">
                <div class="opt-item" *ngFor="let item of optimizationResult.retained_subscriptions">
                  <div class="item-info">
                    <strong>{{ item.name }}</strong>
                    <span class="item-cat">{{ item.category_name }} &bull; Utility: {{ item.utility_score }}/10</span>
                    <span class="item-reason">{{ item.reason }}</span>
                  </div>
                  <div class="item-cost">
                    \${{ item.monthly_cost.toFixed(2) }}/mo
                  </div>
                </div>
              </div>
            </div>

            <!-- Cancel Subscriptions -->
            <div class="saas-card list-card cancel-card">
              <div class="list-card-header">
                <div class="header-title">
                  <span class="material-icons cut-icon">cancel</span>
                  <h4>Recommended Cuts ({{ optimizationResult.cancelled_subscriptions.length }})</h4>
                </div>
                <span class="savings-pill">Save \${{ optimizationResult.total_monthly_savings.toFixed(2) }}/mo</span>
              </div>

              <div class="items-list">
                <div class="opt-item cancel-item" *ngFor="let item of optimizationResult.cancelled_subscriptions">
                  <div class="item-info">
                    <strong>{{ item.name }}</strong>
                    <span class="item-cat">{{ item.category_name }} &bull; Utility: {{ item.utility_score }}/10</span>
                    <span class="item-reason cut-reason">{{ item.reason }}</span>
                  </div>
                  <div class="item-cost cut-cost">
                    -\${{ item.monthly_cost.toFixed(2) }}/mo
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Interactive Preferences & Utility Overrides Table -->
        <div class="saas-card table-card">
          <div class="table-card-header">
            <h3>Subscription Preferences & Essential Toggles</h3>
            <p>Customize the optimizer's inputs. Marking a subscription as Essential locks it into the retained portfolio.</p>
          </div>

          <table class="saas-table">
            <thead>
              <tr>
                <th>Subscription</th>
                <th>Category</th>
                <th>Monthly Cost</th>
                <th>Essential? (Locked)</th>
                <th>Utility Score (1-10)</th>
              </tr>
            </thead>
            <tbody>
              <tr *ngFor="let sub of activeSubscriptions">
                <td><strong>{{ sub.name }}</strong></td>
                <td>{{ sub.category?.name || 'General' }}</td>
                <td><strong>\${{ sub.monthly_equivalent_cost.toFixed(2) }}/mo</strong></td>
                <td>
                  <label class="toggle-switch">
                    <input
                      type="checkbox"
                      [(ngModel)]="essentialOverrides[sub.id]"
                    />
                    <span class="slider"></span>
                  </label>
                </td>
                <td>
                  <div class="utility-slider-wrap">
                    <input
                      type="range"
                      min="1"
                      max="10"
                      [(ngModel)]="utilityOverrides[sub.id]"
                      class="utility-range"
                    />
                    <span class="util-val">{{ utilityOverrides[sub.id] }}/10</span>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </main>
    </div>
  `,
  styles: [`
    .optimizer-layout {
      margin-left: 260px;
      min-height: 100vh;
      background: #f8fafc;
    }
    .page-content {
      padding: 32px;
      display: flex;
      flex-direction: column;
      gap: 24px;
    }
    .config-card {
      display: flex;
      flex-direction: column;
      gap: 20px;
    }
    .config-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 16px;
    }
    .config-header h3 {
      font-size: 1.15rem;
      font-weight: 700;
      color: #0f172a;
    }
    .config-header p {
      font-size: 0.85rem;
      color: #64748b;
      margin-top: 4px;
      max-width: 700px;
    }
    .solve-btn {
      padding: 12px 20px;
      font-size: 0.95rem;
      white-space: nowrap;
    }
    .budget-slider-row {
      display: flex;
      flex-direction: column;
      gap: 12px;
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 8px;
      padding: 16px 20px;
    }
    .slider-left {
      display: flex;
      align-items: center;
      gap: 16px;
    }
    .slider-left label {
      font-weight: 600;
      color: #334155;
      font-size: 0.9rem;
    }
    .budget-input-wrap {
      display: flex;
      align-items: center;
      background: #ffffff;
      border: 1px solid #cbd5e1;
      border-radius: 6px;
      padding: 4px 10px;
    }
    .currency-symbol {
      font-weight: 700;
      color: #64748b;
    }
    .budget-num-input {
      border: none;
      outline: none;
      font-size: 1.1rem;
      font-weight: 700;
      color: #0f172a;
      width: 80px;
      padding: 2px 6px;
    }
    .per-month {
      font-size: 0.8rem;
      color: #64748b;
    }
    .budget-range-bar {
      width: 100%;
    }

    .results-container {
      display: flex;
      flex-direction: column;
      gap: 24px;
    }
    .metrics-banner {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 24px;
      background: #ffffff;
      flex-wrap: wrap;
      gap: 16px;
    }
    .metric-col {
      display: flex;
      flex-direction: column;
      gap: 4px;
    }
    .m-label {
      font-size: 0.75rem;
      text-transform: uppercase;
      font-weight: 700;
      color: #64748b;
      letter-spacing: 0.05em;
    }
    .m-val {
      font-size: 1.5rem;
      font-weight: 800;
      color: #0f172a;
    }
    .baseline-val {
      color: #64748b;
      text-decoration: line-through;
    }
    .opt-val {
      color: #4f46e5;
    }
    .arrow-col .material-icons {
      font-size: 32px;
      color: #94a3b8;
    }
    .highlight-col {
      background: #ecfdf5;
      padding: 12px 18px;
      border-radius: 8px;
      border: 1px solid #a7f3d0;
    }
    .savings-val {
      color: #059669;
    }
    .savings-sub {
      font-size: 0.78rem;
      font-weight: 600;
      color: #047857;
    }
    .headroom-sub {
      font-size: 0.78rem;
      color: #64748b;
    }

    .recommendations-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 24px;
    }
    @media (max-width: 900px) {
      .recommendations-grid { grid-template-columns: 1fr; }
    }
    .list-card {
      display: flex;
      flex-direction: column;
      gap: 16px;
    }
    .list-card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding-bottom: 12px;
      border-bottom: 1px solid #e2e8f0;
    }
    .header-title {
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .check-icon { color: #10b981; }
    .cut-icon { color: #ef4444; }
    .list-card-header h4 {
      font-size: 1.05rem;
      font-weight: 700;
      color: #0f172a;
    }
    .spend-pill {
      font-size: 0.8rem;
      font-weight: 700;
      color: #4f46e5;
      background: #eef2ff;
      padding: 4px 10px;
      border-radius: 9999px;
    }
    .savings-pill {
      font-size: 0.8rem;
      font-weight: 700;
      color: #dc2626;
      background: #fef2f2;
      padding: 4px 10px;
      border-radius: 9999px;
    }
    .items-list {
      display: flex;
      flex-direction: column;
      gap: 10px;
      max-height: 380px;
      overflow-y: auto;
    }
    .opt-item {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      padding: 12px;
      border-radius: 8px;
      background: #f8fafc;
      border: 1px solid #e2e8f0;
    }
    .cancel-item {
      background: #fff5f5;
      border-color: #fed7d7;
    }
    .item-info {
      display: flex;
      flex-direction: column;
      gap: 2px;
    }
    .item-cat {
      font-size: 0.78rem;
      color: #64748b;
    }
    .item-reason {
      font-size: 0.74rem;
      color: #059669;
      margin-top: 4px;
    }
    .cut-reason {
      color: #b91c1c;
    }
    .item-cost {
      font-weight: 700;
      color: #0f172a;
      font-size: 0.95rem;
      white-space: nowrap;
    }
    .cut-cost {
      color: #dc2626;
    }

    .table-card {
      padding: 0;
      overflow: hidden;
    }
    .table-card-header {
      padding: 20px 24px;
      border-bottom: 1px solid #e2e8f0;
    }
    .table-card-header h3 {
      font-size: 1.05rem;
      font-weight: 700;
      color: #0f172a;
    }
    .table-card-header p {
      font-size: 0.82rem;
      color: #64748b;
      margin-top: 4px;
    }
    .saas-table {
      width: 100%;
      border-collapse: collapse;
      text-align: left;
    }
    .saas-table th {
      background: #f8fafc;
      padding: 12px 24px;
      font-size: 0.75rem;
      font-weight: 700;
      color: #64748b;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      border-bottom: 1px solid #e2e8f0;
    }
    .saas-table td {
      padding: 12px 24px;
      border-bottom: 1px solid #f1f5f9;
      font-size: 0.88rem;
      vertical-align: middle;
    }

    /* Toggle switch */
    .toggle-switch {
      position: relative;
      display: inline-block;
      width: 44px;
      height: 24px;
    }
    .toggle-switch input {
      opacity: 0;
      width: 0;
      height: 0;
    }
    .slider {
      position: absolute;
      cursor: pointer;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background-color: #cbd5e1;
      transition: .2s;
      border-radius: 24px;
    }
    .slider:before {
      position: absolute;
      content: "";
      height: 18px;
      width: 18px;
      left: 3px;
      bottom: 3px;
      background-color: white;
      transition: .2s;
      border-radius: 50%;
    }
    input:checked + .slider {
      background-color: #4f46e5;
    }
    input:checked + .slider:before {
      transform: translateX(20px);
    }

    .utility-slider-wrap {
      display: flex;
      align-items: center;
      gap: 10px;
    }
    .utility-range {
      width: 100px;
    }
    .util-val {
      font-weight: 700;
      color: #0f172a;
      font-size: 0.85rem;
      min-width: 36px;
    }
  `]
})
export class BudgetOptimizerComponent implements OnInit {
  activeSubscriptions: Subscription[] = [];
  targetBudget: number = 180.00;
  utilityOverrides: Record<number, number> = {};
  essentialOverrides: Record<number, boolean> = {};

  solving: boolean = false;
  optimizationResult: OptimizationResponse | null = null;

  constructor(
    private optimizationService: OptimizationService,
    private subscriptionService: SubscriptionService
  ) {}

  ngOnInit(): void {
    this.loadActiveSubscriptions();
  }

  loadActiveSubscriptions(): void {
    this.subscriptionService.getSubscriptions({ status: 'ACTIVE' }).subscribe({
      next: (subs) => {
        this.activeSubscriptions = subs;
        subs.forEach(s => {
          this.utilityOverrides[s.id] = s.utility_score;
          this.essentialOverrides[s.id] = s.is_essential;
        });
      }
    });
  }

  runOptimization(): void {
    this.solving = true;

    const request: OptimizationRequest = {
      target_monthly_budget: this.targetBudget,
      custom_utility_overrides: this.utilityOverrides,
      custom_essential_overrides: this.essentialOverrides,
    };

    this.optimizationService.solve(request).subscribe({
      next: (result) => {
        this.solving = false;
        this.optimizationResult = result;
      },
      error: (err) => {
        this.solving = false;
        console.error('Optimization solver error', err);
      }
    });
  }
}
