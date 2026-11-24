import { Component, OnInit, AfterViewInit, ViewChild, ElementRef, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Chart, registerables } from 'chart.js';
import { AnalyticsService } from '../../core/services/analytics.service';
import { SubscriptionService } from '../../core/services/subscription.service';
import { CategorySpendingItem, MonthlySpendingTrendItem } from '../../core/models/analytics.model';
import { Subscription } from '../../core/models/subscription.model';
import { NavbarComponent } from '../../shared/navbar/navbar.component';

Chart.register(...registerables);

@Component({
  selector: 'app-analytics',
  standalone: true,
  imports: [CommonModule, NavbarComponent],
  template: `
    <div class="analytics-layout">
      <app-navbar title="In-Depth Expense Analytics"></app-navbar>

      <main class="page-content">
        <!-- Controls & Latency Benchmark Bar -->
        <div class="controls-bar saas-card">
          <div class="bench-info">
            <span class="material-icons info-icon">speed</span>
            <div>
              <strong>Redis Performance Profiling</strong>
              <p>Compare response times with and without Redis caching layer.</p>
            </div>
          </div>
          <div class="bench-actions">
            <span class="latency-indicator" *ngIf="lastLatencyMs !== null">
              Last Response: <strong>{{ lastLatencyMs }} ms</strong>
              <span class="cache-badge" [class.hit]="wasCached">{{ wasCached ? 'Cache HIT' : 'Cache MISS / Uncached' }}</span>
            </span>
            <button class="btn-secondary" (click)="refreshData(true)">
              <span class="material-icons">refresh</span>
              Bypass Cache & Re-measure
            </button>
          </div>
        </div>

        <!-- Charts Row 1: Line & Doughnut -->
        <div class="charts-row">
          <div class="saas-card chart-card">
            <div class="card-header">
              <h3>Monthly Spending Trend (Last 6 Months)</h3>
              <span class="subtitle">Calculated baseline vs. actual expense records</span>
            </div>
            <div class="canvas-wrap">
              <canvas #trendCanvas></canvas>
            </div>
          </div>

          <div class="saas-card chart-card">
            <div class="card-header">
              <h3>Category Spend Distribution</h3>
              <span class="subtitle">Percentage breakdown of total monthly spend</span>
            </div>
            <div class="canvas-wrap doughnut-wrap">
              <canvas #doughnutCanvas></canvas>
            </div>
          </div>
        </div>

        <!-- Charts Row 2: Top 5 Bar Chart -->
        <div class="saas-card chart-card">
          <div class="card-header">
            <h3>Top 5 Most Expensive Subscriptions</h3>
            <span class="subtitle">Normalized monthly commitment per service</span>
          </div>
          <div class="canvas-wrap bar-wrap">
            <canvas #barCanvas></canvas>
          </div>
        </div>

        <!-- Detailed Category Breakdown Table -->
        <div class="saas-card table-card">
          <div class="card-header">
            <h3>Category Expense Portfolio</h3>
            <span class="subtitle">Aggregated totals and distribution percentages</span>
          </div>

          <table class="saas-table">
            <thead>
              <tr>
                <th>Category</th>
                <th>Subscriptions Count</th>
                <th>Monthly Run-Rate</th>
                <th>Annual Projection</th>
                <th>% of Total Spend</th>
              </tr>
            </thead>
            <tbody>
              <tr *ngFor="let cat of categoryItems">
                <td>
                  <div class="cat-cell">
                    <span class="color-dot" [style.background-color]="cat.color"></span>
                    <strong>{{ cat.category_name }}</strong>
                  </div>
                </td>
                <td>{{ cat.count }} active</td>
                <td><strong class="cost-bold">\${{ cat.total_monthly_spend.toFixed(2) }}</strong></td>
                <td>\${{ (cat.total_monthly_spend * 12).toFixed(2) }}</td>
                <td>
                  <div class="pct-cell">
                    <div class="pct-bar-bg">
                      <div class="pct-bar-fill" [style.width.%]="cat.percentage" [style.background-color]="cat.color"></div>
                    </div>
                    <span>{{ cat.percentage.toFixed(1) }}%</span>
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
    .analytics-layout {
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
    .controls-bar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 16px;
    }
    .bench-info {
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .info-icon {
      color: #6366f1;
      font-size: 28px;
    }
    .bench-info strong {
      font-size: 0.95rem;
      color: #0f172a;
    }
    .bench-info p {
      font-size: 0.82rem;
      color: #64748b;
    }
    .bench-actions {
      display: flex;
      align-items: center;
      gap: 16px;
    }
    .latency-indicator {
      font-size: 0.85rem;
      color: #334155;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .cache-badge {
      font-size: 0.72rem;
      font-weight: 700;
      padding: 3px 8px;
      border-radius: 4px;
      background: #f1f5f9;
      color: #475569;
    }
    .cache-badge.hit {
      background: #ecfdf5;
      color: #065f46;
    }

    .charts-row {
      display: grid;
      grid-template-columns: 2fr 1fr;
      gap: 24px;
    }
    @media (max-width: 1024px) {
      .charts-row { grid-template-columns: 1fr; }
    }
    .chart-card {
      display: flex;
      flex-direction: column;
      gap: 16px;
    }
    .card-header h3 {
      font-size: 1.05rem;
      font-weight: 700;
      color: #0f172a;
    }
    .card-header .subtitle {
      font-size: 0.8rem;
      color: #64748b;
    }
    .canvas-wrap {
      position: relative;
      height: 280px;
      width: 100%;
    }
    .doughnut-wrap {
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .bar-wrap {
      height: 240px;
    }

    .table-card {
      padding: 0;
      overflow: hidden;
    }
    .table-card .card-header {
      padding: 20px 24px;
      border-bottom: 1px solid #e2e8f0;
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
      padding: 14px 24px;
      border-bottom: 1px solid #f1f5f9;
      font-size: 0.88rem;
      vertical-align: middle;
    }
    .cat-cell {
      display: flex;
      align-items: center;
      gap: 10px;
    }
    .color-dot {
      width: 10px;
      height: 10px;
      border-radius: 50%;
    }
    .cost-bold {
      color: #0f172a;
    }
    .pct-cell {
      display: flex;
      align-items: center;
      gap: 12px;
      min-width: 120px;
    }
    .pct-bar-bg {
      flex: 1;
      height: 6px;
      background: #e2e8f0;
      border-radius: 3px;
      overflow: hidden;
    }
    .pct-bar-fill {
      height: 100%;
      border-radius: 3px;
    }
  `]
})
export class AnalyticsComponent implements OnInit, AfterViewInit, OnDestroy {
  @ViewChild('trendCanvas') trendCanvasRef!: ElementRef<HTMLCanvasElement>;
  @ViewChild('doughnutCanvas') doughnutCanvasRef!: ElementRef<HTMLCanvasElement>;
  @ViewChild('barCanvas') barCanvasRef!: ElementRef<HTMLCanvasElement>;

