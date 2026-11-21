import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { LegacyNoticeComponent } from './legacy-notice.component';

// LEGACY NgModule: in Angular v2–v16, every component had to belong to an NgModule.
//   declarations: components owned by this module
//   imports:      other modules this module needs (CommonModule gives *ngIf, *ngFor, pipes)
//   exports:      what other modules/components are allowed to use
@NgModule({
  declarations: [LegacyNoticeComponent],
  imports: [CommonModule],
  exports: [LegacyNoticeComponent],
})
export class LegacyNoticeModule {}
