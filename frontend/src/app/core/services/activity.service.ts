import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { ActivityLogResponse } from '../models/activity.model';

@Injectable({
  providedIn: 'root',
})
export class ActivityService {
  private http = inject(HttpClient);

  getActivities(filters?: {
    actor_id?: number;
    action?: string;
    entity_type?: string;
    entity_id?: number;
    skip?: number;
    limit?: number;
  }): Observable<ActivityLogResponse[]> {
    let params = new HttpParams();

    if (filters) {
      if (filters.actor_id) params = params.set('actor_id', filters.actor_id.toString());
      if (filters.action) params = params.set('action', filters.action);
      if (filters.entity_type) params = params.set('entity_type', filters.entity_type);
      if (filters.entity_id) params = params.set('entity_id', filters.entity_id.toString());
      if (filters.skip !== undefined) params = params.set('skip', filters.skip.toString());
      if (filters.limit !== undefined) params = params.set('limit', filters.limit.toString());
    }

    return this.http.get<ActivityLogResponse[]>('/activity', { params });
  }
}
