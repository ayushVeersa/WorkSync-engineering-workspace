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
  templateUrl: './department-list.component.html',
  styleUrl: './department-list.component.scss'
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
