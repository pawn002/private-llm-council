import { Component, input, output, effect, signal, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../services/api.service';
import { ModalComponent } from '../modal/modal.component';

@Component({
  selector: 'app-save-load-dialog',
  standalone: true,
  imports: [FormsModule, ModalComponent],
  templateUrl: './save-load-dialog.component.html',
  styleUrls: ['./save-load-dialog.component.scss'],
})
export class SaveLoadDialogComponent {
  private readonly api = inject(ApiService);

  // Signal-based inputs
  readonly mode = input<'save' | 'load'>('save');
  readonly isOpen = input(false);
  readonly deliberationId = input<string>();

  // Signal-based outputs
  readonly close = output<void>();
  readonly save = output<string>();
  readonly load = output<{ id: string; passphrase: string }>();
  readonly forget = output<void>();

  // Local state signals
  readonly passphrase = signal('');
  readonly confirmPassphrase = signal('');
  readonly selectedId = signal('');
  readonly savedIds = signal<string[]>([]);
  readonly loading = signal(false);
  readonly error = signal('');

  constructor() {
    // Effect to handle dialog open/close
    effect(() => {
      if (this.isOpen()) {
        this.loadSavedIds();
      } else {
        this.resetForm();
      }
    });
  }

  private loadSavedIds(): void {
    if (this.mode() === 'load') {
      this.api.listDeliberations().subscribe({
        next: (ids) => this.savedIds.set(ids),
        error: () => this.savedIds.set([]),
      });
    }
  }

  private resetForm(): void {
    this.passphrase.set('');
    this.confirmPassphrase.set('');
    this.error.set('');
  }

  onSave(): void {
    if (this.passphrase().length < 8) {
      this.error.set('Passphrase must be at least 8 characters');
      return;
    }
    if (this.passphrase() !== this.confirmPassphrase()) {
      this.error.set('Passphrases do not match');
      return;
    }

    this.error.set('');
    this.save.emit(this.passphrase());
  }

  onLoad(): void {
    if (!this.selectedId()) {
      this.error.set('Please select a deliberation');
      return;
    }
    if (!this.passphrase()) {
      this.error.set('Please enter the passphrase');
      return;
    }

    this.error.set('');
    this.load.emit({ id: this.selectedId(), passphrase: this.passphrase() });
  }

  onForget(): void {
    if (confirm('This will securely delete the deliberation. This cannot be undone.')) {
      this.forget.emit();
    }
  }

  onClose(): void {
    this.close.emit();
  }

  // Two-way binding helpers for ngModel
  updatePassphrase(value: string): void {
    this.passphrase.set(value);
  }

  updateConfirmPassphrase(value: string): void {
    this.confirmPassphrase.set(value);
  }

  updateSelectedId(value: string): void {
    this.selectedId.set(value);
  }
}
