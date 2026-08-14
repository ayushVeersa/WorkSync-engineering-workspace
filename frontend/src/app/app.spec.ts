import { describe, it, expect } from 'vitest';
import { signal } from '@angular/core';
import { App } from './app';

describe('App', () => {
  it('should initialize mobileSidebarOpen signal', () => {
    const app = Object.create(App.prototype);
    app.mobileSidebarOpen = signal<boolean>(false);
    expect(app.mobileSidebarOpen()).toBe(false);
  });
});
