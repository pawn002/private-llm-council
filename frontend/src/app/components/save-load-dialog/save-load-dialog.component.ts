import { Component, EventEmitter, Input, Output, OnInit, OnChanges, SimpleChanges } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-save-load-dialog',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './save-load-dialog.component.html',
  styleUrls: ['./save-load-dialog.component.scss'],
})
export class SaveLoadDialogComponent implements OnInit, OnChanges {
  @Input() mode: 'save' | 'load' = 'save';
  @Input() isOpen = false;
  @Input() deliberationId?: string;

  @Output() close = new EventEmitter<void>();
  @Output() save = new EventEmitter<string>();
  @Output() load = new EventEmitter<{ id: string; passphrase: string }>();
  @Output() forget = new EventEmitter<void>();

  passphrase = '';
  confirmPassphrase = '';
  selectedId = '';
  savedIds: string[] = [];
  loading = false;
  error = '';

  constructor(private api: ApiService) {}

  ngOnInit(): void {
    this.loadSavedIds();
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['isOpen']) {
      if (this.isOpen) {
        this.loadSavedIds();
      } else {
        this.resetForm();
      }
    }
  }

  private loadSavedIds(): void {
    if (this.mode === 'load') {
      this.api.listDeliberations().subscribe({
        next: (ids) => (this.savedIds = ids),
        error: () => (this.savedIds = []),
      });
    }
  }

  private resetForm(): void {
    this.passphrase = '';
    this.confirmPassphrase = '';
    this.error = '';
  }

  onSave(): void {
    if (this.passphrase.length < 8) {
      this.error = 'Passphrase must be at least 8 characters';
      return;
    }
    if (this.passphrase !== this.confirmPassphrase) {
      this.error = 'Passphrases do not match';
      return;
    }

    this.error = '';
    this.save.emit(this.passphrase);
  }

  onLoad(): void {
    if (!this.selectedId) {
      this.error = 'Please select a deliberation';
      return;
    }
    if (!this.passphrase) {
      this.error = 'Please enter the passphrase';
      return;
    }

    this.error = '';
    this.load.emit({ id: this.selectedId, passphrase: this.passphrase });
  }

  onForget(): void {
    if (confirm('This will securely delete the deliberation. This cannot be undone.')) {
      this.forget.emit();
    }
  }

  onClose(): void {
    this.close.emit();
  }
}
