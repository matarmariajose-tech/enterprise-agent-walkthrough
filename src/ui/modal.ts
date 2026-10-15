import type { Detail } from '../domain/types';

const select = <T extends Element>(root: ParentNode, selector: string): T => {
  const element = root.querySelector<T>(selector);
  if (!element) throw new Error(`Missing required element: ${selector}`);
  return element;
};

export class DetailModal {
  readonly #dialog: HTMLDialogElement;

  constructor(root: ParentNode) {
    this.#dialog = select<HTMLDialogElement>(root, '[data-role="modal"]');
    select(root, '[data-action="close-modal"]').addEventListener('click', () => this.close());
    this.#dialog.addEventListener('click', (event) => {
      if (event.target === this.#dialog) this.close();
    });
  }

  open(detail: Detail): void {
    const set = (role: string, value: string): void => {
      select(this.#dialog, `[data-role="${role}"]`).textContent = value;
    };
    set('modal-category', detail.category);
    set('modal-title', detail.title);
    set('modal-observation', detail.observation);
    set('modal-input', detail.input);
    set('modal-output', detail.output);
    set('modal-decision', detail.decision);
    set('modal-failure', detail.failureBehavior);
    set('modal-signal', detail.engineeringSignal);
    this.#dialog.showModal();
  }

  close(): void {
    this.#dialog.close();
  }
}
