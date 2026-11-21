import { Injectable } from '@angular/core';
import { delay, Observable, of } from 'rxjs';
import { Employee, EMPLOYEES } from './employee';

// Fake API: returns data after a short delay (like a real HTTP call).
@Injectable({ providedIn: 'root' })
export class EmployeeService {
  getAll(): Employee[] {
    return EMPLOYEES;
  }

  getById(id: number): Observable<Employee | undefined> {
    return of(EMPLOYEES.find((e) => e.id === id)).pipe(delay(300));
  }
}
