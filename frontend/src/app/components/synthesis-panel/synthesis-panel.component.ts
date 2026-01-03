import { Component, input } from '@angular/core';
import { Synthesis, Disagreement, MinorityReport } from '../../models';
import { ConfidenceMeterComponent } from '../confidence-meter/confidence-meter.component';
import { ListSectionComponent } from '../list-section/list-section.component';

@Component({
  selector: 'app-synthesis-panel',
  standalone: true,
  imports: [ConfidenceMeterComponent, ListSectionComponent],
  templateUrl: './synthesis-panel.component.html',
  styleUrls: ['./synthesis-panel.component.scss'],
})
export class SynthesisPanelComponent {
  // Signal-based inputs
  readonly synthesis = input.required<Synthesis>();
  readonly disagreements = input<Disagreement[]>([]);
  readonly minorityReports = input<MinorityReport[]>([]);

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

  getPositionEntries(positions: Record<string, string>): Array<{ key: string; value: string }> {
    return Object.entries(positions).map(([key, value]) => ({ key, value }));
  }
}
