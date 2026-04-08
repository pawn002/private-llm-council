import type { Meta, StoryObj } from '@storybook/angular';
import { PerspectiveCardComponent } from './perspective-card.component';
import { Perspective } from '../../models';

const meta: Meta<PerspectiveCardComponent> = {
  title: 'Components/PerspectiveCard',
  component: PerspectiveCardComponent,
  tags: ['autodocs'],
  argTypes: {
    isExpanded: { control: 'boolean' },
  },
};
export default meta;
type Story = StoryObj<PerspectiveCardComponent>;

const basePerspective: Perspective = {
  member_id: 'phi',
  model: 'llama3.2:3b',
  character: 'empiricist',
  content: `## Assessment

From an empirical standpoint, the evidence strongly supports this conclusion. The data collected across multiple independent studies demonstrates a consistent pattern.

**Key findings:**

- Three separate meta-analyses confirm the primary hypothesis
- Effect sizes range from moderate (d=0.4) to large (d=0.8)
- No significant publication bias detected via funnel plot analysis

### Limitations

The available longitudinal data remains sparse. We should be cautious about extrapolating beyond the observed time horizon of 18 months.

Further controlled trials are warranted before drawing firm policy conclusions.`,
  timestamp: new Date().toISOString(),
};

export const Collapsed: Story = {
  args: {
    perspective: basePerspective,
    isExpanded: false,
  },
};

export const Expanded: Story = {
  args: {
    perspective: basePerspective,
    isExpanded: true,
  },
};

export const PsiMember: Story = {
  name: 'Psi — rationalist',
  args: {
    perspective: {
      ...basePerspective,
      member_id: 'psi',
      character: 'rationalist',
      model: 'mistral:7b',
      content: `## Logical Analysis

The argument presented contains a valid deductive structure. However, **premise two is contentious** and requires independent justification.

### Formal Structure

1. If A then B
2. A is the case
3. Therefore B

The issue lies in establishing premise (2) without circular reasoning. The empirical support cited conflates correlation with causation — a category error.

> A rational framework demands we separate descriptive claims from normative ones before drawing conclusions.

Until this distinction is addressed, the conclusion remains unsupported.`,
    },
    isExpanded: true,
  },
};

export const OmegaMember: Story = {
  name: 'Omega — pragmatist',
  args: {
    perspective: {
      ...basePerspective,
      member_id: 'omega',
      character: 'pragmatist',
      model: 'qwen2.5:3b',
      content: `## Practical Considerations

What matters here is **what works in practice**. Theoretical elegance is secondary to real-world outcomes.

The proposal has three actionable components:

- **Immediate**: Deploy the existing solution with monitoring
- **Short-term**: Gather feedback over 90 days
- **Long-term**: Iterate based on measured outcomes

### Risk Assessment

The downside is bounded. Worst case, we roll back in 2 weeks. The upside — if it works — is substantial efficiency gains for all stakeholders.

Waiting for perfect certainty is itself a decision with costs.`,
    },
    isExpanded: true,
  },
};
