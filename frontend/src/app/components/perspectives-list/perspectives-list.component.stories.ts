import type { Meta, StoryObj } from '@storybook/angular';
import { PerspectivesListComponent } from './perspectives-list.component';
import { Perspective, FailedPerspective } from '../../models';

const meta: Meta<PerspectivesListComponent> = {
  title: 'Council/Deliberation/Perspectives',
  component: PerspectivesListComponent,
  tags: ['autodocs'],
};
export default meta;
type Story = StoryObj<PerspectivesListComponent>;

const perspectives: Perspective[] = [
  {
    member_id: 'phi',
    model: 'llama3.2:3b',
    character: 'empiricist',
    content: `## Empirical Assessment\n\nThe available data is **compelling but incomplete**. Three independent meta-analyses point in the same direction, yet publication bias remains a concern.\n\n### Recommendation\n\nCollect longitudinal data over 24 months before drawing policy conclusions.`,
    timestamp: new Date().toISOString(),
  },
  {
    member_id: 'psi',
    model: 'mistral:7b',
    character: 'rationalist',
    content: `## Logical Framework\n\nThe argument's formal structure is valid, but **premise two is unsupported**. Without independent justification, the conclusion is epistemically unwarranted.\n\n> Correlation is not causation, and treating it as such is a category error.`,
    timestamp: new Date().toISOString(),
  },
  {
    member_id: 'omega',
    model: 'qwen2.5:3b',
    character: 'pragmatist',
    content: `## Practical Perspective\n\nTheoretical debates aside — what **actually works**? The proposed intervention has been piloted in three comparable contexts with positive outcomes.\n\nI recommend a staged rollout with clear exit criteria.`,
    timestamp: new Date().toISOString(),
  },
];

const failedMembers: FailedPerspective[] = [
  {
    member_id: 'sigma',
    model: 'phi3:mini',
    character: 'synthesist',
    error_type: 'timeout',
    error_message: 'Model timed out after 90 seconds.',
    timestamp: new Date().toISOString(),
    attempted_retries: 2,
  },
];

export const AllSuccessful: Story = {
  args: { perspectives, failedMembers: [] },
};

export const WithFailedMember: Story = {
  args: { perspectives, failedMembers },
};

export const OnlyFailed: Story = {
  args: { perspectives: [], failedMembers },
};
