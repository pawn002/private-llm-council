import { ChangeDetectionStrategy, Component, input, ViewEncapsulation } from '@angular/core';

type ArticleFont = 'reading' | 'sans';

@Component({
  selector: 'app-article',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `<ng-content></ng-content>`,
  styleUrls: ['./article.component.scss'],
  encapsulation: ViewEncapsulation.None,
  host: {
    '[class]': '"article article--font-" + font()',
  },
})
export class ArticleComponent {
  font = input<ArticleFont>('reading');
}
