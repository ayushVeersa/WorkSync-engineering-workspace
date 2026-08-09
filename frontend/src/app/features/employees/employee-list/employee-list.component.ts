import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { EmployeeService } from '../../../core/services/employee.service';
import { DepartmentService } from '../../../core/services/department.service';
import { AuthService } from '../../../core/services/auth.service';
import { ToastService } from '../../../core/services/toast.service';
import { EmployeeResponse } from '../../../core/models/employee.model';
import { DepartmentResponse } from '../../../core/models/department.model';
import { Role } from '../../../core/models/role.model';
import { StatusBadgeComponent } from '../../../shared/components/status-badge/status-badge.component';
import { SvgIconComponent } from '../../../shared/components/svg-icon/svg-icon.component';

@Component({
  selector: 'app-employee-list',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    StatusBadgeComponent,
    SvgIconComponent
  ],
  template: `
    <div class="employees-page">
      <div class="page-header">
        <div>
          <h2>Team Members & Directory</h2>
          <p class="text-muted text-sm">Manage organization employees, designations, and system roles</p>
        </div>

        <button
          *ngIf="authService.isAdmin()"
          class="btn btn-primary btn-sm"
          (click)="openCreateModal()"
        >
          <app-svg-icon name="plus" [size]="14"></app-svg-icon>
          <span>Add Employee</span>
        </button>
      </div>

      <div class="table-wrapper panel">
        <table class="data-table">
          <thead>
            <tr>
              <th>Employee Name</th>
              <th>Work Email</th>
              <th>System Role</th>
              <th>Department</th>
              <th>Designation</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr *ngFor="let emp of employees()">
              <td class="font-semibold">{{ emp.user.name }}</td>
              <td class="text-muted">{{ emp.user.email }}</td>
              <td><app-status-badge [type]="emp.user.role"></app-status-badge></td>
              <td>🏢 {{ emp.department?.name || 'Unassigned' }}</td>
              <td>{{ emp.designation }}</td>
              <td>
                <div class="actions-group">
                  <button
                    *ngIf="authService.isAdminOrManager()"
                    class="btn btn-secondary btn-sm"
                    (click)="openEditModal(emp)"
                  >
                    Edit
                  </button>
                  <button
                    *ngIf="authService.isAdmin()"
                    class="btn btn-danger btn-sm"
                    (click)="deleteEmployee(emp.id)"
                  >
                    Delete
                  </button>
                </div>
              </td>
            </tr>

            <tr *ngIf="employees().length === 0">
              <td colspan="6" class="text-center py-4 text-muted">
                No employees registered in directory.
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Create Employee Modal -->
      <div *ngIf="showCreateModal()" class="modal-backdrop" (click)="closeCreateModal()">
        <div class="modal-dialog" (click)="$event.stopPropagation()">
          <h3>Add New Team Member</h3>

          <form [formGroup]="createForm" (ngSubmit)="submitCreateEmployee()">
            <div class="form-group">
              <label class="form-label">Full Name *</label>
              <input type="text" class="form-control" formControlName="name" placeholder="John Doe" />
            </div>

            <div class="form-group">
              <label class="form-label">Work Email *</label>
              <input type="email" class="form-control" formControlName="email" placeholder="john@worksync.io" />
            </div>

            <div class="form-row">
              <div class="form-group">
                <label class="form-label">Password *</label>
                <input type="password" class="form-control" formControlName="password" placeholder="••••••••" />
              </div>

              <div class="form-group">
                <label class="form-label">Age</label>
                <input type="number" class="form-control" formControlName="age" />
              </div>
            </div>

            <div class="form-group">
              <label class="form-label">Designation *</label>
              <input type="text" class="form-control" formControlName="designation" placeholder="Senior Backend Engineer" />
            </div>

            <div class="form-row">
              <div class="form-group">
                <label class="form-label">Department *</label>
                <select class="form-select" formControlName="department_id">
                  <option *ngFor="let dept of departments()" [value]="dept.id">{{ dept.name }}</option>
                </select>
              </div>

              <div class="form-group">
                <label class="form-label">System Role *</label>
                <select class="form-select" formControlName="role">
                  <option [value]="roles.EMPLOYEE">EMPLOYEE</option>
                  <option [value]="roles.MANAGER">MANAGER</option>
                  <option [value]="roles.ADMIN">ADMIN</option>
                </select>
              </div>
            </div>

            <div class="modal-actions">
              <button type="button" class="btn" (click)="closeCreateModal()">Cancel</button>
              <button type="submit" class="btn btn-primary" [disabled]="createForm.invalid || isSubmitting">Create Employee</button>
            </div>
          </form>
        </div>
      </div>

      <!-- Edit Employee Modal -->
      <div *ngIf="showEditModal() && editingEmployee()" class="modal-backdrop" (click)="closeEditModal()">
        <div class="modal-dialog" (click)="$event.stopPropagation()">
          <h3>Edit {{ editingEmployee()?.user?.name }}</h3>

          <form [formGroup]="editForm" (ngSubmit)="submitEditEmployee()">
            <div class="form-group">
              <label class="form-label">Designation</label>
              <input type="text" class="form-control" formControlName="designation" />
            </div>

            <div class="form-group">
              <label class="form-label">Age</label>
              <input type="number" class="form-control" formControlName="age" />
            </div>

            <div class="modal-actions">
              <button type="button" class="btn" (click)="closeEditModal()">Cancel</button>
              <button type="submit" class="btn btn-primary" [disabled]="editForm.invalid || isSubmitting">Save Changes</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .employees-page { display: flex; flex-direction: column; gap: 14px; }
    .page-header { display: flex; justify-content: space-between; align-items: flex-start; }
    .page-header h2 { font-size: 1.2rem; font-weight: 700; }
    .text-sm { font-size: 0.8rem; }
    .text-muted { color: var(--text-muted); }

    .actions-group { display: flex; gap: 6px; }
    .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
    .modal-actions { display: flex; justify-content: flex-end; gap: 8px; margin-top: 16px; }
  `]
})
export class EmployeeListComponent implements OnInit {
  private employeeService = inject(EmployeeService);
  private departmentService = inject(DepartmentService);
  private fb = inject(FormBuilder);
  private toast = inject(ToastService);
  authService = inject(AuthService);

