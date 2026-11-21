import { CurrencyPipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { StatusFilter } from '../../core/expense.model';
import { ExpenseStore } from '../../core/expense.store';

@Component({
  selector: 'app-expense-list',
  imports: [CurrencyPipe],
  // OnPush: best practice for performance. Only re-renders when signals/inputs change.
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="filters">
      @for (f of filters; track f) {
        <button (click)="store.setFilter(f)" [class.active]="store.filter() === f">{{ f }}</button>
      }
      <button (click)="store.load()">Reload (再読込)</button>
    </div>

    @if (store.loading()) {
      <p>Loading... (読み込み中)</p>
    } @else if (store.error(); as err) {
      <p class="error">{{ err }}</p>
    } @else {
      <table>
        <thead>
          <tr>
            <th>Employee (社員)</th>
            <th>Category (種別)</th>
            <th>Amount (金額)</th>
            <th>Status</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          <!-- Always track by a stable unique ID (e.id) for fast DOM updates -->
          @for (e of store.filtered(); track e.id) {
            <tr>
              <td>{{ e.employeeJp }} / {{ e.employeeEn }}</td>
              <td>{{ e.category }}</td>
              <td>{{ e.amount | currency: 'JPY' : 'symbol' : '1.0-0' }}</td>
              <td>{{ e.status }}</td>
              <td>
                <button (click)="store.approve(e.id)" [disabled]="e.status === 'approved'">Approve</button>
                <button (click)="store.reject(e.id)" [disabled]="e.status === 'rejected'">Reject</button>
              </td>
            </tr>
          } @empty {
            <tr><td colspan="5">No items (該当なし)</td></tr>
          }
        </tbody>
      </table>
    }
  `,
  styles: `
    .filters { display: flex; gap: 6px; margin-bottom: 10px; }
    .active { font-weight: bold; background: #dde8ff; }
    .error { color: #c00; }
    table { border-collapse: collapse; width: 100%; }
    th, td { border: 1px solid #ccc; padding: 6px 8px; text-align: left; }
  `,
})
export class ExpenseList {
  protected readonly store = inject(ExpenseStore);
  protected readonly filters: StatusFilter[] = ['all', 'pending', 'approved', 'rejected'];
}
