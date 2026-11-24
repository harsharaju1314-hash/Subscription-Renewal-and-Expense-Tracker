import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-kpi-card',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="kpi-card saas-card">
      <div class="kpi-header">
        <span class="kpi-title">{{ title }}</span>
        <div class="kpi-icon-wrap" [style.background-color]="iconBg" [style.color]="iconColor">
          <span class="material-icons">{{ icon }}</span>
        </div>
      </div>
      <div class="kpi-value">{{ value }}</div>
      <div class="kpi-footer">
        <span class="kpi-subtitle" [class.highlight]="highlightSubtitle">{{ subtitle }}</span>
      </div>
    </div>
  `,
  styles: [`
    .kpi-card {
      display: flex;
      flex-direction: column;
      gap: 12px;
    }
    .kpi-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .kpi-title {
      font-size: 0.82rem;
      font-weight: 600;
      color: #64748b;
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }
    .kpi-icon-wrap {
      width: 36px;
      height: 36px;
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .kpi-icon-wrap .material-icons {
      font-size: 20px;
    }
    .kpi-value {
      font-size: 1.85rem;
      font-weight: 800;
      color: #0f172a;
      letter-spacing: -0.02em;
    }
    .kpi-footer {
      display: flex;
      align-items: center;
    }
    .kpi-subtitle {
      font-size: 0.78rem;
      color: #64748b;
    }
    .kpi-subtitle.highlight {
      color: #059669;
      font-weight: 600;
    }
  `]
})
export class KpiCardComponent {
  @Input() title: string = '';
  @Input() value: string = '';
  @Input() subtitle: string = '';
  @Input() icon: string = 'insights';
  @Input() iconBg: string = '#eef2ff';
  @Input() iconColor: string = '#4f46e5';
  @Input() highlightSubtitle: boolean = false;
}
