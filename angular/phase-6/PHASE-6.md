# Phase 6 — Real-Project Skills (State, Testing, Performance & Legacy Style)

Goal: learn how real team projects are structured, tested, and kept fast — plus how to read older NgModule codebases.

> Example project: this folder. Run: `cd angular2/phase-6` then `npm start -- --port 4205`.

## 1. State management

| Scale | React | Vue | AngularJS | Angular |
| :--- | :--- | :--- | :--- | :--- |
| Local (1 component) | `useState` | `ref` | `$scope` | `signal()` |
| Shared (small–medium) | Zustand / Context | Pinia / composable | `.service()` | **Service + Signals** (`ExpenseStore`) |
| Large / complex app | Redux Toolkit | Pinia | — | **NgRx** (or `@ngrx/signals`) |

**Service + Signals pattern (recommended default):**
```ts
@Injectable({ providedIn: 'root' })
export class ExpenseStore {
  private readonly _items = signal<Expense[]>([]);  // private: nobody mutates directly
  readonly items = this._items.asReadonly();        // public: read-only
  readonly total = computed(() => ...);             // selector

  approve(id: number) {                             // action
    this._items.update(list => list.map(...));      // immutable update
  }
}
```

**When do teams use NgRx?**
- Many screens share complex state with strict audit/logging (Redux DevTools time-travel).
- NgRx concepts = Redux: `Action` → `Reducer` (pure) → `Store` → `Selector`, plus `Effects` (RxJS) for HTTP.
- For most apps, a Signal Store (or `@ngrx/signals`) is much smaller and easier to read.

## 2. Testing

| Tool | React | Vue | AngularJS | Angular |
| :--- | :--- | :--- | :--- | :--- |
| Runner | Vitest / Jest | Vitest | Karma + Jasmine | **Vitest** (v21 default) or Jasmine/Karma |
| Render component | React Testing Library | Vue Test Utils | `$compile` | `TestBed.createComponent(App)` |
| Mock HTTP | MSW / `vi.fn` | MSW | `$httpBackend` | `HttpTestingController` |
| Mock router | `MemoryRouter` | mock router | — | `RouterTestingHarness` |

```ts
// Test a service/store with a fake HTTP backend
TestBed.configureTestingModule({
  providers: [provideHttpClient(), provideHttpClientTesting()],
});
const store = TestBed.inject(ExpenseStore);
const http = TestBed.inject(HttpTestingController);

store.load();
http.expectOne('/data/expenses.json').flush([...]);
expect(store.pendingCount()).toBe(1);
http.verify(); // fail if any unexpected request is still open
```

- Test **stores, pipes, validators** directly (fast, no DOM needed).
- Test **components** through `fixture.nativeElement` (what the user sees), not private fields.

## 3. Performance

| Technique | What it does | React / Vue idea |
| :--- | :--- | :--- |
| `ChangeDetectionStrategy.OnPush` | Skip checking a component unless inputs/signals change | `React.memo` |
| `@for (...; track e.id)` | Reuse DOM rows by ID (never `track $index` for editable lists) | `key={e.id}` / `:key="e.id"` |
| `@defer (on interaction / viewport)` | Lazy-load a heavy widget into its own JS chunk | `React.lazy` + `Suspense` / `defineAsyncComponent` |
| Route `loadComponent` / `loadChildren` | Split pages into lazy chunks | lazy routes |
| `computed()` & pure pipes | Cache derived values instead of recalculating every render | `useMemo` / `computed` |

`@defer` triggers: `on idle`, `on viewport`, `on interaction`, `on hover`, `on timer(2s)`, or `when condition()`.

## 4. Legacy Angular cheat sheet (v8–v16)

Many Japan enterprise apps still use older Angular. Here is how old code maps to what you learned:

| Feature | Legacy (v8–v16) | Modern (v17–v21) |
| :--- | :--- | :--- |
| Registration | `@NgModule({ declarations, imports, exports })` | Standalone (`imports: [...]` on `@Component`) |
| `if` / `for` / `switch` | `*ngIf`, `*ngFor="let x of list; trackBy: fn"`, `[ngSwitch]` | `@if`, `@for (x of list; track x.id)`, `@switch` |
| Inputs / outputs | `@Input() x`, `@Output() y = new EventEmitter()` | `input()`, `output()`, `model()` |
| DI | `constructor(private http: HttpClient) {}` | `private http = inject(HttpClient)` |
| Host binding | `@HostListener('click')`, `@HostBinding('class.x')` | `host: { '(click)': '...', '[class.x]': '...' }` |
| Route guards | class `implements CanActivate` | function `CanActivateFn` |
| HTTP interceptors | class `implements HttpInterceptor` + `HTTP_INTERCEPTORS` | function `HttpInterceptorFn` + `withInterceptors()` |
| Change detection | `zone.js` + `Default` | Zoneless + `OnPush` + signals |

