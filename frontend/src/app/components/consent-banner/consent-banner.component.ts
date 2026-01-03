import {
  Component,
  input,
  output,
  computed,
  effect,
  ElementRef,
  Renderer2,
  OnDestroy,
} from '@angular/core';
import { PrivacyStatus } from '../../models';

@Component({
  selector: 'app-consent-banner',
  standalone: true,
  templateUrl: './consent-banner.component.html',
  styleUrls: ['./consent-banner.component.scss'],
})
export class ConsentBannerComponent implements OnDestroy {
  private resizeObserver?: ResizeObserver;

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
    // Setup ResizeObserver after view init whenever status or loading changes
    effect(() => {
      // Track dependencies
      this.status();
      this.loading();

      // Trigger ResizeObserver setup after dependencies change
      this.setupResizeObserver();
    });
  }

  ngOnDestroy(): void {
    // Clean up observer on component destruction
    if (this.resizeObserver) {
      this.resizeObserver.disconnect();
    }
  }

  private setupResizeObserver(): void {
    // Clean up existing observer
    if (this.resizeObserver) {
      this.resizeObserver.disconnect();
    }

    // Wait for DOM to settle, then setup observer
    setTimeout(() => {
      const element = this.elementRef.nativeElement as HTMLElement;
      const banner = element.querySelector('.consent-banner') as HTMLElement;

      if (banner) {
        // Create ResizeObserver to watch banner height changes
        this.resizeObserver = new ResizeObserver(() => {
          this.updateBannerHeight();
        });

        this.resizeObserver.observe(banner);

        // Trigger initial measurement
        this.updateBannerHeight();
      }
    }, 0);
  }

  private updateBannerHeight(): void {
    const element = this.elementRef.nativeElement as HTMLElement;
    const banner = element.querySelector('.consent-banner') as HTMLElement;
    if (banner) {
      // Use requestAnimationFrame to ensure measurement happens after reflow
      requestAnimationFrame(() => {
        const height = banner.offsetHeight;
        this.renderer.setStyle(
          document.documentElement,
          '--banner-height',
          `${height}px`
        );
      });
    }
  }

  onDismiss(): void {
    this.dismiss.emit();
  }
}
