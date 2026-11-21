import { AsyncPipe, CurrencyPipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, inject, signal } from '@angular/core';
import { toObservable, toSignal } from '@angular/core/rxjs-interop';
import { FormsModule } from '@angular/forms';
import { catchError, debounceTime, distinctUntilChanged, of, switchMap } from 'rxjs';
import { EmployeeService } from './employee.service';
import { LogService } from './log.service';

@Component({
  selector: 'app-root',
  imports: [AsyncPipe, CurrencyPipe, FormsModule],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './app.html',
  styleUrl: './app.css',
})
export class App {
  private readonly service = inject(EmployeeService);
  protected readonly log = inject(LogService);

  // --- Style A: Observable + `async` pipe (very common in old projects) ---
  // Do NOT call subscribe() yourself. `| async` subscribes and unsubscribes for you.
  protected readonly employees$ = this.service.getAll();

  // --- Style B: Observable -> Signal with toSignal() (new style) ---
  protected readonly keyword = signal('');
  protected readonly results = toSignal(
    // signal -> Observable
    toObservable(this.keyword).pipe(
      debounceTime(300), // wait until the user stops typing
      distinctUntilChanged(), // ignore same value
      // switchMap: cancel the old request when a new keyword comes.
      // React Query / Vue: similar to a watch that cancels the old fetch.
      switchMap((k) => this.service.search(k)),
    ),
    { initialValue: [] },
  );

  // --- Error handling demo ---
  protected readonly errorMessage = signal('');

  protected loadBroken(): void {
    this.errorMessage.set('');
    // A manual subscribe is OK for one-time actions (button click).
    // The subscription finishes by itself after the response (HttpClient completes).
    this.service
      .getBroken()
      .pipe(
        catchError((e: Error) => {
          this.errorMessage.set(e.message);
          return of([]);
        }),
      )
      .subscribe();
  }
}
