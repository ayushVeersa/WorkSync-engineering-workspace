import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-svg-icon',
  standalone: true,
  imports: [CommonModule],
  template: `
    <svg
      [attr.width]="size"
      [attr.height]="size"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      stroke-width="1.8"
      stroke-linecap="round"
      stroke-linejoin="round"
      class="icon-svg"
    >
      <!-- Dashboard -->
      <ng-container *ngIf="name === 'dashboard'">
        <rect x="3" y="3" width="7" height="7"></rect>
        <rect x="14" y="3" width="7" height="7"></rect>
        <rect x="14" y="14" width="7" height="7"></rect>
        <rect x="3" y="14" width="7" height="7"></rect>
      </ng-container>

      <!-- Projects / Folder -->
      <ng-container *ngIf="name === 'folder' || name === 'projects'">
        <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>
      </ng-container>

      <!-- Kanban / Board -->
      <ng-container *ngIf="name === 'kanban' || name === 'tasks'">
        <rect x="3" y="3" width="5" height="18" rx="1"></rect>
        <rect x="11" y="3" width="5" height="12" rx="1"></rect>
        <rect x="19" y="3" width="5" height="15" rx="1"></rect>
      </ng-container>

      <!-- Team / Employees -->
      <ng-container *ngIf="name === 'users' || name === 'team'">
        <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
        <circle cx="9" cy="7" r="4"></circle>
        <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
        <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
      </ng-container>

      <!-- Departments / Building -->
      <ng-container *ngIf="name === 'building' || name === 'departments'">
        <rect x="4" y="2" width="16" height="20" rx="2" ry="2"></rect>
        <path d="M9 22v-4h6v4"></path>
        <path d="M8 6h.01M16 6h.01M8 10h.01M16 10h.01M8 14h.01M16 14h.01"></path>
      </ng-container>

      <!-- Profile / User -->
      <ng-container *ngIf="name === 'user' || name === 'profile'">
        <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
        <circle cx="12" cy="7" r="4"></circle>
      </ng-container>

      <!-- Search -->
      <ng-container *ngIf="name === 'search'">
        <circle cx="11" cy="11" r="8"></circle>
        <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
      </ng-container>

      <!-- Bell / Notifications -->
      <ng-container *ngIf="name === 'bell'">
        <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path>
        <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
      </ng-container>

      <!-- Plus / Add -->
      <ng-container *ngIf="name === 'plus'">
        <line x1="12" y1="5" x2="12" y2="19"></line>
        <line x1="5" y1="12" x2="19" y2="12"></line>
      </ng-container>

      <!-- Trash / Delete -->
      <ng-container *ngIf="name === 'trash'">
        <polyline points="3 6 5 6 21 6"></polyline>
        <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
      </ng-container>

      <!-- Edit / Pencil -->
      <ng-container *ngIf="name === 'edit'">
        <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
        <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
      </ng-container>

      <!-- Paperclip / Attachment -->
      <ng-container *ngIf="name === 'attachment'">
        <path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"></path>
      </ng-container>

      <!-- Check / Confirm -->
      <ng-container *ngIf="name === 'check'">
        <polyline points="20 6 9 17 4 12"></polyline>
      </ng-container>

      <!-- Chevron Down -->
      <ng-container *ngIf="name === 'chevron-down'">
        <polyline points="6 9 12 15 18 9"></polyline>
      </ng-container>

      <!-- Menu / Hamburger -->
      <ng-container *ngIf="name === 'menu'">
        <line x1="3" y1="12" x2="21" y2="12"></line>
        <line x1="3" y1="6" x2="21" y2="6"></line>
        <line x1="3" y1="18" x2="21" y2="18"></line>
      </ng-container>
    </svg>
  `,
  styles: [`
    :host {
      display: inline-flex;
      align-items: center;
      justify-content: center;
    }
    .icon-svg {
      display: block;
      vertical-align: middle;
    }
  `]
})
export class SvgIconComponent {
  @Input({ required: true }) name!: string;
  @Input() size = 16;
}
