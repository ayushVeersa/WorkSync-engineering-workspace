import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterModule } from '@angular/router';
import { DragDropModule, CdkDragDrop, moveItemInArray, transferArrayItem } from '@angular/cdk/drag-drop';
import { ProjectService } from '../../../core/services/project.service';
import { IssueService } from '../../../core/services/issue.service';
import { AuthService } from '../../../core/services/auth.service';
import { ToastService } from '../../../core/services/toast.service';
import { ProjectResponse, ProjectStatus } from '../../../core/models/project.model';
import { EmployeeResponse } from '../../../core/models/employee.model';
import { IssueResponse, IssueStatus } from '../../../core/models/issue.model';
import { StatusBadgeComponent } from '../../../shared/components/status-badge/status-badge.component';
import { SvgIconComponent } from '../../../shared/components/svg-icon/svg-icon.component';

@Component({
  selector: 'app-project-detail',
  standalone: true,
  imports: [CommonModule, RouterModule, DragDropModule, StatusBadgeComponent, SvgIconComponent],
  template: `
    <div *ngIf="project()" class="project-detail-page">
      <!-- Breadcrumb Nav -->
      <a routerLink="/projects" class="back-link">← Back to Projects</a>

      <!-- Banner Header Panel -->
      <div class="panel banner-panel">
        <div class="banner-top">
          <div>
            <div class="title-row">
              <h2>{{ project()?.name }}</h2>
              <app-status-badge *ngIf="project()?.status" [type]="project()!.status"></app-status-badge>
            </div>
            <p class="desc-text">{{ project()?.description || 'No project description provided.' }}</p>
          </div>

          <div *ngIf="authService.isAdminOrManager()" class="status-edit-box">
            <label class="form-label">Project Status</label>
            <select class="form-select" [value]="project()?.status" (change)="onStatusChange($event)">
              <option [value]="statuses.PLANNING">PLANNING</option>
              <option [value]="statuses.ACTIVE">ACTIVE</option>
              <option [value]="statuses.ON_HOLD">ON_HOLD</option>
              <option [value]="statuses.COMPLETED">COMPLETED</option>
            </select>
          </div>
        </div>

        <!-- Tabbed Navigation Bar -->
        <div class="project-tabs">
          <button
            class="tab-btn"
            [class.active]="activeTab() === 'overview'"
            (click)="activeTab.set('overview')"
          >
            Overview
          </button>

          <button
            class="tab-btn"
            [class.active]="activeTab() === 'tasks'"
            (click)="activeTab.set('tasks')"
          >
            Tasks ({{ issues().length }})
          </button>

          <button
            class="tab-btn"
            [class.active]="activeTab() === 'kanban'"
            (click)="activeTab.set('kanban')"
          >
            Kanban Board
          </button>

          <button
            class="tab-btn"
            [class.active]="activeTab() === 'team'"
            (click)="activeTab.set('team')"
          >
            Team Members ({{ members().length }})
          </button>
        </div>
      </div>

      <!-- TAB 1: OVERVIEW -->
      <div *ngIf="activeTab() === 'overview'" class="tab-content overview-grid">
        <div class="panel content-panel">
          <div class="panel-header">
            <h3>Project Summary & Metrics</h3>
          </div>
          <div class="info-rows-list">
            <div class="info-item">
              <span class="info-lbl">Project ID</span>
              <span class="info-val">#{{ project()?.id }}</span>
            </div>
            <div class="info-item">
              <span class="info-lbl">Owner ID</span>
              <span class="info-val">Emp #{{ project()?.owner_id }}</span>
            </div>
            <div class="info-item">
              <span class="info-lbl">Created On</span>
              <span class="info-val">{{ project()?.created_at | date:'medium' }}</span>
            </div>
            <div class="info-item">
              <span class="info-lbl">Last Updated</span>
              <span class="info-val">{{ project()?.updated_at | date:'medium' }}</span>
            </div>
            <div class="info-item">
              <span class="info-lbl">Total Tasks Logged</span>
              <span class="info-val">{{ issues().length }}</span>
            </div>
          </div>
        </div>

        <div class="panel content-panel">
          <div class="panel-header">
            <h3>Assigned Team ({{ members().length }})</h3>
          </div>
          <div class="team-chips-list">
            <div *ngFor="let member of members()" class="member-chip-box">
              <span class="member-name">{{ member.user.name }}</span>
              <span class="member-sub">{{ member.designation }}</span>
            </div>
            <div *ngIf="members().length === 0" class="text-muted text-xs font-italic">
              No team members assigned yet.
            </div>
          </div>
        </div>
      </div>

      <!-- TAB 2: TASKS TABLE LIST -->
      <div *ngIf="activeTab() === 'tasks'" class="tab-content">
        <div class="table-wrapper panel">
          <table class="data-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Title</th>
                <th>Type</th>
                <th>Priority</th>
                <th>Status</th>
                <th>Assignee</th>
                <th>Updated</th>
              </tr>
            </thead>
            <tbody>
              <tr *ngFor="let issue of issues()">
                <td class="font-semibold">#{{ issue.id }}</td>
                <td class="font-semibold">{{ issue.title }}</td>
                <td class="text-muted">{{ issue.issue_type }}</td>
                <td><app-status-badge [type]="issue.priority"></app-status-badge></td>
                <td><app-status-badge [type]="issue.status"></app-status-badge></td>
                <td>Emp #{{ issue.assignee_id }}</td>
                <td class="text-muted">{{ issue.updated_at | date:'shortDate' }}</td>
              </tr>
              <tr *ngIf="issues().length === 0">
                <td colspan="7" class="text-center py-4 text-muted">No tasks logged for this project.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- TAB 3: KANBAN BOARD -->
      <div *ngIf="activeTab() === 'kanban'" class="tab-content">
        <div class="kanban-columns-container" cdkDropListGroup>
          <div *ngFor="let col of kanbanColumns()" class="kanban-col panel">
            <div class="col-header">
              <span class="col-title">{{ col.title }}</span>
              <span class="col-badge">{{ col.issues.length }}</span>
            </div>

            <div
              cdkDropList
              [cdkDropListData]="col.issues"
              (cdkDropListDropped)="onDrop($event, col.status)"
              class="task-drop-list"
            >
              <div *ngFor="let issue of col.issues" cdkDrag class="task-card">
                <div class="card-meta-top">
                  <span class="task-key">#{{ issue.id }}</span>
                  <app-status-badge [type]="issue.priority"></app-status-badge>
                </div>
                <h4 class="task-card-title">{{ issue.title }}</h4>
                <div class="card-meta-bottom">
                  <span class="type-tag">{{ issue.issue_type }}</span>
                  <span>Emp #{{ issue.assignee_id }}</span>
                </div>
              </div>

              <div *ngIf="col.issues.length === 0" class="empty-drop-zone">No {{ col.title }} tasks</div>
            </div>
          </div>
        </div>
      </div>

      <!-- TAB 4: TEAM MEMBERS -->
      <div *ngIf="activeTab() === 'team'" class="tab-content">
        <div class="table-wrapper panel">
          <table class="data-table">
            <thead>
              <tr>
                <th>Member Name</th>
                <th>Work Email</th>
                <th>Designation</th>
                <th>Role</th>
              </tr>
            </thead>
            <tbody>
              <tr *ngFor="let m of members()">
                <td class="font-semibold">{{ m.user.name }}</td>
                <td class="text-muted">{{ m.user.email }}</td>
                <td>{{ m.designation }}</td>
                <td><app-status-badge [type]="m.user.role"></app-status-badge></td>
              </tr>
              <tr *ngIf="members().length === 0">
                <td colspan="4" class="text-center py-4 text-muted">No members assigned to this project.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .project-detail-page { display: flex; flex-direction: column; gap: 14px; }
    .back-link { font-size: 0.775rem; color: var(--text-muted); text-decoration: none; }
    .back-link:hover { color: var(--primary-600); }

    .banner-panel { padding: 16px 20px 0; }
    .banner-top { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px; }
    .title-row { display: flex; align-items: center; gap: 10px; margin-bottom: 4px; }
    .title-row h2 { font-size: 1.3rem; margin: 0; }
    .desc-text { font-size: 0.825rem; color: var(--text-secondary); margin: 0; }

    .status-edit-box { display: flex; flex-direction: column; gap: 4px; width: 140px; }

    .project-tabs { display: flex; gap: 2px; border-top: 1px solid var(--border-color); }
    .tab-btn {
      padding: 9px 14px;
      font-size: 0.8rem;
      font-weight: 500;
      background: none;
      border: none;
      border-bottom: 2px solid transparent;
      color: var(--text-secondary);
      cursor: pointer;
    }
    .tab-btn:hover { color: var(--text-primary); }
    .tab-btn.active { color: var(--primary-600); border-bottom-color: var(--primary-600); font-weight: 600; }

    .overview-grid { display: grid; grid-template-columns: 1fr 300px; gap: 14px; }
    .content-panel { padding: 16px; }
    .panel-header h3 { font-size: 0.9rem; font-weight: 600; margin-bottom: 12px; }

    .info-rows-list { display: flex; flex-direction: column; gap: 8px; }
    .info-item { display: flex; justify-content: space-between; font-size: 0.8rem; border-bottom: 1px solid var(--border-color); padding-bottom: 6px; }
    .info-lbl { color: var(--text-muted); }
    .info-val { font-weight: 600; color: var(--text-primary); }

    .team-chips-list { display: flex; flex-direction: column; gap: 6px; }
    .member-chip-box {
      padding: 8px 10px;
      background: var(--bg-subtle);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-sm);
      display: flex; flex-direction: column;
    }
    .member-name { font-size: 0.8rem; font-weight: 600; }
    .member-sub { font-size: 0.7rem; color: var(--text-muted); }

    /* KANBAN TAB */
    .kanban-columns-container { display: grid; grid-template-columns: repeat(6, minmax(200px, 1fr)); gap: 10px; overflow-x: auto; }
    .kanban-col { display: flex; flex-direction: column; background: var(--bg-subtle); border: 1px solid var(--border-color); }
    .col-header { padding: 8px; background: var(--bg-surface); border-bottom: 1px solid var(--border-color); display: flex; justify-content: space-between; }
    .col-title { font-size: 0.725rem; font-weight: 700; text-transform: uppercase; color: var(--text-secondary); }
    .col-badge { font-size: 0.7rem; background: var(--bg-subtle); padding: 1px 5px; border-radius: var(--radius-sm); }
    .task-drop-list { padding: 6px; display: flex; flex-direction: column; gap: 6px; min-height: 200px; }
    .task-card { background: var(--bg-surface); border: 1px solid var(--border-color); border-radius: var(--radius-sm); padding: 8px; display: flex; flex-direction: column; gap: 4px; }
    .card-meta-top { display: flex; justify-content: space-between; }
    .task-key { font-size: 0.7rem; font-weight: 700; color: var(--text-muted); font-family: var(--font-mono); }
    .task-card-title { font-size: 0.8rem; font-weight: 600; }
    .card-meta-bottom { display: flex; justify-content: space-between; font-size: 0.7rem; color: var(--text-muted); }
    .type-tag { font-weight: 600; text-transform: uppercase; color: var(--primary-600); }
    .empty-drop-zone { padding: 16px 4px; text-align: center; font-size: 0.7rem; color: var(--text-muted); }
    .text-xs { font-size: 0.75rem; }
    .font-italic { font-style: italic; }
  `]
})
export class ProjectDetailComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private projectService = inject(ProjectService);
  private issueService = inject(IssueService);
  private toast = inject(ToastService);
  authService = inject(AuthService);

  projectId!: number;
  project = signal<ProjectResponse | null>(null);
  issues = signal<IssueResponse[]>([]);
  members = signal<EmployeeResponse[]>([]);
  statuses = ProjectStatus;

  activeTab = signal<'overview' | 'tasks' | 'kanban' | 'team'>('overview');

  kanbanColumns = signal<{ title: string; status: IssueStatus; issues: IssueResponse[] }[]>([
    { title: 'Backlog', status: IssueStatus.BACKLOG, issues: [] },
    { title: 'To Do', status: IssueStatus.TODO, issues: [] },
    { title: 'In Progress', status: IssueStatus.IN_PROGRESS, issues: [] },
    { title: 'Review', status: IssueStatus.REVIEW, issues: [] },
    { title: 'Testing', status: IssueStatus.TESTING, issues: [] },
    { title: 'Done', status: IssueStatus.DONE, issues: [] }
  ]);

  ngOnInit() {
    this.route.params.subscribe(params => {
      this.projectId = Number(params['id']);
      this.loadProject();
    });
  }

  loadProject() {
    this.projectService.getProjectById(this.projectId).subscribe(p => this.project.set(p));

    this.issueService.getProjectIssues(this.projectId).subscribe(issues => {
      this.issues.set(issues);
      this.distributeKanban(issues);
    });

    this.projectService.getProjectMembers(this.projectId).subscribe(m => this.members.set(m));
  }

  distributeKanban(issues: IssueResponse[]) {
    this.kanbanColumns.update(cols =>
      cols.map(col => ({
        ...col,
        issues: issues.filter(i => i.status === col.status)
      }))
    );
  }

  onDrop(event: CdkDragDrop<IssueResponse[]>, targetStatus: IssueStatus) {
    if (event.previousContainer === event.container) {
      moveItemInArray(event.container.data, event.previousIndex, event.currentIndex);
    } else {
      transferArrayItem(
        event.previousContainer.data,
        event.container.data,
        event.previousIndex,
        event.currentIndex
      );

      const movedTask = event.container.data[event.currentIndex];
      movedTask.status = targetStatus;

      this.issueService.updateIssue(movedTask.id, { status: targetStatus }).subscribe({
        next: updated => {
          this.toast.success(`Task #${updated.id} moved to ${targetStatus}`);
        }
      });
    }
  }

  onStatusChange(event: any) {
    const newStatus = event.target.value as ProjectStatus;
    const proj = this.project();
    if (!proj) return;

    this.projectService.updateProject(proj.id, { status: newStatus }).subscribe(updated => {
      this.project.set(updated);
      this.toast.success(`Project status updated to ${newStatus}`);
    });
  }
}
