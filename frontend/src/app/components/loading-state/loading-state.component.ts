import { Component, input, output, computed } from '@angular/core';
import { DeliberationPhase } from '../../models';

/**
 * Reusable loading state component for deliberation phases.
 */
@Component({
  selector: 'app-loading-state',
  standalone: true,
  templateUrl: './loading-state.component.html',
  styleUrls: ['./loading-state.component.scss'],
})
export class LoadingStateComponent {
  /** Current deliberation phase */
  readonly phase = input.required<DeliberationPhase>();

  /** Status message to display */
  readonly statusMessage = input<string>('');

  /** Elapsed time in seconds */
  readonly elapsedSeconds = input<number>(0);

  /** Whether Ollama is busy processing other requests */
  readonly ollamaBusy = input<boolean>(false);

  /** Emits when cancel is clicked */
  readonly cancel = output<void>();

  /** Phases in order for progress indicator */
  readonly phases: DeliberationPhase[] = ['gathering', 'reviewing', 'synthesizing', 'analyzing'];

  readonly phaseIcons: Record<DeliberationPhase, string> = {
    idle: 'ph-fill ph-chat-dots',
    gathering: 'ph-fill ph-users',
    reviewing: 'ph-fill ph-magnifying-glass',
    synthesizing: 'ph-fill ph-scales',
    analyzing: 'ph-fill ph-chart-bar',
    complete: 'ph-fill ph-check-circle',
    error: 'ph-fill ph-x-circle',
  };

  readonly phaseMessages: Record<DeliberationPhase, string> = {
    idle: 'Ready',
    gathering: 'Gathering Perspectives',
    reviewing: 'Peer Review',
    synthesizing: 'Synthesizing',
    analyzing: 'Deep Analysis',
    complete: 'Complete',
    error: 'Error',
  };

  readonly elapsedTime = computed(() => {
    const seconds = this.elapsedSeconds();
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return mins > 0 ? `${mins}m ${secs}s` : `${secs}s`;
  });

  readonly currentPhaseIndex = computed(() => this.phases.indexOf(this.phase()));

  onCancel(): void {
    this.cancel.emit();
  }
}
