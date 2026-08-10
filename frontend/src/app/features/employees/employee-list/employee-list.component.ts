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
  templateUrl: './employee-list.component.html',
  styleUrl: './employee-list.component.scss'
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
