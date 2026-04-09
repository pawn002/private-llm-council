import { Component, input, signal, computed } from '@angular/core';

@Component({
  selector: 'app-footer',
  standalone: true,
  templateUrl: './footer.component.html',
  styleUrls: ['./footer.component.scss'],
})
export class FooterComponent {
  readonly mode = input<string | null>(null);

  readonly theme = signal<'light' | 'dark' | 'system'>(
    (localStorage.getItem('theme') as 'light' | 'dark') ?? 'system'
  );

  readonly isDark = computed(() => {
    if (this.theme() === 'dark') return true;
    if (this.theme() === 'light') return false;
    return window.matchMedia('(prefers-color-scheme: dark)').matches;
  });

  toggleTheme(): void {
    const next = this.isDark() ? 'light' : 'dark';
    this.theme.set(next);
    localStorage.setItem('theme', next);
    document.documentElement.setAttribute('data-theme', next);
  }
}
