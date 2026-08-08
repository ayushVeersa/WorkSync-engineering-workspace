import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';
import { EmployeeService } from '../../core/services/employee.service';
import { IssueService } from '../../core/services/issue.service';
import { EmployeeResponse } from '../../core/models/employee.model';
import { IssueResponse } from '../../core/models/issue.model';
import { StatusBadgeComponent } from '../../shared/components/status-badge/status-badge.component';

@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [CommonModule, RouterModule, StatusBadgeComponent],
  template: `
    <div class="profile-page">
      <div class="page-header">
        <div>
          <h2>My Account & Profile</h2>
          <p class="text-muted text-sm">Personal credentials, organization assignment, and active workload</p>
        </div>
      </div>

      <div class="profile-layout-grid">
        <!-- Account Info Panel -->
        <div class="panel content-panel profile-box">
          <div class="avatar-large">
            {{ user()?.name ? user()!.name[0].toUpperCase() : 'U' }}
          </div>

          <h3 class="user-title">{{ user()?.name }}</h3>
          <span class="text-muted text-xs mb-2">{{ user()?.email }}</span>

          <app-status-badge *ngIf="user()?.role" [type]="user()!.role"></app-status-badge>

          <div class="info-list mt-3">
            <div class="info-row">
              <span class="info-lbl">Account ID</span>
              <span class="info-val">#{{ user()?.id }}</span>
            </div>
            <div class="info-row">
              <span class="info-lbl">Designation</span>
              <span class="info-val">{{ employee?.designation || 'Engineer' }}</span>
            </div>
            <div class="info-row">
              <span class="info-lbl">Department</span>
              <span class="info-val">🏢 {{ employee?.department?.name || 'General' }}</span>
            </div>
            <div class="info-row">
              <span class="info-lbl">Age</span>
              <span class="info-val">{{ user()?.age }} years</span>
            </div>
          </div>
        </div>

        <!-- Assigned Tasks Table -->
        <div class="panel content-panel">
          <div class="panel-header">
            <h3>My Assigned Tasks ({{ myIssues.length }})</h3>
            <a routerLink="/issues" class="btn btn-secondary btn-sm">Tasks Board</a>
          </div>

          <div class="table-wrapper">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Task Title</th>
                  <th>Priority</th>
                  <th>Status</th>
                  <th>Updated</th>
                </tr>
              </thead>
              <tbody>
                <tr *ngFor="let issue of myIssues">
                  <td class="font-semibold">{{ issue.title }}</td>
                  <td><app-status-badge [type]="issue.priority"></app-status-badge></td>
                  <td><app-status-badge [type]="issue.status"></app-status-badge></td>
                  <td class="text-muted">{{ issue.updated_at | date:'shortDate' }}</td>
                </tr>

                <tr *ngIf="myIssues.length === 0">
                  <td colspan="4" class="text-center py-3 text-muted">
                    No active tasks assigned.
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .profile-page { display: flex; flex-direction: column; gap: 14px; }
    .page-header h2 { font-size: 1.2rem; font-weight: 700; }
    .text-sm { font-size: 0.8rem; }
    .text-xs { font-size: 0.75rem; }
    .text-muted { color: var(--text-muted); }

    .profile-layout-grid {
      display: grid;
      grid-template-columns: 280px 1fr;
      gap: 14px;
    }

    .content-panel { padding: 16px; }

    .profile-box {
      display: flex;
      flex-direction: column;
      align-items: center;
      text-align: center;
    }

    .avatar-large {
      width: 52px;
      height: 52px;
      background: var(--primary-dark);
      color: #FFFFFF;
      font-size: 1.4rem;
      font-weight: 700;
      border-radius: var(--radius-sm);
      display: flex;
      align-items: center;
      justify-content: center;
      margin-bottom: 10px;
    }

    .user-title { font-size: 1.1rem; font-weight: 700; margin: 0; }
    .mb-2 { margin-bottom: 8px; }
    .mt-3 { margin-top: 12px; }

    .info-list { width: 100%; border-top: 1px solid var(--border-color); padding-top: 10px; display: flex; flex-direction: column; gap: 8px; }
    .info-row { display: flex; justify-content: space-between; font-size: 0.8rem; }
    .info-lbl { color: var(--text-muted); }
    .info-val { font-weight: 600; color: var(--text-primary); }

    .panel-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
    .panel-header h3 { font-size: 0.9rem; font-weight: 600; margin: 0; }

    @media (max-width: 768px) {
      .profile-layout-grid { grid-template-columns: 1fr; }
    }
  `]
})
export class ProfileComponent implements OnInit {
  private authService = inject(AuthService);
  private employeeService = inject(EmployeeService);
  private issueService = inject(IssueService);

  user = this.authService.currentUser;
  employee: EmployeeResponse | null = null;
  myIssues: IssueResponse[] = [];

  ngOnInit() {
    this.employeeService.getCurrentEmployee().subscribe(e => this.employee = e);
    this.issueService.getMyIssues().subscribe(i => this.myIssues = i);
  }
}
