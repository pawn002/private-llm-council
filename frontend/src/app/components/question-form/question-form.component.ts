import { Component, signal, output } from '@angular/core';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-question-form',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './question-form.component.html',
  styleUrls: ['./question-form.component.scss'],
})
export class QuestionFormComponent {
  readonly submitted = output<string>();
  readonly loadClicked = output<void>();

  readonly question = signal('');

  updateQuestion(value: string): void {
    this.question.set(value);
  }

  onSubmit(): void {
    const q = this.question().trim();
    if (q) {
      this.submitted.emit(q);
      this.question.set('');
    }
  }

  onLoadClick(): void {
    this.loadClicked.emit();
  }
}
