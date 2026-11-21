import { JsonPipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, inject, signal } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { FormBuilder, FormControl, ReactiveFormsModule, Validators } from '@angular/forms';
import { DEPARTMENTS } from './employee';
import { engineerNeedsSkill, katakanaValidator, notFutureDate, uniqueCodeValidator } from './validators';

// REACTIVE form: the form is built in TypeScript. Best for big, real forms. Easy to test.
// React: react-hook-form / formik     Vue: vee-validate     AngularJS: no direct match
@Component({
  selector: 'app-employee-form',
  imports: [ReactiveFormsModule, JsonPipe],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <!-- Read the form status as a signal. The screen re-renders when it changes
         (needed for async validators, because no DOM event happens then). -->
    @let status = formStatus();

    <form [formGroup]="form" (ngSubmit)="submit()" novalidate>
      <p>
        <label>Code (社員番号):
          <input formControlName="code" placeholder="E0003" />
        </label>
        @if (c.code.pending) { <small>Checking... (確認中)</small> }
        @if (c.code.invalid && c.code.touched) {
          <small class="error">
            @if (c.code.hasError('required')) { Required. }
            @if (c.code.hasError('pattern')) { Format: E + 4 digits. }
            @if (c.code.hasError('codeTaken')) { This code is already used (使用済み). }
          </small>
        }
      </p>

      <p>
        <label>Name (氏名): <input formControlName="nameJp" /></label>
        @if (c.nameJp.invalid && c.nameJp.touched) { <small class="error">Required.</small> }
      </p>

      <p>
        <label>Furigana (フリガナ): <input formControlName="kana" placeholder="ヤマダ タロウ" /></label>
        @if (c.kana.invalid && c.kana.touched) {
          <small class="error">
            @if (c.kana.hasError('required')) { Required. }
            @if (c.kana.hasError('katakana')) { Use full-width katakana only (全角カタカナ). }
          </small>
        }
      </p>

      <p>
        <label>Email: <input formControlName="email" type="email" /></label>
        @if (c.email.invalid && c.email.touched) { <small class="error">Enter a valid email.</small> }
      </p>

      <p>
        <label>Department (部署):
          <select formControlName="department">
            <option value="">-- select --</option>
            @for (d of departments; track d) { <option [value]="d">{{ d }}</option> }
          </select>
        </label>
        @if (c.department.invalid && c.department.touched) { <small class="error">Required.</small> }
      </p>

      <p>
        <label>Salary (給与, yen): <input formControlName="salary" type="number" /></label>
        @if (c.salary.invalid && c.salary.touched) { <small class="error">Min 200,000.</small> }
      </p>

      <p>
        <label>Joined (入社日): <input formControlName="joinedAt" type="date" /></label>
        @if (c.joinedAt.invalid && c.joinedAt.touched) {
          <small class="error">Required, and not in the future.</small>
        }
      </p>

      <!-- FormArray: a list of controls (add / remove rows) -->
      <fieldset>
        <legend>Skills (スキル)</legend>
        @for (skill of c.skills.controls; track $index) {
          <div>
            <input [formControl]="skill" placeholder="e.g. Angular" />
            <button type="button" (click)="removeSkill($index)">✕</button>
          </div>
        }
        <button type="button" (click)="addSkill()">+ Add skill</button>
      </fieldset>

      <!-- group level error (cross-field) -->
      @if (form.hasError('skillRequired')) {
        <p class="error">Engineering needs at least 1 skill.</p>
      }

      <button type="submit" [disabled]="status === 'INVALID'">Register (登録)</button>
      <button type="button" (click)="form.reset()">Reset</button>
      <small>Form status: {{ status }}</small>
    </form>

    @if (saved(); as s) {
      <h3>Saved value (getRawValue)</h3>
      <pre>{{ s | json }}</pre>
    }
  `,
  styles: `.error { color: #c00; } fieldset { margin: 8px 0; }`,
})
export class EmployeeForm {
  private readonly fb = inject(FormBuilder);
  protected readonly departments = DEPARTMENTS;

  // fb.nonNullable = controls reset to their initial value, not null. Types stay simple (string, not string|null).
  protected readonly form = this.fb.nonNullable.group(
    {
      code: ['', {
        validators: [Validators.required, Validators.pattern(/^E\d{4}$/)],
        asyncValidators: [uniqueCodeValidator()], // runs only if sync validators pass
      }],
      nameJp: ['', Validators.required],
      kana: ['', [Validators.required, katakanaValidator]],
      email: ['', [Validators.required, Validators.email]],
      department: ['', Validators.required],
      salary: [300000, [Validators.required, Validators.min(200000)]],
      joinedAt: ['', [Validators.required, notFutureDate]],
      skills: this.fb.array<FormControl<string>>([]),
    },
    { validators: [engineerNeedsSkill] }, // group-level (cross-field) validator
  );

  // Short name for the template. Typed: c.code is FormControl<string>.
  protected readonly c = this.form.controls;

  protected readonly formStatus = toSignal(this.form.statusChanges, { initialValue: this.form.status });
  protected readonly saved = signal<unknown>(null);

  protected addSkill(): void {
    this.c.skills.push(this.fb.nonNullable.control('', Validators.required));
  }

  protected removeSkill(i: number): void {
    this.c.skills.removeAt(i);
  }

  protected submit(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched(); // show all errors
      return;
    }
    this.saved.set(this.form.getRawValue());
  }
}
