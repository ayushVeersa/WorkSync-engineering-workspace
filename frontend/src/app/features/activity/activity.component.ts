import { Component, OnInit, signal, inject, ChangeDetectionStrategy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivityService } from '../../core/services/activity.service';
import { ActivityLogResponse } from '../../core/models/activity.model';
import { SvgIconComponent } from '../../shared/components/svg-icon/svg-icon.component';
import { EmptyStateComponent } from '../../shared/components/empty-state/empty-state.component';

@Component({
  selector: 'app-activity',
  standalone: true,
  imports: [CommonModule, FormsModule, SvgIconComponent, EmptyStateComponent],
  templateUrl: './activity.component.html',
  styleUrl: './activity.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ActivityComponent implements OnInit {
  private activityService = inject(ActivityService);

  loading = signal<boolean>(true);
  activities = signal<ActivityLogResponse[]>([]);

  selectedAction = signal<string>('');
  selectedEntity = signal<string>('');

  ngOnInit() {
    this.loadActivities();
  }

  loadActivities() {
    this.loading.set(true);
    const filters: any = {};
    if (this.selectedAction()) filters.action = this.selectedAction();
    if (this.selectedEntity()) filters.entity_type = this.selectedEntity();

    this.activityService.getActivities(filters).subscribe({
      next: (logs) => {
        this.activities.set(logs);
        this.loading.set(false);
      },
      error: () => this.loading.set(false),
    });
  }

  onFilterChange() {
    this.loadActivities();
  }

  formatActionText(log: ActivityLogResponse): string {
    const actor = log.actor_name || 'System';
    switch (log.action) {
      case 'TASK_CREATED':
        return `${actor} created task #${log.entity_id}`;
      case 'TASK_STATUS_CHANGED':
        return `${actor} changed task #${log.entity_id} status (${log.metadata?.['old_status'] || ''} → ${log.metadata?.['new_status'] || ''})`;
      case 'TASK_PRIORITY_CHANGED':
        return `${actor} updated task #${log.entity_id} priority to ${log.metadata?.['new_priority'] || ''}`;
      case 'TASK_ASSIGNED':
        return `${actor} updated assignment for task #${log.entity_id}`;
      case 'TASK_DELETED':
        return `${actor} deleted task #${log.entity_id}`;
      case 'GITHUB_PR_OPENED':
        return `${actor} opened Pull Request #${log.metadata?.['pr_number'] || ''} for task #${log.entity_id}`;
      case 'GITHUB_PR_MERGED':
        return `${actor} merged Pull Request #${log.metadata?.['pr_number'] || ''} for task #${log.entity_id}`;
      default:
        return `${actor} performed ${log.action} on ${log.entity_type} #${log.entity_id}`;
    }
  }
}
