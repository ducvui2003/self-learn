import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { App } from './app';

describe('App', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [App],
      providers: [provideHttpClient(), provideHttpClientTesting()],
    }).compileComponents();
  });

  it('renders dashboard, loads data, and displays legacy notice', async () => {
    const fixture = TestBed.createComponent(App);
    const http = TestBed.inject(HttpTestingController);
    fixture.detectChanges(); // triggers ngOnInit -> store.load()

    http.expectOne('/data/expenses.json').flush([
      { id: 1, employeeJp: '山田 太郎', employeeEn: 'Taro Yamada', category: 'Travel', amount: 12000, status: 'pending' },
    ]);
    await fixture.whenStable();

    const text = (fixture.nativeElement as HTMLElement).textContent ?? '';
    expect(text).toContain('Expense Dashboard');
    expect(text).toContain('Taro Yamada');
    expect(text).toContain('1 pending claim'); // from LegacyNoticeComponent
    http.verify();
  });
});
