import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { SubscriptionService } from '../../core/services/subscription.service';
import { RenewalNotice } from '../../core/models/subscription.model';
import { NavbarComponent } from '../../shared/navbar/navbar.component';

@Component({
  selector: 'app-renewals',
  standalone: true,
  imports: [CommonModule, NavbarComponent],
  template: `
    <div class="renewals-layout">
      <app-navbar title="Renewal Schedule & Calendar"></app-navbar>

      <main class="page-content">
        <!-- Schedule Header Card -->
        <div class="saas-card header-card">
          <div>
            <h3>Upcoming Subscription Renewals</h3>
            <p>Chronological schedule of renewals to prevent unexpected credit card charges and service lapses.</p>
          </div>
          <div class="horizon-selector">
            <button
              class="horizon-btn"
              [class.active]="daysHorizon === 14"
              (click)="changeHorizon(14)">14 Days</button>
            <button
              class="horizon-btn"
              [class.active]="daysHorizon === 30"
              (click)="changeHorizon(30)">30 Days</button>
            <button
              class="horizon-btn"
              [class.active]="daysHorizon === 60"
              (click)="changeHorizon(60)">60 Days</button>
            <button
              class="horizon-btn"
              [class.active]="daysHorizon === 90"
              (click)="changeHorizon(90)">90 Days</button>
          </div>
        </div>

        <!-- Schedule Timeline Cards -->
        <div class="renewals-timeline">
          <div *ngIf="renewals.length === 0" class="empty-timeline saas-card">
            <span class="material-icons">event_available</span>
            <h4>No Upcoming Renewals</h4>
            <p>No active subscriptions are scheduled to renew in the selected {{ daysHorizon }}-day window.</p>
          </div>

          <div
            *ngFor="let item of renewals"
            class="renewal-card saas-card"
            [class.urgent-card]="item.days_left <= 3">
            <div class="card-left">
              <div class="date-badge" [class.urgent-badge]="item.days_left <= 3">
                <span class="days-num">{{ item.days_left === 0 ? 'NOW' : item.days_left + 'd' }}</span>
                <span class="days-label">{{ item.days_left === 0 ? 'Due Today' : 'remaining' }}</span>
              </div>
              <div class="info-col">
                <div class="title-row">
                  <strong>{{ item.name }}</strong>
                  <span class="essential-tag" *ngIf="item.is_essential">Essential</span>
                </div>
                <span class="cat-text">{{ item.category_name }} &bull; {{ item.billing_cycle }}</span>
                <span class="exact-date">Renewal Date: <strong>{{ item.renewal_date }}</strong></span>
              </div>
            </div>

            <div class="card-right">
              <span class="cost-amount">\${{ item.cost.toFixed(2) }}</span>
              <span class="status-pill">{{ item.status }}</span>
            </div>
          </div>
        </div>
      </main>
    </div>
  `,
  styles: [`
    .renewals-layout {
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
    .header-card {
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 16px;
    }
    .header-card h3 {
      font-size: 1.15rem;
      font-weight: 700;
      color: #0f172a;
    }
    .header-card p {
      font-size: 0.85rem;
      color: #64748b;
      margin-top: 4px;
    }
    .horizon-selector {
      display: flex;
      gap: 6px;
      background: #f1f5f9;
      padding: 4px;
      border-radius: 8px;
    }
    .horizon-btn {
      border: none;
      background: transparent;
      padding: 6px 14px;
      border-radius: 6px;
      font-size: 0.82rem;
      font-weight: 600;
      color: #64748b;
      cursor: pointer;
      transition: all 0.15s;
    }
    .horizon-btn.active {
      background: #ffffff;
      color: #0f172a;
      box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }

    .renewals-timeline {
      display: flex;
      flex-direction: column;
      gap: 12px;
    }
    .renewal-card {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 18px 24px;
      border-left: 4px solid #4f46e5;
    }
    .urgent-card {
      border-left-color: #ef4444;
      background: #fffdfd;
    }
    .card-left {
      display: flex;
      align-items: center;
      gap: 20px;
    }
    .date-badge {
      width: 70px;
      height: 70px;
      border-radius: 12px;
      background: #eef2ff;
      color: #4338ca;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
    }
    .urgent-badge {
      background: #fee2e2;
      color: #dc2626;
    }
    .days-num {
      font-size: 1.35rem;
      font-weight: 800;
      line-height: 1;
    }
    .days-label {
      font-size: 0.65rem;
      font-weight: 700;
      text-transform: uppercase;
      margin-top: 2px;
    }
    .info-col {
      display: flex;
      flex-direction: column;
      gap: 3px;
    }
    .title-row {
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .title-row strong {
      font-size: 1.05rem;
      color: #0f172a;
    }
    .essential-tag {
      background: #dbeafe;
      color: #1e40af;
      font-size: 0.7rem;
      font-weight: 700;
      padding: 2px 6px;
      border-radius: 4px;
    }
    .cat-text {
      font-size: 0.82rem;
      color: #64748b;
    }
    .exact-date {
      font-size: 0.82rem;
      color: #475569;
      margin-top: 2px;
    }
    .card-right {
      display: flex;
      flex-direction: column;
      align-items: flex-end;
      gap: 6px;
    }
    .cost-amount {
      font-size: 1.35rem;
      font-weight: 800;
      color: #0f172a;
    }
    .status-pill {
      font-size: 0.72rem;
      font-weight: 700;
      background: #ecfdf5;
      color: #065f46;
      padding: 2px 8px;
      border-radius: 4px;
      text-transform: uppercase;
    }
    .empty-timeline {
      text-align: center;
      padding: 60px 20px;
      color: #64748b;
    }
    .empty-timeline .material-icons {
      font-size: 48px;
      color: #10b981;
      margin-bottom: 12px;
    }
    .empty-timeline h4 {
      font-size: 1.1rem;
      color: #0f172a;
      margin-bottom: 6px;
    }
  `]
})
export class RenewalsComponent implements OnInit {
  renewals: RenewalNotice[] = [];
  daysHorizon: number = 30;

  constructor(private subscriptionService: SubscriptionService) {}

  ngOnInit(): void {
    this.loadRenewals();
  }

  changeHorizon(days: number): void {
    this.daysHorizon = days;
    this.loadRenewals();
  }

  loadRenewals(): void {
    this.subscriptionService.getUpcomingRenewals(this.daysHorizon).subscribe({
      next: (data) => this.renewals = data,
      error: (err) => console.error('Failed to load renewals', err)
    });
  }
}
