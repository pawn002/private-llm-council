import type { Meta, StoryObj } from '@storybook/angular';
import { ListSectionComponent } from './list-section.component';

const meta: Meta<ListSectionComponent> = {
  title: 'Council/Deliberation/Synthesis/List Section',
  component: ListSectionComponent,
  tags: ['autodocs'],
  argTypes: {
    bulletColor: { control: 'select', options: ['green', 'yellow', 'purple', ''] },
  },
};
export default meta;
type Story = StoryObj<ListSectionComponent>;

const sampleItems = [
  'All members agree the current evidence base is insufficient for strong policy conclusions.',
  'There is consensus that longitudinal data collection should be prioritised.',
  'The council unanimously endorses a staged pilot approach with defined success metrics.',
];

export const Consensus: Story = {
  args: {
    heading: 'Points of Agreement',
    icon: '✓',
    items: sampleItems,
    cardClass: 'consensus-card',
    bulletColor: 'green',
  },
};

export const Divisions: Story = {
  args: {
    heading: 'Areas of Division',
    icon: '⚡',
    items: [
      'Phi and Psi disagree on whether correlation-based evidence is admissible.',
      'The weighting of short-term vs long-term outcomes remains contested.',
    ],
    cardClass: 'divisions-card',
    bulletColor: 'yellow',
  },
};

export const Insights: Story = {
  args: {
    heading: 'Unique Insights',
    icon: '💡',
    items: [
      'Omega uniquely highlighted the resource asymmetry across deployment contexts.',
      'Sigma introduced a novel framing based on warranted assertability rather than truth.',
    ],
    cardClass: 'insights-card',
    bulletColor: 'purple',
  },
};

export const Empty: Story = {
  args: {
    heading: 'Points of Agreement',
    icon: '✓',
    items: [],
    bulletColor: 'green',
  },
};
