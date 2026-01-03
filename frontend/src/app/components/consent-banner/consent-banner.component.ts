import {
  Component,
  input,
  output,
  computed,
  effect,
  ElementRef,
  Renderer2,
} from '@angular/core';
import { PrivacyStatus } from '../../models';

@Component({
  selector: 'app-consent-banner',
  standalone: true,
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
    if (!s) return '?';
    switch (s.mode.mode) {
      case 'SOVEREIGN':
        return '🏰';
      case 'SANCTUARY':
        return '🛡️';
      case 'CITADEL':
        return '🐳';
      default:
        return '?';
    }
  });

  constructor(
    private elementRef: ElementRef,
    private renderer: Renderer2
  ) {
    // Update banner height CSS variable whenever status or loading changes
    effect(() => {
      // Track dependencies
      this.status();
      this.loading();

      // Update height after DOM settles
      setTimeout(() => this.updateBannerHeight(), 0);
    });
  }

  private updateBannerHeight(): void {
    const element = this.elementRef.nativeElement as HTMLElement;
    const banner = element.querySelector('.consent-banner') as HTMLElement;
    if (banner) {
      const height = banner.offsetHeight;
      this.renderer.setStyle(
        document.documentElement,
        '--banner-height',
        `${height}px`
      );
    }
  }

  onDismiss(): void {
    this.dismiss.emit();
  }
}
