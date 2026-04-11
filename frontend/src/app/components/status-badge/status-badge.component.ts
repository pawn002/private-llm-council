import { Component, input, computed } from '@angular/core';

export type StatusVariant = 'success' | 'warning' | 'error' | 'default';

@Component({
  selector: 'app-status-badge',
  standalone: true,
  templateUrl: './status-badge.component.html',
  styleUrls: ['./status-badge.component.scss'],
})
export class StatusBadgeComponent {
  readonly label = input.required<string>();

  /** The status value to display (text-only mode) */
  readonly value = input<string>('');

  /** Boolean state (boolean mode). When null, renders as text-only. */
  readonly state = input<boolean | null>(null);

  readonly trueText = input<string>('Yes');
  readonly falseText = input<string>('No');

  /** Candor status variant applied when state is true */
  readonly trueVariant = input<StatusVariant>('success');

  /** Candor status variant applied when state is false */
  readonly falseVariant = input<StatusVariant>('error');

  readonly isBooleanStatus = computed(() => this.state() !== null);

  readonly displayText = computed(() => {
    if (this.state() !== null) {
      return this.state() ? this.trueText() : this.falseText();
    }
    return this.value();
  });

  readonly badgeClass = computed(() => {
    const variant = this.state() === null
      ? 'variant-default'
      : `variant-${this.state() ? this.trueVariant() : this.falseVariant()}`;
    return `badge-value ${variant}`;
  });
}
