import { Component, input, output, computed } from '@angular/core';
import { Perspective } from '../../models';

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

  private readonly memberColors: Record<string, string> = {
    phi: 'border-blue',
    psi: 'border-purple',
    omega: 'border-amber',
    sigma: 'border-green',
    delta: 'border-red',
  };

  private readonly memberIcons: Record<string, string> = {
    phi: 'Φ',
    psi: 'Ψ',
    omega: 'Ω',
    sigma: 'Σ',
    delta: 'Δ',
  };

  // Computed signals for derived state
  readonly borderColor = computed(() => {
    return this.memberColors[this.perspective().member_id] || 'border-gray';
  });

  readonly icon = computed(() => {
    const p = this.perspective();
    return this.memberIcons[p.member_id] || p.member_id[0].toUpperCase();
  });

  readonly formattedTimestamp = computed(() => {
    return new Date(this.perspective().timestamp).toLocaleString();
  });

  onToggle(): void {
    this.toggle.emit();
  }
}
