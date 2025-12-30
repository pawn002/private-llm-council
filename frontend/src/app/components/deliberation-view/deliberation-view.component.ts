import { Component, EventEmitter, Input, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Deliberation } from '../../models';
import { PerspectiveCardComponent } from '../perspective-card/perspective-card.component';
import { SynthesisPanelComponent } from '../synthesis-panel/synthesis-panel.component';

@Component({
  selector: 'app-deliberation-view',
  standalone: true,
  imports: [CommonModule, PerspectiveCardComponent, SynthesisPanelComponent],
  templateUrl: './deliberation-view.component.html',
  styleUrls: ['./deliberation-view.component.scss'],
})
export class DeliberationViewComponent {
  @Input() deliberation!: Deliberation;
  @Output() saveClicked = new EventEmitter<void>();
  @Output() newQuestion = new EventEmitter<void>();

  expandedPerspective: string | null = null;
  activeTab: 'synthesis' | 'perspectives' = 'synthesis';

  get formattedTimestamp(): string {
    return new Date(this.deliberation.timestamp).toLocaleString();
  }

  togglePerspective(memberId: string): void {
    this.expandedPerspective =
      this.expandedPerspective === memberId ? null : memberId;
  }

  onSave(): void {
    this.saveClicked.emit();
  }

  onNewQuestion(): void {
    this.newQuestion.emit();
  }
}
