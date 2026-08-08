import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { CommentResponse, CommentCreate, CommentUpdate } from '../models/comment.model';

@Injectable({
  providedIn: 'root'
})
export class CommentService {
  private http = inject(HttpClient);

  getIssueComments(issueId: number): Observable<CommentResponse[]> {
    return this.http.get<CommentResponse[]>(`/comments/issue/${issueId}`);
  }

  createComment(issueId: number, payload: CommentCreate): Observable<CommentResponse> {
    return this.http.post<CommentResponse>(`/comments/issue/${issueId}`, payload);
  }

  updateComment(commentId: number, payload: CommentUpdate): Observable<CommentResponse> {
    return this.http.put<CommentResponse>(`/comments/${commentId}`, payload);
  }

  deleteComment(commentId: number): Observable<any> {
    return this.http.delete(`/comments/${commentId}`);
  }
}
