import { Component, inject, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { AuthService } from '../../../core/services/auth.service';
import { SvgIconComponent } from '../svg-icon/svg-icon.component';

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [CommonModule, RouterModule, SvgIconComponent],
  template: `
    <aside class="sidebar-container" [class.mobile-open]="mobileOpen">
      <div class="sidebar-header">
        <div class="logo-box">WS</div>
        <div class="brand-info">
          <span class="brand-name">WorkSync</span>
          <span class="brand-tag">Enterprise v2.4</span>
        </div>
      </div>

      <nav class="nav-section">
        <div class="nav-group-title">WORKSPACE</div>

        <a routerLink="/dashboard" routerLinkActive="active" class="nav-item" (click)="onNavClick()">
          <app-svg-icon name="dashboard" [size]="16"></app-svg-icon>
          <span>Dashboard</span>
        </a>

        <a routerLink="/projects" routerLinkActive="active" class="nav-item" (click)="onNavClick()">
          <app-svg-icon name="projects" [size]="16"></app-svg-icon>
          <span>Projects</span>
        </a>

        <a routerLink="/issues" routerLinkActive="active" class="nav-item" (click)="onNavClick()">
          <app-svg-icon name="kanban" [size]="16"></app-svg-icon>
          <span>Tasks & Kanban</span>
        </a>

        <div class="nav-group-title">ORGANIZATION</div>

        <a
          *ngIf="authService.isAdminOrManager()"
          routerLink="/employees"
          routerLinkActive="active"
          class="nav-item"
          (click)="onNavClick()"
        >
          <app-svg-icon name="team" [size]="16"></app-svg-icon>
          <span>Team Members</span>
        </a>

        <a
          *ngIf="authService.isAdmin()"
          routerLink="/departments"
          routerLinkActive="active"
          class="nav-item"
          (click)="onNavClick()"
        >
          <app-svg-icon name="departments" [size]="16"></app-svg-icon>
          <span>Departments</span>
        </a>

        <div class="nav-group-title">ACCOUNT</div>

        <a routerLink="/profile" routerLinkActive="active" class="nav-item" (click)="onNavClick()">
          <app-svg-icon name="profile" [size]="16"></app-svg-icon>
          <span>My Account</span>
        </a>
      </nav>

      <div class="sidebar-footer">
        <div class="status-indicator-box">
          <span class="indicator-dot"></span>
          <span>API Connected</span>
        </div>
      </div>
    </aside>

    <div *ngIf="mobileOpen" class="mobile-backdrop" (click)="closeMobileMenu.emit()"></div>
  `,
  styles: [`
    .sidebar-container {
      width: 220px;
      height: 100vh;
      background: var(--bg-surface);
      border-right: 1px solid var(--border-color);
      display: flex;
      flex-direction: column;
      position: fixed;
      left: 0;
      top: 0;
      z-index: 200;
      transition: transform 0.2s ease;
    }

    .sidebar-header {
      height: 48px;
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 0 14px;
      border-bottom: 1px solid var(--border-color);
    }

    .logo-box {
      width: 26px;
      height: 26px;
      background: var(--primary-dark);
      color: #FFFFFF;
      font-size: 0.75rem;
      font-weight: 800;
      border-radius: var(--radius-sm);
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .brand-info {
      display: flex;
      flex-direction: column;
    }

    .brand-name {
      font-size: 0.875rem;
      font-weight: 700;
      color: var(--text-primary);
      line-height: 1.1;
    }

    .brand-tag {
      font-size: 0.65rem;
      color: var(--text-muted);
    }

    .nav-section {
      flex: 1;
      padding: 12px 8px;
      display: flex;
      flex-direction: column;
      gap: 2px;
      overflow-y: auto;
    }

    .nav-group-title {
      font-size: 0.65rem;
      font-weight: 700;
      color: var(--text-muted);
      letter-spacing: 0.06em;
      padding: 10px 10px 4px;
    }

    .nav-item {
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 6px 10px;
      border-radius: var(--radius-sm);
      color: var(--text-secondary);
      text-decoration: none;
      font-size: 0.825rem;
      font-weight: 500;
      transition: background-color 0.15s ease, color 0.15s ease;
    }

    .nav-item:hover {
      background-color: var(--bg-subtle);
      color: var(--text-primary);
    }

    .nav-item.active {
      background-color: var(--primary-50);
      color: var(--primary-600);
      font-weight: 600;
    }

    .sidebar-footer {
      padding: 10px 14px;
      border-top: 1px solid var(--border-color);
    }

    .status-indicator-box {
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 0.725rem;
      color: var(--text-muted);
    }

    .indicator-dot {
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background-color: var(--color-success);
    }

    @media (max-width: 768px) {
      .sidebar-container {
        transform: translateX(-100%);
      }
      .sidebar-container.mobile-open {
        transform: translateX(0);
      }
      .mobile-backdrop {
        position: fixed;
        top: 0; left: 0;
        width: 100vw; height: 100vh;
        background: rgba(15, 23, 42, 0.4);
        z-index: 190;
      }
    }
  `]
})
export class SidebarComponent {
  @Input() mobileOpen = false;
  @Output() closeMobileMenu = new EventEmitter<void>();

  authService = inject(AuthService);

  onNavClick() {
    if (this.mobileOpen) {
      this.closeMobileMenu.emit();
    }
  }
}
