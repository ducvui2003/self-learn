import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { App } from './app';
import { API_BASE_URL } from './tokens';

describe('App', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [App],
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(), // fake backend for tests
        { provide: API_BASE_URL, useValue: '/data' },
      ],
    }).compileComponents();
  });

  it('should create the app', () => {
    const fixture = TestBed.createComponent(App);
    expect(fixture.componentInstance).toBeTruthy();
  });

  it('should show employees from the API', async () => {
    const fixture = TestBed.createComponent(App);
    const http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
    http.match('/data/employees.json').forEach((r) =>
      r.flush([{ id: 1, nameEn: 'Taro Yamada', nameJp: '山田 太郎', department: 'Sales', salary: 1 }]),
    );
    await fixture.whenStable();
    expect((fixture.nativeElement as HTMLElement).textContent).toContain('Taro Yamada');
  });
});
