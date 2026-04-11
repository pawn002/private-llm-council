import { Component, input } from '@angular/core';
import { MinorityReport } from '../../models';
import { MarkdownPipe } from '../../pipes/markdown.pipe';

@Component({
  selector: 'app-minority-item',
  standalone: true,
  imports: [MarkdownPipe],
  templateUrl: './minority-item.component.html',
  styleUrls: ['./minority-item.component.scss'],
})
export class MinorityItemComponent {
  readonly report = input.required<MinorityReport>();
}
