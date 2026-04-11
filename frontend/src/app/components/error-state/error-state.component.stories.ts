import type { Meta, StoryObj } from '@storybook/angular';
import { ErrorStateComponent } from './error-state.component';

const meta: Meta<ErrorStateComponent> = {
  title: 'Council/Error',
  component: ErrorStateComponent,
  tags: ['autodocs'],
};
export default meta;
type Story = StoryObj<ErrorStateComponent>;

export const Default: Story = {
  args: {
    title: 'Deliberation Failed',
    error: 'Could not reach Ollama. Is it running on port 11434?',
    buttonText: 'Try Again',
  },
};

export const ModelUnavailable: Story = {
  args: {
    title: 'Model Unavailable',
    error: 'llama3.2:1b is not pulled. Run: ollama pull llama3.2:1b',
    buttonText: 'Dismiss',
  },
};
