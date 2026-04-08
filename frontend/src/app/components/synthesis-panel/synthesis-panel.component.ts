import { Component, input, computed } from '@angular/core';
import { Synthesis, Disagreement, MinorityReport } from '../../models';
import { ConfidenceMeterComponent } from '../confidence-meter/confidence-meter.component';
import { ListSectionComponent } from '../list-section/list-section.component';
import { MarkdownPipe } from '../../pipes/markdown.pipe';

@Component({
  selector: 'app-synthesis-panel',
  standalone: true,
  imports: [ConfidenceMeterComponent, ListSectionComponent, MarkdownPipe],
  templateUrl: './synthesis-panel.component.html',
  styleUrls: ['./synthesis-panel.component.scss'],
})
export class SynthesisPanelComponent {
  // Signal-based inputs
  readonly synthesis = input.required<Synthesis>();
  readonly disagreements = input<Disagreement[] | null>([]);
  readonly minorityReports = input<MinorityReport[] | null>([]);

  // Safe accessors that guarantee arrays (handles null/undefined edge cases)
  readonly safeDisagreements = computed(() => this.disagreements() ?? []);
  readonly safeMinorityReports = computed(() => this.minorityReports() ?? []);

  getSeverityClass(severity?: string): string {
    switch (severity) {
      case 'minor':
        return 'severity-minor';
      case 'fundamental':
        return 'severity-fundamental';
      default:
        return 'severity-moderate';
    }
  }

  getPositionEntries(positions: Record<string, string> | null | undefined): Array<{ key: string; value: string }> {
    if (!positions) return [];
    return Object.entries(positions).map(([key, value]) => ({ key, value }));
  }
}
