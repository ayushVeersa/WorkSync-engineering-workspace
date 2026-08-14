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

  projectMembers = signal<EmployeeResponse[]>([]);

  viewMode: 'kanban' | 'list' = 'kanban';
  isLoading = true;
  isSubmitting = false;

  allIssues = signal<IssueResponse[]>([]);
  projects = signal<ProjectResponse[]>([]);
  employees = signal<EmployeeResponse[]>([]);

  attachments: File[] = [];

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

  selectedStatusFilter: string = '';
  selectedPriorityFilter: string = '';
  searchQuery: string = '';
  showingMyIssuesOnly = false;

  showCreateModal = signal(false);
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

    this.issueForm.get('project_id')?.valueChanges.subscribe(projectId => {
      if (projectId) {
        this.loadProjectMembers(Number(projectId));
      }
    });
  }

  loadIssues() {
    this.isLoading = true;

    const statusParam = (this.selectedStatusFilter && this.selectedStatusFilter !== 'null' && this.selectedStatusFilter !== 'ALL')
      ? (this.selectedStatusFilter as IssueStatus)
      : undefined;
    const priorityParam = (this.selectedPriorityFilter && this.selectedPriorityFilter !== 'null' && this.selectedPriorityFilter !== 'ALL')
      ? (this.selectedPriorityFilter as IssuePriority)
      : undefined;

    const fetch$ = this.showingMyIssuesOnly
      ? this.issueService.getMyIssues()
      : this.issueService.getIssues(
          statusParam,
          priorityParam,
          undefined,
          undefined,
          undefined,
          this.searchQuery || undefined
        );

    fetch$.subscribe({
      next: data => {
        this.allIssues.set(data);
        this.distributeColumns(data);
        this.isLoading = false;
      },
      error: () => this.isLoading = false
    });
  }

  clearFilters() {
    this.selectedStatusFilter = '';
    this.selectedPriorityFilter = '';
    this.searchQuery = '';
    this.showingMyIssuesOnly = false;
    this.loadIssues();
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

      if (p.length > 0) {
        this.issueForm.patchValue({ project_id: p[0].id });
        this.loadProjectMembers(p[0].id);
      }
    });
  }

  loadProjectMembers(projectId: number) {
    this.projectService.getProjectMembers(projectId).subscribe(members => {
      this.projectMembers.set(members);

      this.issueForm.patchValue({
        assignee_id: members.length > 0 ? members[0].id : 0
      });
    });
  }

  onFileSelected(event: Event) {
    const input = event.target as HTMLInputElement;

    if (input.files) {
      this.attachments = Array.from(input.files);
    }
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
    this.attachments = [];
  }

  submitCreateIssue() {
    if (this.issueForm.invalid) return;

    this.isSubmitting = true;

    const formVal = this.issueForm.value;

    const formData = new FormData();

    formData.append('title', formVal.title!);
    formData.append('description', formVal.description || '');
    formData.append('issue_type', formVal.issue_type as string);
    formData.append('priority', formVal.priority as string);
    formData.append('status', formVal.status as string);
    formData.append('project_id', String(formVal.project_id));
    formData.append('assignee_id', String(formVal.assignee_id));

    this.attachments.forEach(file => {
      formData.append('files', file);
    });

    this.issueService.createIssue(formData).subscribe({
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