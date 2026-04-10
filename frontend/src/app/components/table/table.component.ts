import { ChangeDetectionStrategy, Component, input, ViewEncapsulation } from '@angular/core';

@Component({
  selector: 'app-table',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  encapsulation: ViewEncapsulation.None,
  template: `<ng-content></ng-content>`,
  styleUrls: ['./table.component.scss'],
  host: { class: 'table-host', '[class.table-host--compact]': 'compact()' },
})
export class TableComponent {
  // Compact reduces cell padding — suits dense data panels like the Measurements card.
  compact = input(false);
}
