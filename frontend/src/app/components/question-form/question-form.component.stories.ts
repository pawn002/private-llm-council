import type { Meta, StoryObj } from '@storybook/angular';
import { QuestionFormComponent } from './question-form.component';

const meta: Meta<QuestionFormComponent> = {
  title: 'Council/Question Form',
  component: QuestionFormComponent,
  tags: ['autodocs'],
};
export default meta;
type Story = StoryObj<QuestionFormComponent>;

export const Default: Story = {
  name: 'Empty (button disabled)',
};

export const WithQuestion: Story = {
  name: 'With question (button enabled)',
  play: async ({ canvasElement }) => {
    const textarea = canvasElement.querySelector('textarea')!;
    textarea.value = 'What are the long-term societal implications of widespread AI adoption in knowledge work?';
    textarea.dispatchEvent(new Event('input', { bubbles: true }));
  },
};
