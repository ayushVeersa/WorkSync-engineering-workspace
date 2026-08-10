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
  templateUrl: './issue-board.component.html',
  styleUrl: './issue-board.component.scss'
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
