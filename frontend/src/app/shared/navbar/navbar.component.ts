import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../core/services/auth.service';
import { User } from '../../core/models/user.model';

@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [CommonModule],
  template: `
    <header class="navbar">
      <div class="navbar-left">
        <h1 class="page-title">{{ title }}</h1>
      </div>

      <div class="navbar-right">
        <div class="redis-status-pill">
          <span class="dot"></span>
          <span>Redis Active</span>
        </div>

        <div class="user-profile" *ngIf="user">
          <div class="user-avatar">
            {{ user.username.substring(0, 2).toUpperCase() }}
          </div>
          <div class="user-info">
            <span class="user-name">{{ user.full_name || user.username }}</span>
            <span class="user-email">{{ user.email }}</span>
          </div>
        </div>

        <button class="logout-btn" (click)="onLogout()" title="Sign Out">
          <span class="material-icons">logout</span>
        </button>
      </div>
    </header>
  `,
  styles: [`
    .navbar {
      height: 68px;
      background: #ffffff;
      border-bottom: 1px solid #e2e8f0;
      padding: 0 32px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      position: sticky;
      top: 0;
      z-index: 90;
    }
    .page-title {
      font-size: 1.25rem;
      font-weight: 700;
      color: #0f172a;
    }
    .navbar-right {
      display: flex;
      align-items: center;
      gap: 20px;
    }
    .redis-status-pill {
      display: flex;
      align-items: center;
      gap: 6px;
      background: #f1f5f9;
      padding: 6px 12px;
      border-radius: 9999px;
      font-size: 0.75rem;
      font-weight: 600;
      color: #475569;
    }
    .dot {
      width: 7px;
      height: 7px;
      background: #10b981;
      border-radius: 50%;
    }
    .user-profile {
      display: flex;
      align-items: center;
      gap: 10px;
    }
    .user-avatar {
      width: 36px;
      height: 36px;
      background: #e0e7ff;
      color: #4338ca;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 700;
      font-size: 0.85rem;
    }
    .user-info {
      display: flex;
      flex-direction: column;
    }
    .user-name {
      font-size: 0.85rem;
      font-weight: 600;
      color: #1e293b;
    }
    .user-email {
      font-size: 0.72rem;
      color: #64748b;
    }
    .logout-btn {
      background: transparent;
      border: none;
      color: #64748b;
      cursor: pointer;
      padding: 8px;
      border-radius: 8px;
      display: flex;
      align-items: center;
      transition: all 0.15s;
    }
    .logout-btn:hover {
      background: #fef2f2;
      color: #dc2626;
    }
  `]
})
export class NavbarComponent {
  @Input() title: string = 'Overview';
  user: User | null = null;

  constructor(private authService: AuthService) {
    this.authService.currentUser$.subscribe(u => this.user = u);
  }

  onLogout(): void {
    this.authService.logout();
  }
}
