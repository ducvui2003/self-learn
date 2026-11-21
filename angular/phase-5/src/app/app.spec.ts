import { TestBed } from '@angular/core/testing';
import { provideRouter, Router, withComponentInputBinding } from '@angular/router';
import { RouterTestingHarness } from '@angular/router/testing';
import { routes } from './app.routes';
import { AuthService } from './auth.service';
import { SalaryJpPipe } from './shared/salary-jp.pipe';
import { TruncatePipe } from './shared/truncate.pipe';

describe('pipes', () => {
  it('salaryJp', () => {
    const p = new SalaryJpPipe();
    expect(p.transform(450000)).toBe('45万円');
    expect(p.transform(615000)).toBe('61.5万円');
  });

  it('truncate', () => {
    const p = new TruncatePipe();
    expect(p.transform('abcdef', 3)).toBe('abc…');
    expect(p.transform('abc', 3)).toBe('abc');
  });
});

describe('routing', () => {
  beforeEach(() => {
    TestBed.configureTestingModule({ providers: [provideRouter(routes, withComponentInputBinding())] });
  });

  it('redirects "" to /employees and filters by query param', async () => {
    const harness = await RouterTestingHarness.create();
    await harness.navigateByUrl('/employees?department=HR');
    const text = (harness.routeNativeElement as HTMLElement).textContent;
    expect(text).toContain('Yuki Sato');
    expect(text).not.toContain('Taro Yamada');
  });

  it('resolver loads employee for the detail page', async () => {
    const harness = await RouterTestingHarness.create();
    await harness.navigateByUrl('/employees/2');
    expect((harness.routeNativeElement as HTMLElement).textContent).toContain('Hanako Suzuki');
  });

  it('unknown employee goes to not-found', async () => {
    const harness = await RouterTestingHarness.create();
    await harness.navigateByUrl('/employees/999');
    expect(TestBed.inject(Router).url).toBe('/not-found');
  });

  it('authGuard sends anonymous user to /login with returnUrl', async () => {
    const harness = await RouterTestingHarness.create();
    await harness.navigateByUrl('/admin');
    expect(TestBed.inject(Router).url).toBe('/login?returnUrl=%2Fadmin');
  });

  it('authGuard lets a logged-in user in (lazy route)', async () => {
    TestBed.inject(AuthService).login('test');
    const harness = await RouterTestingHarness.create();
    await harness.navigateByUrl('/admin');
    expect(TestBed.inject(Router).url).toBe('/admin');
  });
});