Tip: standalone components and legacy `NgModule`s can live in the same app (see `LegacyNoticeModule` in this project).

## 5. Team folder structure & conventions

```text
src/app/
├── core/        # App-wide singletons: auth, API clients, stores, interceptors, models
├── shared/      # Reusable dumb UI: buttons, pipes, directives (no feature logic)
├── features/    # One folder per business screen/domain (expenses/, employees/)
└── app.routes.ts
```

- **File names:** `feature.component.ts` or `feature.ts`, `feature.service.ts`, `feature.store.ts`, `feature.pipe.ts`, `feature.directive.ts`, `feature.spec.ts`.
- **Lint & format:** ESLint (`angular-eslint`) + Prettier (`.prettierrc` is already in this project).
- **Strict TypeScript:** keep `"strict": true` in `tsconfig.json`.

## 6. Common pitfalls
- Exposing a writable `signal` from a store → any component can mutate it from anywhere. Always expose `.asReadonly()`.
- Forgetting `http.verify()` in `afterEach()` → hidden extra HTTP calls pass tests silently.
- Putting heavy components directly in `app.html` without `@defer` → bigger initial bundle.
- Mixing `core/` (app-wide) and `features/` (one screen) → circular imports.
- Using `track $index` on a list that sorts or deletes rows → wrong DOM reuse.

## 7. Japan-project tips
- Most legacy Japan apps (Angular 10–15) use `NgModule`, `SharedModule`, `CoreModule`, `RxJS BehaviorSubject` stores (instead of signals), and Karma/Jasmine.
- `BehaviorSubject` store is the old version of `ExpenseStore`: `private _items$ = new BehaviorSubject([])` + `items$ = this._items$.asObservable()`. Same pattern, just Observable instead of signal.
- Check `angular.json` and `package.json` on day 1 of a project to see the Angular version, UI kit (Angular Material / PrimeNG / NG-ZORRO), and test runner.
- Keep commits small and follow the repo's lint/Prettier config.

## 8. Example: Expense Dashboard (経費精算ダッシュボード)

| File | What it shows |
| :--- | :--- |
| [src/app/core/expense.model.ts](./src/app/core/expense.model.ts) | Domain model |
| [src/app/core/expense.api.ts](./src/app/core/expense.api.ts) | Thin HTTP layer |
| [src/app/core/expense.store.ts](./src/app/core/expense.store.ts) | Signal Store (`asReadonly`, `computed`, actions) |
| [src/app/features/expenses/expense-list.ts](./src/app/features/expenses/expense-list.ts) | `OnPush` + `@for (...; track e.id)` + store actions |
| [src/app/features/expenses/expense-chart.ts](./src/app/features/expenses/expense-chart.ts) | Lazy widget loaded via `@defer (on interaction)` |
| [src/app/legacy/legacy-notice.module.ts](./src/app/legacy/legacy-notice.module.ts) & [legacy-notice.component.ts](./src/app/legacy/legacy-notice.component.ts) | Real legacy `NgModule` + `*ngIf` + `*ngFor` + `@Input()` + constructor DI |
| [src/app/core/expense.store.spec.ts](./src/app/core/expense.store.spec.ts) & [src/app/app.spec.ts](./src/app/app.spec.ts) | Store & component unit tests with `HttpTestingController` |
| [public/data/expenses.json](./public/data/expenses.json) | Sample JP/EN expense data |

Run it:
```bash
cd angular2
npm install --legacy-peer-deps   # once
cd phase-6
npm start -- --port 4205
```
Run tests:
```bash
cd angular2/phase-6
npm test -- --watch=false
```

## 9. Practice
1. Add a `resetAll()` action to `ExpenseStore` that sets all items back to `'pending'`, and write a unit test for it.
2. Change `@defer (on interaction)` to `@defer (on viewport)` and check the Network tab in DevTools.
3. Convert `LegacyNoticeComponent` to a standalone component (remove `LegacyNoticeModule`, switch `*ngIf`/`*ngFor` to `@if`/`@for`, `input()`, `inject()`).
