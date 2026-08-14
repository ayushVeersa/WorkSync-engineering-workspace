import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { SvgIconComponent } from '../../shared/components/svg-icon/svg-icon.component';

@Component({
  selector: 'app-not-found',
  standalone: true,
  imports: [CommonModule, RouterModule, SvgIconComponent],
  template: `
    <div class="not-found-container">
      <div class="not-found-card panel">
        <div class="error-badge">404 ERROR</div>
        
        <div class="illustration-box">
          <svg width="120" height="120" viewBox="0 0 120 120" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="60" cy="60" r="50" fill="#EFF6FF" stroke="#BFDBFE" stroke-width="3"/>
            <path d="M40 75C40 75 48 65 60 65C72 65 80 75 80 75" stroke="#2563EB" stroke-width="4" stroke-linecap="round"/>
            <circle cx="45" cy="48" r="6" fill="#1E40AF"/>
            <circle cx="75" cy="48" r="6" fill="#1E40AF"/>
            <line x1="35" y1="36" x2="52" y2="42" stroke="#64748B" stroke-width="3" stroke-linecap="round"/>
            <line x1="85" y1="36" x2="68" y2="42" stroke="#64748B" stroke-width="3" stroke-linecap="round"/>
          </svg>
        </div>

        <h2 class="error-title">Page Not Found</h2>
        <p class="error-desc">
          We couldn't find the page or resource you were looking for. It might have been moved, deleted, or never existed in WorkSync.
        </p>

        <div class="action-buttons">
          <a routerLink="/dashboard" class="btn btn-primary">
            <app-svg-icon name="dashboard" [size]="14"></app-svg-icon>
            <span>Back to Dashboard</span>
          </a>
          <a routerLink="/my-work" class="btn btn-secondary">
            <app-svg-icon name="issues" [size]="14"></app-svg-icon>
            <span>View My Work</span>
          </a>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .not-found-container {
      display: flex;
      align-items: center;
      justify-content: center;
      min-height: calc(100vh - 120px);
      padding: 24px;
    }
    .not-found-card {
      display: flex;
      flex-direction: column;
      align-items: center;
      text-align: center;
      max-width: 480px;
      padding: 40px 32px;
      background: var(--bg-surface);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-md);
      box-shadow: var(--shadow-md);
    }
    .error-badge {
      font-size: 0.725rem;
      font-weight: 800;
      letter-spacing: 0.05em;
      color: var(--primary-600);
      background: var(--primary-50);
      border: 1px solid var(--primary-100);
      padding: 3px 10px;
      border-radius: 12px;
      margin-bottom: 20px;
    }
    .illustration-box {
      margin-bottom: 20px;
    }
    .error-title {
      font-size: 1.4rem;
      font-weight: 800;
      color: var(--text-primary);
      margin-bottom: 8px;
    }
    .error-desc {
      font-size: 0.875rem;
      color: var(--text-secondary);
      line-height: 1.5;
      margin-bottom: 24px;
    }
    .action-buttons {
      display: flex;
      gap: 12px;
    }
  `]
})
export class NotFoundComponent {}
