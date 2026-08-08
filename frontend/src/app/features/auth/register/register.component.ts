import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../../../core/services/auth.service';
import { Role } from '../../../core/models/role.model';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterModule],
  template: `
    <div class="auth-page">
      <div class="auth-box panel">
        <div class="auth-header">
          <div class="brand-badge">WorkSync</div>
          <h2>Create Workspace Account</h2>
          <p class="auth-sub">Register an initial administrator account</p>
        </div>

        <form [formGroup]="registerForm" (ngSubmit)="onSubmit()">
          <div class="form-group">
            <label class="form-label" for="name">Full Name *</label>
            <input
              id="name"
              type="text"
              class="form-control"
              formControlName="name"
              placeholder="Sarah Connor"
            />
          </div>

          <div class="form-group">
            <label class="form-label" for="email">Work Email *</label>
            <input
              id="email"
              type="email"
              class="form-control"
              formControlName="email"
              placeholder="sarah@worksync.io"
            />
          </div>

          <div class="form-row">
            <div class="form-group">
              <label class="form-label" for="age">Age</label>
              <input id="age" type="number" class="form-control" formControlName="age" />
            </div>

            <div class="form-group">
              <label class="form-label" for="role">Role</label>
              <select id="role" class="form-select" formControlName="role">
                <option [value]="roles.ADMIN">ADMIN</option>
                <option [value]="roles.MANAGER">MANAGER</option>
                <option [value]="roles.EMPLOYEE">EMPLOYEE</option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label class="form-label" for="password">Password *</label>
            <input
              id="password"
              type="password"
              class="form-control"
              formControlName="password"
              placeholder="••••••••"
            />
          </div>

          <button
            type="submit"
            class="btn btn-primary w-full"
            [disabled]="registerForm.invalid || isLoading"
          >
            <span *ngIf="!isLoading">Register Account</span>
            <span *ngIf="isLoading">Registering...</span>
          </button>
        </form>

        <div class="auth-footer">
          <p>Already registered? <a routerLink="/auth/login">Back to Sign In</a></p>
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
      max-width: 440px;
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

    .form-row {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 10px;
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
export class RegisterComponent {
  private fb = inject(FormBuilder);
  private authService = inject(AuthService);
  private router = inject(Router);

  roles = Role;
  isLoading = false;

  registerForm = this.fb.group({
    name: ['', [Validators.required, Validators.minLength(2)]],
    email: ['', [Validators.required, Validators.email]],
    password: ['', [Validators.required, Validators.minLength(6)]],
    age: [28, [Validators.required, Validators.min(18)]],
    role: [Role.ADMIN, [Validators.required]]
  });

  isFieldInvalid(field: string): boolean {
    const control = this.registerForm.get(field);
    return !!(control && control.invalid && (control.dirty || control.touched));
  }

  onSubmit() {
    if (this.registerForm.invalid) return;

    this.isLoading = true;
    const formVal = this.registerForm.value;

    this.authService.register({
      name: formVal.name!,
      email: formVal.email!,
      password: formVal.password!,
      age: Number(formVal.age),
      role: formVal.role as Role
    }).subscribe({
      next: () => {
        this.isLoading = false;
        this.router.navigate(['/auth/login']);
      },
      error: () => {
        this.isLoading = false;
      }
    });
  }
}
