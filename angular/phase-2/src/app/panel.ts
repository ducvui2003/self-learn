import { ChangeDetectionStrategy, Component, input } from '@angular/core';

// Content projection = pass HTML into a child.
// React: props.children      Vue: <slot />      AngularJS: transclude
@Component({
  selector: 'app-panel',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <section class="panel">
      <header>
        <h2>{{ title() }}</h2>
        <!-- named slot: <ng-content select="[actions]" /> -->
        <ng-content select="[actions]" />
      </header>
      <!-- default slot -->
      <ng-content />
    </section>
  `,
  styles: `
    .panel { border: 1px solid #bbb; border-radius: 8px; padding: 8px 16px; margin: 16px 0; }
    header { display: flex; justify-content: space-between; align-items: center; }
  `,
})
export class Panel {
  title = input('Panel'); // input with a default value (not required)
}
