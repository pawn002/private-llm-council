import type { Meta, StoryObj } from '@storybook/angular';
import { QuestionHeaderComponent } from './question-header.component';
import { Deliberation } from '../../models';

const meta: Meta<QuestionHeaderComponent> = {
  title: 'Council/Deliberation/Question Header',
  component: QuestionHeaderComponent,
  tags: ['autodocs'],
};
export default meta;
type Story = StoryObj<QuestionHeaderComponent>;

const baseDeliberation: Deliberation = {
  id: 'del-001',
  question: 'What are the long-term societal implications of widespread AI adoption in knowledge work?',
  perspectives: [
    { member_id: 'phi', model: 'llama3.2:3b', character: 'empiricist', content: '...', timestamp: new Date().toISOString() },
    { member_id: 'psi', model: 'mistral:7b', character: 'rationalist', content: '...', timestamp: new Date().toISOString() },
    { member_id: 'omega', model: 'qwen2.5:3b', character: 'pragmatist', content: '...', timestamp: new Date().toISOString() },
  ],
  critiques: [],
  synthesis: { content: '', consensus_points: [], divisions: [], unique_insights: [] },
  disagreements: [{ topic: 'Economic impact', positions: {}, description: '', severity: 'moderate' }],
  minority_reports: [],
  timestamp: new Date(Date.now() - 3600_000).toISOString(),
  session_id: 'sess-001',
};

export const AllPerspectives: Story = {
  args: { deliberation: baseDeliberation },
};

export const WithFailedMembers: Story = {
  args: {
    deliberation: {
      ...baseDeliberation,
      failed_members: [
        { member_id: 'sigma', model: 'phi3:mini', character: 'synthesist', error_type: 'timeout', error_message: 'Timed out.', timestamp: new Date().toISOString(), attempted_retries: 2 },
      ],
    },
  },
};
