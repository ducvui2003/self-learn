import { Directive, input, output } from '@angular/core';

// Directive with an output: asks the user, and emits only if they say OK.
// Usage: <button appConfirm message="Delete?" (confirmed)="remove()">
@Directive({
  selector: '[appConfirm]',
  host: { '(click)': 'onClick()' },
})
export class Confirm {
  readonly message = input('Are you sure?');
  readonly confirmed = output<void>();

  protected onClick(): void {
    if (confirm(this.message())) {
      this.confirmed.emit();
    }
  }
}
