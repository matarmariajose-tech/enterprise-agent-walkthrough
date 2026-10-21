import './styles.css';
import { details } from './data/details';
import { tour as tourSteps } from './data/tour';
import type { TourStep, ViewId } from './domain/types';
import { DetailModal } from './ui/modal';
import { renderApp } from './ui/template';
import { GuidedTour, type TourRenderer } from './ui/tour';
import { TraceRunner } from './ui/trace-runner';

const app = document.querySelector<HTMLElement>('#app');
if (!app) throw new Error('Application root not found');
app.innerHTML = renderApp();

const showView = (view: ViewId): void => {
  app.querySelectorAll('[data-view-panel]').forEach((panel) => panel.classList.toggle('active', panel.getAttribute('data-view-panel') === view));
  app.querySelectorAll('[data-view]').forEach((tab) => {
    const selected = tab.getAttribute('data-view') === view;
    tab.classList.toggle('active', selected);
    tab.setAttribute('aria-pressed', String(selected));
  });
};

const modal = new DetailModal(app);
app.querySelectorAll<HTMLElement>('[data-detail]').forEach((element) => {
  element.addEventListener('click', () => {
    const id = element.dataset.detail;
    const detail = id ? details[id] : undefined;
    if (detail) modal.open(detail);
  });
});

app.querySelectorAll<HTMLElement>('[data-view]').forEach((tab) => {
  tab.addEventListener('click', () => showView(tab.dataset.view as ViewId));
});

const renderer: TourRenderer = {
  showView,
  highlight(target?: string) {
    app.querySelectorAll('.tour-highlight').forEach((element) => element.classList.remove('tour-highlight'));
    if (!target) return;
    const element = app.querySelector<HTMLElement>(`[data-target="${target}"]`);
    element?.classList.add('tour-highlight');
    element?.scrollIntoView({ behavior: 'smooth', block: 'center' });
  },
  renderStep(step: TourStep, index: number, total: number) {
    const banner = app.querySelector<HTMLElement>('[data-role="tour-banner"]');
    const title = app.querySelector<HTMLElement>('[data-role="tour-title"]');
    const summary = app.querySelector<HTMLElement>('[data-role="tour-summary"]');
    const progress = app.querySelector<HTMLElement>('[data-role="progress"]');
    if (!banner || !title || !summary || !progress) throw new Error('Tour UI is incomplete');
    banner.classList.add('show');
    title.textContent = step.title;
    summary.textContent = step.summary;
    progress.style.width = `${((index + 1) / total) * 100}%`;
  },
  reset() {
    showView('discovery');
    app.querySelector('[data-role="tour-banner"]')?.classList.remove('show');
    app.querySelectorAll('.tour-highlight').forEach((element) => element.classList.remove('tour-highlight'));
    const progress = app.querySelector<HTMLElement>('[data-role="progress"]');
    if (progress) progress.style.width = '0';
  }
};

const tour = new GuidedTour(tourSteps, renderer);
app.querySelectorAll('[data-action="next-tour"]').forEach((button) => button.addEventListener('click', () => tour.next()));
app.querySelector('[data-action="reset-tour"]')?.addEventListener('click', () => tour.reset());

const traceRunner = new TraceRunner(app);
app.querySelector('[data-action="execute"]')?.addEventListener('click', () => {
  void traceRunner.run().catch(() => {
    const status = app.querySelector<HTMLElement>('[data-role="trace-status"]');
    if (status) status.textContent = 'failed · retry the simulation';
  });
});
