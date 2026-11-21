import { inject } from '@angular/core';
import { RedirectCommand, ResolveFn, Router } from '@angular/router';
import { map } from 'rxjs';
import { Employee } from './employee';
import { EmployeeService } from './employee.service';

// RESOLVER = loads data BEFORE the route opens. The page then starts with data ready.
// React Router: loader     Vue Router: beforeEnter + fetch     ui-router: resolve
export const employeeResolver: ResolveFn<Employee | RedirectCommand> = (route) => {
  const router = inject(Router);
  const id = Number(route.paramMap.get('id'));
  return inject(EmployeeService)
    .getById(id)
    .pipe(
      // Not found -> go to the not-found page instead of opening an empty detail page.
      map((e) => e ?? new RedirectCommand(router.parseUrl('/not-found'))),
    );
};
