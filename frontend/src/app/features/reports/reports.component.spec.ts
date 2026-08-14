import { describe, it, expect } from 'vitest';
import { ReportsComponent } from './reports.component';

describe('ReportsComponent', () => {
  it('should calculate max count for chart scaling', () => {
    const comp = Object.create(ReportsComponent.prototype);
    const max = comp.getMaxCount([{ count: 5 }, { count: 12 }, { count: 3 }]);
    expect(max).toBe(12);
  });

  it('should return 1 for empty items', () => {
    const comp = Object.create(ReportsComponent.prototype);
    const max = comp.getMaxCount([]);
    expect(max).toBe(1);
  });
});
