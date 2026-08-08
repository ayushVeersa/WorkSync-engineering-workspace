import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, ReactiveFormsModule, FormsModule, Validators } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { ProjectService } from '../../../core/services/project.service';
import { EmployeeService } from '../../../core/services/employee.service';
import { AuthService } from '../../../core/services/auth.service';
import { ToastService } from '../../../core/services/toast.service';
import { ProjectResponse, ProjectStatus } from '../../../core/models/project.model';
import { EmployeeResponse } from '../../../core/models/employee.model';
import { StatusBadgeComponent } from '../../../shared/components/status-badge/status-badge.component';
import { SvgIconComponent } from '../../../shared/components/svg-icon/svg-icon.component';

@Component({
  selector: 'app-project-list',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    FormsModule,
    RouterModule,
    StatusBadgeComponent,
    SvgIconComponent
  ],
  template: `
    <div class="projects-page">
      <div class="page-header">
        <div>
          <h2>Projects Directory</h2>
          <p class="text-muted text-sm">Active engineering projects, timelines, and team allocations</p>
        </div>

        <button
          *ngIf="authService.isAdminOrManager()"
          class="btn btn-primary btn-sm"
          (click)="openCreateModal()"
        >
          <app-svg-icon name="plus" [size]="14"></app-svg-icon>
          <span>New Project</span>
        </button>
      </div>

      <!-- Projects Table List -->
      <div class="table-wrapper panel">
        <table class="data-table">
          <thead>
            <tr>
              <th>Project Name</th>
              <th>Status</th>
              <th>Created Date</th>
              <th>Owner ID</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr *ngFor="let project of projects">
              <td>
                <div class="proj-name-cell">
                  <a [routerLink]="['/projects', project.id]" class="proj-title-link">
                    {{ project.name }}
                  </a>
                  <span class="proj-sub">{{ project.description || 'No description provided' }}</span>
                </div>
              </td>
              <td><app-status-badge [type]="project.status"></app-status-badge></td>
              <td class="text-muted">{{ project.created_at | date:'mediumDate' }}</td>
              <td class="text-muted">Emp #{{ project.owner_id }}</td>
              <td>
                <div class="actions-group">
                  <a [routerLink]="['/projects', project.id]" class="btn btn-secondary btn-sm">
                    Open Details
                  </a>
                  <button
                    *ngIf="authService.isAdminOrManager()"
                    class="btn btn-secondary btn-sm"
                    (click)="openMembersModal(project)"
                  >
                    Manage Team
                  </button>
                </div>
              </td>
            </tr>

            <tr *ngIf="projects.length === 0">
              <td colspan="5" class="text-center py-4 text-muted">
                No active projects found.
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Create Project Modal -->
      <div *ngIf="showCreateModal" class="modal-backdrop" (click)="closeCreateModal()">
        <div class="modal-dialog" (click)="$event.stopPropagation()">
          <h3>Create New Project</h3>

          <form [formGroup]="projectForm" (ngSubmit)="submitCreateProject()">
            <div class="form-group">
              <label class="form-label">Project Name *</label>
              <input type="text" class="form-control" formControlName="name" placeholder="e.g. Next-Gen API Gateway" />
            </div>

            <div class="form-group">
              <label class="form-label">Description</label>
              <textarea rows="3" class="form-control" formControlName="description" placeholder="Project objectives and Scope..."></textarea>
            </div>

            <div class="form-group">
              <label class="form-label">Initial Status</label>
              <select class="form-select" formControlName="status">
                <option [value]="statuses.PLANNING">PLANNING</option>
                <option [value]="statuses.ACTIVE">ACTIVE</option>
                <option [value]="statuses.ON_HOLD">ON_HOLD</option>
                <option [value]="statuses.COMPLETED">COMPLETED</option>
              </select>
            </div>

            <div class="modal-actions">
              <button type="button" class="btn" (click)="closeCreateModal()">Cancel</button>
              <button type="submit" class="btn btn-primary" [disabled]="projectForm.invalid || isSubmitting">Create Project</button>
            </div>
          </form>
        </div>
      </div>

      <!-- Manage Members Modal -->
      <div *ngIf="showMembersModal && selectedProject" class="modal-backdrop" (click)="closeMembersModal()">
        <div class="modal-dialog" (click)="$event.stopPropagation()">
          <h3>Team Members — {{ selectedProject.name }}</h3>

          <!-- Current Members List -->
          <div class="members-stack">
            <label class="form-label">Assigned Members ({{ currentMembers.length }})</label>
            <div class="members-list">
              <div *ngFor="let member of currentMembers" class="member-row">
                <div class="member-info">
                  <span class="member-name">{{ member.user.name }}</span>
                  <span class="member-sub">{{ member.designation }} • {{ member.user.email }}</span>
                </div>
                <button class="btn btn-danger btn-sm" (click)="removeMemberFromProject(member.id)">
                  Remove
                </button>
              </div>

              <div *ngIf="currentMembers.length === 0" class="text-muted text-xs font-italic">
                No team members assigned to this project yet.
              </div>
            </div>
          </div>

          <!-- Add Member Section -->
          <div class="add-member-box mt-3">
            <label class="form-label">Assign Employee</label>
            <div class="flex-row">
              <select class="form-select" [(ngModel)]="selectedEmployeeId">
                <option [value]="null">Select Employee...</option>
                <option *ngFor="let emp of allEmployees" [value]="emp.id">
                  {{ emp.user.name }} ({{ emp.designation }})
                </option>
              </select>
              <button class="btn btn-primary btn-sm" [disabled]="!selectedEmployeeId" (click)="addMemberToProject()">
                Assign
              </button>
            </div>
          </div>

          <div class="modal-actions">
            <button class="btn" (click)="closeMembersModal()">Close</button>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .projects-page { display: flex; flex-direction: column; gap: 14px; }
    .page-header { display: flex; justify-content: space-between; align-items: flex-start; }
    .page-header h2 { font-size: 1.2rem; font-weight: 700; }
    .text-sm { font-size: 0.8rem; }
    .text-muted { color: var(--text-muted); }

    .proj-name-cell { display: flex; flex-direction: column; }
    .proj-title-link { font-weight: 600; color: var(--primary-600); text-decoration: none; font-size: 0.85rem; }
    .proj-title-link:hover { text-decoration: underline; }
    .proj-sub { font-size: 0.75rem; color: var(--text-muted); }
    .actions-group { display: flex; gap: 6px; }

    .modal-actions { display: flex; justify-content: flex-end; gap: 8px; margin-top: 16px; }
    .members-stack { margin-bottom: 14px; }
    .members-list { display: flex; flex-direction: column; gap: 6px; max-height: 180px; overflow-y: auto; }
    .member-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 6px 10px;
      background: var(--bg-subtle);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-sm);
    }
    .member-info { display: flex; flex-direction: column; }
    .member-name { font-size: 0.8rem; font-weight: 600; }
    .member-sub { font-size: 0.7rem; color: var(--text-muted); }

    .flex-row { display: flex; gap: 8px; }
    .mt-3 { margin-top: 12px; }
    .text-xs { font-size: 0.75rem; }
    .font-italic { font-style: italic; }
  `]
})
export class ProjectListComponent implements OnInit {
  private projectService = inject(ProjectService);
  private employeeService = inject(EmployeeService);
  private toast = inject(ToastService);
  private fb = inject(FormBuilder);
  authService = inject(AuthService);

