import { Component, input, computed } from '@angular/core';
import { Synthesis, Disagreement, MinorityReport } from '../../models';
import { ConfidenceMeterComponent } from '../confidence-meter/confidence-meter.component';
import { ListSectionComponent } from '../list-section/list-section.component';
import { MarkdownPipe } from '../../pipes/markdown.pipe';
import { DisagreementItemComponent } from '../disagreement-item/disagreement-item.component';
import { MinorityItemComponent } from '../minority-item/minority-item.component';

@Component({
  selector: 'app-synthesis-panel',
  standalone: true,
  imports: [ConfidenceMeterComponent, ListSectionComponent, MarkdownPipe, DisagreementItemComponent, MinorityItemComponent],
  templateUrl: './synthesis-panel.component.html',
  styleUrls: ['./synthesis-panel.component.scss'],
})
export class SynthesisPanelComponent {
  readonly synthesis = input.required<Synthesis>();
  readonly disagreements = input<Disagreement[] | null>([]);
  readonly minorityReports = input<MinorityReport[] | null>([]);

  readonly safeDisagreements = computed(() => this.disagreements() ?? []);
  readonly safeMinorityReports = computed(() => this.minorityReports() ?? []);
}
