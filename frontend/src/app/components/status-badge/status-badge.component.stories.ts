import type { Meta, StoryObj } from '@storybook/angular';
import { StatusBadgeComponent } from './status-badge.component';

const meta: Meta<StatusBadgeComponent> = {
  title: 'Components/StatusBadge',
  component: StatusBadgeComponent,
  tags: ['autodocs'],
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
    trueClass: 'text-green',
    falseClass: 'text-red',
  },
};

export const BooleanFalse: Story = {
  name: 'Ollama unavailable',
  args: {
    label: 'Ollama',
    state: false,
    trueText: 'Connected',
    falseText: 'Unavailable',
    trueClass: 'text-green',
    falseClass: 'text-red',
  },
};

export const NetworkWarning: Story = {
  name: 'Network external detected',
  args: {
    label: 'Network',
    state: false,
    trueText: 'Local Only',
    falseText: 'External Detected',
    trueClass: 'text-green',
    falseClass: 'text-yellow',
  },
};
