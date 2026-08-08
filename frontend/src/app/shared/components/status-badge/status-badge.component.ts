import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-status-badge',
  standalone: true,
  imports: [CommonModule],
  template: `
    <span class="status-badge" [ngClass]="'status-' + type.toLowerCase()">
      {{ formattedLabel }}
    </span>
  `
})
export class StatusBadgeComponent {
  @Input({ required: true }) type!: string;
  @Input() label?: string;

  get formattedLabel(): string {
    if (this.label) return this.label;
    return this.type.replace(/_/g, ' ');
  }
}
