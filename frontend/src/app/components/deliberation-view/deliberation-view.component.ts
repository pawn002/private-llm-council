import { Component, input, output, signal } from '@angular/core';
import { Deliberation } from '../../models';
import { SynthesisPanelComponent } from '../synthesis-panel/synthesis-panel.component';
import { QuestionHeaderComponent } from '../question-header/question-header.component';
import { PerspectivesListComponent } from '../perspectives-list/perspectives-list.component';

@Component({
  selector: 'app-deliberation-view',
  standalone: true,
  imports: [SynthesisPanelComponent, QuestionHeaderComponent, PerspectivesListComponent],
  templateUrl: './deliberation-view.component.html',
  styleUrls: ['./deliberation-view.component.scss'],
})
export class DeliberationViewComponent {
  readonly deliberation = input.required<Deliberation>();
  readonly saveClicked = output<void>();
  readonly newQuestion = output<void>();

  readonly activeTab = signal<'synthesis' | 'perspectives'>('synthesis');

  setActiveTab(tab: 'synthesis' | 'perspectives'): void {
    this.activeTab.set(tab);
  }
}
