import { Component, input, output, computed } from '@angular/core';
import { PrivacyStatus } from '../../models';
import { StatusBadgeComponent } from '../status-badge/status-badge.component';

@Component({
  selector: 'app-consent-banner',
  standalone: true,
  imports: [StatusBadgeComponent],
  templateUrl: './consent-banner.component.html',
  styleUrls: ['./consent-banner.component.scss'],
})
export class ConsentBannerComponent {
  // Signal-based inputs
  readonly status = input<PrivacyStatus | null>(null);
  readonly loading = input(false);

  // Signal-based output
  readonly dismiss = output<void>();

  // Computed signals for derived state
  readonly modeColor = computed(() => {
    const s = this.status();
    if (!s) return 'border-gray-600';
    switch (s.mode.mode) {
      case 'SOVEREIGN':
        return 'border-green-500';
      case 'SANCTUARY':
        return 'border-blue-500';
      case 'CITADEL':
        return 'border-yellow-500';
      default:
        return 'border-gray-600';
    }
  });

  readonly modeIcon = computed(() => {
    const s = this.status();
    if (!s) return 'ph-fill ph-shield';
    switch (s.mode.mode) {
      case 'SOVEREIGN': return 'ph-fill ph-castle';
      case 'SANCTUARY': return 'ph-fill ph-shield';
      case 'CITADEL':   return 'ph-fill ph-lock-laminated';
      default:          return 'ph-fill ph-shield';
    }
  });

  onDismiss(): void {
    this.dismiss.emit();
  }
}
