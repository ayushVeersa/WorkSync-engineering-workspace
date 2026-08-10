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
  templateUrl: './topbar.component.html',
  styleUrl: './topbar.component.scss'
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
