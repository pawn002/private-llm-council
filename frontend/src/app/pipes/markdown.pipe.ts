import { Pipe, PipeTransform, inject } from '@angular/core';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';
import { marked } from 'marked';

@Pipe({ name: 'markdown', standalone: true })
export class MarkdownPipe implements PipeTransform {
  private sanitizer = inject(DomSanitizer);

  transform(value: string | null | undefined, inline = false): SafeHtml {
    if (!value) return '';
    const html = inline
      ? marked.parseInline(value) as string
      : marked.parse(value) as string;
    return this.sanitizer.sanitize(2 /* SecurityContext.HTML */, html) ?? '';
  }
}
