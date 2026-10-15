import type { TourStep } from '../domain/types';

export const tour: readonly TourStep[] = [
  { view: 'discovery', target: 'gap-auth', title: '1. Start with the missing control model', summary: 'Translate a broad chatbot request into actors, permissions, capabilities, state and failure criteria.' },
  { view: 'discovery', target: 'gap-tools', title: '2. Separate answers from actions', summary: 'Knowledge retrieval, read operations and side effects require different contracts.' },
  { view: 'architecture', target: 'identity', title: '3. Put identity before intelligence', summary: 'Resolve authorization before retrieval or capability discovery.' },
  { view: 'architecture', target: 'retrieval', title: '4. Make retrieval permission-aware', summary: 'Filter access before ranking and preserve provenance with evidence.' },
  { view: 'architecture', target: 'orchestrator', title: '5. Constrain model responsibility', summary: 'The model coordinates intent; deterministic services enforce business behavior.' },
  { view: 'architecture', target: 'tools', title: '6. Turn capabilities into typed contracts', summary: 'MCP tools are narrow, validated and explicit about side effects and retries.' },
  { view: 'architecture', target: 'workflow', title: '7. Model side effects as state transitions', summary: 'Proposal, approval and execution are separate versioned operations.' },
  { view: 'architecture', target: 'observability', title: '8. Keep observability transversal', summary: 'Every boundary emits correlated spans without putting telemetry in the decision path.' },
  { view: 'architecture', target: 'state', title: '9. Separate conversation and operational state', summary: 'Persist evidence, action versions and audit events in a transactional model.' },
  { view: 'execution', title: '10. Execute the controlled request', summary: 'Show the complete path from identity through a proposed, approval-gated action.' },
  { view: 'incident', target: 'incident-symptom', title: '11. Explain the difficult failure', summary: 'A technically successful request can still produce a weakly supported conclusion.' },
  { view: 'incident', target: 'incident-diagnosis', title: '12. Diagnose the whole decision chain', summary: 'Use evidence ids and correlated spans to locate the responsible boundary.' },
  { view: 'incident', target: 'incident-fix', title: '13. Apply layered remediation', summary: 'Map each failure class to a control and a verification method.' }
];
