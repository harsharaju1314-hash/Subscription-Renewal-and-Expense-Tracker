import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../../../core/services/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterModule],
  template: `
    <div class="auth-container">
      <div class="auth-card saas-card">
        <div class="auth-header">
          <div class="logo-box">
            <span class="material-icons">query_stats</span>
          </div>
          <h2>Welcome back</h2>
          <p>Sign in to your AI subscription & expense dashboard</p>
        </div>

        <div *ngIf="errorMessage" class="error-alert">
          <span class="material-icons">error_outline</span>
          <span>{{ errorMessage }}</span>
        </div>

        <form [formGroup]="loginForm" (ngSubmit)="onSubmit()">
          <div class="form-group">
            <label for="username_or_email">Email or Username</label>
            <input
              id="username_or_email"
              type="text"
              formControlName="username_or_email"
              placeholder="e.g. demo@tracker.ai or demouser"
              class="form-control"
              [class.is-invalid]="f['username_or_email'].touched && f['username_or_email'].errors"
            />
          </div>

          <div class="form-group">
            <label for="password">Password</label>
            <input
              id="password"
              type="password"
              formControlName="password"
              placeholder="••••••••"
              class="form-control"
              [class.is-invalid]="f['password'].touched && f['password'].errors"
            />
          </div>

          <div class="demo-creds-hint" (click)="fillDemoCredentials()">
            <span class="material-icons">auto_fix_high</span>
            <span>Click to fill demo account credentials</span>
          </div>

          <button type="submit" class="btn-primary auth-submit" [disabled]="loginForm.invalid || loading">
            <span *ngIf="loading" class="spinner"></span>
            <span>{{ loading ? 'Signing in...' : 'Sign In' }}</span>
          </button>
        </form>

        <div class="auth-footer">
          <span>Don't have an account? </span>
          <a routerLink="/register">Register here</a>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .auth-container {
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
      padding: 20px;
    }
    .auth-card {
      width: 100%;
      max-width: 440px;
      padding: 36px;
      border-radius: 16px;
      background: #ffffff;
      box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.25);
    }
    .auth-header {
      text-align: center;
      margin-bottom: 28px;
    }
    .logo-box {
      width: 48px;
      height: 48px;
      background: linear-gradient(135deg, #6366f1, #4f46e5);
      border-radius: 12px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      color: #ffffff;
      margin-bottom: 16px;
    }
    .auth-header h2 {
      font-size: 1.5rem;
      font-weight: 700;
      color: #0f172a;
    }
    .auth-header p {
      font-size: 0.88rem;
      color: #64748b;
      margin-top: 6px;
    }
    .form-group {
      margin-bottom: 20px;
    }
    .form-group label {
      display: block;
      font-size: 0.85rem;
      font-weight: 600;
      color: #334155;
      margin-bottom: 8px;
    }
    .form-control {
      width: 100%;
      padding: 11px 14px;
      border: 1px solid #cbd5e1;
      border-radius: 8px;
      font-size: 0.92rem;
      transition: border-color 0.15s, box-shadow 0.15s;
    }
    .form-control:focus {
      outline: none;
      border-color: #6366f1;
      box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15);
    }
    .demo-creds-hint {
      display: flex;
      align-items: center;
      gap: 6px;
      background: #eef2ff;
      color: #4338ca;
      padding: 8px 12px;
      border-radius: 6px;
      font-size: 0.78rem;
      font-weight: 600;
      cursor: pointer;
      margin-bottom: 20px;
      transition: background 0.15s;
    }
    .demo-creds-hint:hover {
      background: #e0e7ff;
    }
    .auth-submit {
      width: 100%;
      justify-content: center;
      padding: 12px;
      font-size: 0.95rem;
    }
    .error-alert {
      background: #fef2f2;
      border: 1px solid #fecaca;
      color: #b91c1c;
      padding: 10px 14px;
      border-radius: 8px;
      font-size: 0.85rem;
      margin-bottom: 20px;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .auth-footer {
      text-align: center;
      margin-top: 24px;
      font-size: 0.85rem;
      color: #64748b;
    }
    .auth-footer a {
      color: #4f46e5;
      font-weight: 600;
      text-decoration: none;
    }
    .spinner {
      width: 16px;
      height: 16px;
      border: 2px solid #ffffff;
      border-top-color: transparent;
      border-radius: 50%;
      animation: spin 0.8s linear infinite;
    }
    @keyframes spin {
      to { transform: rotate(360deg); }
    }
  `]
})
export class LoginComponent {
  loginForm: FormGroup;
  loading: boolean = false;
  errorMessage: string = '';

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private router: Router
  ) {
    this.loginForm = this.fb.group({
      username_or_email: ['', [Validators.required]],
      password: ['', [Validators.required, Validators.minLength(6)]]
    });
  }

  get f() { return this.loginForm.controls; }

  fillDemoCredentials(): void {
    this.loginForm.patchValue({
      username_or_email: 'demo@tracker.ai',
      password: 'Password123!'
    });
  }

  onSubmit(): void {
    if (this.loginForm.invalid) return;
    this.loading = true;
    this.errorMessage = '';

    this.authService.login(this.loginForm.value).subscribe({
      next: () => {
        this.loading = false;
        this.router.navigate(['/dashboard']);
      },
      error: (err) => {
        this.loading = false;
        this.errorMessage = err?.error?.detail || 'Invalid username or password.';
      }
    });
  }
}
