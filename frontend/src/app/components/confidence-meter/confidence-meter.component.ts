import { Component, input, computed } from '@angular/core';

@Component({
  selector: 'app-confidence-meter',
  standalone: true,
  templateUrl: './confidence-meter.component.html',
  styleUrls: ['./confidence-meter.component.scss'],
})
export class ConfidenceMeterComponent {
  readonly label = input.required<string>();
  readonly value = input.required<number>();

  readonly percentage = computed(() => Math.round(this.value() * 100));

  readonly colorClass = computed(() => {
    const v = this.value();
    if (v >= 0.7) return 'bg-green';
    if (v >= 0.4) return 'bg-yellow';
    return 'bg-red';
  });
}
