import {
  afterNextRender,
  ChangeDetectionStrategy,
  Component,
  effect,
  input,
  OnChanges,
  OnDestroy,
  OnInit,
  signal,
  SimpleChanges,
} from '@angular/core';

// Shows the order of lifecycle hooks. Toggle it in the parent with @if
// and watch the log on screen.
//
//  React:  useEffect(() => {...; return cleanup}, [])
//  Vue:    onMounted / onUpdated / onUnmounted
//  AngularJS: $onInit / $onChanges / $onDestroy  (same names!)
@Component({
  selector: 'app-lifecycle-demo',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <p>Input value: <strong>{{ value() }}</strong></p>
    <ol>
      @for (line of log(); track $index) {
        <li>{{ line }}</li>
      }
    </ol>
  `,
})
export class LifecycleDemo implements OnChanges, OnInit, OnDestroy {
  value = input.required<number>();
  protected log = signal<string[]>([]);

  constructor() {
    this.add('constructor');

    // effect(): runs now and again when a signal it reads changes.
    // React: useEffect with deps. Vue: watchEffect.
    effect(() => this.add(`effect: value is ${this.value()}`));

    // Runs once after the first render. DOM is ready here.
    // React: useEffect(..., []) / Vue: onMounted
    afterNextRender(() => this.add('afterNextRender (DOM ready)'));
  }

  // Runs when an input changes (before ngOnInit the first time).
  ngOnChanges(changes: SimpleChanges): void {
    this.add(`ngOnChanges: ${Object.keys(changes).join(', ')}`);
  }

  // Runs once, after the first inputs are set. Good place to load data.
  ngOnInit(): void {
    this.add('ngOnInit');
  }

  // Runs when the component is removed. Clean up timers/subscriptions here.
  ngOnDestroy(): void {
    console.log('LifecycleDemo: ngOnDestroy (cleanup)');
  }

  private add(text: string): void {
    // Delay the write with a microtask: writing a signal inside effect() or
    // the constructor is not allowed by default. This is only for the demo log.
    queueMicrotask(() => this.log.update((l) => [...l, text]));
  }
}
