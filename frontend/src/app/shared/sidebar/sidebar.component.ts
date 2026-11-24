import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [CommonModule, RouterModule],
  template: `
    <aside class="sidebar">
      <div class="sidebar-header">
        <div class="logo-icon">
          <span class="material-icons">query_stats</span>
        </div>
        <div class="logo-text">
          <h2>SubTrack <span class="ai-badge">AI</span></h2>
          <span class="tagline">Expense Intelligence</span>
        </div>
      </div>

      <nav class="sidebar-nav">
        <div class="nav-section-label">CORE PLATFORM</div>
        <a routerLink="/dashboard" routerLinkActive="active" class="nav-item">
          <span class="material-icons">dashboard</span>
          <span>Overview</span>
        </a>
        <a routerLink="/subscriptions" routerLinkActive="active" class="nav-item">
          <span class="material-icons">subscriptions</span>
          <span>Subscriptions</span>
        </a>
        <a routerLink="/analytics" routerLinkActive="active" class="nav-item">
          <span class="material-icons">bar_chart</span>
          <span>Expense Analytics</span>
        </a>

        <div class="nav-section-label">GEN-AI & OPTIMIZATION</div>
        <a routerLink="/ai-assistant" routerLinkActive="active" class="nav-item ai-nav-item">
          <span class="material-icons ai-sparkle">psychology</span>
          <span>AI Financial Assistant</span>
        </a>
        <a routerLink="/budget-optimizer" routerLinkActive="active" class="nav-item">
          <span class="material-icons">tune</span>
          <span>Budget Optimizer</span>
        </a>
        <a routerLink="/renewals" routerLinkActive="active" class="nav-item">
          <span class="material-icons">event_repeat</span>
          <span>Renewal Schedule</span>
        </a>

        <div class="nav-section-label">SYSTEM</div>
        <a routerLink="/settings" routerLinkActive="active" class="nav-item">
          <span class="material-icons">settings</span>
          <span>Settings</span>
        </a>
      </nav>

      <div class="sidebar-footer">
        <div class="engine-badge">
          <span class="status-indicator"></span>
          <span>LangChain + FAISS RAG v1.0</span>
        </div>
      </div>
    </aside>
  `,
  styles: [`
    .sidebar {
      width: 260px;
      height: 100vh;
      background: #0f172a;
      color: #94a3b8;
      display: flex;
      flex-direction: column;
      position: fixed;
      left: 0;
      top: 0;
      border-right: 1px solid #1e293b;
      z-index: 100;
    }
    .sidebar-header {
      padding: 24px 20px;
      display: flex;
      align-items: center;
      gap: 12px;
      border-bottom: 1px solid #1e293b;
    }
    .logo-icon {
      width: 40px;
      height: 40px;
      background: linear-gradient(135deg, #6366f1, #4f46e5);
      border-radius: 10px;
      display: flex;
      align-items: center;
      justify-content: center;
      color: #ffffff;
    }
    .logo-text h2 {
      font-size: 1.15rem;
      font-weight: 700;
      color: #ffffff;
      line-height: 1.2;
    }
    .ai-badge {
      background: linear-gradient(135deg, #10b981, #059669);
      color: #ffffff;
      font-size: 0.65rem;
      padding: 2px 6px;
      border-radius: 4px;
      font-weight: 800;
      margin-left: 2px;
    }
    .tagline {
      font-size: 0.72rem;
      color: #64748b;
    }
    .sidebar-nav {
      flex: 1;
      padding: 20px 12px;
      overflow-y: auto;
    }
    .nav-section-label {
      font-size: 0.68rem;
      font-weight: 700;
      color: #475569;
      letter-spacing: 0.05em;
      padding: 12px 12px 6px;
    }
    .nav-item {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 10px 14px;
      border-radius: 8px;
      color: #94a3b8;
      text-decoration: none;
      font-size: 0.88rem;
      font-weight: 500;
      transition: all 0.15s ease;
      margin-bottom: 4px;
    }
    .nav-item:hover {
      background: #1e293b;
      color: #ffffff;
    }
    .nav-item.active {
      background: #4f46e5;
      color: #ffffff;
    }
    .ai-sparkle {
      color: #a5b4fc;
    }
    .sidebar-footer {
      padding: 16px;
      border-top: 1px solid #1e293b;
    }
    .engine-badge {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 0.72rem;
      color: #64748b;
      background: #1e293b;
      padding: 8px 12px;
      border-radius: 6px;
    }
    .status-indicator {
      width: 7px;
      height: 7px;
      background: #10b981;
      border-radius: 50%;
      box-shadow: 0 0 6px #10b981;
    }
  `]
})
export class SidebarComponent {}
