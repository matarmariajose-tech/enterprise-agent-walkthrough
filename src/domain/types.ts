export type ViewId = 'discovery' | 'architecture' | 'execution' | 'incident';

export interface Detail {
  readonly category: string;
  readonly title: string;
  readonly observation: string;
  readonly input: string;
  readonly output: string;
  readonly decision: string;
  readonly failureBehavior: string;
  readonly engineeringSignal: string;
}

export interface TourStep {
  readonly view: ViewId;
  readonly target?: string;
  readonly title: string;
  readonly summary: string;
}

export interface TraceSpan {
  readonly id: string;
  readonly offset: string;
  readonly name: string;
  readonly summary: string;
}

export type ActionState = 'idle' | 'proposed' | 'approved' | 'executing' | 'completed' | 'failed';
export type ActionEvent = 'PROPOSE' | 'APPROVE' | 'EXECUTE' | 'COMPLETE' | 'FAIL' | 'RESET';
