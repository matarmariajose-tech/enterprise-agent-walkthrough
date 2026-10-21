import { transitionAction } from '../domain/action-machine';
import type { ActionState } from '../domain/types';

export class TraceRunner {
  #running = false;
  #actionState: ActionState = 'idle';

  constructor(private readonly root: HTMLElement, private readonly delayMs = 380) {}

  async run(): Promise<void> {
    if (this.#running) return;
    const rows = [...this.root.querySelectorAll<HTMLElement>('.trace-row')];
    const status = this.root.querySelector<HTMLElement>('[data-role="trace-status"]');
    const result = this.root.querySelector<HTMLElement>('[data-role="result"]');
    if (!status || !result) throw new Error('Trace UI is incomplete');

    this.#running = true;
    try {
      this.#actionState = transitionAction(this.#actionState, 'RESET');
      this.#actionState = transitionAction(this.#actionState, 'PROPOSE');
      status.textContent = 'running';
      result.classList.remove('show');
      rows.forEach((row) => {
        row.classList.remove('running', 'done');
        const state = row.querySelector('em');
        if (state) state.textContent = 'pending';
      });

      for (const row of rows) {
        row.classList.add('running');
        const state = row.querySelector('em');
        if (state) state.textContent = 'running';
        await new Promise((resolve) => window.setTimeout(resolve, this.delayMs));
        row.classList.remove('running');
        row.classList.add('done');
        if (state) state.textContent = 'ok';
      }

      result.classList.add('show');
      status.textContent = `completed · action ${this.#actionState}`;
    } catch (error) {
      result.classList.remove('show');
      status.textContent = 'failed · simulation interrupted';
      throw error;
    } finally {
      rows.forEach((row) => row.classList.remove('running'));
      this.#running = false;
    }
  }
}
