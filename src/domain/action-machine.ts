import type { ActionEvent, ActionState } from './types';

const transitions: Readonly<Record<ActionState, Partial<Record<ActionEvent, ActionState>>>> = {
  idle: { PROPOSE: 'proposed', RESET: 'idle' },
  proposed: { APPROVE: 'approved', RESET: 'idle' },
  approved: { EXECUTE: 'executing', RESET: 'idle' },
  executing: { COMPLETE: 'completed', FAIL: 'failed', RESET: 'idle' },
  completed: { RESET: 'idle' },
  failed: { RESET: 'idle' }
};

export function transitionAction(current: ActionState, event: ActionEvent): ActionState {
  const next = transitions[current][event];
  if (!next) throw new Error(`Invalid action transition: ${current} -> ${event}`);
  return next;
}
