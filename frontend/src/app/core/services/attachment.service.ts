import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { AttachmentResponse } from '../models/attachment.model';

@Injectable({
  providedIn: 'root'
})
export class AttachmentService {
  private http = inject(HttpClient);

  getIssueAttachments(issueId: number): Observable<AttachmentResponse[]> {
    return this.http.get<AttachmentResponse[]>(`/attachments/issue/${issueId}`);
  }

  uploadAttachment(issueId: number, file: File): Observable<AttachmentResponse> {
    const formData = new FormData();
    formData.append('file', file);
    return this.http.post<AttachmentResponse>(`/attachments/issue/${issueId}`, formData);
  }

  deleteAttachment(attachmentId: number): Observable<any> {
    return this.http.delete(`/attachments/${attachmentId}`);
  }

  getFileUrl(storedName: string): string {
    return `/uploads/${storedName}`;
  }
}
