import { ChangeDetectionStrategy, Component, input, model, output } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { LeaveRequest } from './request';

// Child component. Shows 3 ways to talk to the parent:
//   input()  : parent -> child   (React: props)
//   output() : child -> parent   (React: callback prop, Vue: emit)
//   model()  : two-way           (Vue: v-model on a component)
@Component({
  selector: 'app-request-card',
  imports: [FormsModule],
  // OnPush: re-render only when an input changes or a signal used here changes.
  // Best practice for big apps (and needed to think "signal-first").
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="card" [class]="request().status">
      <strong>{{ request().employeeJp }} / {{ request().employeeEn }}</strong>
      <div>{{ request().type }} — {{ request().days }} day(s)</div>
      <div>Status: {{ request().status }}</div>

      <!-- model(): [(comment)] in parent keeps parent and child in sync -->
      <input [(ngModel)]="comment" placeholder="Comment (コメント)" />

      <button (click)="approve.emit(request().id)" [disabled]="request().status !== 'pending'">
        Approve (承認)
      </button>
      <button (click)="reject.emit(request().id)" [disabled]="request().status !== 'pending'">
        Reject (却下)
      </button>
    </div>
  `,
  styles: `
    .card { border: 1px solid #ccc; border-radius: 8px; padding: 8px 16px; margin: 8px 0; }
    .approved { background: #e6f7e6; }
    .rejected { background: #fde8e8; }
  `,
})
export class RequestCard {
  request = input.required<LeaveRequest>();
  approve = output<number>(); // emits the request id
  reject = output<number>();
  comment = model(''); // writable signal that the parent can bind with [( )]
}
