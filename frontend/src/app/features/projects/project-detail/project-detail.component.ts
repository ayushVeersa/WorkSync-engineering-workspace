import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterModule } from '@angular/router';
import { DragDropModule, CdkDragDrop, moveItemInArray, transferArrayItem } from '@angular/cdk/drag-drop';
import { ProjectService } from '../../../core/services/project.service';
import { IssueService } from '../../../core/services/issue.service';
import { AuthService } from '../../../core/services/auth.service';
import { ToastService } from '../../../core/services/toast.service';
import { ProjectResponse, ProjectStatus } from '../../../core/models/project.model';
import { EmployeeResponse } from '../../../core/models/employee.model';
import { IssueResponse, IssueStatus } from '../../../core/models/issue.model';
import { StatusBadgeComponent } from '../../../shared/components/status-badge/status-badge.component';
import { SvgIconComponent } from '../../../shared/components/svg-icon/svg-icon.component';

@Component({
  selector: 'app-project-detail',
  standalone: true,
  imports: [CommonModule, RouterModule, DragDropModule, StatusBadgeComponent, SvgIconComponent],
  templateUrl: 'project-detail.component.html',
  styleUrl: 'project-detail.component.scss'
})
export class ProjectDetailComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private projectService = inject(ProjectService);
  private issueService = inject(IssueService);
  private toast = inject(ToastService);
  authService = inject(AuthService);

  projectId!: number;
  project = signal<ProjectResponse | null>(null);
  issues = signal<IssueResponse[]>([]);
  members = signal<EmployeeResponse[]>([]);
  statuses = ProjectStatus;

  activeTab = signal<'overview' | 'tasks' | 'kanban' | 'team'>('overview');

  kanbanColumns = signal<{ title: string; status: IssueStatus; issues: IssueResponse[] }[]>([
    { title: 'Backlog', status: IssueStatus.BACKLOG, issues: [] },
    { title: 'To Do', status: IssueStatus.TODO, issues: [] },
    { title: 'In Progress', status: IssueStatus.IN_PROGRESS, issues: [] },
    { title: 'Review', status: IssueStatus.REVIEW, issues: [] },
    { title: 'Testing', status: IssueStatus.TESTING, issues: [] },
    { title: 'Done', status: IssueStatus.DONE, issues: [] }
  ]);

  ngOnInit() {
    this.route.params.subscribe(params => {
      this.projectId = Number(params['id']);
      this.loadProject();
    });
  }

  loadProject() {
    this.projectService.getProjectById(this.projectId).subscribe(p => this.project.set(p));

    this.issueService.getProjectIssues(this.projectId).subscribe(issues => {
      this.issues.set(issues);
      this.distributeKanban(issues);
    });

    this.projectService.getProjectMembers(this.projectId).subscribe(m => this.members.set(m));
  }

  distributeKanban(issues: IssueResponse[]) {
    this.kanbanColumns.update(cols =>
      cols.map(col => ({
        ...col,
        issues: issues.filter(i => i.status === col.status)
      }))
    );
  }

  onDrop(event: CdkDragDrop<IssueResponse[]>, targetStatus: IssueStatus) {
    if (event.previousContainer === event.container) {
      moveItemInArray(event.container.data, event.previousIndex, event.currentIndex);
    } else {
      transferArrayItem(
        event.previousContainer.data,
        event.container.data,
        event.previousIndex,
        event.currentIndex
      );

      const movedTask = event.container.data[event.currentIndex];
      movedTask.status = targetStatus;

      this.issueService.updateIssue(movedTask.id, { status: targetStatus }).subscribe({
        next: updated => {
          this.toast.success(`Task #${updated.id} moved to ${targetStatus}`);
        }
      });
    }
  }

  onStatusChange(event: any) {
    const newStatus = event.target.value as ProjectStatus;
    const proj = this.project();
    if (!proj) return;

    this.projectService.updateProject(proj.id, { status: newStatus }).subscribe(updated => {
      this.project.set(updated);
      this.toast.success(`Project status updated to ${newStatus}`);
    });
  }
}
