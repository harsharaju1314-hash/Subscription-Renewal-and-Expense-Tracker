import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule, FormsModule } from '@angular/forms';
import { SubscriptionService } from '../../core/services/subscription.service';
import {
  Subscription,
  Category,
  BillingCycle,
  SubscriptionStatus,
} from '../../core/models/subscription.model';
import { NavbarComponent } from '../../shared/navbar/navbar.component';

@Component({
  selector: 'app-subscriptions',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, FormsModule, NavbarComponent],
  template: `
    <div class="subscriptions-layout">
      <app-navbar title="Subscription Management"></app-navbar>

      <main class="page-content">
        <!-- Action & Filter Bar -->
        <div class="action-bar saas-card">
          <div class="search-wrap">
            <span class="material-icons search-icon">search</span>
            <input
              type="text"
              [(ngModel)]="searchQuery"
              (input)="applyFilters()"
              placeholder="Search subscriptions by name, payment method..."
              class="search-input"
            />
          </div>

          <div class="filter-controls">
            <select [(ngModel)]="selectedCategory" (change)="applyFilters()" class="filter-select">
              <option [ngValue]="null">All Categories</option>
              <option *ngFor="let cat of categories" [ngValue]="cat.id">{{ cat.name }}</option>
            </select>

            <select [(ngModel)]="selectedStatus" (change)="applyFilters()" class="filter-select">
              <option [ngValue]="null">All Statuses</option>
              <option value="ACTIVE">Active</option>
              <option value="CANCELLED">Cancelled</option>
              <option value="EXPIRED">Expired</option>
              <option value="PAUSED">Paused</option>
            </select>

            <button class="btn-primary" (click)="openAddModal()">
              <span class="material-icons">add</span>
              <span>Add Subscription</span>
            </button>
          </div>
        </div>

        <!-- Subscriptions Table -->
        <div class="saas-card table-card">
          <div class="table-meta">
            <span class="count-label">Showing {{ filteredSubscriptions.length }} subscriptions</span>
            <span class="cost-summary" *ngIf="filteredSubscriptions.length > 0">
              Filtered Run-rate: <strong>\${{ calculateFilteredMonthly().toFixed(2) }}/mo</strong>
            </span>
          </div>

          <div class="table-responsive">
            <table class="saas-table">
              <thead>
                <tr>
                  <th>Subscription</th>
                  <th>Category</th>
                  <th>Cost & Cycle</th>
                  <th>Monthly Equivalent</th>
                  <th>Renewal Date</th>
                  <th>Status</th>
                  <th>Utility</th>
                  <th class="actions-col">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr *ngFor="let sub of filteredSubscriptions">
                  <td>
                    <div class="sub-name-cell">
                      <strong>{{ sub.name }}</strong>
                      <span class="essential-pill" *ngIf="sub.is_essential">Essential</span>
                      <span class="sub-desc" *ngIf="sub.description">{{ sub.description }}</span>
                    </div>
                  </td>
                  <td>
                    <span class="cat-pill" [style.border-color]="sub.category?.color || '#cbd5e1'">
                      {{ sub.category?.name || 'General' }}
                    </span>
                  </td>
                  <td>
                    <div class="cost-cell">
                      <span class="raw-cost">\${{ sub.cost.toFixed(2) }}</span>
                      <span class="cycle-label">{{ sub.billing_cycle }}</span>
                    </div>
                  </td>
                  <td>
                    <strong class="monthly-cost">\${{ sub.monthly_equivalent_cost.toFixed(2) }}</strong>
                    <span class="annual-cost">(\${{ sub.annual_equivalent_cost.toFixed(2) }}/yr)</span>
                  </td>
                  <td>
                    <div class="renewal-cell">
                      <span>{{ sub.renewal_date }}</span>
                      <span class="days-badge" [class.urgent]="sub.days_until_renewal <= 5 && sub.days_until_renewal >= 0">
                        {{ sub.days_until_renewal >= 0 ? sub.days_until_renewal + 'd left' : 'Expired' }}
                      </span>
                    </div>
                  </td>
                  <td>
                    <span class="badge" [ngClass]="'badge-' + sub.status.toLowerCase()">
                      {{ sub.status }}
                    </span>
                  </td>
                  <td>
                    <div class="utility-rating">
                      <span class="rating-num">{{ sub.utility_score }}</span>
                      <span class="rating-max">/10</span>
                    </div>
                  </td>
                  <td class="actions-col">
                    <button class="action-btn edit-btn" (click)="openEditModal(sub)" title="Edit">
                      <span class="material-icons">edit</span>
                    </button>
                    <button class="action-btn delete-btn" (click)="confirmDelete(sub)" title="Delete">
                      <span class="material-icons">delete</span>
                    </button>
                  </td>
                </tr>

                <tr *ngIf="filteredSubscriptions.length === 0">
                  <td colspan="8" class="no-records-cell">
                    <span class="material-icons">inbox</span>
                    <p>No subscriptions match the selected criteria.</p>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </main>

      <!-- Add / Edit Modal -->
      <div class="modal-backdrop" *ngIf="showModal">
        <div class="modal-card saas-card">
          <div class="modal-header">
            <h3>{{ isEditing ? 'Edit Subscription' : 'Add New Subscription' }}</h3>
            <button class="close-btn" (click)="closeModal()">&times;</button>
          </div>

          <form [formGroup]="subForm" (ngSubmit)="saveSubscription()">
            <div class="form-grid">
              <div class="form-group full-width">
                <label for="name">Subscription Name *</label>
                <input id="name" type="text" formControlName="name" class="form-control" placeholder="e.g. Netflix Premium" />
              </div>

              <div class="form-group">
                <label for="category_id">Category *</label>
                <select id="category_id" formControlName="category_id" class="form-control">
                  <option *ngFor="let cat of categories" [value]="cat.id">{{ cat.name }}</option>
                </select>
              </div>

              <div class="form-group">
                <label for="cost">Price Amount ($) *</label>
                <input id="cost" type="number" step="0.01" formControlName="cost" class="form-control" placeholder="15.99" />
              </div>

              <div class="form-group">
                <label for="billing_cycle">Billing Cycle *</label>
                <select id="billing_cycle" formControlName="billing_cycle" class="form-control">
                  <option value="MONTHLY">Monthly</option>
                  <option value="ANNUAL">Annual</option>
                  <option value="QUARTERLY">Quarterly</option>
                  <option value="WEEKLY">Weekly</option>
                </select>
              </div>

              <div class="form-group">
                <label for="renewal_date">Next Renewal Date *</label>
                <input id="renewal_date" type="date" formControlName="renewal_date" class="form-control" />
              </div>

              <div class="form-group">
                <label for="status">Subscription Status *</label>
                <select id="status" formControlName="status" class="form-control">
                  <option value="ACTIVE">Active</option>
                  <option value="CANCELLED">Cancelled</option>
                  <option value="EXPIRED">Expired</option>
                  <option value="PAUSED">Paused</option>
                </select>
              </div>

              <div class="form-group">
                <label for="payment_method">Payment Method</label>
                <input id="payment_method" type="text" formControlName="payment_method" class="form-control" placeholder="e.g. Visa ****4242" />
              </div>

              <div class="form-group full-width">
                <label for="utility_score">Utility Score ({{ subForm.get('utility_score')?.value }}/10): How critical is this to you?</label>
                <input id="utility_score" type="range" min="1" max="10" formControlName="utility_score" class="form-range" />
              </div>

              <div class="form-group full-width checkbox-row">
                <label class="checkbox-label">
                  <input type="checkbox" formControlName="is_essential" />
                  <span><strong>Mark as Essential</strong> (Cannot be cancelled by Budget Optimizer)</span>
                </label>
              </div>

              <div class="form-group full-width">
                <label for="description">Notes / Description</label>
                <textarea id="description" formControlName="description" class="form-control" rows="2" placeholder="Account login notes, shared family tier, etc."></textarea>
              </div>
            </div>

            <div class="modal-footer">
              <button type="button" class="btn-secondary" (click)="closeModal()">Cancel</button>
              <button type="submit" class="btn-primary" [disabled]="subForm.invalid || saving">
                {{ saving ? 'Saving...' : (isEditing ? 'Update Subscription' : 'Create Subscription') }}
              </button>
            </div>
          </form>
        </div>
      </div>

      <!-- Delete Confirmation Modal -->
      <div class="modal-backdrop" *ngIf="showDeleteModal && subToDelete">
        <div class="modal-card saas-card delete-modal">
          <div class="modal-header">
            <h3>Delete Subscription</h3>
            <button class="close-btn" (click)="showDeleteModal = false">&times;</button>
          </div>
          <p class="delete-warning">
            Are you sure you want to delete <strong>{{ subToDelete.name }}</strong>?
            This will remove all associated payment history and reindex your AI vector store.
          </p>
          <div class="modal-footer">
            <button class="btn-secondary" (click)="showDeleteModal = false">Cancel</button>
            <button class="btn-primary delete-confirm-btn" (click)="executeDelete()">
              Confirm Delete
            </button>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .subscriptions-layout {
      margin-left: 260px;
      min-height: 100vh;
      background: #f8fafc;
    }
    .page-content {
      padding: 32px;
      display: flex;
      flex-direction: column;
      gap: 20px;
    }
    .action-bar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 16px;
      flex-wrap: wrap;
    }
    .search-wrap {
      display: flex;
      align-items: center;
      gap: 8px;
      background: #f8fafc;
      border: 1px solid #cbd5e1;
      border-radius: 8px;
      padding: 8px 14px;
      flex: 1;
      min-width: 260px;
    }
    .search-icon {
      color: #64748b;
      font-size: 20px;
    }
    .search-input {
      border: none;
      background: transparent;
      outline: none;
      width: 100%;
      font-size: 0.9rem;
    }
    .filter-controls {
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .filter-select {
      padding: 9px 12px;
      border: 1px solid #cbd5e1;
      border-radius: 8px;
      background: #ffffff;
      font-size: 0.85rem;
      outline: none;
      cursor: pointer;
    }

    .table-card {
      padding: 0;
      overflow: hidden;
    }
    .table-meta {
      padding: 18px 24px;
      display: flex;
      justify-content: space-between;
      border-bottom: 1px solid #e2e8f0;
      font-size: 0.85rem;
      color: #64748b;
    }
    .table-responsive {
      overflow-x: auto;
    }
    .saas-table {
      width: 100%;
      border-collapse: collapse;
      text-align: left;
    }
    .saas-table th {
      background: #f8fafc;
      padding: 12px 20px;
      font-size: 0.75rem;
      font-weight: 700;
      color: #64748b;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      border-bottom: 1px solid #e2e8f0;
    }
    .saas-table td {
      padding: 14px 20px;
      border-bottom: 1px solid #f1f5f9;
      font-size: 0.88rem;
      vertical-align: middle;
    }
    .saas-table tr:hover {
      background: #fafafa;
    }
    .sub-name-cell {
      display: flex;
      flex-direction: column;
      gap: 2px;
    }
    .essential-pill {
      background: #dbeafe;
      color: #1e40af;
      font-size: 0.68rem;
      font-weight: 700;
      padding: 1px 6px;
      border-radius: 4px;
      width: fit-content;
    }
    .sub-desc {
      font-size: 0.75rem;
      color: #94a3b8;
    }
    .cat-pill {
      font-size: 0.8rem;
      padding: 4px 8px;
      border-left: 3px solid;
      background: #f8fafc;
      border-radius: 2px;
    }
    .cost-cell {
      display: flex;
      flex-direction: column;
    }
    .raw-cost {
      font-weight: 600;
      color: #1e293b;
    }
    .cycle-label {
      font-size: 0.72rem;
      color: #64748b;
    }
    .monthly-cost {
      color: #0f172a;
      font-size: 0.92rem;
    }
    .annual-cost {
      font-size: 0.72rem;
      color: #64748b;
      margin-left: 4px;
    }
    .renewal-cell {
      display: flex;
      flex-direction: column;
      gap: 2px;
    }
    .days-badge {
      font-size: 0.72rem;
      color: #4f46e5;
    }
    .days-badge.urgent {
      color: #dc2626;
      font-weight: 700;
    }
    .utility-rating {
      font-weight: 700;
      color: #0f172a;
    }
    .rating-max {
      font-size: 0.72rem;
      color: #94a3b8;
    }
    .actions-col {
      text-align: right;
    }
    .action-btn {
      background: transparent;
      border: none;
      cursor: pointer;
      padding: 6px;
      border-radius: 6px;
      color: #64748b;
      transition: all 0.15s;
    }
    .action-btn:hover {
      background: #e2e8f0;
      color: #0f172a;
    }
    .delete-btn:hover {
      background: #fee2e2;
      color: #dc2626;
    }
    .no-records-cell {
      text-align: center;
      padding: 40px !important;
      color: #94a3b8;
    }

    /* Modal Styles */
    .modal-backdrop {
      position: fixed;
      top: 0;
      left: 0;
      width: 100vw;
      height: 100vh;
      background: rgba(15, 23, 42, 0.6);
      backdrop-filter: blur(4px);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 1000;
      padding: 20px;
    }
    .modal-card {
      width: 100%;
      max-width: 580px;
      background: #ffffff;
      border-radius: 16px;
      padding: 28px;
      max-height: 90vh;
      overflow-y: auto;
    }
    .modal-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;
      border-bottom: 1px solid #e2e8f0;
      padding-bottom: 14px;
    }
    .modal-header h3 {
      font-size: 1.25rem;
      font-weight: 700;
      color: #0f172a;
    }
    .close-btn {
      background: transparent;
      border: none;
      font-size: 1.5rem;
      cursor: pointer;
      color: #94a3b8;
    }
    .form-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 16px;
    }
    .full-width {
      grid-column: span 2;
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
      padding: 9px 12px;
      border: 1px solid #cbd5e1;
      border-radius: 8px;
      font-size: 0.9rem;
    }
    .form-range {
      width: 100%;
    }
    .checkbox-row {
      display: flex;
      align-items: center;
    }
    .checkbox-label {
      display: flex;
      align-items: center;
      gap: 8px;
      cursor: pointer;
      font-size: 0.88rem;
    }
    .modal-footer {
      display: flex;
      justify-content: flex-end;
      gap: 12px;
      margin-top: 24px;
      border-top: 1px solid #e2e8f0;
      padding-top: 16px;
    }
    .delete-modal {
      max-width: 440px;
    }
    .delete-warning {
      font-size: 0.92rem;
      color: #475569;
      line-height: 1.5;
    }
    .delete-confirm-btn {
      background: #dc2626 !important;
    }
  `]
})
export class SubscriptionsComponent implements OnInit {
  subscriptions: Subscription[] = [];
  filteredSubscriptions: Subscription[] = [];
  categories: Category[] = [];

