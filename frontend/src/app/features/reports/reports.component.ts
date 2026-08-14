import { Component, OnInit, signal, inject, ChangeDetectionStrategy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ReportsService } from '../../core/services/reports.service';
import { ProjectService } from '../../core/services/project.service';
import {
  TaskOverviewReport,
  CompletionTrendReport,
  TaskDistributionReport,
  TeamWorkloadReport,
  CycleTimeReport,
} from '../../core/models/reports.model';
import { ProjectResponse } from '../../core/models/project.model';
import { SvgIconComponent } from '../../shared/components/svg-icon/svg-icon.component';

@Component({
  selector: 'app-reports',
  standalone: true,
  imports: [CommonModule, FormsModule, SvgIconComponent],
  templateUrl: './reports.component.html',
  styleUrl: './reports.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ReportsComponent implements OnInit {
  private reportsService = inject(ReportsService);
  private projectService = inject(ProjectService);

  loading = signal<boolean>(true);
  projects = signal<ProjectResponse[]>([]);
  selectedProjectId = signal<number | null>(null);

  overview = signal<TaskOverviewReport | null>(null);
  trends = signal<CompletionTrendReport | null>(null);
  distribution = signal<TaskDistributionReport | null>(null);
  workload = signal<TeamWorkloadReport | null>(null);
  cycleTime = signal<CycleTimeReport | null>(null);

  ngOnInit() {
    this.loadProjects();
    this.loadAllReports();
  }

  loadProjects() {
    this.projectService.getProjects().subscribe({
      next: (projs) => this.projects.set(projs),
    });
  }

  loadAllReports() {
    this.loading.set(true);
    const pid = this.selectedProjectId() || undefined;

    this.reportsService.getOverview(pid).subscribe({
      next: (data) => this.overview.set(data),
    });

    this.reportsService.getTrends(14, pid).subscribe({
      next: (data) => this.trends.set(data),
    });

    this.reportsService.getDistribution(pid).subscribe({
      next: (data) => this.distribution.set(data),
    });

    this.reportsService.getWorkload().subscribe({
      next: (data) => this.workload.set(data),
    });

    this.reportsService.getCycleTime(pid).subscribe({
      next: (data) => {
        this.cycleTime.set(data);
        this.loading.set(false);
      },
      error: () => this.loading.set(false),
    });
  }

  onProjectChange() {
    this.loadAllReports();
  }

  getMaxCount(items: { count: number }[] = []): number {
    if (!items.length) return 1;
    return Math.max(...items.map((i) => i.count), 1);
  }
}
