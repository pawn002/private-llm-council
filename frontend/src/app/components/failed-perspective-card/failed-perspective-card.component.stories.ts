import type { Meta, StoryObj } from '@storybook/angular';
import { FailedPerspectiveCardComponent } from './failed-perspective-card.component';
import { FailedPerspective } from '../../models';

const meta: Meta<FailedPerspectiveCardComponent> = {
  title: 'Council/Deliberation/Perspectives/Failed Card',
  component: FailedPerspectiveCardComponent,
  tags: ['autodocs'],
};
export default meta;
type Story = StoryObj<FailedPerspectiveCardComponent>;

const base: FailedPerspective = {
  member_id: 'phi',
  model: 'llama3.2:3b',
  character: 'empiricist',
  error_type: 'timeout',
  error_message: 'Model did not respond within the allotted 90 seconds.',
  timestamp: new Date().toISOString(),
  attempted_retries: 2,
};

export const Timeout: Story = {
  args: { failedMember: base },
};

export const ModelUnavailable: Story = {
  args: {
    failedMember: {
      ...base,
      member_id: 'psi',
      model: 'mistral:7b',
      character: 'rationalist',
      error_type: 'model_unavailable',
      error_message: 'mistral:7b is not pulled in this Ollama instance.',
      attempted_retries: 0,
    },
  },
};

export const GatewayError: Story = {
  args: {
    failedMember: {
      ...base,
      member_id: 'omega',
      model: 'qwen2.5:3b',
      character: 'pragmatist',
      error_type: 'gateway_error',
      error_message: 'Connection refused on host.docker.internal:11434.',
      attempted_retries: 3,
    },
  },
};

export const Unknown: Story = {
  args: {
    failedMember: {
      ...base,
      member_id: 'sigma',
      model: 'phi3:mini',
      character: 'synthesist',
      error_type: 'unknown',
      error_message: 'An unexpected error occurred during inference.',
      attempted_retries: 1,
    },
  },
};
