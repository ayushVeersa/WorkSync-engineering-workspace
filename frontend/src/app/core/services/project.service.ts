import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { ProjectResponse, ProjectCreate, ProjectUpdate, AssignmentResponse } from '../models/project.model';
import { EmployeeResponse } from '../models/employee.model';

@Injectable({
  providedIn: 'root'
})
export class ProjectService {
  private http = inject(HttpClient);

  getProjects(): Observable<ProjectResponse[]> {
    return this.http.get<ProjectResponse[]>('/projects').pipe(
      map(projects => Array.isArray(projects) ? projects : [])
    );
  }

  getProjectById(id: number): Observable<ProjectResponse> {
    return this.http.get<ProjectResponse>(`/projects/${id}`);
  }

  createProject(payload: ProjectCreate): Observable<ProjectResponse> {
    return this.http.post<ProjectResponse>('/projects', payload);
  }

  updateProject(id: number, payload: ProjectUpdate): Observable<ProjectResponse> {
    return this.http.put<ProjectResponse>(`/projects/${id}`, payload);
  }

  deleteProject(id: number): Observable<any> {
    return this.http.delete(`/projects/${id}`);
  }

  getProjectMembers(projectId: number): Observable<EmployeeResponse[]> {
    return this.http.get<EmployeeResponse[]>(`/projects/${projectId}/members`);
  }

  assignMember(projectId: number, employeeId: number): Observable<AssignmentResponse> {
    return this.http.post<AssignmentResponse>(`/projects/${projectId}/members/${employeeId}`, {});
  }

  removeMember(projectId: number, employeeId: number): Observable<AssignmentResponse> {
    return this.http.delete<AssignmentResponse>(`/projects/${projectId}/members/${employeeId}`);
  }

  getEmployeeProjects(employeeId: number): Observable<ProjectResponse[]> {
    return this.http.get<ProjectResponse[]>(`/projects/employees/${employeeId}/projects`);
  }
}
