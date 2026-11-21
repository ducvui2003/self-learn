import { Injectable, signal } from '@angular/core';

// A simple shared service. One instance for the whole app (singleton),
// because of providedIn: 'root'.
// Used by the interceptors to write logs, and by the screen to show them.
@Injectable({ providedIn: 'root' })
export class LogService {
  readonly lines = signal<string[]>([]);

  add(text: string): void {
    this.lines.update((l) => [...l, text]);
  }

  clear(): void {
    this.lines.set([]);
  }
}
