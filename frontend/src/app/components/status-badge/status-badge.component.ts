import { Component, input, computed } from '@angular/core';

/**
 * Reusable status badge component for displaying labeled status values
 * with conditional styling based on boolean state.
 */
@Component({
  selector: 'app-status-badge',
  standalone: true,
  templateUrl: './status-badge.component.html',
  styleUrls: ['./status-badge.component.scss'],
})
export class StatusBadgeComponent {
  /** Label displayed before the status value */
  readonly label = input.required<string>();

  /** The status value to display (for simple text display) */
  readonly value = input<string>('');

  /** Boolean state for conditional display (optional) */
  readonly state = input<boolean | null>(null);

  /** Text to display when state is true */
  readonly trueText = input<string>('Yes');

  /** Text to display when state is false */
  readonly falseText = input<string>('No');

  /** CSS class for true state */
  readonly trueClass = input<string>('text-green');

  /** CSS class for false state */
  readonly falseClass = input<string>('text-red');

  /** Whether this is a boolean-based status (vs simple text) */
  readonly isBooleanStatus = computed(() => this.state() !== null);

  /** The display text based on mode */
  readonly displayText = computed(() => {
    if (this.state() !== null) {
      return this.state() ? this.trueText() : this.falseText();
    }
    return this.value();
  });

  /** The CSS class based on state */
  readonly stateClass = computed(() => {
    if (this.state() === null) return 'accent';
    return this.state() ? this.trueClass() : this.falseClass();
  });
}
