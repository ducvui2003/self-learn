import { Routes } from '@angular/router';
import { unsavedChangesGuard } from '../guards';

// Child routes of /admin. This file is loaded lazily (a separate JS chunk).
export const ADMIN_ROUTES: Routes = [
  {
    path: '',
    title: 'Admin (管理)',
    loadComponent: () => import('./admin-home').then((m) => m.AdminHome),
  },
  {
    path: 'edit',
    title: 'Admin edit (編集)',
    loadComponent: () => import('./admin-edit').then((m) => m.AdminEdit),
    canDeactivate: [unsavedChangesGuard], // asks before leaving with unsaved changes
  },
];
