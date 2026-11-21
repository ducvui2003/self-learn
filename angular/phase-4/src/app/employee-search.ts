import { ChangeDetectionStrategy, Component, computed, inject, linkedSignal, signal } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { FormBuilder, ReactiveFormsModule } from '@angular/forms';
import { debounceTime, startWith } from 'rxjs';
import { CurrencyPipe } from '@angular/common';
import { DEPARTMENTS, Employee, EMPLOYEES } from './employee';

type SortKey = keyof Pick<Employee, 'code' | 'nameEn' | 'department' | 'salary'>;

// Search screen: search form + sortable table + paging. The most common screen in Japan business apps.
@Component({
  selector: 'app-employee-search',
  imports: [ReactiveFormsModule, CurrencyPipe],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <form [formGroup]="form" class="search">
      <input formControlName="keyword" placeholder="Keyword (キーワード)" />
      <select formControlName="department">
        <option value="">All departments (全部署)</option>
        @for (d of departments; track d) { <option [value]="d">{{ d }}</option> }
      </select>
      <button type="button" (click)="form.reset()">Clear (クリア)</button>
    </form>

    <p>{{ total() }} result(s) (件)</p>

    <table>
      <thead>
        <tr>
          <!-- click a header to sort -->
          <th (click)="sortBy('code')">Code {{ arrow('code') }}</th>
          <th>Name</th>
          <th (click)="sortBy('nameEn')">Name (EN) {{ arrow('nameEn') }}</th>
          <th (click)="sortBy('department')">Dept {{ arrow('department') }}</th>
          <th (click)="sortBy('salary')">Salary {{ arrow('salary') }}</th>
        </tr>
      </thead>
      <tbody>
        @for (e of rows(); track e.id) {
          <tr>
            <td>{{ e.code }}</td>
            <td>{{ e.nameJp }}</td>
            <td>{{ e.nameEn }}</td>
            <td>{{ e.department }}</td>
            <td>{{ e.salary | currency: 'JPY' : 'symbol' : '1.0-0' }}</td>
          </tr>
        } @empty {
          <tr><td colspan="5">No data (該当なし)</td></tr>
        }
      </tbody>
    </table>

    <div class="pager">
      <button (click)="page.set(page() - 1)" [disabled]="page() <= 1">‹ Prev</button>
      Page {{ page() }} / {{ totalPages() }}
      <button (click)="page.set(page() + 1)" [disabled]="page() >= totalPages()">Next ›</button>
    </div>
  `,
  styles: `
    .search { display: flex; gap: 8px; }
    table { border-collapse: collapse; width: 100%; margin-top: 8px; }
    th, td { border: 1px solid #ccc; padding: 4px 8px; text-align: left; }
    th { cursor: pointer; background: #f4f4f4; }
    .pager { margin-top: 8px; }
  `,
})
export class EmployeeSearch {
  private readonly fb = inject(FormBuilder);
  protected readonly departments = DEPARTMENTS;
  private readonly pageSize = 5;

  protected readonly form = this.fb.nonNullable.group({ keyword: '', department: '' });

  // Form value stream -> signal. debounceTime: wait until the user stops typing.
  private readonly criteria = toSignal(
    this.form.valueChanges.pipe(debounceTime(300), startWith(this.form.getRawValue())),
    { initialValue: this.form.getRawValue() },
  );

  protected readonly sortKey = signal<SortKey>('code');
  protected readonly sortDir = signal<1 | -1>(1);

  // Pipeline with computed: filter -> sort -> page. Each step is cached.
  private readonly filtered = computed(() => {
    const { keyword = '', department = '' } = this.criteria();
    const k = keyword.trim().toLowerCase();
    return EMPLOYEES.filter(
      (e) =>
        (!department || e.department === department) &&
        (!k || e.nameEn.toLowerCase().includes(k) || e.nameJp.includes(k) || e.code.toLowerCase().includes(k)),
    );
  });

  private readonly sorted = computed(() => {
    const key = this.sortKey();
    const dir = this.sortDir();
    return [...this.filtered()].sort((a, b) => (a[key] > b[key] ? 1 : a[key] < b[key] ? -1 : 0) * dir);
  });

  protected readonly total = computed(() => this.filtered().length);
  protected readonly totalPages = computed(() => Math.max(1, Math.ceil(this.total() / this.pageSize)));

  // linkedSignal: a writable signal that RESETS to 1 when the criteria change.
  protected readonly page = linkedSignal({ source: this.criteria, computation: () => 1 });

  protected readonly rows = computed(() => {
    const start = (this.page() - 1) * this.pageSize;
    return this.sorted().slice(start, start + this.pageSize);
  });

  protected sortBy(key: SortKey): void {
    if (this.sortKey() === key) this.sortDir.update((d) => (d === 1 ? -1 : 1));
    else {
      this.sortKey.set(key);
      this.sortDir.set(1);
    }
  }

  protected arrow(key: SortKey): string {
    return this.sortKey() === key ? (this.sortDir() === 1 ? '▲' : '▼') : '';
  }
}
