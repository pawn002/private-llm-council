import type { Meta, StoryObj } from '@storybook/angular';
import { LoadingStateComponent } from './loading-state.component';

const meta: Meta<LoadingStateComponent> = {
  title: 'Components/LoadingState',
  component: LoadingStateComponent,
  tags: ['autodocs'],
};
export default meta;
type Story = StoryObj<LoadingStateComponent>;

export const Gathering: Story = {
  args: {
    phase: 'gathering',
    statusMessage: 'phi is thinking...',
    elapsedSeconds: 12,
    ollamaBusy: false,
  },
};

export const Synthesizing: Story = {
  args: {
    phase: 'synthesizing',
    statusMessage: 'Synthesizing council perspectives...',
    elapsedSeconds: 87,
    ollamaBusy: false,
  },
};

export const LongRunning: Story = {
  name: 'Long running (with warning)',
  args: {
    phase: 'reviewing',
    statusMessage: 'psi is reviewing...',
    elapsedSeconds: 245,
    ollamaBusy: false,
  },
};

export const OllamaBusy: Story = {
  name: 'Ollama busy',
  args: {
    phase: 'gathering',
    statusMessage: 'Waiting for Ollama...',
    elapsedSeconds: 30,
    ollamaBusy: true,
  },
};
