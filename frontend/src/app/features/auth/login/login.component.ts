import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../../../core/services/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterModule],
  template: `
    <div class="auth-page">
      <div class="auth-box panel">
        <div class="auth-header">
          <div class="brand-badge">WorkSync</div>
          <h2>Sign in to WorkSync</h2>
          <p class="auth-sub">Enter your email and password to access your workspace</p>
        </div>

        <form [formGroup]="loginForm" (ngSubmit)="onSubmit()">
          <div class="form-group">
            <label class="form-label" for="email">Work Email</label>
            <input
              id="email"
              type="email"
              class="form-control"
              formControlName="email"
              placeholder="alex@worksync.io"
              [class.is-invalid]="isFieldInvalid('email')"
            />
            <div *ngIf="isFieldInvalid('email')" class="form-error">
              Please enter a valid email address.
            </div>
          </div>

          <div class="form-group">
            <label class="form-label" for="password">Password</label>
            <input
              id="password"
              type="password"
              class="form-control"
              formControlName="password"
              placeholder="••••••••"
              [class.is-invalid]="isFieldInvalid('password')"
            />
            <div *ngIf="isFieldInvalid('password')" class="form-error">
              Password is required.
            </div>
          </div>

          <button
            type="submit"
            class="btn btn-primary w-full"
            [disabled]="loginForm.invalid || isLoading"
          >
            <span *ngIf="!isLoading">Sign In</span>
            <span *ngIf="isLoading">Signing in...</span>
          </button>
        </form>

        <div class="auth-footer">
          <p>Workspace Administrator? <a routerLink="/auth/register">Create Admin Account</a></p>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .auth-page {
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      background-color: var(--bg-app);
      padding: 24px;
    }

    .auth-box {
      width: 100%;
      max-width: 400px;
      padding: 32px;
      background: var(--bg-surface);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-md);
      box-shadow: var(--shadow-sm);
    }

    .auth-header {
      text-align: center;
      margin-bottom: 24px;
    }

    .brand-badge {
      display: inline-block;
      font-size: 0.75rem;
      font-weight: 800;
      letter-spacing: 0.05em;
      text-transform: uppercase;
      background: var(--primary-dark);
      color: #FFFFFF;
      padding: 3px 8px;
      border-radius: var(--radius-sm);
      margin-bottom: 12px;
    }

    .auth-header h2 {
      font-size: 1.25rem;
      margin-bottom: 4px;
    }

    .auth-sub {
      font-size: 0.8rem;
      color: var(--text-muted);
    }

    .w-full { width: 100%; margin-top: 8px; }

    .auth-footer {
      margin-top: 20px;
      text-align: center;
      font-size: 0.8rem;
      color: var(--text-muted);
      border-top: 1px solid var(--border-color);
      padding-top: 16px;
    }

    .auth-footer a {
      color: var(--primary-600);
      text-decoration: none;
      font-weight: 600;
    }
  `]
})
export class LoginComponent {
  private fb = inject(FormBuilder);
  private authService = inject(AuthService);
  private router = inject(Router);

  isLoading = false;

  loginForm = this.fb.group({
    email: ['', [Validators.required, Validators.email]],
    password: ['', [Validators.required]]
  });

  isFieldInvalid(field: string): boolean {
    const control = this.loginForm.get(field);
    return !!(control && control.invalid && (control.dirty || control.touched));
  }

  onSubmit() {
    if (this.loginForm.invalid) return;

    this.isLoading = true;
    const { email, password } = this.loginForm.value;

    this.authService.login({ email: email!, password: password! }).subscribe({
      next: () => {
        this.isLoading = false;
        this.router.navigate(['/dashboard']);
      },
      error: () => {
        this.isLoading = false;
      }
    });
  }
}
