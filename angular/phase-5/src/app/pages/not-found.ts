import { ChangeDetectionStrategy, Component } from '@angular/core';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-not-found',
  imports: [RouterLink],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <h2>404 — Page not found (ページが見つかりません)</h2>
    <a routerLink="/employees">Go to the list</a>
  `,
})
export class NotFound {}
