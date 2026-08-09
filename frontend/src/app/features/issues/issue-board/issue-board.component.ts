import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, ReactiveFormsModule, Validators, FormsModule } from '@angular/forms';
import {
  DragDropModule,
  CdkDragDrop,
  moveItemInArray,
  transferArrayItem
} from '@angular/cdk/drag-drop';

import { IssueService } from '../../../core/services/issue.service';
import { ProjectService } from '../../../core/services/project.service';
import { EmployeeService } from '../../../core/services/employee.service';
import { AuthService } from '../../../core/services/auth.service';
import { ToastService } from '../../../core/services/toast.service';
import {
  IssueResponse,
  IssueStatus,
  IssuePriority,
  IssueType
} from '../../../core/models/issue.model';
import { ProjectResponse } from '../../../core/models/project.model';
import { EmployeeResponse } from '../../../core/models/employee.model';
import { StatusBadgeComponent } from '../../../shared/components/status-badge/status-badge.component';
import { SvgIconComponent } from '../../../shared/components/svg-icon/svg-icon.component';
import { IssueDetailModalComponent } from '../issue-detail-modal/issue-detail-modal.component';

@Component({
  selector: 'app-issue-board',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    FormsModule,
    DragDropModule,
    StatusBadgeComponent,
    SvgIconComponent,
    IssueDetailModalComponent
  ],
  template: `
    <div class="board-page">
      <!-- Header -->
      <div class="page-header">
        <div>
          <h2>Tasks & Kanban Board</h2>
          <p class="text-muted text-sm">Organize, drag, and update task statuses across your engineering workflow</p>
        </div>

        <div class="tools-row">
          <div class="mode-toggle">
            <button
              class="toggle-btn"
              [class.active]="viewMode === 'kanban'"
              (click)="viewMode = 'kanban'"
            >
              <app-svg-icon name="kanban" [size]="14"></app-svg-icon>
              <span>Kanban</span>
            </button>
            <button
              class="toggle-btn"
              [class.active]="viewMode === 'list'"
              (click)="viewMode = 'list'"
            >
              <app-svg-icon name="tasks" [size]="14"></app-svg-icon>
              <span>List View</span>
            </button>
          </div>

          <button class="btn btn-primary btn-sm" (click)="openCreateModal()">
            <app-svg-icon name="plus" [size]="14"></app-svg-icon>
            <span>Log Task</span>
          </button>
        </div>
      </div>

      <!-- Compact Filters Bar -->
      <div class="filter-panel panel">
        <div class="filter-item">
          <label class="form-label">Status</label>
          <select class="form-select" [(ngModel)]="selectedStatusFilter" (change)="loadIssues()">
            <option [value]="null">All Statuses</option>
            <option *ngFor="let st of statusList" [value]="st">{{ st }}</option>
          </select>
        </div>

        <div class="filter-item">
          <label class="form-label">Priority</label>
          <select class="form-select" [(ngModel)]="selectedPriorityFilter" (change)="loadIssues()">
            <option [value]="null">All Priorities</option>
            <option *ngFor="let pr of priorityList" [value]="pr">{{ pr }}</option>
          </select>
        </div>

        <div class="filter-item filter-btn-box">
          <label class="form-label">&nbsp;</label>
          <button class="btn btn-secondary btn-sm" (click)="toggleMyIssues()">
            {{ showingMyIssuesOnly ? 'Showing My Tasks Only' : 'Filter My Tasks' }}
          </button>
        </div>
      </div>

      <!-- KANBAN BOARD VIEW WITH ANGULAR CDK DRAG & DROP -->
      <div
        *ngIf="viewMode === 'kanban'"
        class="kanban-columns-container"
        cdkDropListGroup
      >
        <div *ngFor="let col of columns()" class="kanban-col panel">
          <div class="col-header">
            <div class="col-title-group">
              <span class="col-title">{{ col.title }}</span>
              <span class="col-badge">{{ col.issues.length }}</span>
            </div>
            <button class="col-add-btn" (click)="openCreateModalWithStatus(col.status)" title="Add task to column">
              <app-svg-icon name="plus" [size]="12"></app-svg-icon>
            </button>
          </div>

          <div
            cdkDropList
            [cdkDropListData]="col.issues"
            (cdkDropListDropped)="onDrop($event, col.status)"
            class="task-drop-list"
          >
            <div
              *ngFor="let issue of col.issues"
              cdkDrag
              class="task-card"
              (click)="openIssueDetail(issue)"
            >
              <div class="card-meta-top">
                <span class="task-key">#{{ issue.id }}</span>
                <app-status-badge [type]="issue.priority"></app-status-badge>
              </div>

              <h4 class="task-card-title">{{ issue.title }}</h4>

              <div class="card-meta-bottom">
                <span class="type-tag">{{ issue.issue_type }}</span>
                <span class="assignee-tag">👤 Emp #{{ issue.assignee_id }}</span>
              </div>
            </div>

            <div *ngIf="col.issues.length === 0" class="empty-drop-zone">
              Drag tasks here or click + to add
            </div>
          </div>
        </div>
      </div>

      <!-- LIST VIEW -->
      <div *ngIf="viewMode === 'list'" class="table-wrapper panel">
        <table class="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Task Title</th>
              <th>Type</th>
              <th>Priority</th>
              <th>Status</th>
              <th>Assignee</th>
              <th>Due Date</th>
            </tr>
          </thead>
          <tbody>
            <tr
              *ngFor="let issue of allIssues()"
              class="clickable-row"
              (click)="openIssueDetail(issue)"
            >
              <td class="font-semibold">#{{ issue.id }}</td>
              <td class="font-semibold text-primary">{{ issue.title }}</td>
              <td class="text-muted">{{ issue.issue_type }}</td>
              <td><app-status-badge [type]="issue.priority"></app-status-badge></td>
              <td><app-status-badge [type]="issue.status"></app-status-badge></td>
              <td>Emp #{{ issue.assignee_id }}</td>
              <td class="text-muted">{{ (issue.due_date | date:'mediumDate') || '—' }}</td>
            </tr>

            <tr *ngIf="allIssues().length === 0">
              <td colspan="7" class="text-center py-4 text-muted">
                No tasks match the active filters.
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Log New Task Modal -->
      <div *ngIf="showCreateModal()" class="modal-backdrop" (click)="closeCreateModal()">
        <div class="modal-dialog" (click)="$event.stopPropagation()">
          <h3>Create Task / Issue</h3>

          <form [formGroup]="issueForm" (ngSubmit)="submitCreateIssue()">
            <div class="form-group">
              <label class="form-label">Task Title *</label>
              <input type="text" class="form-control" formControlName="title" placeholder="e.g. Optimize Database Indexes" />
            </div>

            <div class="form-group">
              <label class="form-label">Description</label>
              <textarea rows="3" class="form-control" formControlName="description" placeholder="Technical specifications..."></textarea>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label class="form-label">Project *</label>
                <select class="form-select" formControlName="project_id">
                  <option *ngFor="let proj of projects()" [value]="proj.id">{{ proj.name }}</option>
                </select>
              </div>

              <div class="form-group">
                <label class="form-label">Assignee *</label>
                <select class="form-select" formControlName="assignee_id">
                  <option *ngFor="let emp of employees()" [value]="emp.id">{{ emp.user.name }} ({{ emp.designation }})</option>
                </select>
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label class="form-label">Type</label>
                <select class="form-select" formControlName="issue_type">
                  <option [value]="types.TASK">TASK</option>
                  <option [value]="types.BUG">BUG</option>
                  <option [value]="types.STORY">STORY</option>
                </select>
              </div>

              <div class="form-group">
                <label class="form-label">Priority</label>
                <select class="form-select" formControlName="priority">
                  <option [value]="priorities.LOW">LOW</option>
                  <option [value]="priorities.MEDIUM">MEDIUM</option>
                  <option [value]="priorities.HIGH">HIGH</option>
                  <option [value]="priorities.CRITICAL">CRITICAL</option>
                </select>
              </div>
            </div>

            <div class="modal-actions">
              <button type="button" class="btn" (click)="closeCreateModal()">Cancel</button>
              <button type="submit" class="btn btn-primary" [disabled]="issueForm.invalid || isSubmitting">Submit Task</button>
            </div>
          </form>
        </div>
      </div>

      <!-- Task Detail Modal -->
      <app-issue-detail-modal
        *ngIf="selectedIssue()"
        [issue]="selectedIssue()!"
        (close)="selectedIssue.set(null)"
        (issueUpdated)="loadIssues()"
      ></app-issue-detail-modal>
    </div>
  `,
  styles: [`
    .board-page { display: flex; flex-direction: column; gap: 14px; }

    .page-header { display: flex; justify-content: space-between; align-items: flex-start; }
    .page-header h2 { font-size: 1.2rem; font-weight: 700; }
    .text-sm { font-size: 0.8rem; }
    .text-muted { color: var(--text-muted); }

    .tools-row { display: flex; align-items: center; gap: 12px; }

    .mode-toggle {
      display: flex;
      background: var(--bg-subtle);
      padding: 2px;
      border-radius: var(--radius-sm);
      border: 1px solid var(--border-color);
    }

    .toggle-btn {
      display: flex;
      align-items: center;
      gap: 6px;
      padding: 4px 10px;
      font-size: 0.775rem;
      font-weight: 500;
      background: none;
      border: none;
      color: var(--text-secondary);
      cursor: pointer;
      border-radius: var(--radius-sm);
    }

    .toggle-btn.active {
      background: var(--bg-surface);
      color: var(--primary-600);
      font-weight: 600;
      box-shadow: var(--shadow-sm);
    }

    .filter-panel {
      display: flex;
      align-items: flex-end;
      gap: 12px;
      padding: 10px 14px;
    }

    .filter-item { flex: 1; margin: 0; }
    .filter-btn-box { flex: none; }

    /* KANBAN COLUMNS */
    .kanban-columns-container {
      display: grid;
      grid-template-columns: repeat(6, minmax(220px, 1fr));
      gap: 12px;
      overflow-x: auto;
      align-items: flex-start;
      min-height: 550px;
      padding-bottom: 8px;
    }

    .kanban-col {
      display: flex;
      flex-direction: column;
      background: var(--bg-subtle);
      border: 1px solid var(--border-color);
      max-height: 75vh;
    }

    .col-header {
      padding: 8px 10px;
      border-bottom: 1px solid var(--border-color);
      display: flex;
      justify-content: space-between;
      align-items: center;
      background: var(--bg-surface);
    }

    .col-title-group { display: flex; align-items: center; gap: 6px; }

    .col-title {
      font-size: 0.75rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.03em;
      color: var(--text-secondary);
    }

    .col-badge {
      font-size: 0.7rem;
      font-weight: 700;
      background: var(--bg-subtle);
      border: 1px solid var(--border-color);
      padding: 1px 6px;
      border-radius: var(--radius-sm);
      color: var(--text-muted);
    }

    .col-add-btn {
      background: none;
      border: none;
      cursor: pointer;
      color: var(--text-muted);
      padding: 2px 4px;
      border-radius: var(--radius-sm);
    }

    .col-add-btn:hover { background: var(--bg-subtle); color: var(--text-primary); }

    .task-drop-list {
      padding: 8px;
      display: flex;
      flex-direction: column;
      gap: 8px;
      min-height: 200px;
      flex: 1;
      overflow-y: auto;
    }

    .task-card {
      background: var(--bg-surface);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-sm);
      padding: 10px;
      cursor: grab;
      display: flex;
      flex-direction: column;
      gap: 6px;
      box-shadow: var(--shadow-sm);
    }

    .task-card:active { cursor: grabbing; }
    .task-card:hover { border-color: var(--border-strong); }

    .card-meta-top { display: flex; justify-content: space-between; align-items: center; }
    .task-key { font-size: 0.7rem; font-weight: 700; color: var(--text-muted); font-family: var(--font-mono); }
    .task-card-title { font-size: 0.825rem; font-weight: 600; line-height: 1.35; color: var(--text-primary); }

    .card-meta-bottom { display: flex; justify-content: space-between; font-size: 0.7rem; color: var(--text-muted); }
    .type-tag { font-weight: 600; text-transform: uppercase; color: var(--primary-600); }

    .empty-drop-zone {
      padding: 16px 8px;
      text-align: center;
      font-size: 0.725rem;
      color: var(--text-muted);
      border: 1px dashed var(--border-strong);
      border-radius: var(--radius-sm);
    }

    .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
    .modal-actions { display: flex; justify-content: flex-end; gap: 8px; margin-top: 16px; }
    .clickable-row { cursor: pointer; }
    .text-primary { color: var(--primary-600); }
  `]
})
export class IssueBoardComponent implements OnInit {
  private issueService = inject(IssueService);
  private projectService = inject(ProjectService);
  private employeeService = inject(EmployeeService);
  private fb = inject(FormBuilder);
  private toast = inject(ToastService);
  authService = inject(AuthService);

