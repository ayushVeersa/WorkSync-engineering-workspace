import { Component, OnInit, inject, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';
import { EmployeeService } from '../../core/services/employee.service';
import { IssueService } from '../../core/services/issue.service';
import { ProjectService } from '../../core/services/project.service';
import { ActivityService } from '../../core/services/activity.service';
import { EmployeeResponse } from '../../core/models/employee.model';
import { IssueResponse, IssueStatus, IssuePriority } from '../../core/models/issue.model';
import { ProjectResponse } from '../../core/models/project.model';
import { ActivityLogResponse } from '../../core/models/activity.model';
import { StatusBadgeComponent } from '../../shared/components/status-badge/status-badge.component';
import { SvgIconComponent } from '../../shared/components/svg-icon/svg-icon.component';
import { EmptyStateComponent } from '../../shared/components/empty-state/empty-state.component';

@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    RouterModule,
    StatusBadgeComponent,
    SvgIconComponent,
    EmptyStateComponent
  ],
  templateUrl: './profile.component.html',
  styleUrl: './profile.component.scss'
})
export class ProfileComponent implements OnInit {
  private authService = inject(AuthService);
  private employeeService = inject(EmployeeService);
  private issueService = inject(IssueService);
  private projectService = inject(ProjectService);
  private activityService = inject(ActivityService);

  user = this.authService.currentUser;
  employee = signal<EmployeeResponse | null>(null);
  myIssues = signal<IssueResponse[]>([]);
  myProjects = signal<ProjectResponse[]>([]);
  myActivities = signal<ActivityLogResponse[]>([]);

  activeTab = signal<'tasks' | 'projects' | 'activity'>('tasks');
  selectedStatusFilter = signal<string>('');
  selectedPriorityFilter = signal<string>('');

  statuses = Object.values(IssueStatus);
  priorities = Object.values(IssuePriority);

  stats = computed(() => {
    const issues = this.myIssues();
    const total = issues.length;
    const inProgress = issues.filter(i => i.status === IssueStatus.IN_PROGRESS).length;
    const completed = issues.filter(i => i.status === IssueStatus.DONE).length;
    const now = new Date();
    const overdue = issues.filter(i => i.status !== IssueStatus.DONE && i.due_date && new Date(i.due_date) < now).length;
    const rate = total > 0 ? Math.round((completed / total) * 100) : 0;

    return { total, inProgress, completed, overdue, rate };
  });

  filteredIssues = computed(() => {
    let list = this.myIssues();
    const st = this.selectedStatusFilter();
    const pr = this.selectedPriorityFilter();

    if (st) {
      list = list.filter(i => i.status === st);
    }
    if (pr) {
      list = list.filter(i => i.priority === pr);
    }
    return list;
  });

  ngOnInit() {
    this.employeeService.getCurrentEmployee().subscribe(e => {
      this.employee.set(e);
      if (e) {
        this.projectService.getEmployeeProjects(e.id).subscribe(p => this.myProjects.set(p));
        this.activityService.getActivities({ actor_id: e.id, limit: 10 }).subscribe(act => this.myActivities.set(act));
      }
    });

    this.issueService.getMyIssues().subscribe(i => this.myIssues.set(i));
  }

  setTab(tab: 'tasks' | 'projects' | 'activity') {
    this.activeTab.set(tab);
  }

  clearFilters() {
    this.selectedStatusFilter.set('');
    this.selectedPriorityFilter.set('');
  }
}
