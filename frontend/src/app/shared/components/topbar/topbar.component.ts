import { Component, inject, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, NavigationEnd } from '@angular/router';
import { filter } from 'rxjs';
import { AuthService } from '../../../core/services/auth.service';
import { SvgIconComponent } from '../svg-icon/svg-icon.component';
import { StatusBadgeComponent } from '../status-badge/status-badge.component';

@Component({
  selector: 'app-topbar',
  standalone: true,
  imports: [CommonModule, SvgIconComponent, StatusBadgeComponent],
  template: `
    <header class="topbar-container">
      <div class="topbar-left">
        <button class="menu-toggle-btn" (click)="toggleMobileMenu.emit()">
          <app-svg-icon name="menu" [size]="18"></app-svg-icon>
        </button>

        <div class="breadcrumbs">
          <span class="breadcrumb-item text-muted">Workspace</span>
          <span class="breadcrumb-separator">/</span>
          <span class="breadcrumb-item font-semibold">{{ currentSection }}</span>
        </div>
      </div>

      <div class="topbar-right">
        <div class="topbar-search">
          <app-svg-icon name="search" [size]="14"></app-svg-icon>
          <input type="text" placeholder="Search tasks, projects..." class="search-input" />
        </div>

        <div class="user-profile-menu">
          <div class="avatar-box">
            {{ getInitials(currentUser()?.name) }}
          </div>

          <div class="user-details">
            <span class="user-name">{{ currentUser()?.name }}</span>
            <app-status-badge
              *ngIf="currentUser()?.role"
              [type]="currentUser()!.role"
            ></app-status-badge>
          </div>

          <button class="btn btn-secondary btn-sm logout-btn" (click)="authService.logout()" title="Sign Out">
            Logout
          </button>
        </div>
      </div>
    </header>
  `,
  styles: [`
    .topbar-container {
      height: 48px;
      background: var(--bg-surface);
      border-bottom: 1px solid var(--border-color);
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 16px;
      position: sticky;
      top: 0;
      z-index: 100;
    }

    .topbar-left {
      display: flex;
      align-items: center;
      gap: 12px;
    }

    .menu-toggle-btn {
      display: none;
      background: none;
      border: none;
      cursor: pointer;
      color: var(--text-secondary);
      padding: 4px;
    }

    .breadcrumbs {
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 0.8rem;
    }

    .breadcrumb-separator {
      color: var(--text-muted);
    }

    .topbar-right {
      display: flex;
      align-items: center;
      gap: 16px;
    }

    .topbar-search {
      display: flex;
      align-items: center;
      gap: 6px;
      background: var(--bg-subtle);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-sm);
      padding: 4px 8px;
      width: 200px;
    }

    .search-input {
      border: none;
      background: transparent;
      font-size: 0.775rem;
      color: var(--text-primary);
      width: 100%;
      outline: none;
    }

    .user-profile-menu {
      display: flex;
      align-items: center;
      gap: 10px;
      padding-left: 12px;
      border-left: 1px solid var(--border-color);
    }

    .avatar-box {
      width: 28px;
      height: 28px;
      border-radius: var(--radius-sm);
      background: var(--primary-dark);
      color: #FFFFFF;
      font-size: 0.75rem;
      font-weight: 700;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .user-details {
      display: flex;
      align-items: center;
      gap: 6px;
    }

    .user-name {
      font-size: 0.8rem;
      font-weight: 600;
      color: var(--text-primary);
    }

    .logout-btn {
      font-size: 0.75rem;
      padding: 3px 8px;
    }

    @media (max-width: 768px) {
      .menu-toggle-btn { display: block; }
      .topbar-search { display: none; }
      .user-details { display: none; }
    }
  `]
})
export class TopbarComponent {
  @Output() toggleMobileMenu = new EventEmitter<void>();

  authService = inject(AuthService);
  private router = inject(Router);

  currentUser = this.authService.currentUser;
  currentSection = 'Dashboard';

  constructor() {
    this.router.events.pipe(
      filter((e): e is NavigationEnd => e instanceof NavigationEnd)
    ).subscribe(e => {
      const url = e.urlAfterRedirects;
      if (url.includes('/projects')) this.currentSection = 'Projects';
      else if (url.includes('/issues')) this.currentSection = 'Tasks & Kanban';
      else if (url.includes('/employees')) this.currentSection = 'Employee Directory';
      else if (url.includes('/departments')) this.currentSection = 'Departments';
      else if (url.includes('/profile')) this.currentSection = 'My Account';
      else this.currentSection = 'Dashboard';
    });
  }

  getInitials(name?: string): string {
    if (!name) return 'U';
    return name
      .split(' ')
      .map(p => p[0])
      .slice(0, 2)
      .join('')
      .toUpperCase();
  }
}
