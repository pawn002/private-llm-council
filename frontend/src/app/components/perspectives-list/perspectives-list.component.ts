import { Component, input, signal } from '@angular/core';
import { Perspective, FailedPerspective } from '../../models';
import { PerspectiveCardComponent } from '../perspective-card/perspective-card.component';
import { FailedPerspectiveCardComponent } from '../failed-perspective-card/failed-perspective-card.component';

@Component({
  selector: 'app-perspectives-list',
  standalone: true,
  imports: [PerspectiveCardComponent, FailedPerspectiveCardComponent],
  templateUrl: './perspectives-list.component.html',
  styleUrls: ['./perspectives-list.component.scss'],
})
export class PerspectivesListComponent {
  readonly perspectives = input.required<Perspective[]>();
  readonly failedMembers = input<FailedPerspective[]>([]);

  readonly expandedPerspective = signal<string | null>(null);

  togglePerspective(memberId: string): void {
    this.expandedPerspective.update(current =>
      current === memberId ? null : memberId
    );
  }
}
