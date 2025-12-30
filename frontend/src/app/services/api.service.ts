import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError, Subject } from 'rxjs';
import { catchError, map } from 'rxjs/operators';
import {
  Deliberation,
  HealthStatus,
  PrivacyStatus,
} from '../models';

const API_BASE = '/api';

@Injectable({
  providedIn: 'root',
})
export class ApiService {
  constructor(private http: HttpClient) {}

  private handleError(error: HttpErrorResponse): Observable<never> {
    let message = 'An error occurred';
    if (error.error instanceof ErrorEvent) {
      message = error.error.message;
    } else if (error.error?.detail) {
      message = error.error.detail;
    } else {
      message = error.statusText || message;
    }
    return throwError(() => new Error(message));
  }

  // Health and privacy endpoints
  getHealth(): Observable<HealthStatus> {
    return this.http
      .get<HealthStatus>(`${API_BASE}/health`)
      .pipe(catchError(this.handleError));
  }

  getPrivacyStatus(): Observable<PrivacyStatus> {
    return this.http
      .get<PrivacyStatus>(`${API_BASE}/privacy/status`)
      .pipe(catchError(this.handleError));
  }

  // Deliberation endpoints
  deliberate(question: string): Observable<Deliberation> {
    return this.http
      .post<Deliberation>(`${API_BASE}/deliberate`, { question })
      .pipe(catchError(this.handleError));
  }

  // Streaming deliberation with SSE
  deliberateStream(
    question: string,
    onStatus: (message: string) => void
  ): Observable<Deliberation> {
    return new Observable((observer) => {
      const eventSource = new EventSource(
        `${API_BASE}/deliberate/stream?question=${encodeURIComponent(question)}`
      );

      eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);

          if (data.type === 'status') {
            onStatus(data.message);
          } else if (data.type === 'complete') {
            eventSource.close();
            observer.next(data.deliberation);
            observer.complete();
          } else if (data.type === 'error') {
            eventSource.close();
            observer.error(new Error(data.message));
          }
        } catch (e) {
          console.error('Failed to parse SSE message', e);
        }
      };

      eventSource.onerror = () => {
        eventSource.close();
        // Fall back to regular POST
        this.deliberate(question).subscribe({
          next: (result) => {
            observer.next(result);
            observer.complete();
          },
          error: (err) => observer.error(err),
        });
      };

      return () => {
        eventSource.close();
      };
    });
  }

  // Persistence endpoints
  saveDeliberation(
    deliberationId: string,
    passphrase: string
  ): Observable<{ path: string }> {
    return this.http
      .post<{ path: string }>(`${API_BASE}/deliberations/save`, {
        deliberation_id: deliberationId,
        passphrase,
      })
      .pipe(catchError(this.handleError));
  }

  loadDeliberation(
    deliberationId: string,
    passphrase: string
  ): Observable<Deliberation> {
    return this.http
      .post<Deliberation>(`${API_BASE}/deliberations/load`, {
        deliberation_id: deliberationId,
        passphrase,
      })
      .pipe(catchError(this.handleError));
  }

  forgetDeliberation(deliberationId: string): Observable<{ message: string }> {
    return this.http
      .post<{ message: string }>(`${API_BASE}/deliberations/forget`, {
        deliberation_id: deliberationId,
      })
      .pipe(catchError(this.handleError));
  }

  listDeliberations(): Observable<string[]> {
    return this.http
      .get<string[]>(`${API_BASE}/deliberations`)
      .pipe(catchError(this.handleError));
  }

  checkDeliberationExists(
    deliberationId: string
  ): Observable<{ exists: boolean }> {
    return this.http
      .get<{ exists: boolean }>(`${API_BASE}/deliberations/${deliberationId}/exists`)
      .pipe(catchError(this.handleError));
  }
}
