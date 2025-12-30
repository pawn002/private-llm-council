import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';
import { ApiService } from './api.service';
import { Deliberation, DeliberationPhase } from '../models';

export interface DeliberationState {
  phase: DeliberationPhase;
  statusMessage: string;
  deliberation: Deliberation | null;
  error: string | null;
}

const initialState: DeliberationState = {
  phase: 'idle',
  statusMessage: '',
  deliberation: null,
  error: null,
};

@Injectable({
  providedIn: 'root',
})
export class DeliberationService {
  private stateSubject = new BehaviorSubject<DeliberationState>(initialState);
  state$ = this.stateSubject.asObservable();

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
    });

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
          this.updateState({
            phase: 'complete',
            statusMessage: 'Deliberation complete',
            deliberation,
            error: null,
          });
        },
        error: (err) => {
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

    return new Promise((resolve) => {
      this.api.saveDeliberation(deliberation.id, passphrase).subscribe({
        next: () => resolve(true),
        error: (err) => {
          this.setError(err.message || 'Failed to save deliberation');
          resolve(false);
        },
      });
    });
  }

  load(id: string, passphrase: string): Promise<boolean> {
    this.updateState({
      phase: 'gathering',
      statusMessage: 'Decrypting deliberation...',
      deliberation: null,
      error: null,
    });

    return new Promise((resolve) => {
      this.api.loadDeliberation(id, passphrase).subscribe({
        next: (deliberation) => {
          this.updateState({
            phase: 'complete',
            statusMessage: 'Deliberation loaded',
            deliberation,
            error: null,
          });
          resolve(true);
        },
        error: (err) => {
          this.setError(err.message || 'Failed to load deliberation');
          resolve(false);
        },
      });
    });
  }

  forget(): Promise<boolean> {
    const deliberation = this.stateSubject.value.deliberation;
    if (!deliberation) {
      this.setError('No deliberation to forget');
      return Promise.resolve(false);
    }

    return new Promise((resolve) => {
      this.api.forgetDeliberation(deliberation.id).subscribe({
        next: () => {
          this.reset();
          resolve(true);
        },
        error: (err) => {
          this.setError(err.message || 'Failed to forget deliberation');
          resolve(false);
        },
      });
    });
  }

  reset(): void {
    this.stateSubject.next(initialState);
  }
}
