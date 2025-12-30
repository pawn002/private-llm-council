/**
 * Hook for managing privacy consent and status.
 *
 * Per requirements: consent banner always shown, user can dismiss per session.
 */

import { useState, useEffect, useCallback } from 'react';
import type { PrivacyStatus } from '../types';
import { getPrivacyStatus } from '../api/client';

interface PrivacyState {
  status: PrivacyStatus | null;
  consentDismissed: boolean;
  loading: boolean;
  error: string | null;
}

const CONSENT_DISMISSED_KEY = 'sovereign_council_consent_dismissed';

export function usePrivacy() {
  const [state, setState] = useState<PrivacyState>({
    status: null,
    consentDismissed: false,
    loading: true,
    error: null,
  });

  // Check if consent was dismissed this session
  useEffect(() => {
    const dismissed = sessionStorage.getItem(CONSENT_DISMISSED_KEY) === 'true';
    setState((prev) => ({ ...prev, consentDismissed: dismissed }));
  }, []);

  // Fetch privacy status on mount
  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const status = await getPrivacyStatus();
        setState((prev) => ({
          ...prev,
          status,
          loading: false,
          error: null,
        }));
      } catch (err) {
        setState((prev) => ({
          ...prev,
          loading: false,
          error: err instanceof Error ? err.message : 'Failed to check privacy status',
        }));
      }
    };

    fetchStatus();
  }, []);

  const dismissConsent = useCallback(() => {
    sessionStorage.setItem(CONSENT_DISMISSED_KEY, 'true');
    setState((prev) => ({ ...prev, consentDismissed: true }));
  }, []);

  const refreshStatus = useCallback(async () => {
    setState((prev) => ({ ...prev, loading: true }));
    try {
      const status = await getPrivacyStatus();
      setState((prev) => ({
        ...prev,
        status,
        loading: false,
        error: null,
      }));
    } catch (err) {
      setState((prev) => ({
        ...prev,
        loading: false,
        error: err instanceof Error ? err.message : 'Failed to refresh privacy status',
      }));
    }
  }, []);

  return {
    ...state,
    dismissConsent,
    refreshStatus,
    showConsentBanner: !state.consentDismissed,
  };
}
