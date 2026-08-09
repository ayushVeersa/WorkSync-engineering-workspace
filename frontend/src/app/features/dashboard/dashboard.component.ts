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
  template: `
    <div class="dashboard-container">
      <!-- Page Header -->
      <div class="page-title-row">
        <div>
          <h2>Engineering Overview</h2>
          <p class="text-muted text-sm">System statistics, active workload, and project velocity</p>
        </div>

        <div class="action-buttons">
          <a routerLink="/issues" class="btn btn-primary btn-sm">
            <app-svg-icon name="plus" [size]="14"></app-svg-icon>
            <span>New Task</span>
          </a>
        </div>
      </div>

      <!-- Compact Restrained Metrics Row -->
      <div class="metrics-row">
        <div class="metric-box panel">
          <span class="metric-label">Active Projects</span>
          <span class="metric-number">{{ summary()?.active_projects || 0 }}</span>
          <span class="metric-sub">{{ summary()?.total_projects || 0 }} total</span>
        </div>

        <div class="metric-box panel">
          <span class="metric-label">Total Open Tasks</span>
          <span class="metric-number">{{ summary()?.total_issues || 0 }}</span>
          <span class="metric-sub">Across all projects</span>
        </div>

        <div class="metric-box panel">
          <span class="metric-label">Team Members</span>
          <span class="metric-number">{{ summary()?.total_employees || 0 }}</span>
          <span class="metric-sub">{{ summary()?.total_departments || 0 }} departments</span>
        </div>

        <div class="metric-box panel">
          <span class="metric-label">Discussion Comments</span>
          <span class="metric-number">{{ summary()?.total_comments || 0 }}</span>
          <span class="metric-sub">Logged activity</span>
        </div>
      </div>

      <!-- Main Panels Layout -->
      <div class="panels-grid">
        <!-- Recent Tasks Panel -->
        <div class="panel content-panel">
          <div class="panel-header">
            <h3>Recent Workspace Tasks</h3>
            <a routerLink="/issues" class="link-action">View All Tasks →</a>
          </div>

          <div class="table-wrapper">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Task Title</th>
                  <th>Type</th>
                  <th>Priority</th>
                  <th>Status</th>
                  <th>Updated</th>
                </tr>
              </thead>
              <tbody>
                <tr *ngFor="let issue of recentTasks()">
                  <td class="font-semibold">{{ issue.title }}</td>
                  <td class="text-muted">{{ issue.issue_type }}</td>
                  <td><app-status-badge [type]="issue.priority"></app-status-badge></td>
                  <td><app-status-badge [type]="issue.status"></app-status-badge></td>
                  <td class="text-muted">{{ issue.updated_at | date:'shortDate' }}</td>
                </tr>

                <tr *ngIf="recentTasks().length === 0">
                  <td colspan="5" class="text-center py-3 text-muted">
                    No open tasks found in workspace.
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Right Side Panel: Status Distribution & My Work -->
        <div class="side-stack">
          <!-- Status Distribution Panel -->
          <div class="panel content-panel">
            <div class="panel-header">
              <h3>Task Status Distribution</h3>
            </div>

            <div class="status-rows">
              <div *ngFor="let st of statusSummary()" class="status-item">
                <div class="status-label-group">
                  <app-status-badge [type]="st.status"></app-status-badge>
                  <span class="status-count-val">{{ st.count }}</span>
                </div>
                <div class="bar-track">
                  <div
                    class="bar-fill"
                    [style.width.%]="calcPercentage(st.count, summary()?.total_issues)"
                  ></div>
                </div>
              </div>

              <div *ngIf="statusSummary().length === 0" class="text-muted text-sm py-2 text-center">
                No status data available.
              </div>
            </div>
          </div>

          <!-- My Work Metrics -->
          <div *ngIf="authService.isAdminOrManager()" class="panel content-panel">
            <div class="panel-header">
              <h3>Personal Assignments</h3>
            </div>

            <div class="my-work-grid">
              <div class="work-stat">
                <span class="work-num">{{ myWork()?.assigned_issues || 0 }}</span>
                <span class="work-lbl">Assigned</span>
              </div>
              <div class="work-stat">
                <span class="work-num text-success">{{ myWork()?.completed_issues || 0 }}</span>
                <span class="work-lbl">Completed</span>
              </div>
              <div class="work-stat">
                <span class="work-num text-info">{{ myWork()?.projects || 0 }}</span>
                <span class="work-lbl">Projects</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Projects Overview Panel -->
      <div class="panel content-panel mt-4">
        <div class="panel-header">
          <div>
            <h3>Active Project Overview</h3>
            <p class="panel-sub">Project teams, task volume, and management links</p>
          </div>
          <a routerLink="/projects" class="btn btn-secondary btn-sm">Projects Directory</a>
        </div>

        <div class="table-wrapper">
          <table class="data-table">
            <thead>
              <tr>
                <th>Project Name</th>
                <th>Assigned Members</th>
                <th>Task Count</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              <tr *ngFor="let proj of projectOverview()">
                <td class="font-semibold">{{ proj.name }}</td>
                <td>{{ proj.members }} members</td>
                <td>{{ proj.issues }} tasks</td>
                <td>
                  <a [routerLink]="['/projects', proj.id]" class="btn btn-secondary btn-sm">
                    Open Project
                  </a>
                </td>
              </tr>

              <tr *ngIf="projectOverview().length === 0">
                <td colspan="4" class="text-center py-3 text-muted">
                  No active projects found.
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .dashboard-container {
      display: flex;
      flex-direction: column;
      gap: 16px;
    }

    .page-title-row {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 4px;
    }

    .page-title-row h2 {
      font-size: 1.2rem;
      font-weight: 700;
    }

    .text-sm { font-size: 0.8rem; }
    .text-muted { color: var(--text-muted); }

    /* Compact Restrained Metrics Row */
    .metrics-row {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 12px;
    }

    .metric-box {
      padding: 12px 16px;
      display: flex;
      flex-direction: column;
      background: var(--bg-surface);
    }

    .metric-label {
      font-size: 0.725rem;
      font-weight: 600;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.03em;
    }

    .metric-number {
      font-size: 1.4rem;
      font-weight: 700;
      color: var(--text-primary);
      line-height: 1.2;
      margin: 2px 0;
    }

    .metric-sub {
      font-size: 0.725rem;
      color: var(--text-secondary);
    }

    /* Panels Grid */
    .panels-grid {
      display: grid;
      grid-template-columns: 1fr 320px;
      gap: 16px;
    }

    .content-panel {
      padding: 16px;
    }

    .panel-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 12px;
    }

    .panel-header h3 {
      font-size: 0.925rem;
      font-weight: 600;
      margin: 0;
    }

    .panel-sub {
      font-size: 0.75rem;
      color: var(--text-muted);
      margin-top: 2px;
    }

    .link-action {
      font-size: 0.775rem;
      color: var(--primary-600);
      text-decoration: none;
      font-weight: 600;
    }

    .side-stack {
      display: flex;
      flex-direction: column;
      gap: 16px;
    }

    .status-rows {
      display: flex;
      flex-direction: column;
      gap: 10px;
    }

    .status-item {
      display: flex;
      flex-direction: column;
      gap: 4px;
    }

    .status-label-group {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .status-count-val {
      font-size: 0.775rem;
      font-weight: 700;
      color: var(--text-primary);
    }

    .bar-track {
      height: 5px;
      background: var(--bg-subtle);
      border-radius: 3px;
      overflow: hidden;
    }

    .bar-fill {
      height: 100%;
      background-color: var(--primary-600);
      border-radius: 3px;
    }

    .my-work-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 8px;
    }

    .work-stat {
      background: var(--bg-subtle);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-sm);
      padding: 10px 6px;
      text-align: center;
      display: flex;
      flex-direction: column;
    }

    .work-num { font-size: 1.15rem; font-weight: 700; }
    .work-lbl { font-size: 0.7rem; color: var(--text-muted); }

    .text-success { color: var(--color-success); }
    .text-info { color: var(--color-info); }
    .mt-4 { margin-top: 16px; }

    @media (max-width: 992px) {
      .metrics-row { grid-template-columns: repeat(2, 1fr); }
      .panels-grid { grid-template-columns: 1fr; }
    }
  `]
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
