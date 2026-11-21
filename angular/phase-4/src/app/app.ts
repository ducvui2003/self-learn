import { ChangeDetectionStrategy, Component, signal } from '@angular/core';
import { EmployeeForm } from './employee-form';
import { EmployeeSearch } from './employee-search';
import { TemplateDrivenForm } from './template-driven-form';

type Tab = 'search' | 'reactive' | 'template';

@Component({
  selector: 'app-root',
  imports: [EmployeeForm, EmployeeSearch, TemplateDrivenForm],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './app.html',
  styleUrl: './app.css',
})
export class App {
  protected readonly tab = signal<Tab>('search');
}
