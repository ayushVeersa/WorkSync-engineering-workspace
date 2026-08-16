import { Injectable, signal, computed, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { Observable, tap, catchError, of } from 'rxjs';
import { UserLogin, UserRegister, UserResponse } from '../models/user.model';
import { Role } from '../models/role.model';
import { ToastService } from './toast.service';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private http = inject(HttpClient);
  private router = inject(Router);
  private toast = inject(ToastService);

  currentUser = signal<UserResponse | null>(null);

  isAuthenticated = computed(() => !!this.currentUser());
  userRole = computed(() => this.currentUser()?.role || null);
  isAdmin = computed(() => this.userRole() === Role.ADMIN);
  isManager = computed(() => this.userRole() === Role.MANAGER);
  isAdminOrManager = computed(() => this.isAdmin() || this.isManager());

  constructor() {
    this.fetchCurrentUser().subscribe();
  }

  login(credentials: UserLogin): Observable<UserResponse> {
    return this.http.post<UserResponse>('/auth/login', credentials).pipe(
      tap(res => {
        this.currentUser.set(res);
        this.toast.success(`Welcome back, ${res.name}! 👋`, 'Logged In');
      })
    );
  }

  register(userData: UserRegister): Observable<UserResponse> {
    return this.http.post<UserResponse>('/auth/register', userData).pipe(
      tap(user => {
        this.toast.success(`Account created successfully for ${user.email}`, 'Registration Complete');
      })
    );
  }

  fetchCurrentUser(): Observable<UserResponse | null> {
    return this.http.get<UserResponse>('/auth/me').pipe(
      tap(user => this.currentUser.set(user)),
      catchError(err => {
        this.currentUser.set(null);
        return of(null);
      })
    );
  }

  uploadProfileImage(file: File): Observable<UserResponse> {
    const formData = new FormData();
    formData.append('file', file);
    return this.http.post<UserResponse>('/auth/profile-image', formData).pipe(
      tap(updatedUser => {
        this.currentUser.set(updatedUser);
        this.toast.success('Profile picture updated successfully!', 'Avatar Updated');
      })
    );
  }

  ensureCurrentUser(): Observable<UserResponse | null> {
    return this.currentUser() ? of(this.currentUser()) : this.fetchCurrentUser();
  }

  logout(showToast = true) {
    this.http.post('/auth/logout', {}).pipe(
      catchError(() => of(null))
    ).subscribe(() => {
      this.currentUser.set(null);
      if (showToast) {
        this.toast.info('You have been logged out safely.', 'Goodbye');
      }
      this.router.navigate(['/auth/login']);
    });
  }
}
