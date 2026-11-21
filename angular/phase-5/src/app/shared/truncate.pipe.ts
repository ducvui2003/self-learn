import { Pipe, PipeTransform } from '@angular/core';

// Pipe with an argument: {{ text | truncate: 30 }}
@Pipe({ name: 'truncate' })
export class TruncatePipe implements PipeTransform {
  transform(text: string, max = 20): string {
    return text.length > max ? text.slice(0, max) + '…' : text;
  }
}
