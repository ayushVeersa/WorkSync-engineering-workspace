import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { IssueResponse, IssueCreate, IssueUpdate, IssueStatus, IssuePriority } from '../models/issue.model';

@Injectable({
  providedIn: 'root'
})
export class IssueService {
  private http = inject(HttpClient);

  getIssues(
    status?: string,
    priority?: string,
    issueType?: string,
    assigneeId?: number,
    projectId?: number,
    search?: string
  ): Observable<IssueResponse[]> {
    let params = new HttpParams();
    if (status && status !== 'ALL' && status !== 'null') params = params.set('status', status);
    if (priority && priority !== 'ALL' && priority !== 'null') params = params.set('priority', priority);
    if (issueType && issueType !== 'ALL' && issueType !== 'null') params = params.set('issue_type', issueType);
    if (assigneeId) params = params.set('assignee_id', assigneeId.toString());
    if (projectId) params = params.set('project_id', projectId.toString());
    if (search) params = params.set('search', search);

    return this.http.get<IssueResponse[]>('/issues', { params });
  }

  getMyIssues(): Observable<IssueResponse[]> {
    return this.http.get<IssueResponse[]>('/issues/me');
  }

  getProjectIssues(projectId: number): Observable<IssueResponse[]> {
    return this.http.get<IssueResponse[]>(`/issues/project/${projectId}`);
  }

  getIssueById(id: number): Observable<IssueResponse> {
    return this.http.get<IssueResponse>(`/issues/${id}`);
  }

  createIssue(payload: FormData): Observable<IssueResponse> {
    return this.http.post<IssueResponse>('/issues', payload);
  }

  updateIssue(id: number, payload: IssueUpdate): Observable<IssueResponse> {
    return this.http.put<IssueResponse>(`/issues/${id}`, payload);
  }

  deleteIssue(id: number): Observable<any> {
    return this.http.delete(`/issues/${id}`);
  }
}
