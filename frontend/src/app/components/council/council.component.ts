import { Component, signal, computed, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { toSignal } from '@angular/core/rxjs-interop';
import { DeliberationService } from '../../services/deliberation.service';
import { DeliberationViewComponent } from '../deliberation-view/deliberation-view.component';
import { ErrorStateComponent } from '../error-state/error-state.component';
import { LoadingStateComponent } from '../loading-state/loading-state.component';
import { SaveLoadDialogComponent } from '../save-load-dialog/save-load-dialog.component';

@Component({
  selector: 'app-council',
  standalone: true,
  imports: [
    FormsModule,
    DeliberationViewComponent,
    ErrorStateComponent,
    LoadingStateComponent,
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
}
