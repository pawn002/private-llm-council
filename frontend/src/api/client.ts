/**
 * API client for The Sovereign Council backend.
 *
 * All requests go to the local backend - no external services.
 */

import type {
  Deliberation,
  DeliberationRequest,
  HealthStatus,
  PrivacyStatus,
  SaveRequest,
  LoadRequest,
  ForgetRequest,
} from '../types';

const API_BASE = '/api';

class ApiError extends Error {
  constructor(
    public status: number,
    message: string
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

async function request<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new ApiError(response.status, error.detail || response.statusText);
  }

  return response.json();
}

/**
 * Health and privacy endpoints
 */
export async function getHealth(): Promise<HealthStatus> {
  return request<HealthStatus>('/health');
}

export async function getPrivacyStatus(): Promise<PrivacyStatus> {
  return request<PrivacyStatus>('/privacy/status');
}

/**
 * Deliberation endpoints
 */
export async function startDeliberation(
  question: string,
  onStatus?: (message: string) => void
): Promise<Deliberation> {
  // Use SSE for real-time status updates
  return new Promise((resolve, reject) => {
    const eventSource = new EventSource(
      `${API_BASE}/deliberate/stream?question=${encodeURIComponent(question)}`
    );

    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.type === 'status') {
        onStatus?.(data.message);
      } else if (data.type === 'complete') {
        eventSource.close();
        resolve(data.deliberation);
      } else if (data.type === 'error') {
        eventSource.close();
        reject(new Error(data.message));
      }
    };

    eventSource.onerror = () => {
      eventSource.close();
      // Fall back to regular POST
      request<Deliberation>('/deliberate', {
        method: 'POST',
        body: JSON.stringify({ question } as DeliberationRequest),
      })
        .then(resolve)
        .catch(reject);
    };
  });
}

// Non-streaming fallback
export async function deliberate(question: string): Promise<Deliberation> {
  return request<Deliberation>('/deliberate', {
    method: 'POST',
    body: JSON.stringify({ question } as DeliberationRequest),
  });
}

/**
 * Persistence endpoints
 */
export async function saveDeliberation(
  deliberationId: string,
  passphrase: string
): Promise<{ path: string }> {
  return request<{ path: string }>('/deliberations/save', {
    method: 'POST',
    body: JSON.stringify({
      deliberation_id: deliberationId,
      passphrase,
    } as SaveRequest),
  });
}

export async function loadDeliberation(
  deliberationId: string,
  passphrase: string
): Promise<Deliberation> {
  return request<Deliberation>('/deliberations/load', {
    method: 'POST',
    body: JSON.stringify({
      deliberation_id: deliberationId,
      passphrase,
    } as LoadRequest),
  });
}

export async function forgetDeliberation(
  deliberationId: string
): Promise<{ message: string }> {
  return request<{ message: string }>('/deliberations/forget', {
    method: 'POST',
    body: JSON.stringify({
      deliberation_id: deliberationId,
    } as ForgetRequest),
  });
}

export async function listDeliberations(): Promise<string[]> {
  return request<string[]>('/deliberations');
}

export async function checkDeliberationExists(
  deliberationId: string
): Promise<{ exists: boolean }> {
  return request<{ exists: boolean }>(`/deliberations/${deliberationId}/exists`);
}

export { ApiError };
