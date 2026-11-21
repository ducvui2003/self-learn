import { FormArray, FormControl, FormGroup } from '@angular/forms';
import { TestBed } from '@angular/core/testing';
import { App } from './app';
import { engineerNeedsSkill, katakanaValidator, notFutureDate } from './validators';

describe('validators', () => {
  it('katakana: accepts katakana, rejects others', () => {
    expect(katakanaValidator(new FormControl('ヤマダ タロウ'))).toBeNull();
    expect(katakanaValidator(new FormControl('山田'))).toEqual({ katakana: true });
    expect(katakanaValidator(new FormControl(''))).toBeNull();
  });

  it('notFutureDate: rejects future date', () => {
    expect(notFutureDate(new FormControl('2999-01-01'))).toEqual({ futureDate: true });
    expect(notFutureDate(new FormControl('2020-01-01'))).toBeNull();
  });

  it('engineerNeedsSkill: cross-field rule', () => {
    const group = new FormGroup({ department: new FormControl('Engineering'), skills: new FormArray<FormControl>([]) });
    expect(engineerNeedsSkill(group)).toEqual({ skillRequired: true });
    group.controls.skills.push(new FormControl('Angular'));
    expect(engineerNeedsSkill(group)).toBeNull();
  });
});

describe('App', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({ imports: [App] }).compileComponents();
  });

  it('should show the search screen first', async () => {
    const fixture = TestBed.createComponent(App);
    await fixture.whenStable();
    const el = fixture.nativeElement as HTMLElement;
    expect(el.querySelector('h1')?.textContent).toContain('Employee Forms');
    expect(el.querySelectorAll('tbody tr').length).toBe(5); // page size
  });
});
