import { Pipe, PipeTransform } from '@angular/core';

// CUSTOM PIPE: formats a value in the template. Pure = runs again only when the input changes.
// 450000 -> "45万円"   615000 -> "61.5万円"
// AngularJS: filter     React/Vue: a helper function / formatter
@Pipe({ name: 'salaryJp' })
export class SalaryJpPipe implements PipeTransform {
  transform(yen: number): string {
    const man = Math.round(yen / 1000) / 10; // 1 man = 10,000 yen
    return `${man}万円`;
  }
}
