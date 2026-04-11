import type { Meta, StoryObj } from '@storybook/angular';
import { ConfidenceMeterComponent } from './confidence-meter.component';

const meta: Meta<ConfidenceMeterComponent> = {
  title: 'Council/Deliberation/Synthesis/Confidence Meter',
  component: ConfidenceMeterComponent,
  tags: ['autodocs'],
  argTypes: {
    colorMode: { control: 'radio', options: ['evaluative', 'neutral'] },
    value: { control: { type: 'range', min: 0, max: 1, step: 0.05 } },
  },
};
export default meta;
type Story = StoryObj<ConfidenceMeterComponent>;

export const HighQuality: Story = {
  args: { label: 'Synthesis Quality', value: 0.85, colorMode: 'evaluative' },
};

export const MediumQuality: Story = {
  args: { label: 'Synthesis Quality', value: 0.55, colorMode: 'evaluative' },
};

export const LowQuality: Story = {
  args: { label: 'Synthesis Quality', value: 0.25, colorMode: 'evaluative' },
};

export const NeutralHigh: Story = {
  name: 'Neutral — high dissent',
  args: { label: 'Dissent Strength', value: 0.8, colorMode: 'neutral' },
};

export const NeutralLow: Story = {
  name: 'Neutral — low dissent',
  args: { label: 'Dissent Strength', value: 0.2, colorMode: 'neutral' },
};
