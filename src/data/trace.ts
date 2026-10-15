import type { TraceSpan } from '../domain/types';

export const traceSpans: readonly TraceSpan[] = [
  { id: 'auth', offset: '+000 ms', name: 'auth.resolve_context', summary: 'subject · tenant · permissions' },
  { id: 'retrieval', offset: '+028 ms', name: 'retrieval.query', summary: 'ACL → hybrid search → rerank' },
  { id: 'route', offset: '+163 ms', name: 'orchestrator.route', summary: 'payments.failure_summary' },
  { id: 'schema', offset: '+391 ms', name: 'tool.validate_input', summary: 'region=LATAM · window=24h' },
  { id: 'api', offset: '+403 ms', name: 'payments.failure_summary', summary: 'aggregate only · PII excluded' },
  { id: 'policy', offset: '+644 ms', name: 'policy.evaluate_threshold', summary: 'deterministic comparison' },
  { id: 'action', offset: '+658 ms', name: 'workflow.prepare_alert', summary: 'proposed · approval required' }
];
