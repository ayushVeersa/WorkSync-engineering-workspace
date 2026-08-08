import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-badge',
  standalone: true,
  imports: [CommonModule],
  template: `
    <span class="badge" [ngClass]="'badge-' + type.toLowerCase()">
      {{ label || type }}
    </span>
  `
})
export class BadgeComponent {
  @Input({ required: true }) type!: string;
  @Input() label?: string;
}
