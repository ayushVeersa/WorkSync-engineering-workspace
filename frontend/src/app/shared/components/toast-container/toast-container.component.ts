import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ToastService } from '../../../core/services/toast.service';

@Component({
  selector: 'app-toast-container',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="toast-wrapper">
      <div
        *ngFor="let toast of toastService.toasts()"
        class="toast-card"
        [ngClass]="'toast-' + toast.type"
      >
        <div class="toast-icon">
          <span *ngIf="toast.type === 'success'">✓</span>
          <span *ngIf="toast.type === 'error'">✕</span>
          <span *ngIf="toast.type === 'warning'">⚠</span>
          <span *ngIf="toast.type === 'info'">ℹ</span>
        </div>

        <div class="toast-body">
          <h4 *ngIf="toast.title" class="toast-title">
            {{ toast.title }}
          </h4>

          <p class="toast-message">
            {{ toast.message }}
          </p>
        </div>

        <button
          class="toast-close"
          (click)="toastService.remove(toast.id)"
        >
          ✕
        </button>
      </div>
    </div>
  `,
  styles: [`
    .toast-wrapper {
      position: fixed;
      top: 20px;
      right: 20px;
      z-index: 9999;
      display: flex;
      flex-direction: column;
      gap: 10px;
      max-width: 400px;
      width: 100%;
      pointer-events: none;
    }

    .toast-card {
      pointer-events: auto;
      display: flex;
      align-items: flex-start;
      gap: 12px;
      padding: 14px 16px;
      border-radius: var(--radius-md);

      /* Light toast */
      background: var(--bg-surface);
      color: var(--text-primary);

      box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.15);
      border: 1px solid var(--border-color);

      animation: slideInRight 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .toast-success {
      border-left: 4px solid var(--emerald-500);
    }

    .toast-error {
      border-left: 4px solid var(--rose-500);
    }

    .toast-warning {
      border-left: 4px solid var(--amber-500);
    }

    .toast-info {
      border-left: 4px solid var(--primary-500);
    }

    .toast-icon {
      font-weight: bold;
      font-size: 1rem;
    }

    .toast-success .toast-icon {
      color: var(--emerald-500);
    }

    .toast-error .toast-icon {
      color: var(--rose-500);
    }

    .toast-warning .toast-icon {
      color: var(--amber-500);
    }

    .toast-info .toast-icon {
      color: var(--primary-500);
    }

    .toast-body {
      flex: 1;
    }

    .toast-title {
      font-size: 0.875rem;
      font-weight: 700;
      margin-bottom: 2px;
      color: var(--text-primary);
    }

    .toast-message {
      font-size: 0.825rem;
      color: var(--text-secondary);
      margin: 0;
    }

    .toast-close {
      background: none;
      border: none;
      color: var(--text-muted);
      cursor: pointer;
      font-size: 0.9rem;
    }

    .toast-close:hover {
      color: var(--text-primary);
    }

    @keyframes slideInRight {
      from {
        transform: translateX(100%);
        opacity: 0;
      }

      to {
        transform: translateX(0);
        opacity: 1;
      }
    }
  `]
})
export class ToastContainerComponent {
  toastService = inject(ToastService);
}