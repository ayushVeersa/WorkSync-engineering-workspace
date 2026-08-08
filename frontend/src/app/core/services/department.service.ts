import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { DepartmentResponse, DepartmentRequest, DepartmentUpdate } from '../models/department.model';

@Injectable({
  providedIn: 'root'
})
export class DepartmentService {
  private http = inject(HttpClient);

  getDepartments(skip = 0, limit = 50): Observable<DepartmentResponse[]> {
    const params = new HttpParams().set('skip', skip).set('limit', limit);
    return this.http.get<DepartmentResponse[]>('/department', { params });
  }

  getDepartmentById(id: number): Observable<DepartmentResponse> {
    return this.http.get<DepartmentResponse>(`/department/${id}`);
  }

  createDepartment(payload: DepartmentRequest): Observable<DepartmentResponse> {
    return this.http.post<DepartmentResponse>('/department', payload);
  }

  updateDepartment(id: number, payload: DepartmentUpdate): Observable<DepartmentResponse> {
    const params = new HttpParams().set('dept_id', id);
    return this.http.put<DepartmentResponse>('/department', payload, { params });
  }

  deleteDepartment(id: number): Observable<any> {
    const params = new HttpParams().set('dept_id', id);
    return this.http.delete('/department', { params });
  }
}
