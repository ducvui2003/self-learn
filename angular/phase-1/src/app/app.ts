import { Component, computed, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { EMPLOYEES } from './employee';
import { EmployeeCard } from './employee-card';

@Component({
  selector: 'app-root',
  imports: [FormsModule, EmployeeCard],
  templateUrl: './app.html',
  styleUrl: './app.css',
})
export class App {
  // signal() = reactive state. React: useState. Vue: ref.
  protected readonly employees = signal(EMPLOYEES);
  protected readonly keyword = signal('');
  protected readonly showInactive = signal(true);
  protected readonly clicks = signal(0);

  // computed() = derived value. React: useMemo. Vue: computed.
  protected readonly filtered = computed(() => {
    const k = this.keyword().toLowerCase();
    return this.employees().filter(
      (e) =>
        (this.showInactive() || e.active) &&
        (e.nameEn.toLowerCase().includes(k) || e.nameJp.includes(k)),
    );
  });

  // Event handler. Used with (click)="..." in the template.
  protected increment(): void {
    this.clicks.update((n) => n + 1);
  }
}