  viewMode: 'kanban' | 'list' = 'kanban';
  isLoading = true;
  isSubmitting = false;

  allIssues = signal<IssueResponse[]>([]);
  projects = signal<ProjectResponse[]>([]);
  employees = signal<EmployeeResponse[]>([]);

  statusList = Object.values(IssueStatus);
  priorityList = Object.values(IssuePriority);

  columns = signal<{ title: string; status: IssueStatus; issues: IssueResponse[] }[]>([
    { title: 'Backlog', status: IssueStatus.BACKLOG, issues: [] },
    { title: 'To Do', status: IssueStatus.TODO, issues: [] },
    { title: 'In Progress', status: IssueStatus.IN_PROGRESS, issues: [] },
    { title: 'Review', status: IssueStatus.REVIEW, issues: [] },
    { title: 'Testing', status: IssueStatus.TESTING, issues: [] },
    { title: 'Done', status: IssueStatus.DONE, issues: [] }
  ]);

  selectedStatusFilter: IssueStatus | null = null;
  selectedPriorityFilter: IssuePriority | null = null;
  showingMyIssuesOnly = false;

  showCreateModal = signal<boolean>(false);
  selectedIssue = signal<IssueResponse | null>(null);

  types = IssueType;
  priorities = IssuePriority;
  statuses = IssueStatus;

