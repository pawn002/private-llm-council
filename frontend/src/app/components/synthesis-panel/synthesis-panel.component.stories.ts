import type { Meta, StoryObj } from '@storybook/angular';
import { SynthesisPanelComponent } from './synthesis-panel.component';
import { Synthesis, Disagreement, MinorityReport } from '../../models';

const meta: Meta<SynthesisPanelComponent> = {
  title: 'Council/Deliberation/Synthesis',
  component: SynthesisPanelComponent,
  tags: ['autodocs'],
};
export default meta;
type Story = StoryObj<SynthesisPanelComponent>;

const mockSynthesis: Synthesis = {
  content: `## Council Consensus

After deliberation, the council finds **moderate agreement** on the core question with notable dissent on implementation timelines.

The empirical evidence presented by Phi is compelling, and the logical framework offered by Psi provides a useful structure for evaluation. Where the council diverges is on risk tolerance and the pace of action.

### Areas of Convergence

All members acknowledge that the status quo is unsustainable. The disagreement is fundamentally about *how fast* to move, not *whether* to move.

### Synthesis

A phased approach — acting on well-established components now while deferring contested elements pending further evidence — appears to satisfy the majority of concerns raised.`,
  consensus_points: [
    'The current approach is insufficient given available evidence',
    'Stakeholder consultation is necessary before full implementation',
    'Monitoring and feedback loops must be built into any rollout',
  ],
  divisions: [
    'Timeline: Phi advocates 30 days, Omega 90 days, Psi indefinite pending more data',
    'Risk tolerance varies significantly between pragmatist and rationalist positions',
  ],
  unique_insights: [
    'Omega identified a third path not considered in the initial framing',
    'Psi\'s formal analysis revealed a hidden assumption in the original question',
  ],
  confidence: {
    overall: 0.72,
    consensus_strength: 0.68,
    dissent_strength: 0.41,
    reasoning: 'Strong agreement on diagnosis, moderate disagreement on remedy. The minority position is coherent but rests on contested empirical claims.',
  },
};

const mockDisagreements: Disagreement[] = [
  {
    topic: 'Implementation timeline',
    description: 'Members disagree significantly on how quickly to proceed given current evidence quality.',
    severity: 'moderate',
    positions: {
      phi: 'Evidence is sufficient now. Delay has measurable costs.',
      psi: 'Premise two remains unestablished. Acting now is premature.',
      omega: 'A 90-day pilot minimises risk while generating real-world data.',
    },
  },
  {
    topic: 'Burden of proof',
    description: 'Fundamental disagreement on what level of certainty is required before action.',
    severity: 'fundamental',
    positions: {
      phi: 'Preponderance of evidence is sufficient for policy.',
      psi: 'Causal mechanism must be established, not merely correlational.',
    },
  },
];

const mockMinorityReports: MinorityReport[] = [
  {
    member_id: 'psi',
    position: '**Dissenting on timeline.** The majority recommendation to act within 30 days is premature.',
    rationale: `The empirical evidence, while suggestive, does not yet establish the causal mechanism required for confident policy action.

Specifically, the three meta-analyses cited conflate observational and experimental designs. Until a properly controlled trial confirms the effect, we risk acting on a correlation that may not survive intervention.

I recommend a 6-month data collection period with pre-registered analysis criteria before any implementation decision.`,
  },
];

export const Full: Story = {
  args: {
    synthesis: mockSynthesis,
    disagreements: mockDisagreements,
    minorityReports: mockMinorityReports,
  },
};

export const NoMinority: Story = {
  name: 'Without minority report',
  args: {
    synthesis: mockSynthesis,
    disagreements: mockDisagreements,
    minorityReports: [],
  },
};

export const Minimal: Story = {
  name: 'Minimal (no confidence, no extras)',
  args: {
    synthesis: {
      content: `## Quick Synthesis\n\nThe council reached broad agreement on this question with no significant dissent.`,
      consensus_points: ['All members agree on the core finding'],
      divisions: [],
      unique_insights: [],
    },
    disagreements: [],
    minorityReports: [],
  },
};
