# Phase 1 — Foundations

Goal: set up Angular, build your first components, and learn templates and control flow.

> Version: Angular 21 (standalone components, signals, zoneless). One `ng new` project per phase: the example is in this folder.

## 1. Setup and CLI

| Task | React (Vite) | Vue (Vite) | AngularJS 1.x | Angular |
| :--- | :--- | :--- | :--- | :--- |
| Create project | `npm create vite` | `npm create vue` | add `<script>` from CDN | `ng new app` |
| Run dev server | `npm run dev` | `npm run dev` | open `index.html` | `ng serve` |
| Build | `npm run build` | `npm run build` | none | `ng build` |
| Generate code | none | none | none | `ng generate component name` (`ng g c name`) |

## 2. Project structure

| File | Purpose | React / Vue equivalent |
| :--- | :--- | :--- |
| `src/main.ts` | Start point. Calls `bootstrapApplication(App, appConfig)` | `main.jsx` / `main.ts` |
| `src/app/app.config.ts` | App-wide providers (router, http...) | plugins in `createApp().use()` |
| `src/app/app.ts` | Root component class | `App.jsx` / `App.vue` |
| `src/app/app.html` / `app.css` | Template and styles of the component | JSX / `<template>` / `<style>` |
| `src/index.html` | Page shell with `<app-root>` | `index.html` with `#root` |
| `angular.json` | CLI settings | `vite.config.ts` |

## 3. Component

| Topic | React | Vue | AngularJS | Angular |
| :--- | :--- | :--- | :--- | :--- |
| Define | `function Card(){}` | `<script setup>` | `.component('card', {})` | `@Component({...}) class Card {}` |
| Use | `<Card />` | `<Card />` | `<card></card>` | `<app-card />` (the `selector`) |
| Register | `import` | `import` | module | `imports: [Card]` in parent |
| State | `useState` | `ref` | `$scope.x` | `x = signal(0)` |
| Props | `props` | `defineProps` | `bindings` | `x = input()` |

```ts
@Component({
  selector: 'app-employee-card',
  imports: [DatePipe],      // standalone: list what the template uses
  template: `...`,
})
export class EmployeeCard {
  employee = input.required<Employee>();
}
```

## 4. Data binding

| Type | Angular | React | Vue | AngularJS |
| :--- | :--- | :--- | :--- | :--- |
| Text | `{{ name() }}` | `{name}` | `{{ name }}` | `{{ name }}` |
| Property | `[disabled]="x()"` | `disabled={x}` | `:disabled="x"` | `ng-disabled="x"` |
| Event | `(click)="save()"` | `onClick={save}` | `@click="save"` | `ng-click="save()"` |
| Two-way | `[(ngModel)]="name"` | value + onChange | `v-model` | `ng-model` |
| Class | `[class.active]="x()"` | `className` | `:class` | `ng-class` |

Note: `[(ngModel)]` needs `FormsModule` in `imports`.

## 5. Control flow (new syntax)

| Task | Angular (new) | Angular (old, legacy) | React | Vue | AngularJS |
| :--- | :--- | :--- | :--- | :--- | :--- |
| If | `@if (x) {} @else {}` | `*ngIf="x; else tpl"` | `x && <A/>` | `v-if` | `ng-if` |
| Loop | `@for (e of list; track e.id) {}` | `*ngFor="let e of list; trackBy: fn"` | `list.map` + `key` | `v-for` + `:key` | `ng-repeat ... track by` |
| Empty list | `@empty {}` | extra `*ngIf` | manual | manual | manual |
| Switch | `@switch (x) { @case (1) {} }` | `[ngSwitch]` | `switch` | `v-if/else-if` | `ng-switch` |

## 6. Pipes (= AngularJS filters)

| AngularJS | Angular |
| :--- | :--- |
| `{{ d \| date:'yyyy/MM/dd' }}` | `{{ d \| date: 'yyyy/MM/dd' }}` |
| `{{ n \| currency }}` | `{{ n \| currency: 'JPY' }}` |
| `{{ s \| uppercase }}` | `{{ s \| uppercase }}` |

Pipes must be imported in the component (`DatePipe`, `CurrencyPipe`, `UpperCasePipe`).

## 7. Common pitfalls
- Forgot to add a component/pipe to `imports` → error "is not a known element" or "pipe not found".
- Forgot `()` when reading a signal: `{{ name }}` shows a function. Use `{{ name() }}`.
- Forgot `track` in `@for` → build error.
- Mixed up `[ ]` (value from code) and plain attribute (text): `title="x"` is text, `[title]="x"` is code.
- Used `[(ngModel)]` without `FormsModule`.

## 8. Japan-project tips
- Many projects still use old Angular (v8–v15) with `NgModule`, `*ngIf`, `*ngFor`. Learn to read both styles.
- In old code, a component = 4 files: `.ts`, `.html`, `.css`, `.spec.ts`, and it is declared in `declarations: []` of an `NgModule`.
- Use `date: 'yyyy/MM/dd'` and `currency: 'JPY'` — common formats in Japanese screens.
- Keep UI labels in both Japanese and English (later: i18n).

## 9. Example: Employee Directory
Folder: this folder (`phase-1/`)

| File | What it shows |
| :--- | :--- |
| [src/app/employee.ts](./src/app/employee.ts) | Type and sample data |
| [src/app/app.ts](./src/app/app.ts) | `signal`, `computed`, event handler |
| [src/app/app.html](./src/app/app.html) | Binding, `@if`, `@for`, `@switch` |
| [src/app/employee-card.ts](./src/app/employee-card.ts) | Child component, `input()`, pipes |

Run it:
```bash
cd angular2
npm install --legacy-peer-deps   # once, installs shared libs for all phases
cd phase-1
npm start
```
Open http://localhost:4200.

## 10. Practice
1. Add a `department` dropdown filter.
2. Show a red badge for employees with salary over 600,000.
3. Run `ng g c employee-badge` and use it in the card.

