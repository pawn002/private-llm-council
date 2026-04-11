import type { Meta, StoryObj } from '@storybook/angular';
import { ConsentBannerComponent } from './consent-banner.component';
import { PrivacyStatus } from '../../models';

const meta: Meta<ConsentBannerComponent> = {
  title: 'App/Consent Banner',
  component: ConsentBannerComponent,
  tags: ['autodocs'],
  argTypes: {
    loading: { control: 'boolean' },
  },
};
export default meta;
type Story = StoryObj<ConsentBannerComponent>;

const sovereignStatus: PrivacyStatus = {
  mode: { mode: 'SOVEREIGN', description: 'Fully air-gapped, no external network.' },
  network_status: { external_reachable: false, ollama_reachable: true, local_only: true },
  warnings: [],
  verified: true,
};

const citadelStatus: PrivacyStatus = {
  mode: { mode: 'CITADEL', description: 'Docker-isolated, Ollama via host bridge.' },
  network_status: { external_reachable: true, ollama_reachable: true, local_only: false },
  warnings: ['External network is reachable. Ensure no exfiltration paths exist.'],
  verified: true,
};

export const Sovereign: Story = {
  args: { status: sovereignStatus, loading: false },
};

export const CitadelWithWarning: Story = {
  name: 'Citadel — with warning',
  args: { status: citadelStatus, loading: false },
};

export const Loading: Story = {
  args: { status: null, loading: true },
};

export const StatusError: Story = {
  name: 'Status unavailable',
  args: { status: null, loading: false },
};
