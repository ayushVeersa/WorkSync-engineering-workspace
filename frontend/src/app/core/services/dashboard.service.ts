import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import {
  DashboardSummary,
  MyWorkSummary,
  IssueStatusSummary,
  IssuePrioritySummary,
  ProjectOverview
} from '../models/dashboard.model';

@Injectable({
  providedIn: 'root'
})
export class DashboardService {
  private http = inject(HttpClient);

  getSummary(): Observable<DashboardSummary> {
    return this.http.get<DashboardSummary>('/dashboard/summary');
  }

  getMyWork(): Observable<MyWorkSummary> {
    return this.http.get<MyWorkSummary>('/dashboard/my-work');
  }

  getIssuesByStatus(): Observable<IssueStatusSummary[]> {
    return this.http.get<IssueStatusSummary[]>('/dashboard/issues/status');
  }

  getIssuesByPriority(): Observable<IssuePrioritySummary[]> {
    return this.http.get<IssuePrioritySummary[]>('/dashboard/issues/priority');
  }

  getProjectOverview(): Observable<ProjectOverview[]> {
    return this.http.get<ProjectOverview[]>('/dashboard/projects');
  }
}
