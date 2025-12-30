import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { ApiService } from './api.service';
import { PrivacyStatus } from '../models';

const CONSENT_DISMISSED_KEY = 'sovereign_council_consent_dismissed';

@Injectable({
  providedIn: 'root',
})
export class PrivacyService {
  private statusSubject = new BehaviorSubject<PrivacyStatus | null>(null);
  private loadingSubject = new BehaviorSubject<boolean>(true);
  private errorSubject = new BehaviorSubject<string | null>(null);
  private consentDismissedSubject = new BehaviorSubject<boolean>(false);

  status$ = this.statusSubject.asObservable();
  loading$ = this.loadingSubject.asObservable();
  error$ = this.errorSubject.asObservable();
  consentDismissed$ = this.consentDismissedSubject.asObservable();

  constructor(private api: ApiService) {
    // Check session storage for dismissed consent
    const dismissed = sessionStorage.getItem(CONSENT_DISMISSED_KEY) === 'true';
    this.consentDismissedSubject.next(dismissed);

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
    sessionStorage.setItem(CONSENT_DISMISSED_KEY, 'true');
    this.consentDismissedSubject.next(true);
  }

  refreshStatus(): void {
    this.loadingSubject.next(true);
    this.api.getPrivacyStatus().subscribe({
      next: (status) => {
        this.statusSubject.next(status);
        this.loadingSubject.next(false);
        this.errorSubject.next(null);
      },
      error: (err) => {
        this.loadingSubject.next(false);
        this.errorSubject.next(err.message || 'Failed to check privacy status');
      },
    });
  }
}
