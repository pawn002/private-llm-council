import { Component, inject, computed, signal } from '@angular/core';
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

  // Theme toggle
  readonly theme = signal<'light' | 'dark' | 'system'>(
    (localStorage.getItem('theme') as 'light' | 'dark') ?? 'system'
  );

  readonly isDark = computed(() => {
    if (this.theme() === 'dark') return true;
    if (this.theme() === 'light') return false;
    return window.matchMedia('(prefers-color-scheme: dark)').matches;
  });

  toggleTheme(): void {
    const next = this.isDark() ? 'light' : 'dark';
    this.theme.set(next);
    localStorage.setItem('theme', next);
    document.documentElement.setAttribute('data-theme', next);
  }
}
