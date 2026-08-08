import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { EmployeeResponse, EmployeeRegistrationRequest, EmployeeUpdate } from '../models/employee.model';

@Injectable({
  providedIn: 'root'
})
export class EmployeeService {
  private http = inject(HttpClient);

  getEmployees(skip = 0, limit = 50): Observable<EmployeeResponse[]> {
    const params = new HttpParams().set('skip', skip).set('limit', limit);
    return this.http.get<EmployeeResponse[]>('/employees', { params });
  }

  getCurrentEmployee(): Observable<EmployeeResponse> {
    return this.http.get<EmployeeResponse>('/employees/me');
  }

  getEmployeeById(id: number): Observable<EmployeeResponse> {
    return this.http.get<EmployeeResponse>(`/employees/${id}`);
  }

  createEmployee(payload: EmployeeRegistrationRequest): Observable<EmployeeResponse> {
    return this.http.post<EmployeeResponse>('/employees', payload);
  }

  updateEmployee(id: number, payload: EmployeeUpdate): Observable<EmployeeResponse> {
    return this.http.put<EmployeeResponse>(`/employees/${id}`, payload);
  }

  deleteEmployee(id: number): Observable<any> {
    return this.http.delete(`/employees/${id}`);
  }
}
