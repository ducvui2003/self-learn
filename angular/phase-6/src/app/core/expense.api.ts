import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { Expense } from './expense.model';

// API layer: only talks to HTTP. No state here.
@Injectable({ providedIn: 'root' })
export class ExpenseApi {
  private readonly http = inject(HttpClient);

  getAll(): Observable<Expense[]> {
    return this.http.get<Expense[]>('/data/expenses.json');
  }
}
