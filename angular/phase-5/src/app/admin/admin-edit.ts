import { ChangeDetectionStrategy, Component, computed, signal } from '@angular/core';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-admin-edit',
  imports: [RouterLink],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <h2>Edit notice (お知らせ編集)</h2>
    <textarea rows="4" cols="40" [value]="text()" (input)="text.set($any($event.target).value)"></textarea>
    <p>
      <button (click)="save()" [disabled]="!dirty()">Save (保存)</button>
      @if (dirty()) { <small>Unsaved changes (未保存)</small> }
    </p>
    <!-- Type something, then click this link: the canDeactivate guard asks you. -->
    <a routerLink="/employees">Leave to the list</a>
  `,
})
export class AdminEdit {
  private readonly saved = signal('');
  protected readonly text = signal('');
  // Public: the guard reads it.
  readonly dirty = computed(() => this.text() !== this.saved());

  protected save(): void {
    this.saved.set(this.text());
  }
}
