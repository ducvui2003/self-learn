import { computed, inject, Injectable, signal } from '@angular/core';
import { ExpenseApi } from './expense.api';
import { Expense, ExpenseStatus, StatusFilter } from './expense.model';

// SIGNAL STORE = Service + Signals.
// React: Zustand store.   Vue: Pinia store.   Angular (large apps): NgRx.
// Rules:
//   1. Keep writable signals `private` so components cannot mutate state directly.
//   2. Expose read-only signals and `computed()` selectors.
//   3. Change state only through methods (actions).
@Injectable({ providedIn: 'root' })
export class ExpenseStore {
  private readonly api = inject(ExpenseApi);

  // --- Private state ---
  private readonly _items = signal<Expense[]>([]);
  private readonly _filter = signal<StatusFilter>('all');
  private readonly _loading = signal(false);
  private readonly _error = signal<string | null>(null);

  // --- Public read-only state ---
  readonly items = this._items.asReadonly();
  readonly filter = this._filter.asReadonly();
  readonly loading = this._loading.asReadonly();
  readonly error = this._error.asReadonly();

  // --- Derived state (selectors) ---
  readonly filtered = computed(() => {
    const f = this._filter();
    return f === 'all' ? this._items() : this._items().filter((e) => e.status === f);
  });

  readonly approvedTotal = computed(() =>
    this._items()
      .filter((e) => e.status === 'approved')
      .reduce((sum, e) => sum + e.amount, 0),
  );

  readonly pendingCount = computed(
    () => this._items().filter((e) => e.status === 'pending').length,
  );

  readonly byCategory = computed(() => {
    const map = new Map<string, number>();
    for (const e of this._items()) {
      map.set(e.category, (map.get(e.category) ?? 0) + e.amount);
    }
    return [...map.entries()].map(([category, total]) => ({ category, total }));
  });

  // --- Actions ---
  load(): void {
    this._loading.set(true);
    this._error.set(null);
    this.api.getAll().subscribe({
      next: (list) => {
        this._items.set(list);
        this._loading.set(false);
      },
      error: () => {
        this._error.set('Failed to load expenses (読み込みエラー)');
        this._loading.set(false);
      },
    });
  }

  setFilter(filter: StatusFilter): void {
    this._filter.set(filter);
  }

  approve(id: number): void {
    this.setStatus(id, 'approved');
  }

  reject(id: number): void {
    this.setStatus(id, 'rejected');
  }

  private setStatus(id: number, status: ExpenseStatus): void {
    // Immutable update: create a new array & object so OnPush/signals update cleanly.
    this._items.update((list) => list.map((e) => (e.id === id ? { ...e, status } : e)));
  }
}
