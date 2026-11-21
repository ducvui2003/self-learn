import { ChangeDetectionStrategy, Component, inject, input } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from '../auth.service';

@Component({
  selector: 'app-login',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <h2>Login (ログイン)</h2>
    <p>This is a fake login. Click the button.</p>
    <button (click)="login()">Login as demo user</button>
  `,
})
export class Login {
  private readonly auth = inject(AuthService);
  private readonly router = inject(Router);

  // ?returnUrl=/admin/edit  -> input. After login, go back to the page the user wanted.
  readonly returnUrl = input<string | undefined>();

  protected login(): void {
    this.auth.login('demo-user');
    this.router.navigateByUrl(this.returnUrl() ?? '/employees');
  }
}
