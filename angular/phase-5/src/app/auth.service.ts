import { computed, Injectable, signal } from '@angular/core';

// Very small fake login. Real apps keep a token and call an API.
@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly _user = signal<string | null>(null);
  readonly user = this._user.asReadonly();
  readonly isLoggedIn = computed(() => this._user() !== null);

  login(name: string): void {
    this._user.set(name);
  }

  logout(): void {
    this._user.set(null);
  }
}
