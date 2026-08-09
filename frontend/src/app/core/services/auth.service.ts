import { Injectable, signal, computed, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { Observable, tap, catchError, of } from 'rxjs';
import { UserLogin, UserRegister, UserResponse, TokenResponse } from '../models/user.model';
import { Role } from '../models/role.model';
import { ToastService } from './toast.service';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private http = inject(HttpClient);
  private router = inject(Router);
  private toast = inject(ToastService);

  private readonly TOKEN_KEY = 'worksync_token';

  currentUser = signal<UserResponse | null>(null);
  token = signal<string | null>(localStorage.getItem(this.TOKEN_KEY));

  isAuthenticated = computed(() => !!this.currentUser() && !!this.token());
  userRole = computed(() => this.currentUser()?.role || null);
  isAdmin = computed(() => this.userRole() === Role.ADMIN);
  isManager = computed(() => this.userRole() === Role.MANAGER);
  isAdminOrManager = computed(() => this.isAdmin() || this.isManager());

  constructor() {
    if (this.token()) {
      this.fetchCurrentUser().subscribe();
    }
  }

  login(credentials: UserLogin): Observable<TokenResponse> {
    return this.http.post<TokenResponse>('/auth/login', credentials).pipe(
      tap(res => {
        this.setToken(res.access_token);
        this.currentUser.set(res.user);
        this.toast.success(`Welcome back, ${res.user.name}! 👋`, 'Logged In');
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
    if (!this.getToken()) return of(null);
    return this.http.get<UserResponse>('/auth/me').pipe(
      tap(user => this.currentUser.set(user)),
      catchError(err => {
        return of(null);
      })
    );
  }

  ensureCurrentUser(): Observable<UserResponse | null> {
    return this.currentUser() ? of(this.currentUser()) : this.fetchCurrentUser();
  }

  logout(showToast = true) {
    localStorage.removeItem(this.TOKEN_KEY);
    this.token.set(null);
    this.currentUser.set(null);
    if (showToast) {
      this.toast.info('You have been logged out safely.', 'Goodbye');
    }
    this.router.navigate(['/auth/login']);
  }

  getToken(): string | null {
    return localStorage.getItem(this.TOKEN_KEY);
  }

  private setToken(token: string) {
    localStorage.setItem(this.TOKEN_KEY, token);
    this.token.set(token);
  }
}
