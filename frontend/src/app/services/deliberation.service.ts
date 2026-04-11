import { Injectable } from '@angular/core';
import { ApiService } from './api.service';
import { Deliberation, DeliberationPhase } from '../models';
import { ObjectStateSubject, subscribeWithPromise } from '../utils';

export interface DeliberationState {
  phase: DeliberationPhase;
  statusMessage: string;
  deliberation: Deliberation | null;
  error: string | null;
  startTime: number | null;
  elapsedSeconds: number;
  ollamaBusy: boolean;
}

const initialState: DeliberationState = {
  phase: 'idle',
  statusMessage: '',
  deliberation: null,
  error: null,
  startTime: null,
  elapsedSeconds: 0,
  ollamaBusy: false,
};

@Injectable({
  providedIn: 'root',
})
export class DeliberationService {
  private stateSubject = new ObjectStateSubject<DeliberationState>(initialState);
  state$ = this.stateSubject.$;
  private timerInterval: ReturnType<typeof setInterval> | null = null;
  private busyPollingInterval: ReturnType<typeof setInterval> | null = null;

  constructor(private api: ApiService) {}

  get state(): DeliberationState {
    return this.stateSubject.value;
  }

  get isLoading(): boolean {
    const phase = this.stateSubject.value.phase;
    return ['gathering', 'reviewing', 'analyzing', 'synthesizing'].includes(phase);
  }

  private setPhase(phase: DeliberationPhase, message = ''): void {
    this.stateSubject.patch({ phase, statusMessage: message });
  }

  private setError(error: string): void {
    this.stateSubject.patch({ phase: 'error', error, statusMessage: '' });
  }

  ask(question: string): void {
    if (!question.trim()) {
      this.setError('Please enter a question');
      return;
    }

    this.stateSubject.patch({
      phase: 'gathering',
      statusMessage: 'Gathering perspectives from council members...',
      deliberation: null,
      error: null,
      startTime: Date.now(),
      elapsedSeconds: 0,
    });

    // Start timer
    this.startTimer();
    this.startBusyPolling();

    // Try streaming first
    this.api
      .deliberateStream(question, (message) => {
        const lower = message.toLowerCase();
        if (lower.includes('gathering')) {
          this.setPhase('gathering', message);
        } else if (lower.includes('review')) {
          this.setPhase('reviewing', message);
        } else if (lower.includes('synthesi')) {
          this.setPhase('synthesizing', message);
        } else if (lower.includes('analy')) {
          this.setPhase('analyzing', message);
        } else {
          this.stateSubject.patch({ statusMessage: message });
        }
      })
      .subscribe({
        next: (deliberation) => {
          this.stopTimer();
          this.stopBusyPolling();
          this.stateSubject.patch({
            phase: 'complete',
            statusMessage: 'Deliberation complete',
            deliberation,
            error: null,
          });
        },
        error: (err) => {
          this.stopTimer();
          this.stopBusyPolling();
          this.setError(err.message || 'Deliberation failed');
        },
      });
  }

  save(passphrase: string): Promise<boolean> {
    const deliberation = this.stateSubject.value.deliberation;
    if (!deliberation) {
      this.setError('No deliberation to save');
      return Promise.resolve(false);
    }

    return subscribeWithPromise(
      this.api.saveDeliberation(deliberation.id, passphrase),
      () => {},
      (err) => this.setError(err.message || 'Failed to save deliberation')
    );
  }

  load(id: string, passphrase: string): Promise<boolean> {
    this.stateSubject.patch({
      phase: 'gathering',
      statusMessage: 'Decrypting deliberation...',
      deliberation: null,
      error: null,
    });

    return subscribeWithPromise(
      this.api.loadDeliberation(id, passphrase),
      (deliberation) => {
        this.stateSubject.patch({
          phase: 'complete',
          statusMessage: 'Deliberation loaded',
          deliberation,
          error: null,
        });
      },
      (err) => this.setError(err.message || 'Failed to load deliberation')
    );
  }

  forget(): Promise<boolean> {
    const deliberation = this.stateSubject.value.deliberation;
    if (!deliberation) {
      this.setError('No deliberation to forget');
      return Promise.resolve(false);
    }

    return subscribeWithPromise(
      this.api.forgetDeliberation(deliberation.id),
      () => this.reset(),
      (err) => this.setError(err.message || 'Failed to forget deliberation')
    );
  }

  reset(): void {
    this.stopBusyPolling();
    this.stateSubject.resetToInitial();
  }

  cancel(): void {
    // Stop timer
    this.stopTimer();
    this.stopBusyPolling();

    // Cancel API stream
    this.api.cancelStream();

    // Reset state
    this.stateSubject.patch({
      phase: 'idle',
      statusMessage: 'Deliberation canceled',
      deliberation: null,
      error: null,
      startTime: null,
      elapsedSeconds: 0,
    });

    // Clear message after 3 seconds
    setTimeout(() => {
      if (this.stateSubject.value.statusMessage === 'Deliberation canceled') {
        this.stateSubject.patch({ statusMessage: '' });
      }
    }, 3000);
  }

  private startTimer(): void {
    this.stopTimer(); // Clear any existing timer

    this.timerInterval = setInterval(() => {
      const current = this.stateSubject.value;
      if (current.startTime) {
        const elapsed = Math.floor((Date.now() - current.startTime) / 1000);
        this.stateSubject.patch({ elapsedSeconds: elapsed });
      }
    }, 1000); // Update every second
  }

  private stopTimer(): void {
    if (this.timerInterval) {
      clearInterval(this.timerInterval);
      this.timerInterval = null;
    }
  }

  private startBusyPolling(): void {
    this.stopBusyPolling(); // Clear any existing polling

    // Delay first poll by 15 seconds to give current deliberation time to load models
    // This prevents false positives from warmup models
    setTimeout(() => {
      // Poll every 8 seconds for Ollama busy status
      this.busyPollingInterval = setInterval(() => {
        const startTime = this.stateSubject.value.startTime;
        this.api.getGatewayBusyStatus(startTime ?? undefined).subscribe({
          next: (status) => {
            this.stateSubject.patch({ ollamaBusy: status.is_busy });
          },
          error: (err) => {
            // Silently fail - don't break deliberations if polling fails
            console.warn('Failed to check Ollama busy status:', err);
            this.stateSubject.patch({ ollamaBusy: false });
          },
        });
      }, 8000); // 8 seconds interval
    }, 15000); // Delay 15 seconds before starting to poll
  }

  private stopBusyPolling(): void {
    if (this.busyPollingInterval) {
      clearInterval(this.busyPollingInterval);
      this.busyPollingInterval = null;
    }
  }
}
