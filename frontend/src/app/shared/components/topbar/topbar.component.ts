import { Component, inject, Output, EventEmitter, HostListener, signal, ElementRef, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, NavigationEnd, RouterModule } from '@angular/router';
import { filter } from 'rxjs';
import { AuthService } from '../../../core/services/auth.service';
import { IssueService } from '../../../core/services/issue.service';
import { ProjectService } from '../../../core/services/project.service';
import { EmployeeService } from '../../../core/services/employee.service';
import { IssueResponse } from '../../../core/models/issue.model';
import { ProjectResponse } from '../../../core/models/project.model';
import { EmployeeResponse } from '../../../core/models/employee.model';
import { SvgIconComponent } from '../svg-icon/svg-icon.component';
import { StatusBadgeComponent } from '../status-badge/status-badge.component';

@Component({
  selector: 'app-topbar',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule, SvgIconComponent, StatusBadgeComponent],
  templateUrl: './topbar.component.html',
  styleUrl: './topbar.component.scss'
})
export class TopbarComponent {
  @Output() toggleMobileMenu = new EventEmitter<void>();
  @ViewChild('searchInput') searchInputElement!: ElementRef<HTMLInputElement>;

  authService = inject(AuthService);
  private issueService = inject(IssueService);
  private projectService = inject(ProjectService);
  private employeeService = inject(EmployeeService);
  private router = inject(Router);

  currentUser = this.authService.currentUser;
  currentSection = 'Dashboard';

  searchQuery = signal<string>('');
  isSearchOpen = signal<boolean>(false);
  isLoading = signal<boolean>(false);

  matchingTasks = signal<IssueResponse[]>([]);
  matchingProjects = signal<ProjectResponse[]>([]);
  matchingEmployees = signal<EmployeeResponse[]>([]);

  private searchDebounceTimer: any;

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
      this.closeSearch();
    });
  }

  @HostListener('window:keydown', ['$event'])
  handleGlobalKeydown(event: KeyboardEvent) {
    if ((event.ctrlKey || event.metaKey) && event.key === 'k') {
      event.preventDefault();
      this.searchInputElement?.nativeElement?.focus();
    } else if (event.key === 'Escape' && this.isSearchOpen()) {
      this.closeSearch();
    }
  }

  onSearchInput(query: string) {
    this.searchQuery.set(query);
    clearTimeout(this.searchDebounceTimer);

    if (!query || query.trim().length < 2) {
      this.isSearchOpen.set(false);
      this.matchingTasks.set([]);
      this.matchingProjects.set([]);
      this.matchingEmployees.set([]);
      return;
    }

    this.isLoading.set(true);
    this.isSearchOpen.set(true);

    this.searchDebounceTimer = setTimeout(() => {
      const q = query.trim().toLowerCase();

      // Query Tasks
      this.issueService.getIssues(undefined, undefined, undefined, undefined, undefined, q).subscribe({
        next: tasks => this.matchingTasks.set(tasks.slice(0, 4))
      });

      // Query Projects
      this.projectService.getProjects(q).subscribe({
        next: projects => this.matchingProjects.set(projects.slice(0, 4))
      });

      // Query Employees
      this.employeeService.getEmployees().subscribe({
        next: emps => {
          const matched = emps.filter(e =>
            e.user.name.toLowerCase().includes(q) ||
            e.user.email.toLowerCase().includes(q) ||
            e.designation.toLowerCase().includes(q)
          );
          this.matchingEmployees.set(matched.slice(0, 4));
          this.isLoading.set(false);
        },
        error: () => this.isLoading.set(false)
      });
    }, 250);
  }

  onSearchFocus() {
    if (this.searchQuery().trim().length >= 2) {
      this.isSearchOpen.set(true);
    }
  }

  closeSearch() {
    this.isSearchOpen.set(false);
  }

  selectResult(type: 'task' | 'project' | 'employee', item: any) {
    this.closeSearch();
    if (type === 'task') {
      this.router.navigate(['/issues']);
    } else if (type === 'project') {
      this.router.navigate(['/projects', item.id]);
    } else if (type === 'employee') {
      this.router.navigate(['/employees']);
    }
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
