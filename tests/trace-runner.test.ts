import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { TraceRunner } from '../src/ui/trace-runner';

describe('trace simulation', () => {
  let root: HTMLElement;

  beforeEach(() => {
    vi.useFakeTimers();
    document.body.innerHTML = `
      <main>
        <span data-role="trace-status">idle</span>
        <div class="trace-row"><em>pending</em></div>
        <div class="trace-row"><em>pending</em></div>
        <div data-role="result"></div>
      </main>`;
    root = document.querySelector('main')!;
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  async function complete(runner: TraceRunner): Promise<void> {
    const pending = runner.run();
    await vi.runAllTimersAsync();
    await pending;
  }

  it('can complete consecutive runs without carrying over action state', async () => {
    const runner = new TraceRunner(root, 5);
    await complete(runner);
    await complete(runner);
    expect(root.querySelector('[data-role="trace-status"]')?.textContent)
      .toBe('completed · action proposed');
    expect(root.querySelectorAll('.trace-row.done')).toHaveLength(2);
    expect(root.querySelectorAll('.running')).toHaveLength(0);
    expect(root.querySelector('[data-role="result"]')?.classList.contains('show')).toBe(true);
  });

  it('ignores a second click while the simulation is running', async () => {
    const runner = new TraceRunner(root, 5);
    const first = runner.run();
    await runner.run();
    expect(root.querySelector('[data-role="trace-status"]')?.textContent).toBe('running');
    await vi.runAllTimersAsync();
    await first;
    expect(root.querySelectorAll('.trace-row.done')).toHaveLength(2);
  });

  it('can recover after incomplete markup is repaired', async () => {
    const runner = new TraceRunner(root, 5);
    const result = root.querySelector('[data-role="result"]')!;
    result.remove();
    await expect(runner.run()).rejects.toThrow('Trace UI is incomplete');
    root.appendChild(result);
    await complete(runner);
    expect(result.classList.contains('show')).toBe(true);
  });

  it('releases its running flag after a rendering error', async () => {
    const runner = new TraceRunner(root, 5);
    const row = root.querySelector<HTMLElement>('.trace-row')!;
    const fault = vi.spyOn(row.classList, 'add').mockImplementationOnce(() => {
      throw new Error('DOM unavailable');
    });
    await expect(runner.run()).rejects.toThrow('DOM unavailable');
    expect(root.querySelector('[data-role="result"]')?.classList.contains('show')).toBe(false);
    expect(root.querySelectorAll('.running')).toHaveLength(0);
    fault.mockRestore();
    await complete(runner);
    expect(root.querySelector('[data-role="result"]')?.classList.contains('show')).toBe(true);
  });
});
