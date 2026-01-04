import { Component, input, output, computed } from '@angular/core';
import { Perspective } from '../../models';
import { getMemberColor, getMemberIcon } from '../../constants';

@Component({
  selector: 'app-perspective-card',
  standalone: true,
  templateUrl: './perspective-card.component.html',
  styleUrls: ['./perspective-card.component.scss'],
})
export class PerspectiveCardComponent {
  // Signal-based inputs
  readonly perspective = input.required<Perspective>();
  readonly isExpanded = input(false);

  // Signal-based output
  readonly toggle = output<void>();

  // Computed signals for derived state
  readonly borderColor = computed(() => getMemberColor(this.perspective().member_id));

  readonly icon = computed(() => getMemberIcon(this.perspective().member_id));

  readonly formattedTimestamp = computed(() => {
    return new Date(this.perspective().timestamp).toLocaleString(undefined, {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
      timeZoneName: 'short',
    });
  });

  onToggle(): void {
    this.toggle.emit();
  }
}
