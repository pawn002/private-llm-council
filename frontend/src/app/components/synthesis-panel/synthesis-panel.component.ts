import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Synthesis, Disagreement, MinorityReport } from '../../models';

@Component({
  selector: 'app-synthesis-panel',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './synthesis-panel.component.html',
  styleUrls: ['./synthesis-panel.component.scss'],
})
export class SynthesisPanelComponent {
  @Input() synthesis!: Synthesis;
  @Input() disagreements: Disagreement[] = [];
  @Input() minorityReports: MinorityReport[] = [];

  getConfidencePercentage(value: number): number {
    return Math.round(value * 100);
  }

  getConfidenceColor(value: number): string {
    if (value >= 0.7) return 'bg-green';
    if (value >= 0.4) return 'bg-yellow';
    return 'bg-red';
  }

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
