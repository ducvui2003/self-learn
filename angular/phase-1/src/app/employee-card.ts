import { Component, input } from '@angular/core';
import { CurrencyPipe, DatePipe, UpperCasePipe } from '@angular/common';
import { Employee } from './employee';

// A small child component.
// React: function EmployeeCard({ employee }) {...}
// Vue:   <EmployeeCard :employee="e" />
@Component({
  selector: 'app-employee-card',
  // Standalone: we list what the template needs here (no NgModule).
  imports: [CurrencyPipe, DatePipe, UpperCasePipe],
  template: `
    <div class="card" [class.inactive]="!employee().active">
      <h3>{{ employee().nameJp }} / {{ employee().nameEn | uppercase }}</h3>
      <p>Department (部署): {{ employee().department }}</p>
      <!-- Pipes format data in the template. AngularJS: filters -->
      <p>Salary (給与): {{ employee().salary | currency: 'JPY' : 'symbol' : '1.0-0' }}</p>
      <p>Joined (入社日): {{ employee().joinedAt | date: 'yyyy/MM/dd' }}</p>
    </div>
  `,
  styles: `
    .card { border: 1px solid #ccc; border-radius: 8px; padding: 8px 16px; margin: 8px 0; }
    .inactive { opacity: 0.5; background: #eee; }
  `,
})
export class EmployeeCard {
  // input() = a prop. It is a signal, so we read it with ().
  // React: props.employee   Vue: defineProps()
  employee = input.required<Employee>();
}
