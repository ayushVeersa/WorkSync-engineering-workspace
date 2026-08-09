import { CanActivateFn, Router } from '@angular/router';
import { inject } from '@angular/core';
import { AuthService } from '../services/auth.service';
import { Role } from '../models/role.model';
import { ToastService } from '../services/toast.service';
import { map } from 'rxjs';

export const roleGuard = (allowedRoles: Role[]): CanActivateFn => {
  return (route, state) => {
    const authService = inject(AuthService);
    const router = inject(Router);
    const toast = inject(ToastService);

    return authService.ensureCurrentUser().pipe(
      map(user => {
        if (user && allowedRoles.includes(user.role)) {
          return true;
        }

        toast.warning('You do not have administrative privileges to access that section.', 'Restricted Access');
        router.navigate(['/dashboard']);
        return false;
      })
    );
  };
};
