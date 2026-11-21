import { inject } from '@angular/core';
import { CanActivateFn, CanDeactivateFn, Router } from '@angular/router';
import { AuthService } from './auth.service';
import type { AdminEdit } from './admin/admin-edit';

// GUARD = a function that decides if the route may open.
// Return true = allow.  Return a UrlTree = redirect.  Return false = stay.
// React Router: loader + redirect() / <ProtectedRoute>     Vue Router: beforeEach / beforeEnter
// AngularJS ui-router: $stateChangeStart / resolve that rejects
export const authGuard: CanActivateFn = (_route, state) => {
  const auth = inject(AuthService);
  const router = inject(Router);
  return auth.isLoggedIn()
    ? true
    : router.createUrlTree(['/login'], { queryParams: { returnUrl: state.url } });
};

// canDeactivate: runs when the user LEAVES a page. Used for "unsaved changes" dialogs.
export const unsavedChangesGuard: CanDeactivateFn<AdminEdit> = (component) =>
  !component.dirty() || confirm('You have unsaved changes. Leave this page? (変更を破棄しますか？)');
