import { ChangeDetectionStrategy, Component, computed, inject, input } from '@angular/core';
import { Router, RouterLink } from '@angular/router';
import { DEPARTMENTS } from '../employee';
import { EmployeeService } from '../employee.service';
import { Highlight } from '../shared/highlight.directive';
import { SalaryJpPipe } from '../shared/salary-jp.pipe';

@Component({
  selector: 'app-employee-list',
  imports: [RouterLink, Highlight, SalaryJpPipe],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <h2>Employees (社員一覧)</h2>

    <input [value]="keyword() ?? ''" (input)="search($any($event.target).value)" placeholder="Keyword (キーワード)" />

    <p>
      Department:
      <!-- [routerLink]="[]" = same page. Only the query params change. -->
      <a [routerLink]="[]" [queryParams]="{ department: null }" queryParamsHandling="merge">All</a>
      @for (d of departments; track d) {
        |
        <a [routerLink]="[]" [queryParams]="{ department: d }" queryParamsHandling="merge"
           [class.current]="department() === d">{{ d }}</a>
      }
    </p>

    <ul>
      @for (e of filtered(); track e.id) {
        <!-- appHighlight: custom attribute directive; salaryJp: custom pipe -->
        <li appHighlight>
          <a [routerLink]="['/employees', e.id]">{{ e.nameJp }} / {{ e.nameEn }}</a>
          — {{ e.department }} — {{ e.salary | salaryJp }}
        </li>
      } @empty {
        <li>No result (該当なし)</li>
      }
    </ul>
  `,
  styles: `.current { font-weight: bold; } li { padding: 4px; }`,
})
export class EmployeeList {
  private readonly router = inject(Router);
  protected readonly departments = DEPARTMENTS;
  private readonly all = inject(EmployeeService).getAll();

  // Query params -> input(). URL: /employees?keyword=ya&department=Sales
  // The value is undefined when the param is not in the URL.
  readonly keyword = input<string | undefined>();
  readonly department = input<string | undefined>();

  protected readonly filtered = computed(() => {
    const k = (this.keyword() ?? '').toLowerCase();
    const d = this.department();
    return this.all.filter(
      (e) => (!d || e.department === d) && (!k || e.nameEn.toLowerCase().includes(k) || e.nameJp.includes(k)),
    );
  });

  protected search(value: string): void {
    // The URL is the state: the search can be bookmarked / shared / back button works.
    this.router.navigate([], {
      queryParams: { keyword: value || null },
      queryParamsHandling: 'merge',
      replaceUrl: true,
    });
  }
}
