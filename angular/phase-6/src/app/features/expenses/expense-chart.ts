import { CurrencyPipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { ExpenseStore } from '../../core/expense.store';

// Imagine this is a heavy chart component (e.g. Chart.js / ECharts).
// Because App wraps it in `@defer (on interaction)`, Angular puts this file
// in a separate lazy JS chunk and downloads it only when the user clicks!
@Component({
  selector: 'app-expense-chart',
  imports: [CurrencyPipe],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="chart">
      <h3>Category Breakdown (種別ごとの合計)</h3>
      @for (row of store.byCategory(); track row.category) {
        <div class="bar-row">
          <span class="label">{{ row.category }}</span>
          <span class="bar" [style.width.px]="row.total / 250"></span>
          <span>{{ row.total | currency: 'JPY' : 'symbol' : '1.0-0' }}</span>
        </div>
      }
    </div>
  `,
  styles: `
    .chart { border: 1px solid #bbb; border-radius: 6px; padding: 12px; margin-top: 12px; }
    .bar-row { display: flex; align-items: center; gap: 8px; margin: 6px 0; }
    .label { width: 160px; }
    .bar { display: inline-block; height: 14px; background: #4a7bd0; }
  `,
})
export class ExpenseChart {
  protected readonly store = inject(ExpenseStore);
}
