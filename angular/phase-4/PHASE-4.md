# Phase 4 — Forms, Validation & Search Screens

Goal: build real forms (template-driven and reactive, typed), write validators, and make a search + table + paging screen.

> Example project: this folder. Run: `cd angular2/phase-4` then `npm start -- --port 4203`.

## 1. Two kinds of forms

| | Template-driven | Reactive |
| :--- | :--- | :--- |
| Where rules live | in the HTML (`required`, `ngModel`) | in TypeScript (`FormGroup`) |
| Import | `FormsModule` | `ReactiveFormsModule` |
| Binding | `[(ngModel)]`, `name="..."` | `[formGroup]`, `formControlName` |
| Best for | small, simple forms | big forms, dynamic fields, tests |
| AngularJS match | yes (`ng-model`, `form.$valid`) | no |
| React / Vue match | — | react-hook-form / vee-validate |

Use **reactive forms** for new work. Read both in old code.

## 2. Reactive form (typed)

| Class | Meaning | React Hook Form idea |
| :--- | :--- | :--- |
| `FormControl<T>` | one field | `register('name')` |
| `FormGroup` | object of controls | the `useForm()` object |
| `FormArray` | list of controls | `useFieldArray` |
| `FormBuilder` | short way to create them | — |

```ts
form = this.fb.nonNullable.group({        // nonNullable: reset() goes back to '' (not null)
  code: ['', [Validators.required]],
  skills: this.fb.array<FormControl<string>>([]),
});
form.controls.code.value   // string  (typed!)
form.getRawValue()         // full typed value
```

Form state (same idea as AngularJS `$valid`, `$dirty`, `$touched`):

| State | AngularJS | Angular |
| :--- | :--- | :--- |
| passes all rules | `$valid` / `$invalid` | `valid` / `invalid` |
| value changed | `$dirty` | `dirty` |
| user left the field | `$touched` | `touched` |
| errors object | `$error` | `errors`, `hasError('required')` |
| async check running | — | `pending` |

## 3. Validation

| Type | Built in / custom | Example |
| :--- | :--- | :--- |
| Built in | `Validators.required`, `minLength`, `min`, `email`, `pattern` | `[Validators.required, Validators.min(200000)]` |
| Custom (one field) | `(control) => errors \| null` | `katakanaValidator` (フリガナ) |
| Cross-field | validator on the **group** | `engineerNeedsSkill` |
| Async | returns an Observable | `uniqueCodeValidator` (check on server) |

```ts
export const katakanaValidator: ValidatorFn = (c) =>
  !c.value || /^[ァ-ヶー\s　]+$/.test(c.value) ? null : { katakana: true };
```
- Return `null` = OK. Return an object = error. The key is the error name.
- Async validators run only after all sync validators pass.
- Show errors only after `touched` (or after submit), not right at the start.
- On submit, if invalid: `form.markAllAsTouched()` to show every error.

## 4. Search screen pattern

| Part | How |
| :--- | :--- |
| Search form | a small reactive form (`keyword`, `department`) |
| Form → signal | `toSignal(form.valueChanges.pipe(debounceTime(300), startWith(initial)))` |
| Filter → sort → page | a chain of `computed()` |
| Reset page when search changes | `linkedSignal({ source: criteria, computation: () => 1 })` |
| Sort | `sortKey` + `sortDir` signals |

React / Vue idea: it is the same as `useMemo` chains, or Vue `computed` chains.

## 5. Common pitfalls
- Forgot `FormsModule` / `ReactiveFormsModule` → "Can't bind to 'ngModel' / 'formGroup'".
- Template-driven: `ngModel` inside a `<form>` needs a `name` attribute.
- Zoneless + `OnPush`: an async validator finishes with no DOM event, so the screen may not update. Read `toSignal(form.statusChanges)` in the template (this example does this).
- `form.value` skips disabled controls. Use `getRawValue()` for everything.
- Without `nonNullable`, `reset()` sets values to `null` and types become `string | null`.
- Mutating a `FormArray` by assigning: use `push()`, `removeAt()`.
- Showing errors immediately: users see red text before they type. Check `touched`.
- Number inputs: `type="number"` with reactive forms gives a number. Without a type you get a string.
- Cross-field rule on one control: it only runs when that control changes. Put it on the group.

## 6. Japan-project tips
- Furigana (フリガナ), full-width katakana, zip code (〒 `123-4567`), phone (`03-1234-5678`) are common validators. Write them once in a shared `validators.ts`.
- Show errors in Japanese from one place (a small `FormError` component or a map `{ required: '必須です' }`).
- Search screens (検索画面) = search form + result table + paging + sort. Keep the "clear" (クリア) button.
- Old projects use `new FormGroup({ ... })` or untyped forms (`FormGroup` without types). Typed forms came in Angular 14. Learn to read both.
- Date input: store as `yyyy-MM-dd` string, convert at the API layer.

## 7. Example: Employee Forms

| File | What it shows |
| :--- | :--- |
| [src/app/validators.ts](./src/app/validators.ts) | custom, cross-field and async validators |
| [src/app/employee-form.ts](./src/app/employee-form.ts) | reactive typed form, `FormArray`, error messages, `statusChanges` signal |
| [src/app/template-driven-form.ts](./src/app/template-driven-form.ts) | `ngModel`, `#ref="ngModel"`, `ngForm` |
| [src/app/employee-search.ts](./src/app/employee-search.ts) | search form → signals, sort, paging, `linkedSignal` |
| [src/app/employee.ts](./src/app/employee.ts) | type + 25 sample rows |
| [src/app/app.spec.ts](./src/app/app.spec.ts) | validator unit tests |

Run it:
```bash
cd angular2
npm install --legacy-peer-deps   # once
cd phase-4
npm start -- --port 4203
```
Try: register code `E0001` (already used), type a kanji name in furigana, choose Engineering without a skill.

## 8. Practice
1. Add a zip code field (`〒123-4567`) with `Validators.pattern`.
2. Add a "password" + "confirm password" cross-field validator.
3. Add a Japanese error message map and show it in one `@for`.
4. Add page size select (5 / 10 / 20) to the search screen.
