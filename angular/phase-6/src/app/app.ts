import { CurrencyPipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, inject, OnInit } from '@angular/core';
import { ExpenseStore } from './core/expense.store';
import { ExpenseChart } from './features/expenses/expense-chart';
import { ExpenseList } from './features/expenses/expense-list';
import { LegacyNoticeModule } from './legacy/legacy-notice.module';

@Component({
  selector: 'app-root',
  // Standalone components can still import a legacy NgModule!
  imports: [CurrencyPipe, ExpenseList, ExpenseChart, LegacyNoticeModule],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './app.html',
  styleUrl: './app.css',
})
export class App implements OnInit {
  protected readonly store = inject(ExpenseStore);

  ngOnInit(): void {
    this.store.load();
  }
}
