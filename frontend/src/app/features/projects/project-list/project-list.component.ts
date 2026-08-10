import { Component, OnInit, inject, signal } from '@angular/core';
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
  templateUrl: './project-list.component.html',
  styleUrl: './project-list.component.scss'
})
export class ProjectListComponent implements OnInit {
  private projectService = inject(ProjectService);
  private employeeService = inject(EmployeeService);
  private toast = inject(ToastService);
  private fb = inject(FormBuilder);
  authService = inject(AuthService);

  projects = signal<ProjectResponse[]>([]);
  statuses = ProjectStatus;
  showCreateModal = signal<boolean>(false);
  showMembersModal = signal<boolean>(false);
  isSubmitting = false;

  selectedProject = signal<ProjectResponse | null>(null);
  currentMembers = signal<EmployeeResponse[]>([]);
  allEmployees = signal<EmployeeResponse[]>([]);
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
    this.projectService.getProjects().subscribe(p => this.projects.set(p));
  }

  openCreateModal() {
    this.projectForm.reset({ status: ProjectStatus.PLANNING });
    this.showCreateModal.set(true);
  }

  closeCreateModal() {
    this.showCreateModal.set(false);
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
    this.selectedProject.set(project);
    this.showMembersModal.set(true);
    this.loadProjectMembers(project.id);
    this.loadAllEmployees();
  }

  closeMembersModal() {
    this.showMembersModal.set(false);
    this.selectedProject.set(null);
    this.selectedEmployeeId = null;
  }

  loadProjectMembers(projectId: number) {
    this.projectService.getProjectMembers(projectId).subscribe(m => this.currentMembers.set(m));
  }

  loadAllEmployees() {
    this.employeeService.getEmployees().subscribe(e => this.allEmployees.set(e));
  }

  addMemberToProject() {
    const proj = this.selectedProject();
    if (!proj || !this.selectedEmployeeId) return;

    this.projectService.assignMember(proj.id, Number(this.selectedEmployeeId)).subscribe({
      next: () => {
        this.toast.success('Team member assigned to project!');
        this.loadProjectMembers(proj.id);
        this.selectedEmployeeId = null;
      }
    });
  }

  removeMemberFromProject(employeeId: number) {
    const proj = this.selectedProject();
    if (!proj) return;

    this.projectService.removeMember(proj.id, employeeId).subscribe({
      next: () => {
        this.toast.info('Member removed from project.');
        this.loadProjectMembers(proj.id);
      }
    });
  }
}
