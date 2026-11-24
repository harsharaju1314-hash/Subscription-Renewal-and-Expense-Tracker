import { Component, OnInit, AfterViewInit, ViewChild, ElementRef, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router } from '@angular/router';
import { Chart, registerables } from 'chart.js';
import { AnalyticsService } from '../../core/services/analytics.service';
import { SubscriptionService } from '../../core/services/subscription.service';
import { ExpenseSummary, CategorySpendingResponse, TrendsResponse } from '../../core/models/analytics.model';
import { RenewalNotice } from '../../core/models/subscription.model';
import { KpiCardComponent } from '../../shared/kpi-card/kpi-card.component';
import { NavbarComponent } from '../../shared/navbar/navbar.component';

Chart.register(...registerables);

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, RouterModule, KpiCardComponent, NavbarComponent],
  template: `
    <div class="dashboard-layout">
      <app-navbar title="Executive Spending Dashboard"></app-navbar>

      <main class="dashboard-content">
        <!-- Top KPI Grid -->
        <section class="kpi-grid">
          <app-kpi-card
            title="Total Monthly Spend"
            [value]="summary ? '$' + summary.total_monthly_spend.toFixed(2) : '$0.00'"
            [subtitle]="summary ? 'Projected $' + summary.total_annual_spend.toFixed(2) + ' / year' : ''"
            icon="payments"
            iconBg="#eef2ff"
            iconColor="#4f46e5">
          </app-kpi-card>

          <app-kpi-card
            title="Active Subscriptions"
            [value]="summary ? summary.active_subscriptions_count.toString() : '0'"
            [subtitle]="summary ? summary.total_subscriptions_count + ' total on record' : ''"
            icon="subscriptions"
            iconBg="#ecfdf5"
            iconColor="#059669">
          </app-kpi-card>

          <app-kpi-card
            title="Renewals Next 7 Days"
            [value]="summary ? summary.upcoming_renewals_7d_count.toString() : '0'"
            [subtitle]="summary ? summary.upcoming_renewals_30d_count + ' renewing within 30 days' : ''"
            icon="event_repeat"
            iconBg="#fffbeb"
            iconColor="#d97706">
          </app-kpi-card>

          <app-kpi-card
            title="Potential Monthly Savings"
            [value]="summary ? '$' + summary.potential_monthly_savings.toFixed(2) : '$0.00'"
            subtitle="Identified via AI Utility Scoring"
            icon="savings"
            iconBg="#f0fdf4"
            iconColor="#16a34a"
            [highlightSubtitle]="true">
          </app-kpi-card>
        </section>

        <!-- Budget Utilization Card -->
        <section class="saas-card budget-meter-card" *ngIf="summary">
          <div class="budget-header">
            <div>
              <h3>Monthly Budget Utilization</h3>
              <p class="budget-desc">
                Current recurring spend: <strong>\${{ summary.total_monthly_spend.toFixed(2) }}</strong> of
                <strong>\${{ summary.monthly_budget.toFixed(2) }}</strong> limit
              </p>
            </div>
            <div class="budget-badge" [ngClass]="getBudgetStatusClass()">
              {{ summary.budget_utilization_pct.toFixed(1) }}% Used
            </div>
          </div>
          <div class="progress-bar-bg">
            <div
              class="progress-bar-fill"
              [style.width.%]="Math.min(summary.budget_utilization_pct, 100)"
              [ngClass]="getBudgetFillClass()">
            </div>
          </div>
        </section>

        <!-- Charts Grid -->
        <section class="charts-grid">
          <!-- Trends Line Chart -->
          <div class="saas-card chart-card">
            <div class="chart-header">
              <div>
                <h3>Spending Run-Rate Trends</h3>
                <span class="chart-subtitle">Monthly expense projection & actual payments</span>
              </div>
              <span class="cache-pill" *ngIf="trendsCached">Redis Cached</span>
            </div>
            <div class="canvas-container">
              <canvas #trendChartCanvas></canvas>
            </div>
          </div>

          <!-- Category Doughnut Chart -->
          <div class="saas-card chart-card">
            <div class="chart-header">
              <div>
                <h3>Expenditure by Category</h3>
                <span class="chart-subtitle">Monthly spend distribution</span>
              </div>
              <span class="cache-pill" *ngIf="categoriesCached">Redis Cached</span>
            </div>
            <div class="canvas-container doughnut-container">
              <canvas #categoryChartCanvas></canvas>
            </div>
          </div>
        </section>

        <!-- Lower Section: Upcoming Renewals & AI Quick Prompts -->
        <section class="bottom-grid">
          <!-- Upcoming Renewals List -->
          <div class="saas-card renewals-card">
            <div class="section-title-row">
              <h3>Upcoming Renewals (Next 14 Days)</h3>
              <a routerLink="/renewals" class="view-all-link">View Full Calendar &rarr;</a>
            </div>

            <div *ngIf="upcomingRenewals.length === 0" class="empty-state">
              <span class="material-icons">task_alt</span>
              <p>No renewals due in the next 14 days.</p>
            </div>

            <div class="renewals-list" *ngIf="upcomingRenewals.length > 0">
              <div class="renewal-row" *ngFor="let item of upcomingRenewals">
                <div class="renewal-left">
                  <span class="item-name">{{ item.name }}</span>
                  <span class="item-category">{{ item.category_name }} &bull; {{ item.billing_cycle }}</span>
                </div>
                <div class="renewal-right">
                  <span class="item-cost">\${{ item.cost.toFixed(2) }}</span>
                  <span class="days-pill" [class.urgent]="item.days_left <= 3">
                    {{ item.days_left === 0 ? 'Today' : (item.days_left === 1 ? 'Tomorrow' : 'in ' + item.days_left + ' days') }}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- AI Assistant Quick Prompts Widget -->
          <div class="saas-card ai-prompts-card">
            <div class="ai-widget-header">
              <div class="ai-title-wrap">
                <span class="material-icons sparkle-icon">psychology</span>
                <h3>AI Financial Copilot</h3>
              </div>
              <span class="rag-badge">RAG Powered</span>
            </div>
            <p class="ai-sub">Ask instant questions grounded strictly in your real subscriptions:</p>

            <div class="prompts-list">
              <button class="prompt-chip" (click)="askPrompt('How much am I spending every month?')">
                <span class="material-icons">chat</span>
                "How much am I spending every month?"
              </button>
              <button class="prompt-chip" (click)="askPrompt('Which subscriptions cost me the most?')">
                <span class="material-icons">chat</span>
                "Which subscriptions cost me the most?"
              </button>
              <button class="prompt-chip" (click)="askPrompt('What subscriptions renew next week?')">
                <span class="material-icons">chat</span>
                "What subscriptions renew next week?"
              </button>
              <button class="prompt-chip" (click)="askPrompt('How can I reduce my monthly expenses?')">
                <span class="material-icons">chat</span>
                "How can I reduce my monthly expenses?"
              </button>
            </div>

            <div class="optimizer-cta" routerLink="/budget-optimizer">
              <span class="material-icons">tune</span>
              <div>
                <strong>Need deeper optimization?</strong>
                <p>Run the 0-1 Knapsack MILP algorithm on your budget</p>
              </div>
            </div>
          </div>
        </section>
      </main>
    </div>
  `,
  styles: [`
    .dashboard-layout {
      margin-left: 260px;
      min-height: 100vh;
      background: #f8fafc;
    }
    .dashboard-content {
      padding: 32px;
      display: flex;
      flex-direction: column;
      gap: 24px;
    }
    .kpi-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
      gap: 20px;
    }
    .budget-meter-card {
      display: flex;
      flex-direction: column;
      gap: 12px;
    }
    .budget-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .budget-header h3 {
      font-size: 1.05rem;
      font-weight: 700;
      color: #0f172a;
    }
    .budget-desc {
      font-size: 0.85rem;
      color: #64748b;
      margin-top: 2px;
    }
    .budget-badge {
      padding: 6px 14px;
      border-radius: 9999px;
      font-size: 0.8rem;
      font-weight: 700;
    }
    .badge-healthy {
      background: #ecfdf5;
      color: #059669;
    }
    .badge-warning {
      background: #fffbeb;
      color: #d97706;
    }
    .badge-danger {
      background: #fef2f2;
      color: #dc2626;
    }
    .progress-bar-bg {
      height: 10px;
      background: #e2e8f0;
      border-radius: 6px;
      overflow: hidden;
    }
    .progress-bar-fill {
      height: 100%;
      border-radius: 6px;
      transition: width 0.6s ease;
    }
    .fill-healthy { background: #10b981; }
    .fill-warning { background: #f59e0b; }
    .fill-danger { background: #ef4444; }

    .charts-grid {
      display: grid;
      grid-template-columns: 2fr 1fr;
      gap: 24px;
    }
    @media (max-width: 1024px) {
      .charts-grid { grid-template-columns: 1fr; }
    }
    .chart-card {
      display: flex;
      flex-direction: column;
      gap: 16px;
    }
    .chart-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
    }
    .chart-header h3 {
      font-size: 1.05rem;
      font-weight: 700;
      color: #0f172a;
    }
    .chart-subtitle {
      font-size: 0.8rem;
      color: #64748b;
    }
    .cache-pill {
      background: #f1f5f9;
      color: #475569;
      font-size: 0.7rem;
      font-weight: 700;
      padding: 3px 8px;
      border-radius: 4px;
      border: 1px solid #cbd5e1;
    }
    .canvas-container {
      position: relative;
      height: 280px;
      width: 100%;
    }
    .doughnut-container {
      height: 280px;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .bottom-grid {
      display: grid;
      grid-template-columns: 1.2fr 1fr;
      gap: 24px;
    }
    @media (max-width: 1024px) {
      .bottom-grid { grid-template-columns: 1fr; }
    }
    .section-title-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 16px;
    }
    .section-title-row h3 {
      font-size: 1.05rem;
      font-weight: 700;
      color: #0f172a;
    }
    .view-all-link {
      font-size: 0.82rem;
      font-weight: 600;
      color: #4f46e5;
      text-decoration: none;
    }
    .renewals-list {
      display: flex;
      flex-direction: column;
      gap: 10px;
    }
    .renewal-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 12px;
      background: #f8fafc;
      border-radius: 8px;
      border: 1px solid #e2e8f0;
    }
    .renewal-left {
      display: flex;
      flex-direction: column;
    }
    .item-name {
      font-size: 0.92rem;
      font-weight: 600;
      color: #1e293b;
    }
    .item-category {
      font-size: 0.78rem;
      color: #64748b;
    }
    .renewal-right {
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .item-cost {
      font-weight: 700;
      color: #0f172a;
      font-size: 0.95rem;
    }
    .days-pill {
      font-size: 0.75rem;
      font-weight: 600;
      padding: 4px 8px;
      border-radius: 6px;
      background: #e0e7ff;
      color: #4338ca;
    }
    .days-pill.urgent {
      background: #fee2e2;
      color: #dc2626;
    }
    .empty-state {
      text-align: center;
      padding: 30px;
      color: #64748b;
    }
    .empty-state .material-icons {
      font-size: 32px;
      color: #10b981;
      margin-bottom: 8px;
    }

    .ai-widget-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 8px;
    }
    .ai-title-wrap {
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .sparkle-icon {
      color: #6366f1;
    }
    .rag-badge {
      background: linear-gradient(135deg, #6366f1, #4f46e5);
      color: #ffffff;
      font-size: 0.7rem;
      font-weight: 700;
      padding: 2px 8px;
      border-radius: 4px;
    }
    .ai-sub {
      font-size: 0.82rem;
      color: #64748b;
      margin-bottom: 14px;
    }
    .prompts-list {
      display: flex;
      flex-direction: column;
      gap: 8px;
      margin-bottom: 16px;
    }
    .prompt-chip {
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 8px;
      padding: 10px 14px;
      font-size: 0.85rem;
      color: #1e293b;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 8px;
      text-align: left;
      transition: all 0.15s;
    }
    .prompt-chip:hover {
      background: #eef2ff;
      border-color: #c7d2fe;
      color: #4338ca;
    }
    .prompt-chip .material-icons {
      font-size: 16px;
      color: #6366f1;
    }
    .optimizer-cta {
      display: flex;
      align-items: center;
      gap: 12px;
      background: linear-gradient(135deg, #f8fafc, #eef2ff);
      border: 1px dashed #6366f1;
      padding: 14px;
      border-radius: 8px;
      cursor: pointer;
      color: #1e293b;
    }
    .optimizer-cta .material-icons {
      color: #4f46e5;
      font-size: 26px;
    }
    .optimizer-cta strong {
      font-size: 0.88rem;
    }
    .optimizer-cta p {
      font-size: 0.78rem;
      color: #64748b;
    }
  `]
})
export class DashboardComponent implements OnInit, AfterViewInit, OnDestroy {
  @ViewChild('trendChartCanvas') trendChartRef!: ElementRef<HTMLCanvasElement>;
  @ViewChild('categoryChartCanvas') categoryChartRef!: ElementRef<HTMLCanvasElement>;

