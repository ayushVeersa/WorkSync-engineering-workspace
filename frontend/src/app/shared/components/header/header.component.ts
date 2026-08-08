import { Component, inject, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { AuthService } from '../../../core/services/auth.service';
import { BadgeComponent } from '../badge/badge.component';

@Component({
  selector: 'app-header',
  standalone: true,
  imports: [CommonModule, RouterModule, BadgeComponent],
  template: `
    <header class="app-header">
      <div class="header-left">
        <h2 class="page-greeting">
          {{ greeting() }}, <span class="user-highlight">{{ currentUser()?.name }}</span> 👋
        </h2>
        <span class="user-email">{{ currentUser()?.email }}</span>
      </div>

      <div class="header-right">
        <app-badge
          *ngIf="currentUser()?.role"
          [type]="currentUser()!.role"
        ></app-badge>

        <div class="user-menu">
          <div class="avatar">
            {{ getInitials(currentUser()?.name) }}
          </div>
          <button class="btn btn-secondary btn-sm" (click)="authService.logout()">
            Sign Out
          </button>
        </div>
      </div>
    </header>
  `,
  styles: [`
    .app-header {
      height: 72px;
      background: rgba(30, 41, 59, 0.8);
      backdrop-filter: blur(12px);
      border-bottom: 1px solid var(--border-color);
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 28px;
      position: sticky;
      top: 0;
      z-index: 100;
    }

    .header-left {
      display: flex;
      flex-direction: column;
    }

    .page-greeting {
      font-size: 1.15rem;
      font-weight: 700;
      color: var(--text-primary);
      margin: 0;
    }

    .user-highlight {
      color: var(--primary-500);
    }

    .user-email {
      font-size: 0.775rem;
      color: var(--text-muted);
    }

    .header-right {
      display: flex;
      align-items: center;
      gap: 16px;
    }

    .user-menu {
      display: flex;
      align-items: center;
      gap: 12px;
    }
  `]
})
export class HeaderComponent {
  authService = inject(AuthService);
  currentUser = this.authService.currentUser;

  greeting = computed(() => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 18) return 'Good afternoon';
    return 'Good evening';
  });

  getInitials(name?: string): string {
    if (!name) return 'U';
    return name
      .split(' ')
      .map(part => part[0])
      .slice(0, 2)
      .join('')
      .toUpperCase();
  }
}
