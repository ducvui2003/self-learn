import { ChangeDetectionStrategy, Component } from '@angular/core';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-admin-home',
  imports: [RouterLink],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <h2>Admin (管理画面)</h2>
    <p>You can see this page only after login (authGuard).</p>
    <a routerLink="edit">Edit notice (お知らせ編集)</a>
  `,
})
export class AdminHome {}
