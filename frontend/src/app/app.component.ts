import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterOutlet, Router, NavigationEnd } from '@angular/router';
import { SidebarComponent } from './shared/sidebar/sidebar.component';
import { AuthService } from './core/services/auth.service';
import { filter } from 'rxjs';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, RouterOutlet, SidebarComponent],
  template: `
    <div class="app-container">
      <app-sidebar *ngIf="showSidebar"></app-sidebar>
      <div class="main-viewport" [class.no-sidebar]="!showSidebar">
        <router-outlet></router-outlet>
      </div>
    </div>
  `,
  styles: [`
    .app-container {
      display: flex;
      min-height: 100vh;
      width: 100%;
    }
    .main-viewport {
      flex: 1;
      width: 100%;
    }
    .no-sidebar {
      margin-left: 0 !important;
    }
  `]
})
export class AppComponent {
  showSidebar: boolean = false;

  constructor(private router: Router, private authService: AuthService) {
    this.router.events
      .pipe(filter(event => event instanceof NavigationEnd))
      .subscribe((event: any) => {
        const url = event.urlAfterRedirects || event.url;
        const isAuthPage = url.includes('/login') || url.includes('/register');
        this.showSidebar = !isAuthPage && this.authService.isAuthenticated();
      });
  }
}
