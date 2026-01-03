import { Component, input } from '@angular/core';

@Component({
  selector: 'app-list-section',
  standalone: true,
  templateUrl: './list-section.component.html',
  styleUrls: ['./list-section.component.scss'],
})
export class ListSectionComponent {
  readonly title = input.required<string>();
  readonly items = input.required<string[]>();
  readonly icon = input<string>('');
  readonly cardClass = input<string>('');
  readonly bulletColor = input<string>('');
}
