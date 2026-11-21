import { ChangeDetectionStrategy, Component, computed, effect, signal } from '@angular/core';
import { LifecycleDemo } from './lifecycle-demo';
import { Panel } from './panel';
import { RequestCard } from './request-card';
import { LeaveRequest, REQUESTS, Status } from './request';

@Component({
  selector: 'app-root',
  imports: [Panel, RequestCard, LifecycleDemo],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './app.html',
  styleUrl: './app.css',
})
export class App {
  // --- signal: state ---
  protected readonly requests = signal<LeaveRequest[]>(REQUESTS);
  protected readonly showDemo = signal(false);
  protected readonly demoValue = signal(1);

  // --- computed: derived state (cached, updates only when needed) ---
  protected readonly pendingCount = computed(
    () => this.requests().filter((r) => r.status === 'pending').length,
  );
  protected readonly approvedDays = computed(() =>
    this.requests()
      .filter((r) => r.status === 'approved')
      .reduce((sum, r) => sum + r.days, 0),
  );

  constructor() {
    // --- effect: side effect when signals change (logging, saving...) ---
    // Do NOT use effect to set other signals. Use computed instead.
    effect(() => console.log('Pending requests:', this.pendingCount()));
  }

  // Child -> parent: handlers for output() events.
  protected approve(id: number): void {
    this.setStatus(id, 'approved');
  }
  protected reject(id: number): void {
    this.setStatus(id, 'rejected');
  }

  // Parent <- child: model() two-way. Receives the new comment text.
  protected setComment(id: number, comment: string): void {
    this.requests.update((list) => list.map((r) => (r.id === id ? { ...r, comment } : r)));
  }

  protected toggleDemo(): void {
    this.showDemo.update((v) => !v);
  }
  protected bumpDemo(): void {
    this.demoValue.update((n) => n + 1);
  }

  // Immutable update: create a NEW array/object. Needed for OnPush + signals.
  private setStatus(id: number, status: Status): void {
    this.requests.update((list) => list.map((r) => (r.id === id ? { ...r, status } : r)));
  }
}
