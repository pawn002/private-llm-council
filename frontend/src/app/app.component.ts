import { Component, inject, computed } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { PrivacyService } from './services/privacy.service';
import { ConsentBannerComponent } from './components/consent-banner/consent-banner.component';
import { CouncilComponent } from './components/council/council.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [ConsentBannerComponent, CouncilComponent],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss'],
})
export class AppComponent {
  private readonly privacyService = inject(PrivacyService);

  // Convert observables to signals
  readonly status = toSignal(this.privacyService.status$, { initialValue: null });
  readonly loading = toSignal(this.privacyService.loading$, { initialValue: true });
  readonly consentDismissed = toSignal(this.privacyService.consentDismissed$, { initialValue: false });

  // Computed signal for showing banner
  readonly showConsentBanner = computed(() => !this.consentDismissed());

  onDismissConsent(): void {
    this.privacyService.dismissConsent();
  }
}
