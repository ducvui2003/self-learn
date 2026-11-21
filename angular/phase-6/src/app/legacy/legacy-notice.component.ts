import { Component, Input } from '@angular/core';
import { ExpenseStore } from '../core/expense.store';

// LEGACY STYLE EXAMPLE (Angular v8–v16) — kept here so you can read old Japan codebases.
// Compare with modern style:
//   standalone: false          -> declared inside an @NgModule (legacy-notice.module.ts)
//   *ngIf / *ngFor             -> old structural directives (needs CommonModule in the NgModule)
//   @Input()                   -> old decorator input (modern: input())
//   constructor(private ...)   -> old DI (modern: inject())
@Component({
  selector: 'app-legacy-notice',
  standalone: false,
  template: `
    <aside class="legacy">
      <strong>{{ title }}</strong>
      <p *ngIf="store.pendingCount() > 0; else allDone">
        You have {{ store.pendingCount() }} pending claim(s) (未承認あり).
      </p>
      <ng-template #allDone>
        <p>All claims handled! (すべて処理済み)</p>
      </ng-template>
      <ul>
        <li *ngFor="let rule of rules">{{ rule }}</li>
      </ul>
    </aside>
  `,
  styles: `.legacy { background: #fff8e1; border: 1px dashed #c8a200; padding: 10px; margin-top: 16px; }`,
})
export class LegacyNoticeComponent {
  @Input() title = 'Legacy NgModule Notice (旧スタイルの例)';
  rules = ['Submit receipts by the 25th (領収書は25日まで)', 'Manager approval required (上長承認必須)'];

  // Old style DI: constructor parameter
  constructor(public store: ExpenseStore) {}
}
