import {
  ChangeDetectionStrategy,
  Component,
  effect,
  ElementRef,
  input,
  output,
  viewChild,
  ViewEncapsulation,
} from '@angular/core';

export type ModalSize = 'sm' | 'md' | 'lg';

@Component({
  selector: 'app-modal',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [],
  encapsulation: ViewEncapsulation.None,
  template: `
    <dialog
      #dialog
      class="modal"
      [attr.aria-labelledby]="titleId"
      [attr.aria-modal]="true"
      (click)="onBackdropClick($event)"
      (close)="onDialogClose()"
      (cancel)="onDialogClose()"
    >
      <div [class]="'modal__panel modal__panel--' + size()">
        <!-- role="none" suppresses the implicit banner landmark Chrome assigns to <header>
             inside <dialog> (spec only strips it for article/aside/main/nav/section) -->
        <header class="modal__header" role="none">
          <h2 class="modal__title" [id]="titleId">{{ title() }}</h2>
          <button class="modal__close" type="button" aria-label="Close" (click)="close()">
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none" aria-hidden="true">
              <path d="M15 5L5 15M5 5l10 10" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
          </button>
        </header>

        <!-- tabindex="0" makes the overflow scroll region keyboard-reachable.
             aria-label gives AT users a named stop instead of reading all content verbatim. -->
        <div class="modal__body" tabindex="0" aria-label="Dialog content">
          <ng-content></ng-content>
        </div>

        <ng-content select="[slot=footer]"></ng-content>
      </div>
    </dialog>
  `,
  styleUrls: ['./modal.component.scss'],
})
export class ModalComponent {
  open = input(false);
  title = input('');
  size = input<ModalSize>('md');

  closed = output<void>();

  private dialogRef = viewChild<ElementRef<HTMLDialogElement>>('dialog');

  readonly titleId = `modal-title-${Math.random().toString(36).slice(2, 9)}`;

  constructor() {
    effect(() => {
      const dialog = this.dialogRef()?.nativeElement;
      if (!dialog) return;
      this.open() ? dialog.showModal() : dialog.close();
    });
  }

  close(): void {
    this.dialogRef()?.nativeElement.close();
  }

  onDialogClose(): void {
    this.closed.emit();
  }

  onBackdropClick(event: MouseEvent): void {
    if (event.target === this.dialogRef()?.nativeElement) {
      this.close();
    }
  }
}
