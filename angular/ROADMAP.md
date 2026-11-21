# Angular (2+) Roadmap

Goal: learn modern Angular for a Japan client project. You know JS, React, Vue and AngularJS, so each topic is mapped to what you already know.

## Mental-model mapping

| Concept | React | Vue | AngularJS 1.x | Angular (2+) |
| :--- | :--- | :--- | :--- | :--- |
| UI unit | Function component | SFC component | `.component()` | `@Component` class (standalone) |
| Template | JSX | `<template>` | HTML + `{{ }}` | HTML + `{{ }}`, `[prop]`, `(event)` |
| Conditional / loop | `&&`, `map` | `v-if`, `v-for` | `ng-if`, `ng-repeat` | `@if`, `@for` (old: `*ngIf`, `*ngFor`) |
| Local state | `useState` | `ref` | `$scope` / `controllerAs` | `signal()` |
| Derived state | `useMemo` | `computed` | `$watch` / getter | `computed()` |
| Side effect | `useEffect` | `watch` | `$watch` | `effect()` |
| Props / events | props / callbacks | props / `emit` | `bindings` (`<`, `&`) | `input()` / `output()` |
| Two-way bind | controlled input | `v-model` | `ng-model` | `[(ngModel)]` / `model()` |
| Shared logic | custom hook | composable | service / factory | `@Injectable` service + `inject()` |
| HTTP | fetch / axios | fetch / axios | `$http` | `HttpClient` (Observable) |
| Async | Promise | Promise | `$q` | RxJS `Observable` |
| Forms | react-hook-form | vee-validate | `ngModel` + `$error` | Reactive Forms (typed) |
| Routing | react-router | vue-router | ui-router / ngRoute | `@angular/router` |
| Global state | Redux / Zustand | Pinia | service / `$rootScope` | service + signals / NgRx |
| Build tool | Vite / CRA | Vite | none (CDN) | Angular CLI (`ng`) |

## Phases

| Phase | Topic | Status |
| :--- | :--- | :--- |
| 1 | Setup, Angular CLI, project structure, components, templates, data binding, control flow (`@if`, `@for`) | ✅ Ready — [phase-1/PHASE-1.md](./phase-1/PHASE-1.md) |
| 2 | Signals (`signal`, `computed`, `effect`), `input`/`output`, component communication, lifecycle hooks, `OnPush` | ✅ Ready — [phase-2/PHASE-2.md](./phase-2/PHASE-2.md) |
| 3 | Dependency injection, services, RxJS basics, `HttpClient`, interceptors | ✅ Ready — [phase-3/PHASE-3.md](./phase-3/PHASE-3.md) |
| 4 | Forms: template-driven and reactive (typed), validation, custom validators, search/table screens | ✅ Ready — [phase-4/PHASE-4.md](./phase-4/PHASE-4.md) |
| 5 | Routing, route guards, resolvers, lazy loading, custom directives, pipes | ✅ Ready — [phase-5/PHASE-5.md](./phase-5/PHASE-5.md) |
| 6 | State management (signals / NgRx), testing, performance, project conventions, legacy NgModule style | ✅ Ready — [phase-6/PHASE-6.md](./phase-6/PHASE-6.md) |

### Phase 1 — Foundations
- Install Node and Angular CLI, run `ng new`, `ng serve`
- Project structure: `main.ts`, `app.config.ts`, `app.component.ts`
- Standalone component: selector, template, styles
- Binding: interpolation, property `[ ]`, event `( )`, two-way `[( )]`
- Control flow: `@if`, `@for` with `track`, `@switch`
- Built-in pipes: `date`, `currency`, `uppercase`
- Example: employee directory (JP/EN labels)

### Phase 2 — Signals & Components
- `signal`, `computed`, `effect`
- `input()`, `output()`, `model()`
- Parent-child communication, content projection (`ng-content`)
- Lifecycle hooks: `ngOnInit`, `ngOnChanges`, `ngOnDestroy`
- Change detection: Default vs `OnPush`

### Phase 3 — Services & HTTP
- `@Injectable`, `providedIn: 'root'`, `inject()`
- RxJS: `Observable`, `map`, `switchMap`, `catchError`, `async` pipe
- `HttpClient`, `provideHttpClient(withInterceptors())`
- Error handling, loading state, `toSignal`

### Phase 4 — Forms
- Template-driven forms (`ngModel`) — like AngularJS
- Reactive forms: `FormControl`, `FormGroup`, `FormArray`, `FormBuilder`
- Built-in and custom validators, async validators
- Search form + result table + paging

### Phase 5 — Routing & Reuse
- Routes, `routerLink`, params, query params
- Guards (`CanActivateFn`), resolvers
- Lazy loading (`loadComponent`, `loadChildren`)
- Custom attribute directives, custom pipes

### Phase 6 — Real-project Skills
- State: service + signals, intro to NgRx
- Testing: Jasmine/Karma (or Jest), `TestBed`, `HttpTestingController`
- Performance: `OnPush`, `trackBy`/`track`, `@defer`, lazy loading
- Legacy style: NgModule, `*ngIf`/`*ngFor`, constructor injection
- Folder structure, lint, naming conventions for team projects
