# Phase 2 — Signals & Components

Goal: manage state with signals, and make components talk to each other.

> Example project: this folder. Run: `cd angular2/phase-2` then `npm start`.

## 1. Signals (state)

| Topic | React | Vue | AngularJS | Angular |
| :--- | :--- | :--- | :--- | :--- |
| State | `useState` | `ref` | `$scope.x` | `x = signal(0)` |
| Read | `x` | `x.value` | `x` | `x()` |
| Write | `setX(1)` | `x.value = 1` | `x = 1` + digest | `x.set(1)` |
| Update from old | `setX(n => n+1)` | `x.value++` | — | `x.update(n => n + 1)` |
| Derived | `useMemo` | `computed` | getter / `$watch` | `computed(() => ...)` |
| Side effect | `useEffect` | `watchEffect` | `$watch` | `effect(() => ...)` |

Rules:
- `computed` is read-only and cached. Use it for any derived value.
- `effect` is for side effects only (log, save, call outside code). Do not set other signals inside it.
- Update objects and arrays **immutably**: `list.map(...)`, `{ ...r, status }`.

## 2. Component communication

| Direction | React | Vue | AngularJS | Angular |
| :--- | :--- | :--- | :--- | :--- |
| Parent → child | props | `defineProps` | `bindings: { x: '<' }` | `x = input<T>()` / `input.required<T>()` |
| Child → parent | callback prop | `defineEmits` | `bindings: { onX: '&' }` | `x = output<T>()`, `x.emit(v)` |
| Two-way | value + onChange | `defineModel` / `v-model` | `bindings: { x: '=' }` | `x = model('')`, `[(x)]="..."` |
| Slots | `children` | `<slot>` | `transclude` | `<ng-content>` (`select="[name]"` for named) |

Template side:
```html
<app-request-card
  [request]="r"                 <!-- input  -->
  (approve)="approve($event)"   <!-- output -->
  [(comment)]="text" />         <!-- model (short form) -->
```
`[(x)]` is a short form of `[x]="v"` + `(xChange)="v = $event"`.

## 3. Lifecycle hooks

| Moment | React | Vue | AngularJS | Angular |
| :--- | :--- | :--- | :--- | :--- |
| Created | function body | `setup` | `controller` | `constructor` |
| Input changed | deps array | `watch(props)` | `$onChanges` | `ngOnChanges` |
| Ready (init) | `useEffect([])` | `onMounted` | `$onInit` | `ngOnInit` |
| DOM ready | `useEffect([])` | `onMounted` | `$postLink` | `afterNextRender()` |
| Removed | effect cleanup | `onUnmounted` | `$onDestroy` | `ngOnDestroy` (or `inject(DestroyRef).onDestroy()`) |

Tip: with signals you often do not need `ngOnChanges`. Use `computed` or `effect` on the input.

## 4. Change detection and `OnPush`

| Strategy | Meaning |
| :--- | :--- |
| Default | Angular checks the component on every event. Simple, but slower in big apps. |
| `OnPush` | Check only when an input changes, an event comes from the component, or a signal used in the template changes. |

- This project is **zoneless** (no `zone.js`), so signals are the way to update the screen.
- Set `changeDetection: ChangeDetectionStrategy.OnPush` on every component. It is the safe default.

## 5. Common pitfalls
- `x.push(item)` on a signal array: the screen does not update. Use `x.update(l => [...l, item])`.
- Forgot `()` to read a signal in TS or template.
- Using `effect` to copy one signal to another → use `computed`.
- Using `input()` value in the constructor: it is not ready yet. Use `computed`, `effect` or `ngOnInit`.
- Mutating an object that comes from `input()`. Treat inputs as read-only.
- Reading `@Input()` style in old code: it is the same idea (`@Input() x`, `@Output() y = new EventEmitter()`).

## 6. Japan-project tips
- Old projects use decorators: `@Input()`, `@Output() change = new EventEmitter<T>()`, `ngOnChanges`, `ngOnDestroy`. Learn to read them. They still work.
- Old projects use `Default` change detection and mutate objects. When you move to `OnPush`, you must use immutable updates.
- Always unsubscribe/cleanup in `ngOnDestroy` in old code (RxJS comes in Phase 3).
- Approval / list-and-detail screens (申請, 承認) are very common: parent holds the list, child shows one row and emits events.

## 7. Example: Leave Approval

| File | What it shows |
| :--- | :--- |
| [src/app/request.ts](./src/app/request.ts) | Type and sample data |
| [src/app/app.ts](./src/app/app.ts) | `signal`, `computed`, `effect`, immutable update, handlers |
| [src/app/app.html](./src/app/app.html) | Using `input`/`output`/`model`, content projection |
| [src/app/request-card.ts](./src/app/request-card.ts) | `input.required`, `output`, `model`, `OnPush` |
| [src/app/panel.ts](./src/app/panel.ts) | `ng-content` (default + named slot) |
| [src/app/lifecycle-demo.ts](./src/app/lifecycle-demo.ts) | Lifecycle hooks, `effect`, `afterNextRender` |

Run it:
```bash
cd angular2
npm install --legacy-peer-deps   # once
cd phase-2
npm start
```
Open http://localhost:4200 (use `npm start -- --port 4201` if Phase 1 is running).

## 8. Practice
1. Add a "Reset" button in the card that emits a new `reset` output.
2. Add a computed `rejectedCount` and show it.
3. Add a "Delete" action that removes a request (immutable update with `filter`).
4. Add `ngOnDestroy` with `console.log` to `RequestCard` and watch it when you delete.
