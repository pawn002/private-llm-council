import { Observable, Subscription } from 'rxjs';

/**
 * Helper for handling API calls that resolve a Promise.
 *
 * Reduces boilerplate for the common pattern:
 * - Subscribe to an observable
 * - On success: perform action and resolve true
 * - On error: set error message and resolve false
 */
export function subscribeWithPromise<T>(
  observable: Observable<T>,
  onSuccess: (result: T) => void,
  onError: (error: Error) => void
): Promise<boolean> {
  return new Promise((resolve) => {
    observable.subscribe({
      next: (result) => {
        onSuccess(result);
        resolve(true);
      },
      error: (err) => {
        onError(err);
        resolve(false);
      },
    });
  });
}

/**
 * Helper for simple subscriptions with error handling.
 *
 * @param observable The observable to subscribe to
 * @param onSuccess Callback for successful results
 * @param onError Optional error handler (logs to console if not provided)
 * @returns The subscription for cleanup
 */
export function subscribeWithErrorHandling<T>(
  observable: Observable<T>,
  onSuccess: (result: T) => void,
  onError?: (error: Error) => void
): Subscription {
  return observable.subscribe({
    next: onSuccess,
    error: (err) => {
      const message = err.message || 'An unexpected error occurred';
      console.error('Subscription error:', message);
      onError?.(err);
    },
  });
}
