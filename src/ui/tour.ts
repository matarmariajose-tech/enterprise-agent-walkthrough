import type { TourStep, ViewId } from '../domain/types';

export interface TourRenderer {
  showView(view: ViewId): void;
  highlight(target?: string): void;
  renderStep(step: TourStep, index: number, total: number): void;
  reset(): void;
}

export class GuidedTour {
  #index = -1;
  constructor(private readonly steps: readonly TourStep[], private readonly renderer: TourRenderer) {}

  next(): void {
    this.#index = (this.#index + 1) % this.steps.length;
    const step = this.steps[this.#index];
    if (!step) throw new Error('Tour configuration is empty');
    this.renderer.showView(step.view);
    this.renderer.highlight(step.target);
    this.renderer.renderStep(step, this.#index, this.steps.length);
  }

  reset(): void {
    this.#index = -1;
    this.renderer.reset();
  }
}