  employees = signal<EmployeeResponse[]>([]);
  departments = signal<DepartmentResponse[]>([]);
  roles = Role;

  showCreateModal = signal<boolean>(false);
  showEditModal = signal<boolean>(false);
  isSubmitting = false;
  editingEmployee = signal<EmployeeResponse | null>(null);

  createForm = this.fb.group({
    name: ['', [Validators.required, Validators.minLength(2)]],
    email: ['', [Validators.required, Validators.email]],
    password: ['', [Validators.required, Validators.minLength(6)]],
    designation: ['', [Validators.required]],
    department_id: [0, [Validators.required]],
    role: [Role.EMPLOYEE, [Validators.required]],
    age: [28, [Validators.required]]
  });

  editForm = this.fb.group({
    designation: ['', [Validators.required]],
    age: [28, [Validators.required]]
  });

  ngOnInit() {
    this.loadEmployees();
    this.loadDepartments();
  }

  loadEmployees() {
    this.employeeService.getEmployees().subscribe(e => this.employees.set(e));
  }

  loadDepartments() {
    this.departmentService.getDepartments().subscribe(d => {
      this.departments.set(d);
      if (d.length > 0) this.createForm.patchValue({ department_id: d[0].id });
    });
  }

  openCreateModal() {
    this.showCreateModal.set(true);
  }

  closeCreateModal() {
    this.showCreateModal.set(false);
  }

  submitCreateEmployee() {
    if (this.createForm.invalid) return;

    this.isSubmitting = true;
    const formVal = this.createForm.value;

    this.employeeService.createEmployee({
      name: formVal.name!,
      email: formVal.email!,
      password: formVal.password!,
      designation: formVal.designation!,
      department_id: Number(formVal.department_id),
      role: formVal.role as Role,
      age: Number(formVal.age)
    }).subscribe({
      next: created => {
        this.toast.success(`Employee ${created.user.name} created!`);
        this.isSubmitting = false;
        this.closeCreateModal();
        this.loadEmployees();
      },
      error: () => this.isSubmitting = false
    });
  }

  openEditModal(emp: EmployeeResponse) {
    this.editingEmployee.set(emp);
    this.editForm.patchValue({
      designation: emp.designation,
      age: emp.age
    });
    this.showEditModal.set(true);
  }

  closeEditModal() {
    this.showEditModal.set(false);
    this.editingEmployee.set(null);
  }

  submitEditEmployee() {
    const emp = this.editingEmployee();
    if (!emp || this.editForm.invalid) return;

    this.isSubmitting = true;
    const formVal = this.editForm.value;

    this.employeeService.updateEmployee(emp.id, {
      designation: formVal.designation!,
      age: Number(formVal.age)
    }).subscribe({
      next: () => {
        this.toast.success('Employee updated');
        this.isSubmitting = false;
        this.closeEditModal();
        this.loadEmployees();
      },
      error: () => this.isSubmitting = false
    });
  }

  deleteEmployee(id: number) {
    if (!confirm('Are you sure you want to remove this employee?')) return;

    this.employeeService.deleteEmployee(id).subscribe({
      next: () => {
        this.toast.info('Employee removed');
        this.loadEmployees();
      }
    });
  }
}
