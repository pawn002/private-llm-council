import { Component, input, computed } from '@angular/core';
import { Disagreement } from '../../models';

@Component({
  selector: 'app-disagreement-item',
  standalone: true,
  templateUrl: './disagreement-item.component.html',
  styleUrls: ['./disagreement-item.component.scss'],
})
export class DisagreementItemComponent {
  readonly disagreement = input.required<Disagreement>();

  readonly severityClass = computed(() => {
    switch (this.disagreement().severity) {
      case 'minor': return 'severity-minor';
      case 'fundamental': return 'severity-fundamental';
      default: return 'severity-moderate';
    }
  });

  readonly positions = computed(() =>
    Object.entries(this.disagreement().positions ?? {}).map(([key, value]) => ({ key, value }))
  );
}
