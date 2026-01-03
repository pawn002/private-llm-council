import { Component, signal, computed, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { toSignal } from '@angular/core/rxjs-interop';
import { DeliberationService } from '../../services/deliberation.service';
import { DeliberationViewComponent } from '../deliberation-view/deliberation-view.component';
import { SaveLoadDialogComponent } from '../save-load-dialog/save-load-dialog.component';
import { DeliberationPhase } from '../../models';

@Component({
  selector: 'app-council',
  standalone: true,
  imports: [
    FormsModule,
    DeliberationViewComponent,
    SaveLoadDialogComponent,
  ],
  templateUrl: './council.component.html',
  styleUrls: ['./council.component.scss'],
})
export class CouncilComponent {
  private readonly deliberationService = inject(DeliberationService);

  // Local state signals
  readonly question = signal('');
  readonly dialogMode = signal<'save' | 'load' | null>(null);

  // Convert service observable to signal
  readonly state = toSignal(this.deliberationService.state$, {
    initialValue: this.deliberationService.state,
  });

  // Computed signals
  readonly isLoading = computed(() => {
    const phase = this.state().phase;
    return ['gathering', 'reviewing', 'synthesizing', 'analyzing'].includes(phase);
  });

  readonly elapsedTime = computed(() => {
    const seconds = this.state().elapsedSeconds;
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}m ${remainingSeconds}s`;
  });

  readonly phaseMessages: Record<DeliberationPhase, string> = {
    idle: '',
    gathering: 'Gathering perspectives from council members...',
    reviewing: 'Council members reviewing each other...',
    synthesizing: 'Chairman synthesizing perspectives...',
    analyzing: 'Analyzing disagreements and minority positions...',
    complete: 'Deliberation complete',
    error: 'An error occurred',
  };

  readonly phaseIcons: Record<DeliberationPhase, string> = {
    idle: '',
    gathering: '🎭',
    reviewing: '👁️',
    synthesizing: '⚖️',
    analyzing: '🔍',
    complete: '✅',
    error: '❌',
  };

  readonly phases: DeliberationPhase[] = ['gathering', 'reviewing', 'synthesizing', 'analyzing'];

  onSubmit(): void {
    const q = this.question().trim();
    if (q && !this.isLoading()) {
      this.deliberationService.ask(q);
      this.question.set('');
    }
  }

  updateQuestion(value: string): void {
    this.question.set(value);
  }

  onSave(): void {
    this.dialogMode.set('save');
  }

  onLoadClick(): void {
    this.dialogMode.set('load');
  }

  onReset(): void {
    this.deliberationService.reset();
  }

  onCancel(): void {
    if (confirm('Are you sure you want to cancel this deliberation?')) {
      this.deliberationService.cancel();
      this.question.set(''); // Clear question input
    }
  }

  async handleSave(passphrase: string): Promise<void> {
    const success = await this.deliberationService.save(passphrase);
    if (success) {
      this.dialogMode.set(null);
    }
  }

  async handleLoad(data: { id: string; passphrase: string }): Promise<void> {
    const success = await this.deliberationService.load(data.id, data.passphrase);
    if (success) {
      this.dialogMode.set(null);
    }
  }

  async handleForget(): Promise<void> {
    const success = await this.deliberationService.forget();
    if (success) {
      this.dialogMode.set(null);
    }
  }

  closeDialog(): void {
    this.dialogMode.set(null);
  }

  getPhaseIndex(phase: DeliberationPhase): number {
    return this.phases.indexOf(phase);
  }
}
