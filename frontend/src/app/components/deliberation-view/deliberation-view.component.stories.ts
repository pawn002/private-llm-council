import type { Meta, StoryObj } from '@storybook/angular';
import { DeliberationViewComponent } from './deliberation-view.component';
import { Deliberation } from '../../models';

const meta: Meta<DeliberationViewComponent> = {
  title: 'Council/Deliberation',
  component: DeliberationViewComponent,
  tags: ['autodocs'],
};
export default meta;
type Story = StoryObj<DeliberationViewComponent>;

const fullDeliberation: Deliberation = {
  id: 'del-001',
  question: 'What are the long-term societal implications of widespread AI adoption in knowledge work?',
  perspectives: [
    {
      member_id: 'phi',
      model: 'llama3.2:3b',
      character: 'empiricist',
      content: `## Empirical Assessment\n\nThe available data is **compelling but incomplete**. Three independent meta-analyses point in the same direction.\n\n### Key Findings\n\n- Effect sizes range from moderate to large\n- No significant publication bias detected\n- Longitudinal data remains sparse`,
      timestamp: new Date().toISOString(),
    },
    {
      member_id: 'psi',
      model: 'mistral:7b',
      character: 'rationalist',
      content: `## Logical Analysis\n\nThe argument's formal structure is valid, but **premise two requires independent justification**.\n\n> Correlation is not causation.`,
      timestamp: new Date().toISOString(),
    },
    {
      member_id: 'omega',
      model: 'qwen2.5:3b',
      character: 'pragmatist',
      content: `## Practical Considerations\n\nWhat works in practice matters most. A staged rollout with monitoring is the prudent path forward.`,
      timestamp: new Date().toISOString(),
    },
  ],
  critiques: [],
  synthesis: {
    content: `## Council Synthesis\n\nAfter deliberation, the council finds broad agreement that the evidence warrants cautious optimism, tempered by significant methodological concerns.\n\n**Primary recommendation**: commission a 24-month longitudinal study before adopting policy-level conclusions.`,
    consensus_points: [
      'The current evidence base is insufficient for strong policy conclusions.',
      'A staged pilot approach with clear success metrics is prudent.',
    ],
    divisions: [
      'Phi and Psi disagree on the admissibility of correlation-based evidence.',
    ],
    unique_insights: [
      'Omega highlighted resource asymmetry across deployment contexts.',
    ],
    confidence: { overall: 0.72, consensus_strength: 0.68, dissent_strength: 0.35, reasoning: 'Moderate consensus with one substantive minority position.' },
  },
  disagreements: [
    {
      topic: 'Epistemic Standards',
      description: 'Disagreement on what counts as sufficient evidence.',
      severity: 'moderate',
      positions: {
        phi: 'Meta-analytic consensus is sufficient to act.',
        psi: 'Mechanistic understanding must accompany statistical association.',
      },
    },
  ],
  minority_reports: [
    {
      member_id: 'psi',
      position: `## Formal Dissent\n\nI cannot endorse conclusions that rest on unvalidated causal claims.`,
      rationale: `The majority's synthesis treats correlation as causation. Until mechanistic pathways are established, strong recommendations are epistemically premature.`,
    },
  ],
  timestamp: new Date(Date.now() - 7_200_000).toISOString(),
  session_id: 'sess-001',
};

export const Complete: Story = {
  args: { deliberation: fullDeliberation },
};

export const WithFailedMember: Story = {
  args: {
    deliberation: {
      ...fullDeliberation,
      failed_members: [
        { member_id: 'sigma', model: 'phi3:mini', character: 'synthesist', error_type: 'timeout', error_message: 'Timed out.', timestamp: new Date().toISOString(), attempted_retries: 2 },
      ],
    },
  },
};
