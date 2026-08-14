import { describe, it, expect } from 'vitest';
import { ActivityComponent } from './activity.component';

describe('ActivityComponent', () => {
  it('should format action text for TASK_CREATED', () => {
    const comp = Object.create(ActivityComponent.prototype);
    const text = comp.formatActionText({
      id: 1,
      actor_name: 'Rahul',
      action: 'TASK_CREATED',
      entity_type: 'issue',
      entity_id: 142,
      created_at: '2026-08-13T00:00:00Z',
    });
    expect(text).toContain('Rahul created task #142');
  });

  it('should format action text for GITHUB_PR_MERGED', () => {
    const comp = Object.create(ActivityComponent.prototype);
    const text = comp.formatActionText({
      id: 2,
      actor_name: 'Alice',
      action: 'GITHUB_PR_MERGED',
      entity_type: 'issue',
      entity_id: 142,
      metadata: { pr_number: 381 },
      created_at: '2026-08-13T00:00:00Z',
    });
    expect(text).toContain('Alice merged Pull Request #381 for task #142');
  });
});