  issueForm = this.fb.group({
    title: ['', [Validators.required, Validators.minLength(3)]],
    description: [''],
    issue_type: [IssueType.TASK, [Validators.required]],
    priority: [IssuePriority.MEDIUM, [Validators.required]],
    status: [IssueStatus.TODO, [Validators.required]],
    project_id: [0, [Validators.required]],
    assignee_id: [0, [Validators.required]]
  });

  ngOnInit() {
    this.loadIssues();
    this.loadProjectsAndEmployees();
  }

  loadIssues() {
    this.isLoading = true;

    const fetch$ = this.showingMyIssuesOnly
      ? this.issueService.getMyIssues()
      : this.issueService.getIssues(this.selectedStatusFilter || undefined, this.selectedPriorityFilter || undefined);

    fetch$.subscribe({
      next: data => {
        this.allIssues.set(data);
        this.distributeColumns(data);
        this.isLoading = false;
      },
      error: () => this.isLoading = false
    });
  }

  distributeColumns(data: IssueResponse[]) {
    this.columns.update(cols =>
      cols.map(col => ({
        ...col,
        issues: data.filter(i => i.status === col.status)
      }))
    );
  }

  loadProjectsAndEmployees() {
    this.projectService.getProjects().subscribe(p => {
      this.projects.set(p);
      if (p.length > 0) this.issueForm.patchValue({ project_id: p[0].id });
    });

    this.employeeService.getEmployees().subscribe(e => {
      this.employees.set(e);
      if (e.length > 0) this.issueForm.patchValue({ assignee_id: e[0].id });
    });
  }

