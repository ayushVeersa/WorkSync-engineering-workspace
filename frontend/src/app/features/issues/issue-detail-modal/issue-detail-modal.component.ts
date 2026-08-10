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
  templateUrl: './issue-detail-modal.component.html',
  styleUrl: './issue-detail-modal.component.scss' 
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
