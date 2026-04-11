import type { Meta, StoryObj } from '@storybook/angular';
import { MinorityItemComponent } from './minority-item.component';
import { MinorityReport } from '../../models';

const meta: Meta<MinorityItemComponent> = {
  title: 'Council/Deliberation/Synthesis/Minority Item',
  component: MinorityItemComponent,
  tags: ['autodocs'],
};
export default meta;
type Story = StoryObj<MinorityItemComponent>;

const baseReport: MinorityReport = {
  member_id: 'psi',
  position: `## Dissent

I cannot endorse the council's synthesis in good conscience. The majority's conclusion rests on an **unexamined premise**: that the current evidence base is sufficient to support policy-level recommendations.`,
  rationale: `The meta-analyses cited suffer from substantial heterogeneity (I² > 75%). Pooling results across such divergent study designs produces a confidence interval so wide as to be practically uninformative. A more honest summary would acknowledge deep uncertainty rather than project false precision.

Until higher-quality longitudinal data is available, I recommend withholding strong recommendations.`,
};

export const Default: Story = {
  args: { report: baseReport },
};

export const OmegaMember: Story = {
  name: 'Omega — pragmatist dissent',
  args: {
    report: {
      member_id: 'omega',
      position: `## Pragmatic Objection

The synthesis prioritises theoretical coherence over **immediate practical impact**. Real-world constraints make the recommended approach unworkable in most deployment contexts.`,
      rationale: `Three concrete problems the majority did not address:

1. Resource requirements exceed what 90% of organisations can sustain
2. The 18-month timeline ignores seasonal variability in the data
3. No rollback plan is specified if outcomes diverge

I advocate for a phased pilot with clearly defined exit criteria before any broad rollout.`,
    },
  },
};
