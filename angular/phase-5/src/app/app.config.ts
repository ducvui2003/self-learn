import { ApplicationConfig, provideBrowserGlobalErrorListeners } from '@angular/core';
import { provideRouter, withComponentInputBinding } from '@angular/router';
import { routes } from './app.routes';

export const appConfig: ApplicationConfig = {
  providers: [
    provideBrowserGlobalErrorListeners(),
    // withComponentInputBinding: route params, query params and resolver data
    // become input() values of the page component. No ActivatedRoute needed.
    provideRouter(routes, withComponentInputBinding()),
  ],
};
