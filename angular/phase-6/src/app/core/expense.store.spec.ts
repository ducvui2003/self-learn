import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { ExpenseStore } from './expense.store';

describe('ExpenseStore', () => {
  let store: ExpenseStore;
  let http: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting()],
    });
    store = TestBed.inject(ExpenseStore);
    http = TestBed.inject(HttpTestingController);
  });

  afterEach(() => http.verify()); // fails if any unexpected HTTP call was left open

  it('loads items, calculates totals, and approves an item', () => {
    store.load();
    expect(store.loading()).toBe(true);

    http.expectOne('/data/expenses.json').flush([
      { id: 1, employeeJp: '山田', employeeEn: 'Taro', category: 'Travel', amount: 10000, status: 'pending' },
      { id: 2, employeeJp: '鈴木', employeeEn: 'Hanako', category: 'Books', amount: 5000, status: 'approved' },
    ]);

    expect(store.loading()).toBe(false);
    expect(store.approvedTotal()).toBe(5000);
    expect(store.pendingCount()).toBe(1);

    store.approve(1);
    expect(store.approvedTotal()).toBe(15000);
    expect(store.pendingCount()).toBe(0);
  });

  it('filters by status', () => {
    store.load();
    http.expectOne('/data/expenses.json').flush([
      { id: 1, employeeJp: 'A', employeeEn: 'A', category: 'Travel', amount: 1000, status: 'pending' },
      { id: 2, employeeJp: 'B', employeeEn: 'B', category: 'Books', amount: 2000, status: 'approved' },
    ]);

    store.setFilter('approved');
    expect(store.filtered().map((e) => e.id)).toEqual([2]);
  });

  it('sets error message when API fails', () => {
    store.load();
    http.expectOne('/data/expenses.json').flush('Server error', { status: 500, statusText: 'Error' });
    expect(store.loading()).toBe(false);
    expect(store.error()).toContain('Failed to load');
  });
});
