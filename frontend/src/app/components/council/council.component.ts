import { Component, computed, inject, signal } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { DeliberationService } from '../../services/deliberation.service';
import { DeliberationViewComponent } from '../deliberation-view/deliberation-view.component';
import { ErrorStateComponent } from '../error-state/error-state.component';
import { LoadingStateComponent } from '../loading-state/loading-state.component';
import { SaveLoadDialogComponent } from '../save-load-dialog/save-load-dialog.component';
import { QuestionFormComponent } from '../question-form/question-form.component';

@Component({
  selector: 'app-council',
  standalone: true,
  imports: [
    QuestionFormComponent,
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

  readonly dialogMode = signal<'save' | 'load' | null>(null);

  readonly state = toSignal(this.deliberationService.state$, {
    initialValue: this.deliberationService.state,
  });

  readonly isLoading = computed(() => {
    const phase = this.state().phase;
    return ['gathering', 'reviewing', 'analyzing', 'synthesizing'].includes(phase);
  });

  onQuestionSubmitted(question: string): void {
    this.deliberationService.ask(question);
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
