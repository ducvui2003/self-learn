# Phase 3 — Services, DI, RxJS & HTTP

Goal: share logic with services, understand Dependency Injection (DI), use RxJS basics, and call APIs with `HttpClient` and interceptors.

> Example project: this folder. Run: `cd angular2/phase-3` then `npm start`.

## 1. Dependency Injection (DI)

DI = you do not create dependencies with `new`. You ask Angular, and it gives you one.

| Topic | React | Vue | AngularJS | Angular |
| :--- | :--- | :--- | :--- | :--- |
| Shared logic | custom hook / module | composable | `.service()` / `.factory()` | `@Injectable()` class |
| Get it | `useX()` | `useX()` | function params (`$inject`) | `inject(X)` |
| App-wide config value | Context | `provide` / `inject` | `.constant()` / `.value()` | `InjectionToken` + `providers` |
| Singleton | module scope | module scope | always singleton | `providedIn: 'root'` |

```ts
@Injectable({ providedIn: 'root' })        // one instance for the whole app
export class EmployeeService {
  private readonly http = inject(HttpClient);       // new style
  // constructor(private http: HttpClient) {}       // old style (same result)
}
```

Where can you provide a service?

| Place | Scope |
| :--- | :--- |
| `providedIn: 'root'` | whole app, one instance (most common) |
| `providers` in `app.config.ts` | whole app (for tokens, config, `provideHttpClient()`) |
| `providers` in a `@Component` | one instance **per component** (own state per screen) |

## 2. RxJS basics

An **Observable** is a stream of values over time. A Promise gives one value. An Observable can give many, and can be cancelled.

| Topic | Promise (AngularJS `$q`) | Observable (RxJS) |
| :--- | :--- | :--- |
| Values | one | zero, one, or many |
| Start | starts at once | **lazy**: starts on `subscribe` |
| Cancel | no | yes (`unsubscribe`) |
| Transform | `.then()` | `.pipe(map(...))` |
| Error | `.catch()` | `catchError` |

Operators you need first:

| Operator | Use | React / Vue idea |
| :--- | :--- | :--- |
| `map` | change each value | `array.map` |
| `tap` | side effect (log), no change | `console.log` in the middle |
| `switchMap` | on new value, cancel old request, start new | search box; cancels old fetch |
| `debounceTime(ms)` | wait for pause | lodash `debounce` |
| `distinctUntilChanged` | skip same value | — |
| `catchError` | handle error, return fallback | `try/catch` |
| `finalize` | run at the end (success or error) | `finally` |

Ways to use an Observable in a component:

| Way | Code | When |
| :--- | :--- | :--- |
| `async` pipe | `@if (data$ \| async; as list)` | old and new code, auto unsubscribe |
| `toSignal()` | `data = toSignal(data$, { initialValue: [] })` | new style, signals |
| `subscribe()` | `data$.subscribe(...)` | one-time action (button). Remember to unsubscribe for long streams. |

Signal ↔ Observable: `toSignal(obs$)` and `toObservable(signal)` (from `@angular/core/rxjs-interop`).

## 3. HttpClient

| Task | AngularJS `$http` | axios / fetch | Angular `HttpClient` |
| :--- | :--- | :--- | :--- |
| GET | `$http.get(url).then(r => r.data)` | `axios.get(url)` | `http.get<T>(url)` |
| Result | Promise of response | Promise | `Observable<T>` (body only) |
| Setup | built in | install | `provideHttpClient()` in `app.config.ts` |

- It is lazy. Nothing is sent until you subscribe.
- One subscribe = one request. Two `| async` on the same Observable = two requests.
- It returns the body (JSON) directly, not `response.data`.

## 4. Interceptors

| AngularJS | Angular |
| :--- | :--- |
| `$httpProvider.interceptors.push(factory)` | `provideHttpClient(withInterceptors([fn1, fn2]))` |
| `request` / `responseError` | one function: before `next(req)` = request, `pipe(...)` after = response |

```ts
export const authInterceptor: HttpInterceptorFn = (req, next) =>
  next(req.clone({ setHeaders: { Authorization: 'Bearer ...' } }));
```
- Requests are immutable: use `req.clone()`.
- Order matters: they run in the order of the array for requests, and in reverse for responses.
- Typical jobs: auth token, logging, loading spinner, global error message, 401 → go to login.

