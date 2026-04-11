import type { Meta, StoryObj } from '@storybook/angular';
import { DisagreementItemComponent } from './disagreement-item.component';
import { Disagreement } from '../../models';

const meta: Meta<DisagreementItemComponent> = {
  title: 'Council/Deliberation/Synthesis/Disagreement Item',
  component: DisagreementItemComponent,
  tags: ['autodocs'],
};
export default meta;
type Story = StoryObj<DisagreementItemComponent>;

const baseDisagreement: Disagreement = {
  topic: 'Epistemic Foundations',
  description: 'Members disagree on whether empirical evidence or logical deduction should take precedence when evaluating the claim.',
  severity: 'moderate',
  positions: {
    phi: 'Empirical data is primary — no theory survives contact with disconfirming evidence.',
    psi: 'Logical consistency must be established first; data interpretation depends on it.',
    omega: 'Both are tools; pragmatic outcomes should guide which we weight more heavily.',
  },
};

export const Minor: Story = {
  args: {
    disagreement: { ...baseDisagreement, topic: 'Terminology', description: 'Slight definitional differences in how "evidence" is scoped.', severity: 'minor', positions: { phi: 'Broad definition including indirect evidence.', psi: 'Strict definition: direct, replicable observations only.' } },
  },
};

export const Moderate: Story = {
  args: { disagreement: baseDisagreement },
};

export const Fundamental: Story = {
  args: {
    disagreement: {
      ...baseDisagreement,
      topic: 'Nature of Truth',
      description: 'A deep philosophical divide on whether objective truth is accessible at all.',
      severity: 'fundamental',
      positions: {
        phi: 'Truth is correspondence to empirical reality and is in principle discoverable.',
        psi: 'Truth is a coherence property of propositions within a system — not world-matching.',
        sigma: 'The question itself may be ill-formed; we should focus on warranted assertability.',
      },
    },
  },
};
