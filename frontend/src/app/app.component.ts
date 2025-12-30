import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { PrivacyService } from './services/privacy.service';
import { ConsentBannerComponent } from './components/consent-banner/consent-banner.component';
import { CouncilComponent } from './components/council/council.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, ConsentBannerComponent, CouncilComponent],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss'],
})
export class AppComponent {
  constructor(public privacyService: PrivacyService) {}

  onDismissConsent(): void {
    this.privacyService.dismissConsent();
  }
}