  projects: ProjectResponse[] = [];
  statuses = ProjectStatus;
  showCreateModal = false;
  showMembersModal = false;
  isSubmitting = false;

  selectedProject: ProjectResponse | null = null;
  currentMembers: EmployeeResponse[] = [];
  allEmployees: EmployeeResponse[] = [];
  selectedEmployeeId: number | null = null;

  projectForm = this.fb.group({
    name: ['', [Validators.required, Validators.minLength(3)]],
    description: [''],
    status: [ProjectStatus.PLANNING, [Validators.required]]
  });

  ngOnInit() {
    this.loadProjects();
  }

  loadProjects() {
    this.projectService.getProjects().subscribe(p => this.projects = p);
  }

  openCreateModal() {
    this.projectForm.reset({ status: ProjectStatus.PLANNING });
    this.showCreateModal = true;
  }

  closeCreateModal() {
    this.showCreateModal = false;
  }

  submitCreateProject() {
    if (this.projectForm.invalid) return;

    this.isSubmitting = true;
    const formVal = this.projectForm.value;

    this.projectService.createProject({
      name: formVal.name!,
      description: formVal.description || undefined,
      status: formVal.status as ProjectStatus
    }).subscribe({
      next: created => {
        this.toast.success(`Project "${created.name}" created!`);
        this.isSubmitting = false;
        this.closeCreateModal();
        this.loadProjects();
      },
      error: () => this.isSubmitting = false
    });
  }

  openMembersModal(project: ProjectResponse) {
    this.selectedProject = project;
    this.showMembersModal = true;
    this.loadProjectMembers(project.id);
    this.loadAllEmployees();
  }

  closeMembersModal() {
    this.showMembersModal = false;
    this.selectedProject = null;
    this.selectedEmployeeId = null;
  }

  loadProjectMembers(projectId: number) {
    this.projectService.getProjectMembers(projectId).subscribe(m => this.currentMembers = m);
  }

  loadAllEmployees() {
    this.employeeService.getEmployees().subscribe(e => this.allEmployees = e);
  }

  addMemberToProject() {
    if (!this.selectedProject || !this.selectedEmployeeId) return;

    this.projectService.assignMember(this.selectedProject.id, Number(this.selectedEmployeeId)).subscribe({
      next: () => {
        this.toast.success('Team member assigned to project!');
        this.loadProjectMembers(this.selectedProject!.id);
        this.selectedEmployeeId = null;
      }
    });
  }

  removeMemberFromProject(employeeId: number) {
    if (!this.selectedProject) return;

    this.projectService.removeMember(this.selectedProject.id, employeeId).subscribe({
      next: () => {
        this.toast.info('Member removed from project.');
        this.loadProjectMembers(this.selectedProject!.id);
      }
    });
  }
}
