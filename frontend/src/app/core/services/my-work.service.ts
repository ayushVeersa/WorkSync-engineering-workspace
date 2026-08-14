import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { MyWorkResponse } from '../models/my-work.model';

@Injectable({
  providedIn: 'root',
})
export class MyWorkService {
  private http = inject(HttpClient);

  getMyWork(filters?: {
    status?: string;
    priority?: string;
    project_id?: number;
    search?: string;
    skip?: number;
    limit?: number;
  }): Observable<MyWorkResponse> {
    let params = new HttpParams();

    if (filters) {
      if (filters.status) params = params.set('status', filters.status);
      if (filters.priority) params = params.set('priority', filters.priority);
      if (filters.project_id) params = params.set('project_id', filters.project_id.toString());
      if (filters.search) params = params.set('search', filters.search);
      if (filters.skip !== undefined) params = params.set('skip', filters.skip.toString());
      if (filters.limit !== undefined) params = params.set('limit', filters.limit.toString());
    }

    return this.http.get<MyWorkResponse>('/me/work', { params });
  }
}
