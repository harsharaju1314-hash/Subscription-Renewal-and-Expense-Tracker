import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AuthService } from '../../core/services/auth.service';
import { User } from '../../core/models/user.model';
import { NavbarComponent } from '../../shared/navbar/navbar.component';

@Component({
  selector: 'app-settings',
  standalone: true,
  imports: [CommonModule, FormsModule, NavbarComponent],
  template: `
    <div class="settings-layout">
      <app-navbar title="Account & Platform Settings"></app-navbar>

      <main class="page-content">
        <div class="settings-grid">
          <!-- Profile Card -->
          <div class="saas-card">
            <div class="card-header">
              <h3>Profile & Credentials</h3>
              <p>User account details and authentication identity</p>
            </div>
            <div class="form-group">
              <label>Full Name</label>
              <input type="text" [value]="user?.full_name || 'N/A'" class="form-control" disabled />
            </div>
            <div class="form-group">
              <label>Username</label>
              <input type="text" [value]="user?.username || ''" class="form-control" disabled />
            </div>
            <div class="form-group">
              <label>Email Address</label>
              <input type="email" [value]="user?.email || ''" class="form-control" disabled />
            </div>
            <div class="form-group">
              <label>User Status</label>
              <span class="badge badge-active">Active Verified</span>
            </div>
          </div>

          <!-- Financial Preferences -->
          <div class="saas-card">
            <div class="card-header">
              <h3>Financial & Notification Thresholds</h3>
              <p>Default preferences for budget limits and renewal reminders</p>
            </div>
            <div class="form-group">
              <label>Primary Currency</label>
              <select class="form-control" [(ngModel)]="selectedCurrency">
                <option value="USD">USD ($) - United States Dollar</option>
                <option value="EUR">EUR (€) - Euro</option>
                <option value="GBP">GBP (£) - British Pound</option>
                <option value="INR">INR (₹) - Indian Rupee</option>
                <option value="CAD">CAD ($) - Canadian Dollar</option>
              </select>
            </div>
            <div class="form-group">
              <label>Default Monthly Budget Cap ($)</label>
              <input type="number" [(ngModel)]="monthlyBudget" class="form-control" />
            </div>
            <div class="form-group">
              <label>Budget Alert Threshold (%)</label>
              <input type="number" [(ngModel)]="alertThreshold" class="form-control" min="50" max="100" />
              <span class="hint">Alert triggered when monthly spending reaches {{ alertThreshold }}% of budget.</span>
            </div>
            <button class="btn-primary" (click)="savePreferences()">Save Preferences</button>
            <span class="save-toast" *ngIf="savedNotice">Preferences saved successfully!</span>
          </div>

          <!-- Microservice Architecture Info -->
          <div class="saas-card full-width">
            <div class="card-header">
              <h3>System Architecture & Connected Services</h3>
              <p>Deployment topology and microservice interfaces</p>
            </div>
            <div class="services-list">
              <div class="service-item">
                <span class="material-icons service-icon">api</span>
                <div class="service-details">
                  <strong>FastAPI REST Gateway (Port 8000)</strong>
                  <p>Handles authentication, JWT verification, subscription CRUD, and analytics orchestration.</p>
                </div>
                <span class="badge badge-active">ONLINE</span>
              </div>

              <div class="service-item">
                <span class="material-icons service-icon">psychology</span>
                <div class="service-details">
                  <strong>Flask AI Inference Engine (Port 5001)</strong>
                  <p>Manages LangChain pipelines, FAISS vector indexing, semantic search, and OpenAI inference.</p>
                </div>
                <span class="badge badge-active">ONLINE</span>
              </div>

              <div class="service-item">
                <span class="material-icons service-icon">memory</span>
                <div class="service-details">
                  <strong>Redis Caching Layer (Port 6379)</strong>
                  <p>In-memory cache for dashboard analytics summaries, category breakdowns, and spending trends.</p>
                </div>
                <span class="badge badge-active">ONLINE</span>
              </div>

              <div class="service-item">
                <span class="material-icons service-icon">storage</span>
                <div class="service-details">
                  <strong>MySQL 8.0 Database (Port 3306)</strong>
                  <p>ACID-compliant relational store with normalized tables, indexes, and Alembic migrations.</p>
                </div>
                <span class="badge badge-active">ONLINE</span>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  `,
  styles: [`
    .settings-layout {
      margin-left: 260px;
      min-height: 100vh;
      background: #f8fafc;
    }
    .page-content {
      padding: 32px;
    }
    .settings-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 24px;
    }
    @media (max-width: 900px) {
      .settings-grid { grid-template-columns: 1fr; }
    }
    .full-width {
      grid-column: span 2;
    }
    @media (max-width: 900px) {
      .full-width { grid-column: span 1; }
    }
    .card-header {
      margin-bottom: 20px;
      padding-bottom: 12px;
      border-bottom: 1px solid #e2e8f0;
    }
    .card-header h3 {
      font-size: 1.1rem;
      font-weight: 700;
      color: #0f172a;
    }
    .card-header p {
      font-size: 0.82rem;
      color: #64748b;
      margin-top: 4px;
    }
    .form-group {
      margin-bottom: 18px;
    }
    .form-group label {
      display: block;
      font-size: 0.82rem;
      font-weight: 600;
      color: #334155;
      margin-bottom: 6px;
    }
    .form-control {
      width: 100%;
      padding: 10px 12px;
      border: 1px solid #cbd5e1;
      border-radius: 8px;
      font-size: 0.9rem;
    }
    .form-control:disabled {
      background: #f8fafc;
      color: #64748b;
    }
    .hint {
      font-size: 0.75rem;
      color: #64748b;
      margin-top: 4px;
      display: block;
    }
    .save-toast {
      margin-left: 12px;
      color: #059669;
      font-weight: 600;
      font-size: 0.85rem;
    }
    .services-list {
      display: flex;
      flex-direction: column;
      gap: 12px;
    }
    .service-item {
      display: flex;
      align-items: center;
      gap: 16px;
      padding: 14px 18px;
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 8px;
    }
    .service-icon {
      font-size: 28px;
      color: #4f46e5;
    }
    .service-details {
      flex: 1;
    }
    .service-details strong {
      font-size: 0.92rem;
      color: #0f172a;
    }
    .service-details p {
      font-size: 0.8rem;
      color: #64748b;
    }
  `]
})
export class SettingsComponent implements OnInit {
  user: User | null = null;
  selectedCurrency: string = 'USD';
  monthlyBudget: number = 250.00;
  alertThreshold: number = 80;
  savedNotice: boolean = false;

  constructor(private authService: AuthService) {}

  ngOnInit(): void {
    this.authService.currentUser$.subscribe(u => this.user = u);
  }

  savePreferences(): void {
    this.savedNotice = true;
    setTimeout(() => this.savedNotice = false, 3000);
  }
}
