import { Component, input, computed } from '@angular/core';
import { FailedPerspective } from '../../models';
import { getMemberColor, getMemberIcon } from '../../constants';

@Component({
  selector: 'app-failed-perspective-card',
  standalone: true,
  templateUrl: './failed-perspective-card.component.html',
  styleUrls: ['./failed-perspective-card.component.scss'],
})
export class FailedPerspectiveCardComponent {
  readonly failedMember = input.required<FailedPerspective>();

  readonly borderColor = computed(() =>
    getMemberColor(this.failedMember().member_id)
  );

  readonly icon = computed(() =>
    getMemberIcon(this.failedMember().member_id)
  );

  readonly errorIcon = computed(() => {
    const type = this.failedMember().error_type;
    return {
      'timeout': '⏱',
      'model_unavailable': '🚫',
      'gateway_error': '🔌',
      'unknown': '❌'
    }[type] || '❌';
  });

  readonly errorDescription = computed(() => {
    const type = this.failedMember().error_type;
    return {
      'timeout': 'Request timed out',
      'model_unavailable': 'Model not available',
      'gateway_error': 'Gateway communication error',
      'unknown': 'Unknown error'
    }[type] || 'Unknown error';
  });

  readonly formattedTimestamp = computed(() => {
    return new Date(this.failedMember().timestamp).toLocaleString(undefined, {
      hour: 'numeric',
      minute: '2-digit',
    });
  });
}
