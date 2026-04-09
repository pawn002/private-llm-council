import type { Meta, StoryObj } from '@storybook/angular';
import { QuestionFormComponent } from './question-form.component';

const meta: Meta<QuestionFormComponent> = {
  title: 'Council/Question Form',
  component: QuestionFormComponent,
  tags: ['autodocs'],
};
export default meta;
type Story = StoryObj<QuestionFormComponent>;

export const Default: Story = {};
