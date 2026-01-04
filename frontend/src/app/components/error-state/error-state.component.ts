import { Component, input, output } from '@angular/core';

/**
 * Reusable error state component for displaying error messages.
 */
@Component({
  selector: 'app-error-state',
  standalone: true,
  templateUrl: './error-state.component.html',
  styleUrls: ['./error-state.component.scss'],
})
export class ErrorStateComponent {
  /** Error message to display */
  readonly error = input<string | null>(null);

  /** Title for the error card */
  readonly title = input<string>('Deliberation Failed');

  /** Button text */
  readonly buttonText = input<string>('Try Again');

  /** Emits when retry button is clicked */
  readonly retry = output<void>();

  onRetry(): void {
    this.retry.emit();
  }
}