  searchQuery: string = '';
  selectedCategory: number | null = null;
  selectedStatus: SubscriptionStatus | null = null;

  showModal: boolean = false;
  isEditing: boolean = false;
  currentSubId: number | null = null;
  saving: boolean = false;

  showDeleteModal: boolean = false;
  subToDelete: Subscription | null = null;

  subForm: FormGroup;

  constructor(
    private subscriptionService: SubscriptionService,
    private fb: FormBuilder
  ) {
    this.subForm = this.fb.group({
      name: ['', [Validators.required]],
      category_id: [1, [Validators.required]],
      cost: [null, [Validators.required, Validators.min(0.01)]],
      currency: ['USD'],
      billing_cycle: ['MONTHLY', [Validators.required]],
      renewal_date: ['', [Validators.required]],
      status: ['ACTIVE', [Validators.required]],
      auto_renew: [true],
      payment_method: [''],
      utility_score: [5],
      is_essential: [false],
      description: ['']
    });
  }

  ngOnInit(): void {
    this.loadCategories();
    this.loadSubscriptions();
  }

  loadCategories(): void {
    this.subscriptionService.getCategories().subscribe({
      next: (cats) => {
        this.categories = cats;
        if (cats.length > 0 && !this.subForm.get('category_id')?.value) {
          this.subForm.patchValue({ category_id: cats[0].id });
        }
      }
    });
  }

