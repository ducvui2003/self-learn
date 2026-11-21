# Phase 5 — Routing, Guards, Lazy Loading, Directives & Pipes

Goal: build a multi-page app with the Angular router, protect pages, load code lazily, and write your own directives and pipes.

> Example project: this folder. Run: `cd angular2/phase-5` then `npm start -- --port 4204`.

## 1. Router basics

| Topic | React Router | Vue Router | AngularJS (ui-router) | Angular |
| :--- | :--- | :--- | :--- | :--- |
| Route table | `<Route path element>` / `createBrowserRouter` | `routes: [{ path, component }]` | `$stateProvider.state()` | `Routes` array in `app.routes.ts` |
| Where the page shows | `<Outlet />` | `<RouterView />` | `<ui-view>` | `<router-outlet />` |
| Link | `<Link to>` | `<RouterLink to>` | `ui-sref` | `routerLink` |
| Active link class | `<NavLink>` | `router-link-active` | `ui-sref-active` | `routerLinkActive="active"` |
| Navigate in code | `useNavigate()` | `router.push()` | `$state.go()` | `inject(Router).navigate()` / `navigateByUrl()` |
| Route param | `useParams()` | `route.params` | `$stateParams` | `input()` with `withComponentInputBinding()` |
| Query param | `useSearchParams()` | `route.query` | `$location.search()` | same: `input()` |
| 404 | `path="*"` | `/:pathMatch(.*)*` | `$urlRouterProvider.otherwise` | `path: '**'` (put it last) |
| Page title | `document.title` | `meta.title` | — | `title` in the route |

```ts
// app.config.ts
provideRouter(routes, withComponentInputBinding())
```
With `withComponentInputBinding()`, params, query params and resolver data go straight into `input()`:
```ts
// route: employees/:id?tab=...   resolve: { employee: ... }
id = input.required<string>();            // :id
tab = input<string | undefined>();        // ?tab=
employee = input.required<Employee>();    // resolver data
```
Old code uses `ActivatedRoute` (`route.paramMap`, `route.snapshot.params`). Learn to read it.

## 2. Guards and resolvers

| Name | When it runs | Use | Return |
| :--- | :--- | :--- | :--- |
| `canActivate` | before opening a route | login check | `true` / `false` / `UrlTree` (redirect) |
| `canActivateChild` | before opening any child | same, for a group | same |
| `canMatch` | when matching the route | hide a route and **do not download** its code (roles) | same |
| `canDeactivate` | before leaving a route | "unsaved changes" dialog | `true` / `false` |
| `resolve` | before opening a route | load data first | the data, or `RedirectCommand` |

All are plain functions (`CanActivateFn`, `ResolveFn`) that can call `inject()`.

```ts
export const authGuard: CanActivateFn = (_r, state) =>
  inject(AuthService).isLoggedIn()
    ? true
    : inject(Router).createUrlTree(['/login'], { queryParams: { returnUrl: state.url } });
```

| Guard idea | React Router | Vue Router |
| :--- | :--- | :--- |
| Login check | `loader` + `redirect()` or a `<ProtectedRoute>` wrapper | `beforeEach` / `beforeEnter` |
| Load data first | `loader` | fetch in `beforeEnter` |
| Unsaved changes | `useBlocker` | `beforeRouteLeave` |

Resolver or load in the component?
- Resolver: page opens with data ready. Good for detail pages. But the user waits on the old page.
- In the component: page opens at once and shows a spinner. Better feel for slow APIs.

## 3. Lazy loading

| | Code |
| :--- | :--- |
| One component | `loadComponent: () => import('./login').then(m => m.Login)` |
| A group of routes | `loadChildren: () => import('./admin/admin.routes').then(m => m.ADMIN_ROUTES)` |
| Old NgModule style | `loadChildren: () => import('./admin/admin.module').then(m => m.AdminModule)` |
| Load part of a template | `@defer { <heavy-chart /> }` |

| | React | Vue |
| :--- | :--- | :--- |
| Lazy page | `React.lazy(() => import(...))` | `component: () => import(...)` |

`ng build` prints the lazy chunks. Check that `admin` is a separate file.

## 4. Custom directives

| Type | Changes | Example | AngularJS |
| :--- | :--- | :--- | :--- |
| Attribute directive | behavior / style of an element | `appHighlight`, `appConfirm` | `restrict: 'A'` |
| Structural directive | adds / removes elements (`*ngIf`) | rarely written now; use `@if` / `@for` | `ng-if`, `ng-repeat` |
| Component | a directive with a template | `@Component` | `.component()` |

