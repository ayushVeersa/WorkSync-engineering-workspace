import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { DashboardService } from '../../core/services/dashboard.service';
import { AuthService } from '../../core/services/auth.service';
import { IssueService } from '../../core/services/issue.service';
import {
  DashboardSummary,
  MyWorkSummary,
  IssueStatusSummary,
  ProjectOverview
} from '../../core/models/dashboard.model';
import { IssueResponse } from '../../core/models/issue.model';
import { StatusBadgeComponent } from '../../shared/components/status-badge/status-badge.component';
import { SvgIconComponent } from '../../shared/components/svg-icon/svg-icon.component';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, RouterModule, StatusBadgeComponent, SvgIconComponent],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.scss'
})
export class DashboardComponent implements OnInit {
  private dashboardService = inject(DashboardService);
  private issueService = inject(IssueService);
  authService = inject(AuthService);

  summary = signal<DashboardSummary | null>(null);
  myWork = signal<MyWorkSummary | null>(null);
  statusSummary = signal<IssueStatusSummary[]>([]);
  projectOverview = signal<ProjectOverview[]>([]);
  recentTasks = signal<IssueResponse[]>([]);

  ngOnInit() {
    this.fetchDashboardData();
  }

  fetchDashboardData() {
    this.dashboardService.getSummary().subscribe(s => this.summary.set(s));
    this.issueService.getIssues().subscribe(issues => this.recentTasks.set(issues.slice(0, 8)));

    this.authService.ensureCurrentUser().subscribe(user => {
      if (user?.role === 'ADMIN' || user?.role === 'MANAGER') {
        this.dashboardService.getMyWork().subscribe(w => this.myWork.set(w));
        this.dashboardService.getIssuesByStatus().subscribe(st => this.statusSummary.set(st));
        this.dashboardService.getProjectOverview().subscribe(p => this.projectOverview.set(p));
      }
    });
  }

  calcPercentage(count: number, total?: number): number {
    if (!total || total === 0) return 0;
    return Math.round((count / total) * 100);
  }
}
