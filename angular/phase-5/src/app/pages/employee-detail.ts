import { ChangeDetectionStrategy, Component, input } from '@angular/core';
import { RouterLink } from '@angular/router';
import { Employee } from '../employee';
import { SalaryJpPipe } from '../shared/salary-jp.pipe';
import { TruncatePipe } from '../shared/truncate.pipe';

@Component({
  selector: 'app-employee-detail',
  imports: [RouterLink, SalaryJpPipe, TruncatePipe],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <a routerLink="/employees">‹ Back to list (一覧へ)</a>
    <h2>{{ employee().nameJp }} / {{ employee().nameEn }}</h2>
    <p>ID from the URL: {{ id() }}</p>
    <p>Department: {{ employee().department }}</p>
    <p>Salary: {{ employee().salary | salaryJp }}</p>
    <p>Notes: {{ employee().notes | truncate: 30 }}</p>
  `,
})
export class EmployeeDetail {
  // Route param :id  -> input
  readonly id = input.required<string>();
  // Resolver data `employee` -> input. It is ready when the page opens (no loading state).
  readonly employee = input.required<Employee>();
}
