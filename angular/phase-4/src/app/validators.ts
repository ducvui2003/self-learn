import { AbstractControl, AsyncValidatorFn, FormArray, ValidationErrors, ValidatorFn } from '@angular/forms';
import { map, Observable, timer } from 'rxjs';

// A validator is just a function: (control) => errors object, or null if OK.
// React Hook Form: validate: (v) => ...      Vue (vee-validate): rules      AngularJS: $validators

// 1) Sync, one field: furigana must be full-width katakana (フリガナ). Very common in Japan forms.
export const katakanaValidator: ValidatorFn = (control: AbstractControl): ValidationErrors | null => {
  const v: string = control.value ?? '';
  if (v === '') return null; // empty is OK here. Use Validators.required for that.
  return /^[ァ-ヶー\s　]+$/.test(v) ? null : { katakana: true };
};

// 2) Sync, one field: date must not be in the future.
export const notFutureDate: ValidatorFn = (control) => {
  const v: string = control.value ?? '';
  if (v === '') return null;
  return new Date(v) > new Date() ? { futureDate: true } : null;
};

// 3) Cross-field (put on the GROUP): Engineering needs at least one skill.
export const engineerNeedsSkill: ValidatorFn = (group: AbstractControl): ValidationErrors | null => {
  const department = group.get('department')?.value;
  const skills = group.get('skills') as FormArray | null;
  return department === 'Engineering' && skills?.length === 0 ? { skillRequired: true } : null;
};

// 4) Async: ask the "server" if the code is already used. Here we fake it with a timer.
const TAKEN_CODES = ['E0001', 'E0002', 'E9999'];

export function uniqueCodeValidator(): AsyncValidatorFn {
  return (control: AbstractControl): Observable<ValidationErrors | null> =>
    timer(500).pipe(map(() => (TAKEN_CODES.includes(control.value) ? { codeTaken: true } : null)));
}
