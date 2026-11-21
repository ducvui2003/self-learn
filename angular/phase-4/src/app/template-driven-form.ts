import { ChangeDetectionStrategy, Component, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';

// TEMPLATE-DRIVEN form: the template holds the rules. This is the AngularJS way
// (ng-model, ng-required, form.$valid). Good for small forms.
@Component({
  selector: 'app-template-driven-form',
  imports: [FormsModule],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <!-- #f="ngForm": a reference to the form object. AngularJS: <form name="f"> -->
    <form #f="ngForm" (ngSubmit)="submit(f.valid)" novalidate>
      <p>
        <label>Name (氏名):
          <!-- #name="ngModel": a reference to this control's state -->
          <input name="name" [(ngModel)]="model.name" required minlength="2" #name="ngModel" />
        </label>
        @if (name.invalid && (name.touched || f.submitted)) {
          <small class="error">
            @if (name.hasError('required')) { Name is required (必須). }
            @if (name.hasError('minlength')) { At least 2 characters. }
          </small>
        }
      </p>
      <p>
        <label>Email:
          <input name="email" type="email" [(ngModel)]="model.email" required email #email="ngModel" />
        </label>
        @if (email.invalid && (email.touched || f.submitted)) {
          <small class="error">Enter a valid email.</small>
        }
      </p>
      <!-- f.valid / f.dirty / f.touched are like $valid / $dirty / $touched in AngularJS -->
      <button type="submit" [disabled]="f.invalid && f.submitted">Send (送信)</button>
      @if (message()) { <p>{{ message() }}</p> }
    </form>
  `,
  styles: `.error { color: #c00; }`,
})
export class TemplateDrivenForm {
  protected model = { name: '', email: '' };
  protected readonly message = signal('');

  protected submit(valid: boolean | null): void {
    this.message.set(valid ? `Sent: ${this.model.name} <${this.model.email}>` : 'Fix the errors first.');
  }
}