  loadSubscriptions(): void {
    this.subscriptionService.getSubscriptions().subscribe({
      next: (subs) => {
        this.subscriptions = subs;
        this.applyFilters();
      }
    });
  }

  applyFilters(): void {
    let result = [...this.subscriptions];

    if (this.searchQuery.trim()) {
      const q = this.searchQuery.toLowerCase();
      result = result.filter(s =>
        s.name.toLowerCase().includes(q) ||
        (s.description && s.description.toLowerCase().includes(q)) ||
        (s.payment_method && s.payment_method.toLowerCase().includes(q))
      );
    }

    if (this.selectedCategory !== null) {
      result = result.filter(s => s.category_id === this.selectedCategory);
    }

    if (this.selectedStatus !== null) {
      result = result.filter(s => s.status === this.selectedStatus);
    }

    this.filteredSubscriptions = result;
  }

  calculateFilteredMonthly(): number {
    return this.filteredSubscriptions
      .filter(s => s.status === 'ACTIVE')
      .reduce((acc, curr) => acc + curr.monthly_equivalent_cost, 0);
  }

  openAddModal(): void {
    this.isEditing = false;
    this.currentSubId = null;
    this.subForm.reset({
      currency: 'USD',
      billing_cycle: 'MONTHLY',
      status: 'ACTIVE',
      auto_renew: true,
      utility_score: 5,
      is_essential: false,
      category_id: this.categories.length > 0 ? this.categories[0].id : 1,
      renewal_date: new Date().toISOString().split('T')[0]
    });
    this.showModal = true;
  }

