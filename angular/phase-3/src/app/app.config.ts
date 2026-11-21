import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { ApplicationConfig, provideBrowserGlobalErrorListeners } from '@angular/core';
import { authInterceptor, errorInterceptor, loggingInterceptor } from './interceptors';
import { API_BASE_URL } from './tokens';

export const appConfig: ApplicationConfig = {
  providers: [
    provideBrowserGlobalErrorListeners(),
    // Turn on HttpClient. Interceptors run in the order listed.
    provideHttpClient(withInterceptors([authInterceptor, loggingInterceptor, errorInterceptor])),
    // Provide a value for the token. Change it per environment (dev/prod).
    { provide: API_BASE_URL, useValue: '/data' },
  ],
};
