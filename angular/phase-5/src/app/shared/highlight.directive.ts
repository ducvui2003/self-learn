import { computed, Directive, input, signal } from '@angular/core';

// ATTRIBUTE DIRECTIVE = adds behavior or style to an existing element. No template.
// React: a wrapper component / hook     Vue: custom directive (v-highlight)     AngularJS: directive with restrict: 'A'
// Usage: <li appHighlight>   or   <li appHighlight="#cdf">
@Directive({
  selector: '[appHighlight]',
  host: {
    // host = the element the directive is on
    '(mouseenter)': 'active.set(true)',
    '(mouseleave)': 'active.set(false)',
    '[style.background-color]': 'background()',
  },
})
export class Highlight {
  // The input has the same name as the selector, so the value goes in the attribute.
  readonly color = input('#fff3b0', { alias: 'appHighlight' });
  protected readonly active = signal(false);
  protected readonly background = computed(() => (this.active() ? this.color() : ''));
}
