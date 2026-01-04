import { Component, input, output, signal, computed } from '@angular/core';
import { Deliberation } from '../../models';
import { PerspectiveCardComponent } from '../perspective-card/perspective-card.component';
import { SynthesisPanelComponent } from '../synthesis-panel/synthesis-panel.component';

@Component({
  selector: 'app-deliberation-view',
  standalone: true,
  imports: [PerspectiveCardComponent, SynthesisPanelComponent],
  templateUrl: './deliberation-view.component.html',
  styleUrls: ['./deliberation-view.component.scss'],
})
export class DeliberationViewComponent {
  // Signal-based inputs
  readonly deliberation = input.required<Deliberation>();

  // Signal-based outputs
  readonly saveClicked = output<void>();
  readonly newQuestion = output<void>();

  // Local state signals
  readonly expandedPerspective = signal<string | null>(null);
  readonly activeTab = signal<'synthesis' | 'perspectives'>('synthesis');

  // Computed signals
  readonly formattedTimestamp = computed(() => {
    return new Date(this.deliberation().timestamp).toLocaleString(undefined, {
      dateStyle: 'medium',
      timeStyle: 'short',
      timeZoneName: 'short',
    });
  });

  togglePerspective(memberId: string): void {
    this.expandedPerspective.update(current =>
      current === memberId ? null : memberId
    );
  }

  setActiveTab(tab: 'synthesis' | 'perspectives'): void {
    this.activeTab.set(tab);
  }

  onSave(): void {
    this.saveClicked.emit();
  }

  onNewQuestion(): void {
    this.newQuestion.emit();
  }
}
