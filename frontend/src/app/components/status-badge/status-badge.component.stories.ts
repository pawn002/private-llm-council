import type { Meta, StoryObj } from '@storybook/angular';
import { StatusBadgeComponent } from './status-badge.component';

const meta: Meta<StatusBadgeComponent> = {
  title: 'App/Consent Banner/Status Badge',
  component: StatusBadgeComponent,
  tags: ['autodocs'],
  argTypes: {
    trueVariant: { control: 'select', options: ['success', 'warning', 'error', 'default'] },
    falseVariant: { control: 'select', options: ['success', 'warning', 'error', 'default'] },
  },
};
export default meta;
type Story = StoryObj<StatusBadgeComponent>;

export const TextValue: Story = {
  name: 'Mode label (text value)',
  args: { label: 'Mode', value: 'CITADEL' },
};

export const BooleanTrue: Story = {
  name: 'Ollama connected',
  args: {
    label: 'Ollama',
    state: true,
    trueText: 'Connected',
    falseText: 'Unavailable',
    trueVariant: 'success',
    falseVariant: 'error',
  },
};

export const BooleanFalse: Story = {
  name: 'Ollama unavailable',
  args: {
    label: 'Ollama',
    state: false,
    trueText: 'Connected',
    falseText: 'Unavailable',
    trueVariant: 'success',
    falseVariant: 'error',
  },
};

export const NetworkWarning: Story = {
  name: 'Network external detected',
  args: {
    label: 'Network',
    state: false,
    trueText: 'Local Only',
    falseText: 'External Detected',
    trueVariant: 'success',
    falseVariant: 'warning',
  },
};