  summary: ExpenseSummary | null = null;
  upcomingRenewals: RenewalNotice[] = [];
  trendsCached: boolean = false;
  categoriesCached: boolean = false;
  Math = Math;

  private trendChart?: Chart;
  private categoryChart?: Chart;

  constructor(
    private analyticsService: AnalyticsService,
    private subscriptionService: SubscriptionService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.loadSummary();
    this.loadRenewals();
  }

  ngAfterViewInit(): void {
    this.loadTrendsAndRender();
    this.loadCategoriesAndRender();
  }

  ngOnDestroy(): void {
    this.trendChart?.destroy();
    this.categoryChart?.destroy();
  }

  loadSummary(): void {
    this.analyticsService.getSummary().subscribe({
      next: (data) => this.summary = data,
      error: (err) => console.error('Failed to load expense summary', err)
    });
  }

  loadRenewals(): void {
    this.subscriptionService.getUpcomingRenewals(14).subscribe({
      next: (data) => this.upcomingRenewals = data.slice(0, 5),
      error: (err) => console.error('Failed to load upcoming renewals', err)
    });
  }

  loadTrendsAndRender(): void {
    this.analyticsService.getTrends(6).subscribe({
      next: (data) => {
        this.trendsCached = data.cached;
        const labels = data.trends.map(t => t.month_label);
        const values = data.trends.map(t => t.total_spend);

        if (this.trendChartRef) {
          const ctx = this.trendChartRef.nativeElement.getContext('2d');
          if (ctx) {
            this.trendChart = new Chart(ctx, {
              type: 'line',
              data: {
                labels,
                datasets: [{
                  label: 'Monthly Expense ($)',
                  data: values,
                  borderColor: '#4f46e5',
                  backgroundColor: 'rgba(79, 70, 229, 0.08)',
                  fill: true,
                  tension: 0.35,
                  pointRadius: 4,
                  pointHoverRadius: 6,
                  borderWidth: 2,
                }]
              },
              options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                  legend: { display: false },
                  tooltip: {
                    callbacks: {
                      label: (ctx) => ` \$${Number(ctx.parsed.y).toFixed(2)}`
                    }
                  }
                },
                scales: {
                  y: {
                    beginAtZero: true,
                    grid: { color: '#f1f5f9' },
                    ticks: {
                      callback: (v) => `\$${v}`
                    }
                  },
                  x: {
                    grid: { display: false }
                  }
                }
              }
            });
          }
        }
      }
    });
  }

  loadCategoriesAndRender(): void {
    this.analyticsService.getCategorySpending().subscribe({
      next: (data) => {
        this.categoriesCached = data.cached;
        const labels = data.items.map(i => i.category_name);
        const values = data.items.map(i => i.total_monthly_spend);
        const colors = data.items.map(i => i.color || '#4f46e5');

        if (this.categoryChartRef) {
          const ctx = this.categoryChartRef.nativeElement.getContext('2d');
          if (ctx) {
            this.categoryChart = new Chart(ctx, {
              type: 'doughnut',
              data: {
                labels,
                datasets: [{
                  data: values,
                  backgroundColor: colors,
                  borderWidth: 2,
                  borderColor: '#ffffff',
                }]
              },
              options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                  legend: {
                    position: 'bottom',
                    labels: { boxWidth: 12, font: { size: 11 } }
                  },
                  tooltip: {
                    callbacks: {
                      label: (ctx) => ` ${ctx.label}: \$${Number(ctx.parsed).toFixed(2)}`
                    }
                  }
                },
                cutout: '70%'
              }
            });
          }
        }
      }
    });
  }

  getBudgetStatusClass(): string {
    if (!this.summary) return 'badge-healthy';
    if (this.summary.budget_utilization_pct > 100) return 'badge-danger';
    if (this.summary.budget_utilization_pct >= 80) return 'badge-warning';
    return 'badge-healthy';
  }

  getBudgetFillClass(): string {
    if (!this.summary) return 'fill-healthy';
    if (this.summary.budget_utilization_pct > 100) return 'fill-danger';
    if (this.summary.budget_utilization_pct >= 80) return 'fill-warning';
    return 'fill-healthy';
  }

  askPrompt(query: string): void {
    this.router.navigate(['/ai-assistant'], { queryParams: { prompt: query } });
  }
}
