import { Component, input, output, computed } from '@angular/core';
import { Deliberation } from '../../models';

@Component({
  selector: 'app-question-header',
  standalone: true,
  templateUrl: './question-header.component.html',
  styleUrls: ['./question-header.component.scss'],
})
export class QuestionHeaderComponent {
  readonly deliberation = input.required<Deliberation>();
  readonly saveClicked = output<void>();
  readonly newQuestion = output<void>();

  readonly formattedTimestamp = computed(() =>
    new Date(this.deliberation().timestamp).toLocaleString(undefined, {
      year: 'numeric', month: 'short', day: 'numeric',
      hour: 'numeric', minute: '2-digit', timeZoneName: 'short',
    })
  );

  readonly totalMembers = computed(() =>
    this.deliberation().perspectives.length + (this.deliberation().failed_members?.length ?? 0)
  );

  readonly failedCount = computed(() => this.deliberation().failed_members?.length ?? 0);
}
