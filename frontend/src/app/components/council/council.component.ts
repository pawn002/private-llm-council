import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { DeliberationService } from '../../services/deliberation.service';
import { DeliberationViewComponent } from '../deliberation-view/deliberation-view.component';
import { SaveLoadDialogComponent } from '../save-load-dialog/save-load-dialog.component';
import { DeliberationPhase } from '../../models';

@Component({
  selector: 'app-council',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    DeliberationViewComponent,
    SaveLoadDialogComponent,
  ],
  templateUrl: './council.component.html',
  styleUrls: ['./council.component.scss'],
})
export class CouncilComponent {
  question = '';
  dialogMode: 'save' | 'load' | null = null;

  phaseMessages: Record<DeliberationPhase, string> = {
    idle: '',
    gathering: 'Gathering perspectives from council members...',
    reviewing: 'Council members reviewing each other...',
    synthesizing: 'Chairman synthesizing perspectives...',
    analyzing: 'Analyzing disagreements and minority positions...',
    complete: 'Deliberation complete',
    error: 'An error occurred',
  };

  phaseIcons: Record<DeliberationPhase, string> = {
    idle: '',
    gathering: '🎭',
    reviewing: '👁️',
    synthesizing: '⚖️',
    analyzing: '🔍',
    complete: '✅',
    error: '❌',
  };

  phases: DeliberationPhase[] = ['gathering', 'reviewing', 'synthesizing', 'analyzing'];

  constructor(public deliberationService: DeliberationService) {}

  get state() {
    return this.deliberationService.state;
  }

  get isLoading() {
    return this.deliberationService.isLoading;
  }

  onSubmit(): void {
    if (this.question.trim() && !this.isLoading) {
      this.deliberationService.ask(this.question.trim());
      this.question = '';
    }
  }

  onSave(): void {
    this.dialogMode = 'save';
  }

  onLoadClick(): void {
    this.dialogMode = 'load';
  }

  onReset(): void {
    this.deliberationService.reset();
  }

  async handleSave(passphrase: string): Promise<void> {
    const success = await this.deliberationService.save(passphrase);
    if (success) {
      this.dialogMode = null;
    }
  }

  async handleLoad(data: { id: string; passphrase: string }): Promise<void> {
    const success = await this.deliberationService.load(data.id, data.passphrase);
    if (success) {
      this.dialogMode = null;
    }
  }

  async handleForget(): Promise<void> {
    const success = await this.deliberationService.forget();
    if (success) {
      this.dialogMode = null;
    }
  }

  closeDialog(): void {
    this.dialogMode = null;
  }

  getPhaseIndex(phase: DeliberationPhase): number {
    return this.phases.indexOf(phase);
  }
}
