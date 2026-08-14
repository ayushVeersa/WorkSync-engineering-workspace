import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import {
  TaskOverviewReport,
  CompletionTrendReport,
  TaskDistributionReport,
  TeamWorkloadReport,
  CycleTimeReport,
} from '../models/reports.model';

@Injectable({
  providedIn: 'root',
})
export class ReportsService {
  private http = inject(HttpClient);

  getOverview(projectId?: number, assigneeId?: number): Observable<TaskOverviewReport> {
    let params = new HttpParams();
    if (projectId) params = params.set('project_id', projectId.toString());
    if (assigneeId) params = params.set('assignee_id', assigneeId.toString());
    return this.http.get<TaskOverviewReport>('/reports/overview', { params });
  }

  getTrends(days: number = 14, projectId?: number): Observable<CompletionTrendReport> {
    let params = new HttpParams().set('days', days.toString());
    if (projectId) params = params.set('project_id', projectId.toString());
    return this.http.get<CompletionTrendReport>('/reports/trends', { params });
  }

  getDistribution(projectId?: number): Observable<TaskDistributionReport> {
    let params = new HttpParams();
    if (projectId) params = params.set('project_id', projectId.toString());
    return this.http.get<TaskDistributionReport>('/reports/distribution', { params });
  }

  getWorkload(departmentId?: number): Observable<TeamWorkloadReport> {
    let params = new HttpParams();
    if (departmentId) params = params.set('department_id', departmentId.toString());
    return this.http.get<TeamWorkloadReport>('/reports/workload', { params });
  }

  getCycleTime(projectId?: number): Observable<CycleTimeReport> {
    let params = new HttpParams();
    if (projectId) params = params.set('project_id', projectId.toString());
    return this.http.get<CycleTimeReport>('/reports/cycle-time', { params });
  }
}