  /**
   * ANGULAR CDK DRAG & DROP HANDLER
   * Handles re-ordering within column or transferring task across status columns,
   * and persists new status to backend via PUT /issues/{id}
   */
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
          this.toast.success(`Task #${updated.id} moved to ${targetStatus.replace(/_/g, ' ')}`);
        },
        error: () => {
          this.loadIssues();
        }
      });
    }
  }

  toggleMyIssues() {
    this.showingMyIssuesOnly = !this.showingMyIssuesOnly;
    this.loadIssues();
  }

  openCreateModal() {
    this.showCreateModal.set(true);
  }

  openCreateModalWithStatus(status: IssueStatus) {
    this.issueForm.patchValue({ status });
    this.showCreateModal.set(true);
  }

  closeCreateModal() {
    this.showCreateModal.set(false);
  }

  submitCreateIssue() {
    if (this.issueForm.invalid) return;

    this.isSubmitting = true;
    const formVal = this.issueForm.value;

    this.issueService.createIssue({
      title: formVal.title!,
      description: formVal.description || undefined,
      issue_type: formVal.issue_type as IssueType,
      priority: formVal.priority as IssuePriority,
      status: formVal.status as IssueStatus,
      project_id: Number(formVal.project_id),
      assignee_id: Number(formVal.assignee_id)
    }).subscribe({
      next: created => {
        this.toast.success(`Task #${created.id} logged!`);
        this.isSubmitting = false;
        this.closeCreateModal();
        this.loadIssues();
      },
      error: () => this.isSubmitting = false
    });
  }

  openIssueDetail(issue: IssueResponse) {
    this.selectedIssue.set(issue);
  }
}
