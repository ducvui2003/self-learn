import { InjectionToken } from '@angular/core';

// InjectionToken = a key for values that are not classes (strings, config...).
// React: Context.   Vue: provide/inject key.   AngularJS: .constant('API_URL', ...)
export const API_BASE_URL = new InjectionToken<string>('API_BASE_URL');
