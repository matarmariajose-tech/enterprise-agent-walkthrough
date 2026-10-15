import { describe, expect, it } from 'vitest';
import { transitionAction } from '../src/domain/action-machine';

describe('action state machine', () => {
  it('requires approval before execution', () => {
    const proposed = transitionAction('idle', 'PROPOSE');
    expect(proposed).toBe('proposed');
    expect(() => transitionAction(proposed, 'EXECUTE')).toThrow(/Invalid action transition/);
  });

  it('supports the successful action lifecycle', () => {
    let state = transitionAction('idle', 'PROPOSE');
    state = transitionAction(state, 'APPROVE');
    state = transitionAction(state, 'EXECUTE');
    state = transitionAction(state, 'COMPLETE');
    expect(state).toBe('completed');
  });

  it('can reset a failed action without skipping state checks', () => {
    let state = transitionAction('approved', 'EXECUTE');
    state = transitionAction(state, 'FAIL');
    expect(transitionAction(state, 'RESET')).toBe('idle');
  });
});
