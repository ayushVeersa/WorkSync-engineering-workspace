import {
  Component,
  OnInit,
  signal,
  computed,
  inject,
  ChangeDetectionStrategy,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MyWorkService } from '../../core/services/my-work.service';
import { ProjectService } from '../../core/services/project.service';
import { ToastService } from '../../core/services/toast.service';
import { MyWorkResponse, WorkSummary } from '../../core/models/my-work.model';
import { IssueResponse, IssueStatus, IssuePriority } from '../../core/models/issue.model';
import { ProjectResponse } from '../../core/models/project.model';
import { StatusBadgeComponent } from '../../shared/components/status-badge/status-badge.component';
import { SvgIconComponent } from '../../shared/components/svg-icon/svg-icon.component';
import { EmptyStateComponent } from '../../shared/components/empty-state/empty-state.component';
import { IssueDetailModalComponent } from '../issues/issue-detail-modal/issue-detail-modal.component';

type SectionTab = 'today' | 'upcoming' | 'overdue' | 'completed';

@Component({
  selector: 'app-my-work',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    StatusBadgeComponent,
    SvgIconComponent,
    EmptyStateComponent,
    IssueDetailModalComponent,
  ],
  templateUrl: './my-work.component.html',
  styleUrl: './my-work.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class MyWorkComponent implements OnInit {
  private myWorkService = inject(MyWorkService);
  private projectService = inject(ProjectService);
  private toast = inject(ToastService);

  // State Signals
  loading = signal<boolean>(true);
  error = signal<string | null>(null);

  workData = signal<MyWorkResponse | null>(null);
  projects = signal<ProjectResponse[]>([]);

  // Filter Signals
  selectedStatus = signal<string>('');
  selectedPriority = signal<string>('');
  selectedProjectId = signal<number | null>(null);
  searchQuery = signal<string>('');
  activeTab = signal<SectionTab>('today');

  // Modal State
  selectedIssue = signal<IssueResponse | null>(null);

  // Computed Signals
  summary = computed<WorkSummary>(() => {
    return (
      this.workData()?.summary || {
        assigned: 0,
        in_progress: 0,
        due_soon: 0,
        overdue: 0,
        completed: 0,
      }
    );
  });

  activeTasks = computed<IssueResponse[]>(() => {
    const data = this.workData();
    if (!data) return [];

    switch (this.activeTab()) {
      case 'today':
        return data.today;
      case 'upcoming':
        return data.upcoming;
      case 'overdue':
        return data.overdue;
      case 'completed':
        return data.recently_completed;
      default:
        return data.today;
    }
  });

  ngOnInit() {
    this.loadProjects();
    this.loadWorkData();
  }

  loadProjects() {
    this.projectService.getProjects().subscribe({
      next: (projs) => this.projects.set(projs),
      error: () => {},
    });
  }

  loadWorkData() {
    this.loading.set(true);
    this.error.set(null);

    const filters: any = {};
    if (this.selectedStatus()) filters.status = this.selectedStatus();
    if (this.selectedPriority()) filters.priority = this.selectedPriority();
    if (this.selectedProjectId()) filters.project_id = this.selectedProjectId();
    if (this.searchQuery()) filters.search = this.searchQuery();

    this.myWorkService.getMyWork(filters).subscribe({
      next: (res) => {
        this.workData.set(res);
        this.loading.set(false);
      },
      error: (err) => {
        this.error.set('Unable to load your work. Please try again.');
        this.loading.set(false);
        this.toast.error('Failed to load My Work dataset');
      },
    });
  }

  onFilterChange() {
    this.loadWorkData();
  }

  clearFilters() {
    this.selectedStatus.set('');
    this.selectedPriority.set('');
    this.selectedProjectId.set(null);
    this.searchQuery.set('');
    this.loadWorkData();
  }

  setTab(tab: SectionTab) {
    this.activeTab.set(tab);
  }

  openTaskModal(task: IssueResponse) {
    this.selectedIssue.set(task);
  }

  closeTaskModal() {
    this.selectedIssue.set(null);
  }

  onTaskUpdated() {
    this.loadWorkData();
  }
}
