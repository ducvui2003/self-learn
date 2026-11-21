import { Routes } from '@angular/router';
import { EmployeeDetail } from './pages/employee-detail';
import { EmployeeList } from './pages/employee-list';
import { NotFound } from './pages/not-found';
import { authGuard } from './guards';
import { employeeResolver } from './resolvers';

export const routes: Routes = [
  { path: '', pathMatch: 'full', redirectTo: 'employees' },

  // Query params (?keyword=..&department=..) are bound to input() of the page.
  { path: 'employees', component: EmployeeList, title: 'Employees (社員一覧)' },

  // :id is a route param. `resolve` loads `employee` BEFORE the page opens
  // and gives it to the page's input() named `employee`.
  {
    path: 'employees/:id',
    component: EmployeeDetail,
    resolve: { employee: employeeResolver },
    title: 'Employee detail (社員詳細)',
  },

  // LAZY LOADING: the code of this page is downloaded only when the user opens it.
  // React: React.lazy / lazy route    Vue: () => import(...)
  { path: 'login', loadComponent: () => import('./pages/login').then((m) => m.Login), title: 'Login' },

  // LAZY CHILD ROUTES + GUARD: the admin area is a separate chunk.
  {
    path: 'admin',
    canActivate: [authGuard],
    loadChildren: () => import('./admin/admin.routes').then((m) => m.ADMIN_ROUTES),
  },

  { path: 'not-found', component: NotFound, title: 'Not found' },
  { path: '**', redirectTo: 'not-found' }, // must be LAST
];
