import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { DepartmentService } from '../../../core/services/department.service';
import { AuthService } from '../../../core/services/auth.service';
import { ToastService } from '../../../core/services/toast.service';
import { DepartmentResponse } from '../../../core/models/department.model';
import { SvgIconComponent } from '../../../shared/components/svg-icon/svg-icon.component';

@Component({
  selector: 'app-department-list',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, SvgIconComponent],
  template: `
    <div class="departments-page">
      <div class="page-header">
        <div>
          <h2>Departments Management</h2>
          <p class="text-muted text-sm">Configure organizational departments and engineering divisions</p>
        </div>

        <button
          *ngIf="authService.isAdmin()"
          class="btn btn-primary btn-sm"
          (click)="openCreateModal()"
        >
          <app-svg-icon name="plus" [size]="14"></app-svg-icon>
          <span>New Department</span>
        </button>
      </div>

      <div class="table-wrapper panel">
        <table class="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Department Name</th>
              <th>Description</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr *ngFor="let dept of departments()">
              <td class="font-semibold text-muted">#{{ dept.id }}</td>
              <td class="font-semibold">{{ dept.name }}</td>
              <td class="text-secondary">{{ dept.description || 'No description provided.' }}</td>
              <td>
                <div *ngIf="authService.isAdmin()" class="actions-group">
                  <button class="btn btn-secondary btn-sm" (click)="openEditModal(dept)">Edit</button>
                  <button class="btn btn-danger btn-sm" (click)="deleteDepartment(dept.id)">Delete</button>
                </div>
              </td>
            </tr>

            <tr *ngIf="departments().length === 0">
              <td colspan="4" class="text-center py-4 text-muted">
                No departments configured.
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Create Department Modal -->
      <div *ngIf="showCreateModal()" class="modal-backdrop" (click)="closeCreateModal()">
        <div class="modal-dialog" (click)="$event.stopPropagation()">
          <h3>Create New Department</h3>

          <form [formGroup]="deptForm" (ngSubmit)="submitCreateDepartment()">
            <div class="form-group">
              <label class="form-label">Department Name *</label>
              <input type="text" class="form-control" formControlName="name" placeholder="e.g. Core Platform" />
            </div>

            <div class="form-group">
              <label class="form-label">Description *</label>
              <textarea rows="3" class="form-control" formControlName="description" placeholder="Responsibilities and scope..."></textarea>
            </div>

            <div class="modal-actions">
              <button type="button" class="btn" (click)="closeCreateModal()">Cancel</button>
              <button type="submit" class="btn btn-primary" [disabled]="deptForm.invalid || isSubmitting">Create Department</button>
            </div>
          </form>
        </div>
      </div>

      <!-- Edit Department Modal -->
      <div *ngIf="showEditModal() && editingDept()" class="modal-backdrop" (click)="closeEditModal()">
        <div class="modal-dialog" (click)="$event.stopPropagation()">
          <h3>Edit {{ editingDept()?.name }}</h3>

          <form [formGroup]="editDeptForm" (ngSubmit)="submitEditDepartment()">
            <div class="form-group">
              <label class="form-label">Department Name</label>
              <input type="text" class="form-control" formControlName="name" />
            </div>

            <div class="form-group">
              <label class="form-label">Description</label>
              <textarea rows="3" class="form-control" formControlName="description"></textarea>
            </div>

            <div class="modal-actions">
              <button type="button" class="btn" (click)="closeEditModal()">Cancel</button>
              <button type="submit" class="btn btn-primary" [disabled]="editDeptForm.invalid || isSubmitting">Save Changes</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .departments-page { display: flex; flex-direction: column; gap: 14px; }
    .page-header { display: flex; justify-content: space-between; align-items: flex-start; }
    .page-header h2 { font-size: 1.2rem; font-weight: 700; }
    .text-sm { font-size: 0.8rem; }
    .text-muted { color: var(--text-muted); }
    .actions-group { display: flex; gap: 6px; }
    .modal-actions { display: flex; justify-content: flex-end; gap: 8px; margin-top: 16px; }
  `]
})
export class DepartmentListComponent implements OnInit {
  private departmentService = inject(DepartmentService);
  private fb = inject(FormBuilder);
  private toast = inject(ToastService);
  authService = inject(AuthService);

  departments = signal<DepartmentResponse[]>([]);
  showCreateModal = signal<boolean>(false);
  showEditModal = signal<boolean>(false);
  isSubmitting = false;
  editingDept = signal<DepartmentResponse | null>(null);

  deptForm = this.fb.group({
    name: ['', [Validators.required, Validators.minLength(2)]],
    description: ['', [Validators.required]]
  });

  editDeptForm = this.fb.group({
    name: ['', [Validators.required]],
    description: ['', [Validators.required]]
  });

  ngOnInit() {
    this.loadDepartments();
  }

  loadDepartments() {
    this.departmentService.getDepartments().subscribe(d => this.departments.set(d));
  }

  openCreateModal() {
    this.showCreateModal.set(true);
  }

  closeCreateModal() {
    this.showCreateModal.set(false);
  }

  submitCreateDepartment() {
    if (this.deptForm.invalid) return;

    this.isSubmitting = true;
    const formVal = this.deptForm.value;

    this.departmentService.createDepartment({
      name: formVal.name!,
      description: formVal.description!
    }).subscribe({
      next: created => {
        this.toast.success(`Department "${created.name}" created!`);
        this.isSubmitting = false;
        this.closeCreateModal();
        this.loadDepartments();
      },
      error: () => this.isSubmitting = false
    });
  }

  openEditModal(dept: DepartmentResponse) {
    this.editingDept.set(dept);
    this.editDeptForm.patchValue({
      name: dept.name,
      description: dept.description
    });
    this.showEditModal.set(true);
  }

  closeEditModal() {
    this.showEditModal.set(false);
    this.editingDept.set(null);
  }

  submitEditDepartment() {
    const dept = this.editingDept();
    if (!dept || this.editDeptForm.invalid) return;

    this.isSubmitting = true;
    const formVal = this.editDeptForm.value;

    this.departmentService.updateDepartment(dept.id, {
      name: formVal.name!,
      description: formVal.description!
    }).subscribe({
      next: () => {
        this.toast.success('Department updated');
        this.isSubmitting = false;
        this.closeEditModal();
        this.loadDepartments();
      },
      error: () => this.isSubmitting = false
    });
  }

  deleteDepartment(id: number) {
    if (!confirm('Are you sure you want to delete this department?')) return;

    this.departmentService.deleteDepartment(id).subscribe({
      next: () => {
        this.toast.info('Department deleted');
        this.loadDepartments();
      }
    });
  }
}
