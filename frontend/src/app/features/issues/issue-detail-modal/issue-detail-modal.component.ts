import { Component, Input, Output, EventEmitter, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { IssueService } from '../../../core/services/issue.service';
import { CommentService } from '../../../core/services/comment.service';
import { AttachmentService } from '../../../core/services/attachment.service';
import { EmployeeService } from '../../../core/services/employee.service';
import { ToastService } from '../../../core/services/toast.service';
import { IssueResponse, IssueStatus, IssuePriority } from '../../../core/models/issue.model';
import { CommentResponse } from '../../../core/models/comment.model';
import { AttachmentResponse } from '../../../core/models/attachment.model';
import { EmployeeResponse } from '../../../core/models/employee.model';
import { StatusBadgeComponent } from '../../../shared/components/status-badge/status-badge.component';
import { SvgIconComponent } from '../../../shared/components/svg-icon/svg-icon.component';

@Component({
  selector: 'app-issue-detail-modal',
  standalone: true,
  imports: [CommonModule, FormsModule, StatusBadgeComponent, SvgIconComponent],
  template: `
    <div class="modal-backdrop" (click)="close.emit()">
      <div class="modal-dialog task-modal" (click)="$event.stopPropagation()">
        <div class="modal-top">
          <div class="task-badge-row">
            <span class="type-tag">{{ issue.issue_type }}</span>
            <span class="task-id">#{{ issue.id }}</span>
          </div>

          <button class="close-btn" (click)="close.emit()">✕</button>
        </div>

        <h2 class="task-title">{{ issue.title }}</h2>

        <!-- Controls Bar -->
        <div class="meta-controls-grid">
          <div class="meta-field">
            <label class="form-label">Status</label>
            <select class="form-select" [ngModel]="issue.status" (ngModelChange)="updateStatus($event)">
              <option [value]="statuses.BACKLOG">BACKLOG</option>
              <option [value]="statuses.TODO">TODO</option>
              <option [value]="statuses.IN_PROGRESS">IN_PROGRESS</option>
              <option [value]="statuses.REVIEW">REVIEW</option>
              <option [value]="statuses.TESTING">TESTING</option>
              <option [value]="statuses.DONE">DONE</option>
            </select>
          </div>

          <div class="meta-field">
            <label class="form-label">Priority</label>
            <select class="form-select" [ngModel]="issue.priority" (ngModelChange)="updatePriority($event)">
              <option [value]="priorities.LOW">LOW</option>
              <option [value]="priorities.MEDIUM">MEDIUM</option>
              <option [value]="priorities.HIGH">HIGH</option>
              <option [value]="priorities.CRITICAL">CRITICAL</option>
            </select>
          </div>

          <div class="meta-field">
            <label class="form-label">Assignee</label>
            <select class="form-select" [ngModel]="issue.assignee_id" (ngModelChange)="updateAssignee($event)">
              <option *ngFor="let emp of employees" [value]="emp.id">
                {{ emp.user.name }}
              </option>
            </select>
          </div>
        </div>

        <div class="section-box">
          <h4>Description</h4>
          <p class="desc-text">{{ issue.description || 'No description provided.' }}</p>
        </div>

        <!-- File Attachments Section -->
        <div class="section-box">
          <div class="section-header">
            <h4>Attachments ({{ attachments.length }})</h4>
            <label class="btn btn-secondary btn-sm upload-label">
              <app-svg-icon name="attachment" [size]="12"></app-svg-icon>
              <span>Upload File</span>
              <input type="file" (change)="onFileSelected($event)" hidden />
            </label>
          </div>

          <div class="attachments-list">
            <div *ngFor="let att of attachments" class="att-item">
              <div class="att-meta">
                <span class="att-name">{{ att.original_name }}</span>
                <span class="att-size">{{ (att.file_size / 1024) | number:'1.0-1' }} KB</span>
              </div>
              <div class="att-actions">
                <a [href]="attachmentService.getFileUrl(att.stored_name)" target="_blank" class="btn btn-secondary btn-sm">
                  Download
                </a>
                <button class="btn btn-danger btn-sm" (click)="deleteAttachment(att.id)">
                  <app-svg-icon name="trash" [size]="12"></app-svg-icon>
                </button>
              </div>
            </div>

            <div *ngIf="attachments.length === 0" class="text-muted text-xs font-italic">
              No attached files.
            </div>
          </div>
        </div>

        <!-- Discussion Comments Thread -->
        <div class="section-box">
          <h4>Comments & Discussion ({{ comments.length }})</h4>

          <div class="comments-stack">
            <div *ngFor="let c of comments" class="comment-bubble">
              <div class="comment-top">
                <span class="author">Employee #{{ c.employee_id }}</span>
                <span class="date">{{ c.created_at | date:'short' }}</span>
              </div>
              <p class="comment-body">{{ c.content }}</p>
            </div>

            <div *ngIf="comments.length === 0" class="text-muted text-xs font-italic">
              No comments posted yet.
            </div>
          </div>

          <div class="add-comment-row">
            <textarea
              rows="2"
              class="form-control"
              placeholder="Add a comment or update..."
              [(ngModel)]="newCommentText"
            ></textarea>
            <button
              class="btn btn-primary btn-sm mt-2"
              [disabled]="!newCommentText.trim()"
              (click)="postComment()"
            >
              Post Comment
            </button>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .task-modal { max-width: 640px; }
    .modal-top { display: flex; justify-content: space-between; align-items: center; }
    .task-badge-row { display: flex; align-items: center; gap: 8px; font-size: 0.775rem; }
    .type-tag { font-weight: 700; color: var(--primary-600); text-transform: uppercase; }
    .task-id { color: var(--text-muted); font-family: var(--font-mono); }
    .close-btn { background: none; border: none; font-size: 1.1rem; cursor: pointer; color: var(--text-muted); }

    .task-title { font-size: 1.15rem; font-weight: 700; margin: 8px 0 16px; }
    .meta-controls-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-bottom: 16px; }
    .meta-field label { font-size: 0.725rem; }

    .section-box { border-top: 1px solid var(--border-color); padding-top: 14px; margin-top: 14px; }
    .section-box h4 { font-size: 0.85rem; font-weight: 700; margin-bottom: 8px; }
    .desc-text { font-size: 0.825rem; color: var(--text-secondary); line-height: 1.45; }

    .section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
    .upload-label { cursor: pointer; }

    .attachments-list { display: flex; flex-direction: column; gap: 6px; }
    .att-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 6px 10px;
      background: var(--bg-subtle);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-sm);
    }
    .att-meta { display: flex; flex-direction: column; }
    .att-name { font-size: 0.8rem; font-weight: 600; }
    .att-size { font-size: 0.7rem; color: var(--text-muted); }
    .att-actions { display: flex; gap: 6px; }

    .comments-stack { display: flex; flex-direction: column; gap: 8px; margin-bottom: 12px; max-height: 180px; overflow-y: auto; }
    .comment-bubble {
      padding: 8px 10px;
      background: var(--bg-subtle);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-sm);
    }
    .comment-top { display: flex; justify-content: space-between; font-size: 0.725rem; margin-bottom: 4px; }
    .author { font-weight: 700; color: var(--primary-600); }
    .date { color: var(--text-muted); }
    .comment-body { font-size: 0.825rem; color: var(--text-primary); margin: 0; }

    .add-comment-row { display: flex; flex-direction: column; align-items: flex-end; }
    .text-xs { font-size: 0.75rem; }
    .font-italic { font-style: italic; }
    .mt-2 { margin-top: 6px; }
  `]
})
export class IssueDetailModalComponent implements OnInit {
  @Input({ required: true }) issue!: IssueResponse;
  @Output() close = new EventEmitter<void>();
  @Output() issueUpdated = new EventEmitter<void>();