## 5. Common pitfalls
- Forgot `provideHttpClient()` → `NullInjectorError: No provider for HttpClient`.
- Forgot to subscribe → no request. (Or the opposite: subscribed twice → two requests.)
- Manual `subscribe()` in a long-living stream without cleanup → memory leak. Prefer `async` / `toSignal`.
- Nested `subscribe` inside `subscribe`. Use `switchMap` instead.
- Mutating `req` in an interceptor. Use `clone()`.
- Using `switchMap` for save/POST: it can cancel a save. Use `concatMap` or `exhaustMap` for writes. See the examples below.

### Example: `switchMap` vs `exhaustMap`

Both start an inner Observable (for example an HTTP call) for each outer value. They differ when a **new value comes while the old call is still running**.

| Operator | New value while busy | Use for |
| :--- | :--- | :--- |
| `switchMap` | **cancel the old**, start the new | search, load detail by id (only the latest matters) |
| `exhaustMap` | **ignore the new**, keep the old | save / submit button (stop double click) |
| `concatMap` | **queue the new**, run after the old | ordered writes (every one must run, in order) |
| `mergeMap` | run **all at the same time** | independent calls, order not important |

**`switchMap`: search (latest wins)**
```ts
// user types "ya", then "yam" quickly
toObservable(this.keyword).pipe(
  debounceTime(300),
  switchMap((k) => this.service.search(k)),   // request for "ya" is cancelled when "yam" comes
);
```
Why: the old result is useless, and an old slow response must not overwrite the new one.

**`exhaustMap`: save button (first wins)**
```ts
private readonly saveClick$ = new Subject<Employee>();

constructor() {
  this.saveClick$.pipe(
    exhaustMap((emp) => this.service.save(emp)),  // clicks during a running save are ignored
    takeUntilDestroyed(),
  ).subscribe(() => this.log.add('Saved (保存しました)'));
}

protected save(emp: Employee): void {
  this.saveClick$.next(emp);   // user may double click: only 1 POST is sent
}
```
Why: if you used `switchMap` here, the second click would **cancel** the first request in the browser (the server may still save it), and you could save twice or get a wrong state. With `exhaustMap`, only the first click sends a POST.

**Timeline**
```
clicks:      ──1────2──────3──
switchMap:   ──[1──x]
                    [2──────✓]      1 is cancelled by 2
exhaustMap:  ──[1────────✓]
                    (2 ignored)  (3 runs if 1 is done)
```

**React / Vue idea**
| Need | React / Vue | RxJS |
| :--- | :--- | :--- |
| Cancel old fetch | `AbortController` in `useEffect` cleanup / `watch` cleanup | `switchMap` |
| Disable button while saving | `if (loading) return;` | `exhaustMap` |
- Providing a service in a component by mistake: you get a new instance each time.

## 6. Japan-project tips
- Old code: `constructor(private http: HttpClient)`, `this.http.get(...).subscribe(...)`, `ngOnDestroy` with `Subscription.unsubscribe()` or `takeUntil(this.destroy$)`. Learn to read it.
- Many projects wrap `HttpClient` in an `ApiService` and add an interceptor for token, error dialogs (エラーダイアログ) and a loading overlay.
- Error messages are often shown in Japanese from one central place: the error interceptor is a good spot.
- Backend is often REST + JSON with Java (Spring). Check date formats and `null` handling in your types.

## 7. Example: Employee Directory + API

The "API" is a static JSON file in `public/data/` so that it runs with no server.

| File | What it shows |
| :--- | :--- |
| [src/app/employee.service.ts](./src/app/employee.service.ts) | `@Injectable`, `inject()`, `HttpClient`, `map` |
| [src/app/tokens.ts](./src/app/tokens.ts) | `InjectionToken` |
| [src/app/app.config.ts](./src/app/app.config.ts) | `provideHttpClient`, `withInterceptors`, token value |
| [src/app/interceptors.ts](./src/app/interceptors.ts) | auth, logging, error interceptors |
| [src/app/log.service.ts](./src/app/log.service.ts) | shared singleton service with a signal |
| [src/app/app.ts](./src/app/app.ts) | `async` pipe, `toSignal`, `debounceTime`, `switchMap`, `catchError` |
| [src/app/app.spec.ts](./src/app/app.spec.ts) | test with `HttpTestingController` (fake backend) |
| [public/data/employees.json](./public/data/employees.json) | fake API data |

Run it:
```bash
cd angular2
npm install --legacy-peer-deps   # once
cd phase-3
npm start -- --port 4202
```
Open the page, type in the search box, click "Call a missing URL", and watch the interceptor log.

## 8. Practice
1. Add `getById(id)` in the service and show one employee.
2. Add a loading flag: set it in an interceptor with a counter (`+1` before, `-1` in `finalize`).
3. Add `retry(2)` in the service for `getAll()`.
4. Make `LogService` keep only the last 10 lines.
