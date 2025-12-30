import { Component, EventEmitter, Input, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Perspective } from '../../models';

@Component({
  selector: 'app-perspective-card',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './perspective-card.component.html',
  styleUrls: ['./perspective-card.component.scss'],
})
export class PerspectiveCardComponent {
  @Input() perspective!: Perspective;
  @Input() isExpanded = false;
  @Output() toggle = new EventEmitter<void>();

  private memberColors: Record<string, string> = {
    phi: 'border-blue',
    psi: 'border-purple',
    omega: 'border-amber',
    sigma: 'border-green',
    delta: 'border-red',
  };

  private memberIcons: Record<string, string> = {
    phi: 'Φ',
    psi: 'Ψ',
    omega: 'Ω',
    sigma: 'Σ',
    delta: 'Δ',
  };

  get borderColor(): string {
    return this.memberColors[this.perspective.member_id] || 'border-gray';
  }

  get icon(): string {
    return (
      this.memberIcons[this.perspective.member_id] ||
      this.perspective.member_id[0].toUpperCase()
    );
  }

  get formattedTimestamp(): string {
    return new Date(this.perspective.timestamp).toLocaleString();
  }

  onToggle(): void {
    this.toggle.emit();
  }
}