  private issueService = inject(IssueService);
  private commentService = inject(CommentService);
  attachmentService = inject(AttachmentService);
  private employeeService = inject(EmployeeService);
  private toast = inject(ToastService);

  statuses = IssueStatus;
  priorities = IssuePriority;

  comments: CommentResponse[] = [];
  attachments: AttachmentResponse[] = [];
  employees: EmployeeResponse[] = [];
  newCommentText = '';

  ngOnInit() {
    this.loadComments();
    this.loadAttachments();
    this.loadEmployees();
  }

  loadComments() {
    this.commentService.getIssueComments(this.issue.id).subscribe(c => this.comments = c);
  }

  loadAttachments() {
    this.attachmentService.getIssueAttachments(this.issue.id).subscribe(a => this.attachments = a);
  }

  loadEmployees() {
    this.employeeService.getEmployees().subscribe(e => this.employees = e);
  }

  updateStatus(newStatus: IssueStatus) {
    this.issueService.updateIssue(this.issue.id, { status: newStatus }).subscribe({
      next: updated => {
        this.issue = updated;
        this.toast.success(`Status updated to ${newStatus}`);
        this.issueUpdated.emit();
      }
    });
  }

  updatePriority(newPriority: IssuePriority) {
    this.issueService.updateIssue(this.issue.id, { priority: newPriority }).subscribe({
      next: updated => {
        this.issue = updated;
        this.toast.success(`Priority updated to ${newPriority}`);
        this.issueUpdated.emit();
      }
    });
  }

  updateAssignee(employeeId: any) {
    this.issueService.updateIssue(this.issue.id, { assignee_id: Number(employeeId) }).subscribe({
      next: updated => {
        this.issue = updated;
        this.toast.success('Assignee updated');
        this.issueUpdated.emit();
      }
    });
  }

  postComment() {
    if (!this.newCommentText.trim()) return;

    this.commentService.createComment(this.issue.id, { content: this.newCommentText.trim() }).subscribe({
      next: () => {
        this.toast.success('Comment posted');
        this.newCommentText = '';
        this.loadComments();
      }
    });
  }

  onFileSelected(event: any) {
    const file = event.target.files[0];
    if (!file) return;

    this.attachmentService.uploadAttachment(this.issue.id, file).subscribe({
      next: () => {
        this.toast.success('File uploaded!');
        this.loadAttachments();
      }
    });
  }

  deleteAttachment(attId: number) {
    this.attachmentService.deleteAttachment(attId).subscribe({
      next: () => {
        this.toast.info('Attachment deleted.');
        this.loadAttachments();
      }
    });
  }
}
