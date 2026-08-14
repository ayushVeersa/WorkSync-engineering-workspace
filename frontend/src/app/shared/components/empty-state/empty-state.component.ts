import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-empty-state',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="empty-state-card">
      <div class="empty-icon-wrapper">
        <span class="empty-icon">{{ icon }}</span>
      </div>
      <h3 class="empty-title">{{ title }}</h3>
      <p class="empty-description">{{ description }}</p>
      <button *ngIf="actionLabel" class="btn btn-secondary btn-sm" (click)="action.emit()">
        {{ actionLabel }}
      </button>
    </div>
  `,
  styles: [`
    .empty-state-card {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      text-align: center;
      padding: 40px 20px;
      border: 1px dashed var(--border-color);
      border-radius: var(--radius-md);
      background: var(--bg-subtle);
      margin: 12px 0;
      transition: all 0.2s ease;
    }
    .empty-icon-wrapper {
      width: 48px;
      height: 48px;
      border-radius: 50%;
      background: var(--bg-surface);
      border: 1px solid var(--border-color);
      display: flex;
      align-items: center;
      justify-content: center;
      margin-bottom: 12px;
      box-shadow: var(--shadow-sm);
    }
    .empty-icon {
      font-size: 1.5rem;
      line-height: 1;
    }
    .empty-title {
      font-size: 0.95rem;
      font-weight: 700;
      color: var(--text-primary);
      margin-bottom: 4px;
    }
    .empty-description {
      font-size: 0.825rem;
      color: var(--text-secondary);
      max-width: 380px;
      margin-bottom: 14px;
      line-height: 1.4;
    }
  `]
})
export class EmptyStateComponent {
  @Input() icon = '📁';
  @Input() title = 'No records found';
  @Input() description = 'Everything looks clear right now.';
  @Input() actionLabel?: string;
  @Output() action = new EventEmitter<void>();
}