  openEditModal(sub: Subscription): void {
    this.isEditing = true;
    this.currentSubId = sub.id;
    this.subForm.patchValue({
      name: sub.name,
      category_id: sub.category_id,
      cost: sub.cost,
      currency: sub.currency,
      billing_cycle: sub.billing_cycle,
      renewal_date: sub.renewal_date,
      status: sub.status,
      auto_renew: sub.auto_renew,
      payment_method: sub.payment_method || '',
      utility_score: sub.utility_score,
      is_essential: sub.is_essential,
      description: sub.description || ''
    });
    this.showModal = true;
  }

  closeModal(): void {
    this.showModal = false;
    this.saving = false;
  }

  saveSubscription(): void {
    if (this.subForm.invalid) return;
    this.saving = true;

    if (this.isEditing && this.currentSubId) {
      this.subscriptionService.updateSubscription(this.currentSubId, this.subForm.value).subscribe({
        next: () => {
          this.closeModal();
          this.loadSubscriptions();
        },
        error: () => this.saving = false
      });
    } else {
      this.subscriptionService.createSubscription(this.subForm.value).subscribe({
        next: () => {
          this.closeModal();
          this.loadSubscriptions();
        },
        error: () => this.saving = false
      });
    }
  }

  confirmDelete(sub: Subscription): void {
    this.subToDelete = sub;
    this.showDeleteModal = true;
  }

  executeDelete(): void {
    if (!this.subToDelete) return;
    this.subscriptionService.deleteSubscription(this.subToDelete.id).subscribe({
      next: () => {
        this.showDeleteModal = false;
        this.subToDelete = null;
        this.loadSubscriptions();
      }
    });
  }
}