  categoryItems: CategorySpendingItem[] = [];
  lastLatencyMs: number | null = null;
  wasCached: boolean = false;

  private trendChart?: Chart;
  private doughnutChart?: Chart;
  private barChart?: Chart;

  constructor(
    private analyticsService: AnalyticsService,
    private subscriptionService: SubscriptionService
  ) {}

  ngOnInit(): void {
    this.loadData(false);
  }

  ngAfterViewInit(): void {
    // Canvas initialized after view
  }

  ngOnDestroy(): void {
    this.trendChart?.destroy();
    this.doughnutChart?.destroy();
    this.barChart?.destroy();
  }

  refreshData(bypass: boolean): void {
    this.loadData(bypass);
  }

  loadData(bypass: boolean): void {
    const t0 = performance.now();
    this.analyticsService.getCategorySpending(bypass).subscribe({
      next: (data) => {
        const t1 = performance.now();
        this.lastLatencyMs = Math.round(t1 - t0);
        this.wasCached = data.cached;
        this.categoryItems = data.items;
        this.renderCategoryDoughnut(data.items);
      }
    });

    this.analyticsService.getTrends(6, bypass).subscribe({
      next: (data) => {
        this.renderTrendsLine(data.trends);
      }
    });

    this.subscriptionService.getSubscriptions({ status: 'ACTIVE' }).subscribe({
      next: (subs) => {
        const sorted = [...subs].sort((a, b) => b.monthly_equivalent_cost - a.monthly_equivalent_cost).slice(0, 5);
        this.renderTopBars(sorted);
      }
    });
  }

  renderTrendsLine(trends: MonthlySpendingTrendItem[]): void {
    if (!this.trendCanvasRef) return;
    this.trendChart?.destroy();

    const ctx = this.trendCanvasRef.nativeElement.getContext('2d');
    if (!ctx) return;

    this.trendChart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: trends.map(t => t.month_label),
        datasets: [{
          label: 'Monthly Expense ($)',
          data: trends.map(t => t.total_spend),
          borderColor: '#4f46e5',
          backgroundColor: 'rgba(79, 70, 229, 0.1)',
          fill: true,
          tension: 0.35,
          borderWidth: 2,
          pointRadius: 5,
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          y: {
            beginAtZero: true,
            grid: { color: '#f1f5f9' },
            ticks: { callback: (v) => `\$${v}` }
          },
          x: { grid: { display: false } }
        }
      }
    });
  }

  renderCategoryDoughnut(items: CategorySpendingItem[]): void {
    if (!this.doughnutCanvasRef) return;
    this.doughnutChart?.destroy();

    const ctx = this.doughnutCanvasRef.nativeElement.getContext('2d');
    if (!ctx) return;

    this.doughnutChart = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: items.map(i => i.category_name),
        datasets: [{
          data: items.map(i => i.total_monthly_spend),
          backgroundColor: items.map(i => i.color || '#4f46e5'),
          borderWidth: 2,
          borderColor: '#ffffff',
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'bottom', labels: { boxWidth: 12 } }
        },
        cutout: '68%'
      }
    });
  }

  renderTopBars(subs: Subscription[]): void {
    if (!this.barCanvasRef) return;
    this.barChart?.destroy();

    const ctx = this.barCanvasRef.nativeElement.getContext('2d');
    if (!ctx) return;

    this.barChart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: subs.map(s => s.name),
        datasets: [{
          label: 'Monthly Run-Rate ($)',
          data: subs.map(s => s.monthly_equivalent_cost),
          backgroundColor: '#6366f1',
          borderRadius: 6,
        }]
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: {
            beginAtZero: true,
            ticks: { callback: (v) => `\$${v}` }
          },
          y: { grid: { display: false } }
        }
      }
    });
  }
}