```ts
@Directive({
  selector: '[appHighlight]',
  host: { '(mouseenter)': 'active.set(true)', '[style.background-color]': 'bg()' },
})
export class Highlight { color = input('#fff3b0', { alias: 'appHighlight' }); /* ... */ }
```
- `host: {}` replaces the old `@HostListener` and `@HostBinding` decorators.
- Vue has custom directives (`v-focus`). React has no direct match (use a hook or a wrapper).

## 5. Custom pipes

| | Angular | React / Vue |
| :--- | :--- | :--- |
| Define | `@Pipe({ name: 'salaryJp' })` + `transform()` | a helper function |
| Use | `{{ salary \| salaryJp }}`, `{{ text \| truncate: 30 }}` | `{{ format(salary) }}` / `{format(salary)}` |
| Purity | pure by default: runs only when the input changes | — |

- Keep pipes **pure**. Impure pipes (`pure: false`) run on every change detection and are slow.
- Use a pipe for display formatting only. Put business logic in services.

## 6. Common pitfalls
- `path: '**'` is not last → it catches everything.
- Wrong `pathMatch` on the empty path: use `pathMatch: 'full'` with `redirectTo`.
- Forgot `withComponentInputBinding()` → route inputs are always empty.
- Query param input is `undefined` when missing. Type it as `string | undefined`.
- Guard returns `false` and the user sees nothing. Return a `UrlTree` to redirect.
- `canActivate` on a lazy route: the code is already downloaded. Use `canMatch` to avoid the download.
- Used `routerLink` without importing `RouterLink` in a standalone component.
- Relative links: `routerLink="edit"` is relative to the current route, `routerLink="/edit"` is absolute.
- Impure pipe or method call in the template for heavy work. Use `computed` or a pure pipe.

## 7. Japan-project tips
- Admin / master data screens (管理画面) are often lazy modules with guards. You will see `canActivate` + roles.
- Old code: `RouterModule.forRoot(routes)` + `loadChildren: () => import(...).then(m => m.XxxModule)` + class guards (`implements CanActivate`). The new way is only a function.
- "Unsaved changes" dialogs (`canDeactivate`) are very common on input screens.
- Keep search conditions in the URL (query params) so users can use the back button and bookmarks. This is the same idea as `criteria` in Phase 4.
- Money in Japanese format (万円) is a classic custom pipe.

## 8. Example: Employee app with routes

| File | What it shows |
| :--- | :--- |
| [src/app/app.routes.ts](./src/app/app.routes.ts) | route table, params, resolve, lazy load, guard, `**` |
| [src/app/app.config.ts](./src/app/app.config.ts) | `provideRouter` + `withComponentInputBinding` |
| [src/app/guards.ts](./src/app/guards.ts) | `authGuard` (`canActivate`), `unsavedChangesGuard` (`canDeactivate`) |
| [src/app/resolvers.ts](./src/app/resolvers.ts) | `ResolveFn` with `RedirectCommand` |
| [src/app/pages/employee-list.ts](./src/app/pages/employee-list.ts) | query params → `input()`, `routerLink` with `queryParams` |
| [src/app/pages/employee-detail.ts](./src/app/pages/employee-detail.ts) | param + resolver data → `input()` |
| [src/app/pages/login.ts](./src/app/pages/login.ts) | `returnUrl` flow |
| [src/app/admin/](./src/app/admin) | lazy child routes, `canDeactivate` |
| [src/app/shared/highlight.directive.ts](./src/app/shared/highlight.directive.ts) | attribute directive with `host` |
| [src/app/shared/confirm.directive.ts](./src/app/shared/confirm.directive.ts) | directive with `input` and `output` |
| [src/app/shared/salary-jp.pipe.ts](./src/app/shared/salary-jp.pipe.ts), [truncate.pipe.ts](./src/app/shared/truncate.pipe.ts) | custom pipes |
| [src/app/app.spec.ts](./src/app/app.spec.ts) | tests with `RouterTestingHarness` |

Run it:
```bash
cd angular2
npm install --legacy-peer-deps   # once
cd phase-5
npm start -- --port 4204
```
Try:
1. Open `/employees?department=Engineering` (the filter is in the URL).
2. Click an employee (resolver loads the data, `/employees/999` goes to 404).
3. Click Admin while logged out → login → you return to Admin.
4. In Admin → Edit, type text and click "Leave" (the guard asks).
5. Run `npm run build` and look at the lazy chunks in the output.

## 9. Practice
1. Add a `roleGuard` with `canMatch` that allows only `admin` users.
2. Add `canActivateChild` to the admin routes.
3. Add a `tab` query param to the detail page (`?tab=notes`) and bind it with `input()`.
4. Write an `appAutofocus` directive that focuses an input on creation (`inject(ElementRef)`).
5. Wrap the notes block in `@defer (on viewport)`.
