import type { Meta, StoryObj } from '@storybook/angular';
import { FooterComponent } from './footer.component';

const meta: Meta<FooterComponent> = {
  title: 'App/Footer',
  component: FooterComponent,
  tags: ['autodocs'],
  argTypes: {
    mode: { control: 'select', options: [null, 'SOVEREIGN', 'SANCTUARY', 'CITADEL'] },
  },
};
export default meta;
type Story = StoryObj<FooterComponent>;

export const Sovereign: Story = {
  args: { mode: 'SOVEREIGN' },
};

export const Sanctuary: Story = {
  args: { mode: 'SANCTUARY' },
};

export const Citadel: Story = {
  args: { mode: 'CITADEL' },
};

export const Loading: Story = {
  args: { mode: null },
};
