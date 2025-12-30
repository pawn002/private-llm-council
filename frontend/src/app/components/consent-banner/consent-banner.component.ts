import { Component, EventEmitter, Input, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { PrivacyStatus } from '../../models';

@Component({
  selector: 'app-consent-banner',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './consent-banner.component.html',
  styleUrls: ['./consent-banner.component.scss'],
})
export class ConsentBannerComponent {
  @Input() status: PrivacyStatus | null = null;
  @Input() loading = false;
  @Output() dismiss = new EventEmitter<void>();

  get modeColor(): string {
    if (!this.status) return 'border-gray-600';
    switch (this.status.mode.mode) {
      case 'SOVEREIGN':
        return 'border-green-500';
      case 'SANCTUARY':
        return 'border-blue-500';
      case 'CITADEL':
        return 'border-yellow-500';
      default:
        return 'border-gray-600';
    }
  }

  get modeIcon(): string {
    if (!this.status) return '?';
    switch (this.status.mode.mode) {
      case 'SOVEREIGN':
        return '🏰';
      case 'SANCTUARY':
        return '🛡️';
      case 'CITADEL':
        return '🐳';
      default:
        return '?';
    }
  }

  onDismiss(): void {
    this.dismiss.emit();
  }
}
