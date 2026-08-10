import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../../../core/services/auth.service';
import { Role } from '../../../core/models/role.model';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterModule],
  templateUrl: './register.component.html',
  styleUrl: './register.component.scss'
})
export class RegisterComponent {
  private fb = inject(FormBuilder);
  private authService = inject(AuthService);
  private router = inject(Router);

  roles = Role;
  isLoading = false;

  registerForm = this.fb.group({
    name: ['', [Validators.required, Validators.minLength(2)]],
    email: ['', [Validators.required, Validators.email]],
    password: ['', [Validators.required, Validators.minLength(6)]],
    age: [28, [Validators.required, Validators.min(18)]],
    role: [Role.ADMIN, [Validators.required]]
  });

  isFieldInvalid(field: string): boolean {
    const control = this.registerForm.get(field);
    return !!(control && control.invalid && (control.dirty || control.touched));
  }

  onSubmit() {
    if (this.registerForm.invalid) return;

    this.isLoading = true;
    const formVal = this.registerForm.value;

    this.authService.register({
      name: formVal.name!,
      email: formVal.email!,
      password: formVal.password!,
      age: Number(formVal.age),
      role: formVal.role as Role
    }).subscribe({
      next: () => {
        this.isLoading = false;
        this.router.navigate(['/auth/login']);
      },
      error: () => {
        this.isLoading = false;
      }
    });
  }
}
