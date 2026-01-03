import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';
import { ApiService } from './api.service';
import { Deliberation, DeliberationPhase } from '../models';
import { subscribeWithPromise } from '../utils';

export interface DeliberationState {
  phase: DeliberationPhase;
  statusMessage: string;
  deliberation: Deliberation | null;
  error: string | null;
  startTime: number | null;
  elapsedSeconds: number;
}

const initialState: DeliberationState = {
  phase: 'idle',
  statusMessage: '',
  deliberation: null,
  error: null,
  startTime: null,
  elapsedSeconds: 0,
};

@Injectable({
  providedIn: 'root',
})
export class DeliberationService {
  private stateSubject = new BehaviorSubject<DeliberationState>(initialState);
  state$ = this.stateSubject.asObservable();
  private timerInterval: any = null;

  constructor(private api: ApiService) {}

  get state(): DeliberationState {
    return this.stateSubject.value;
  }

  get isLoading(): boolean {
    const phase = this.stateSubject.value.phase;
    return ['gathering', 'reviewing', 'synthesizing', 'analyzing'].includes(phase);
  }

  private updateState(partial: Partial<DeliberationState>): void {
    this.stateSubject.next({ ...this.stateSubject.value, ...partial });
  }

  private setPhase(phase: DeliberationPhase, message = ''): void {
    this.updateState({ phase, statusMessage: message });
  }

  private setError(error: string): void {
    this.updateState({ phase: 'error', error, statusMessage: '' });
  }

  ask(question: string): void {
    if (!question.trim()) {
      this.setError('Please enter a question');
      return;
    }

    this.updateState({
      phase: 'gathering',
      statusMessage: 'Gathering perspectives from council members...',
      deliberation: null,
      error: null,
      startTime: Date.now(),
      elapsedSeconds: 0,
    });

    // Start timer
    this.startTimer();

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
          this.updateState({ statusMessage: message });
        }
      })
      .subscribe({
        next: (deliberation) => {
          this.stopTimer();
          this.updateState({
            phase: 'complete',
            statusMessage: 'Deliberation complete',
            deliberation,
            error: null,
          });
        },
        error: (err) => {
          this.stopTimer();
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
    this.updateState({
      phase: 'gathering',
      statusMessage: 'Decrypting deliberation...',
      deliberation: null,
      error: null,
    });

    return subscribeWithPromise(
      this.api.loadDeliberation(id, passphrase),
      (deliberation) => {
        this.updateState({
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
    this.stateSubject.next(initialState);
  }

  cancel(): void {
    // Stop timer
    this.stopTimer();

    // Cancel API stream
    this.api.cancelStream();

    // Reset state
    this.updateState({
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
        this.updateState({ statusMessage: '' });
      }
    }, 3000);
  }

  private startTimer(): void {
    this.stopTimer(); // Clear any existing timer

    this.timerInterval = setInterval(() => {
      const current = this.stateSubject.value;
      if (current.startTime) {
        const elapsed = Math.floor((Date.now() - current.startTime) / 1000);
        this.stateSubject.next({
          ...current,
          elapsedSeconds: elapsed
        });
      }
    }, 1000); // Update every second
  }

  private stopTimer(): void {
    if (this.timerInterval) {
      clearInterval(this.timerInterval);
      this.timerInterval = null;
    }
  }
}
