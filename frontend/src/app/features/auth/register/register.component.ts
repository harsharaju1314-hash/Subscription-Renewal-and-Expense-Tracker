import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../../../core/services/auth.service';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterModule],
  template: `
    <div class="auth-container">
      <div class="auth-card saas-card">
        <div class="auth-header">
          <div class="logo-box">
            <span class="material-icons">query_stats</span>
          </div>
          <h2>Create an Account</h2>
          <p>Get started with AI-driven subscription analytics</p>
        </div>

        <div *ngIf="errorMessage" class="error-alert">
          <span class="material-icons">error_outline</span>
          <span>{{ errorMessage }}</span>
        </div>

        <form [formGroup]="registerForm" (ngSubmit)="onSubmit()">
          <div class="form-group">
            <label for="full_name">Full Name</label>
            <input
              id="full_name"
              type="text"
              formControlName="full_name"
              placeholder="e.g. Jane Doe"
              class="form-control"
            />
          </div>

          <div class="form-group">
            <label for="email">Work or Personal Email</label>
            <input
              id="email"
              type="email"
              formControlName="email"
              placeholder="jane@example.com"
              class="form-control"
              [class.is-invalid]="f['email'].touched && f['email'].errors"
            />
          </div>

          <div class="form-group">
            <label for="username">Username</label>
            <input
              id="username"
              type="text"
              formControlName="username"
              placeholder="janedoe"
              class="form-control"
              [class.is-invalid]="f['username'].touched && f['username'].errors"
            />
          </div>

          <div class="form-group">
            <label for="password">Password (min 8 characters)</label>
            <input
              id="password"
              type="password"
              formControlName="password"
              placeholder="••••••••"
              class="form-control"
              [class.is-invalid]="f['password'].touched && f['password'].errors"
            />
          </div>

          <button type="submit" class="btn-primary auth-submit" [disabled]="registerForm.invalid || loading">
            <span *ngIf="loading" class="spinner"></span>
            <span>{{ loading ? 'Creating Account...' : 'Create Account' }}</span>
          </button>
        </form>

        <div class="auth-footer">
          <span>Already have an account? </span>
          <a routerLink="/login">Sign in</a>
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
      max-width: 460px;
      padding: 36px;
      border-radius: 16px;
      background: #ffffff;
      box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.25);
    }
    .auth-header {
      text-align: center;
      margin-bottom: 24px;
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
      margin-bottom: 16px;
    }
    .form-group label {
      display: block;
      font-size: 0.85rem;
      font-weight: 600;
      color: #334155;
      margin-bottom: 6px;
    }
    .form-control {
      width: 100%;
      padding: 10px 14px;
      border: 1px solid #cbd5e1;
      border-radius: 8px;
      font-size: 0.92rem;
    }
    .form-control:focus {
      outline: none;
      border-color: #6366f1;
      box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15);
    }
    .auth-submit {
      width: 100%;
      justify-content: center;
      padding: 12px;
      font-size: 0.95rem;
      margin-top: 10px;
    }
    .error-alert {
      background: #fef2f2;
      border: 1px solid #fecaca;
      color: #b91c1c;
      padding: 10px 14px;
      border-radius: 8px;
      font-size: 0.85rem;
      margin-bottom: 18px;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .auth-footer {
      text-align: center;
      margin-top: 20px;
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
export class RegisterComponent {
  registerForm: FormGroup;
  loading: boolean = false;
  errorMessage: string = '';

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private router: Router
  ) {
    this.registerForm = this.fb.group({
      full_name: [''],
      email: ['', [Validators.required, Validators.email]],
      username: ['', [Validators.required, Validators.minLength(3)]],
      password: ['', [Validators.required, Validators.minLength(8)]]
    });
  }

  get f() { return this.registerForm.controls; }

  onSubmit(): void {
    if (this.registerForm.invalid) return;
    this.loading = true;
    this.errorMessage = '';

    this.authService.register(this.registerForm.value).subscribe({
      next: () => {
        this.loading = false;
        this.router.navigate(['/dashboard']);
      },
      error: (err) => {
        this.loading = false;
        this.errorMessage = err?.error?.detail || 'Registration failed. Try again.';
      }
    });
  }
}
