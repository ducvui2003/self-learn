import { HttpErrorResponse, HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { catchError, finalize, throwError } from 'rxjs';
import { LogService } from './log.service';

// Functional interceptors (new style). They run in order for every request.
// AngularJS: $httpProvider.interceptors.push(...)   React: axios.interceptors

// 1) Request: add a header (for example a login token).
export const authInterceptor: HttpInterceptorFn = (req, next) => {
  // Requests are immutable. Use clone() to change them.
  const authReq = req.clone({ setHeaders: { Authorization: 'Bearer demo-token' } });
  return next(authReq);
};

// 2) Request + response: log URL and time.
export const loggingInterceptor: HttpInterceptorFn = (req, next) => {
  const log = inject(LogService); // inject() works inside an interceptor
  const start = Date.now();
  log.add(`→ ${req.method} ${req.url}`);
  return next(req).pipe(
    // finalize runs on success, error, or cancel.
    finalize(() => log.add(`← ${req.url} (${Date.now() - start} ms)`)),
  );
};

// 3) Error: one place to handle all HTTP errors.
export const errorInterceptor: HttpInterceptorFn = (req, next) => {
  const log = inject(LogService);
  return next(req).pipe(
    catchError((err: HttpErrorResponse) => {
      const message =
        err.status === 401 ? 'Please log in again (401)'
        : err.status === 404 ? 'Not found (404)'
        : err.status === 0 ? 'Network error'
        : `Server error (${err.status})`;
      log.add(`✖ ${message}`);
      // Re-throw so the caller can also react.
      return throwError(() => new Error(message));
    }),
  );
};
