import { Injectable } from '@angular/core';
import { ApiService } from './api.service';
import { PrivacyStatus } from '../models';
import { StateSubject } from '../utils';

@Injectable({
  providedIn: 'root',
})
export class PrivacyService {
  private statusSubject = new StateSubject<PrivacyStatus | null>(null);
  private loadingSubject = new StateSubject<boolean>(true);
  private errorSubject = new StateSubject<string | null>(null);
  private consentDismissedSubject = new StateSubject<boolean>(false);

  status$ = this.statusSubject.$;
  loading$ = this.loadingSubject.$;
  error$ = this.errorSubject.$;
  consentDismissed$ = this.consentDismissedSubject.$;

  constructor(private api: ApiService) {
    // Banner is always shown on initial load (no persistence)
    this.consentDismissedSubject.set(false);

    // Fetch privacy status
    this.refreshStatus();
  }

  get status(): PrivacyStatus | null {
    return this.statusSubject.value;
  }

  get loading(): boolean {
    return this.loadingSubject.value;
  }

  get consentDismissed(): boolean {
    return this.consentDismissedSubject.value;
  }

  get showConsentBanner(): boolean {
    return !this.consentDismissedSubject.value;
  }

  dismissConsent(): void {
    // Only dismiss for current page session (no persistence)
    this.consentDismissedSubject.set(true);
  }

  refreshStatus(): void {
    this.loadingSubject.set(true);
    this.api.getPrivacyStatus().subscribe({
      next: (status) => {
        this.statusSubject.set(status);
        this.loadingSubject.set(false);
        this.errorSubject.set(null);
      },
      error: (err) => {
        this.loadingSubject.set(false);
        this.errorSubject.set(err.message || 'Failed to check privacy status');
      },
    });
  }
}
