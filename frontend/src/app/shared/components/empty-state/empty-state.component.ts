import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-empty-state',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="empty-state-card">
      <div class="empty-icon">{{ icon }}</div>
      <h3 class="empty-title">{{ title }}</h3>
      <p class="empty-description">{{ description }}</p>
      <button *ngIf="actionLabel" class="btn btn-primary btn-sm" (click)="action.emit()">
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
      padding: 48px 24px;
      border: 2px dashed var(--border-color);
      border-radius: var(--radius-lg);
      background: rgba(15, 23, 42, 0.4);
      margin: 16px 0;
    }
    .empty-icon {
      font-size: 2.5rem;
      margin-bottom: 12px;
      opacity: 0.8;
    }
    .empty-title {
      font-size: 1.1rem;
      font-weight: 700;
      margin-bottom: 6px;
    }
    .empty-description {
      font-size: 0.875rem;
      color: var(--text-secondary);
      max-width: 400px;
      margin-bottom: 16px;
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
