import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { map, Observable } from 'rxjs';
import { Employee } from './employee';
import { API_BASE_URL } from './tokens';

// Service = class with business / data logic, shared by components.
// React: custom hook / API module.   Vue: composable.   AngularJS: .service / .factory
@Injectable({ providedIn: 'root' }) // 'root' = one instance for the app
export class EmployeeService {
  // inject() = ask Angular for a dependency (DI). No `new` needed.
  // Old style: constructor(private http: HttpClient) {}   <- you will see this a lot
  private readonly http = inject(HttpClient);
  private readonly baseUrl = inject(API_BASE_URL);

  // HttpClient returns an Observable. It is LAZY: no request until someone subscribes
  // (with `| async`, `subscribe`, or `toSignal`).
  // AngularJS $http returned a Promise and started right away.
  getAll(): Observable<Employee[]> {
    return this.http.get<Employee[]>(`${this.baseUrl}/employees.json`);
  }

  // Compose with RxJS operators. map() changes the value in the stream.
  search(keyword: string): Observable<Employee[]> {
    const k = keyword.trim().toLowerCase();
    return this.getAll().pipe(
      map((list) =>
        list.filter((e) => e.nameEn.toLowerCase().includes(k) || e.nameJp.includes(k)),
      ),
    );
  }

  // A URL that does not exist, to see error handling.
  getBroken(): Observable<Employee[]> {
    return this.http.get<Employee[]>(`${this.baseUrl}/missing.json`);
  }
}
