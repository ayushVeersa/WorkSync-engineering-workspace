import { HttpInterceptorFn, HttpErrorResponse } from '@angular/common/http';
import { inject } from '@angular/core';
import { catchError, throwError } from 'rxjs';
import { ToastService } from '../services/toast.service';
import { AuthService } from '../services/auth.service';

export const errorInterceptor: HttpInterceptorFn = (req, next) => {
  const toast = inject(ToastService);
  const authService = inject(AuthService);

  return next(req).pipe(
    catchError((error: HttpErrorResponse) => {
      let errorMessage = 'An unexpected error occurred. Please try again.';

      if (error.error) {
        if (typeof error.error.detail === 'string') {
          errorMessage = error.error.detail;
        } else if (Array.isArray(error.error.detail)) {
          errorMessage = error.error.detail.map((e: any) => e.msg || e.message || JSON.stringify(e)).join(', ');
        } else if (error.error.message) {
          errorMessage = error.error.message;
        }
      }

      if (error.status === 401) {
        if (req.url.includes('/auth/me')) {
          return throwError(() => error);
        } else if (!req.url.includes('/auth/login')) {
          authService.logout(false);
          toast.error('Your session expired. Please sign in again.', 'Session Expired');
        } else {
          toast.error(errorMessage, 'Authentication Failed');
        }
      } else if (error.status === 403) {
        toast.error(errorMessage || 'You do not have permission for this action.', 'Access Restricted');
      } else if (error.status === 404) {
        toast.warning(errorMessage || 'The requested resource was not found.', 'Not Found');
      } else if (error.status >= 500) {
        toast.error('Server error encountered. Our team is looking into it.', 'Server Error');
      } else {
        toast.error(errorMessage, 'Operation Error');
      }

      return throwError(() => error);
    })
  );
};
