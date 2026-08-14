import { describe, it, expect } from 'vitest';
import { signal } from '@angular/core';
import { MyWorkComponent } from './my-work.component';

describe('MyWorkComponent', () => {
  it('should switch tabs when setTab is called', () => {
    const comp = Object.create(MyWorkComponent.prototype);
    comp.activeTab = signal('today');
    comp.setTab('overdue');
    expect(comp.activeTab()).toBe('overdue');
  });
});
