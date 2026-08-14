import { Routes } from '@angular/router';
import { authGuard } from './core/guards/auth.guard';
import { roleGuard } from './core/guards/role.guard';
import { Role } from './core/models/role.model';

export const routes: Routes = [
  {
    path: '',
    redirectTo: 'dashboard',
    pathMatch: 'full'
  },
  {
    path: 'auth/login',
    loadComponent: () => import('./features/auth/login/login.component').then(m => m.LoginComponent)
  },
  {
    path: 'auth/register',
    loadComponent: () => import('./features/auth/register/register.component').then(m => m.RegisterComponent)
  },
  {
    path: 'dashboard',
    loadComponent: () => import('./features/dashboard/dashboard.component').then(m => m.DashboardComponent),
    canActivate: [authGuard]
  },
  {
    path: 'projects',
    loadComponent: () => import('./features/projects/project-list/project-list.component').then(m => m.ProjectListComponent),
    canActivate: [authGuard]
  },
  {
    path: 'projects/:id',
    loadComponent: () => import('./features/projects/project-detail/project-detail.component').then(m => m.ProjectDetailComponent),
    canActivate: [authGuard]
  },
  {
    path: 'issues',
    loadComponent: () => import('./features/issues/issue-board/issue-board.component').then(m => m.IssueBoardComponent),
    canActivate: [authGuard]
  },
  {
    path: 'employees',
    loadComponent: () => import('./features/employees/employee-list/employee-list.component').then(m => m.EmployeeListComponent),
    canActivate: [authGuard, roleGuard([Role.ADMIN, Role.MANAGER])]
  },
  {
    path: 'departments',
    loadComponent: () => import('./features/departments/department-list/department-list.component').then(m => m.DepartmentListComponent),
    canActivate: [authGuard, roleGuard([Role.ADMIN])]
  },
  {
    path: 'my-work',
    loadComponent: () => import('./features/my-work/my-work.component').then(m => m.MyWorkComponent),
    canActivate: [authGuard]
  },
  {
    path: 'activity',
    loadComponent: () => import('./features/activity/activity.component').then(m => m.ActivityComponent),
    canActivate: [authGuard]
  },
  {
    path: 'reports',
    loadComponent: () => import('./features/reports/reports.component').then(m => m.ReportsComponent),
    canActivate: [authGuard]
  },
  {
    path: 'profile',
    loadComponent: () => import('./features/profile/profile.component').then(m => m.ProfileComponent),
    canActivate: [authGuard]
  },
  {
    path: '404',
    loadComponent: () => import('./features/not-found/not-found.component').then(m => m.NotFoundComponent)
  },
  {
    path: '**',
    loadComponent: () => import('./features/not-found/not-found.component').then(m => m.NotFoundComponent)
  }
];
