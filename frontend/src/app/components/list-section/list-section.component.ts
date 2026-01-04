import { Component, input, computed } from '@angular/core';

@Component({
  selector: 'app-list-section',
  standalone: true,
  templateUrl: './list-section.component.html',
  styleUrls: ['./list-section.component.scss'],
})
export class ListSectionComponent {
  readonly title = input.required<string>();
  readonly items = input<string[] | null>([]);
  readonly icon = input<string>('');
  readonly cardClass = input<string>('');
  readonly bulletColor = input<string>('');

  // Safe accessor that guarantees an array (handles null/undefined edge cases)
  readonly safeItems = computed(() => this.items() ?? []);
}
