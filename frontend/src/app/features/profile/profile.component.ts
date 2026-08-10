import { Component, OnInit, inject, signal } from '@angular/core';
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
  templateUrl: './profile.component.html',
  styleUrl: './profile.component.scss'
})
export class ProfileComponent implements OnInit {
  private authService = inject(AuthService);
  private employeeService = inject(EmployeeService);
  private issueService = inject(IssueService);

  user = this.authService.currentUser;
  employee = signal<EmployeeResponse | null>(null);
  myIssues = signal<IssueResponse[]>([]);

  ngOnInit() {
    this.employeeService.getCurrentEmployee().subscribe(e => this.employee.set(e));
    this.issueService.getMyIssues().subscribe(i => this.myIssues.set(i));
  }
}
