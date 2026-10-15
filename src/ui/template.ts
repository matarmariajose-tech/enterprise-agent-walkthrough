import { traceSpans } from '../data/trace';

const node = (id: string, kind: string, title: string, meta: string, className = '') => `
  <button class="node ${className}" data-detail="${id}" data-target="${id}">
    <b>${kind}</b><strong>${title}</strong><small>${meta}</small>
  </button>`;

export function renderApp(): string {
  const spans = traceSpans.map((span) => `
    <button class="trace-row" data-span="${span.id}">
      <span>${span.offset}</span><strong>${span.name}</strong><small>${span.summary}</small><em>pending</em>
    </button>`).join('');

  return `
    <header class="header">
      <div class="brand"><div class="mark">AP</div><div><h1>Enterprise Agent Runtime</h1><p>Interactive architecture walkthrough · sanitized reconstruction</p></div></div>
      <div class="badges"><span>ENV: DEMO</span><span>TRACE: ENABLED</span><span class="safe">CLIENT DATA: NONE</span></div>
    </header>
    <main class="shell">
      <nav class="nav">
        <div class="tabs">
          <button class="tab active" data-view="discovery">1. Discovery</button>
          <button class="tab" data-view="architecture">2. Architecture</button>
          <button class="tab" data-view="execution">3. Execution</button>
          <button class="tab" data-view="incident">4. Failure analysis</button>
        </div>
        <div class="tour-controls"><button data-action="reset-tour">Reset</button><button class="primary" data-action="next-tour">Start guided path</button></div>
      </nav>
      <div class="progress"><div data-role="progress"></div></div>
      <aside class="tour-banner" data-role="tour-banner"><div><strong data-role="tour-title"></strong><span data-role="tour-summary"></span></div><button data-action="next-tour">Next step</button></aside>

      <section class="view active" data-view-panel="discovery">
        <div class="page-head"><span>01 · Discovery</span><h2>Translate an ambiguous chatbot request into system requirements</h2><p>Business language described outcomes. Architecture work identified actors, trust boundaries, state ownership and measurable failure modes.</p></div>
        <div class="discovery-grid">
          <article class="card"><header>Initial request</header><div class="body"><blockquote>“We need a chatbot that can answer internal questions, generate reports, identify issues and execute actions in existing systems.”</blockquote><div class="capabilities"><span>Internal knowledge</span><span>Reports and alerts</span><span>Multiple user types</span><span>Action history</span></div></div></article>
          <article class="card"><header>Requirements identified</header><div class="body gaps">
            <button data-detail="gap-auth" data-target="gap-auth"><strong>Identity and authorization were undefined</strong><small>Who can retrieve which source or execute each operation?</small></button>
            <button data-detail="gap-tools" data-target="gap-tools"><strong>Capabilities had no explicit boundaries</strong><small>What is read-only and what creates a side effect?</small></button>
            <button data-detail="gap-evaluation"><strong>There was no semantic success model</strong><small>How do we detect weak evidence or wrong routing?</small></button>
          </div></article>
        </div>
      </section>

      <section class="view" data-view-panel="architecture">
        <div class="page-head"><span>02 · Runtime architecture</span><h2>Separate reasoning, control, execution and state</h2><p>Observability and state are transversal planes. They are intentionally outside the synchronous decision path.</p></div>
        <div class="architecture">
          <div class="request-path">
            ${node('identity', 'Control', 'OIDC / RBAC', 'subject · tenant · resource scope', 'control')}
            <i>→</i>${node('orchestrator', 'Coordination', 'Agent Orchestrator', 'intent · plan · capability selection')}
            <i>→</i>${node('policy', 'Control', 'Policy Engine', 'authorize · evidence · side effects', 'control')}
            <i>→</i>${node('tools', 'Execution', 'MCP Tool Gateway', 'schema · timeout · retry class')}
          </div>
          <div class="secondary-path">
            ${node('retrieval', 'Read path', 'Retrieval Service', 'ACL · hybrid search · provenance')}
            ${node('workflow', 'State machine', 'Action Workflow', 'proposed → approved → executed')}
          </div>
          <button class="plane observability" data-detail="observability" data-target="observability"><strong>OBSERVABILITY PLANE</strong><span>OpenTelemetry spans · structured logs · evaluations · redaction · correlation_id</span></button>
          <button class="plane state" data-detail="state" data-target="state"><strong>STATE PLANE</strong><span>PostgreSQL · evidence references · action versions · immutable audit events</span></button>
        </div>
      </section>

      <section class="view" data-view-panel="execution">
        <div class="page-head"><span>03 · Execution trace</span><h2>Evidence-backed analysis with a controlled side effect</h2><p>The request is synthetic. Execute it to inspect the complete runtime path.</p></div>
        <div class="execution-grid">
          <article class="card"><header>Request envelope</header><div class="body"><dl><div><dt>Subject</dt><dd>user:ops_manager</dd></div><div><dt>Scope</dt><dd>region:LATAM</dd></div><div><dt>Trace</dt><dd>demo_8f21</dd></div><div><dt>Policy</dt><dd>explicit_approval</dd></div></dl><blockquote>Analyze failed payment activity from the last 24 hours and prepare an alert if the documented threshold was exceeded.</blockquote><button class="execute" data-action="execute">Execute request</button></div></article>
          <article class="card"><header>Distributed trace <span data-role="trace-status">idle</span></header><div class="trace-list">${spans}</div><div class="result" data-role="result"><span><small>Finding</small><strong>Threshold exceeded</strong></span><span><small>Evidence</small><strong>Policy + API aggregate</strong></span><span><small>Action</small><strong>Proposed · awaiting approval</strong></span></div></article>
        </div>
      </section>

      <section class="view" data-view-panel="incident">
        <div class="page-head"><span>04 · Failure analysis</span><h2>Diagnose a request that succeeded technically but failed semantically</h2><p>The important failure class was not a crash. The request could complete while its conclusion remained weakly supported.</p></div>
        <div class="incident-flow">
          <button class="incident red" data-detail="incident-symptom" data-target="incident-symptom"><b>Observed behavior</b><strong>Plausible answer, insufficient support</strong><small>Weak retrieval or overlapping tools produced convincing output.</small></button><i>→</i>
          <button class="incident amber" data-detail="incident-diagnosis" data-target="incident-diagnosis"><b>Diagnosis</b><strong>Reconstruct the decision path</strong><small>Inspect ACLs, chunks, routing, arguments, API result and evidence.</small></button><i>→</i>
          <button class="incident green" data-detail="incident-fix" data-target="incident-fix"><b>Remediation</b><strong>Constrain every boundary</strong><small>Map each failure class to a control and verification method.</small></button>
        </div>
        <table><thead><tr><th>Boundary</th><th>Failure</th><th>Control</th><th>Verification</th></tr></thead><tbody>
          <tr><td>Retrieval</td><td>Cross-scope or weak chunks</td><td>ACL before ranking, threshold, provenance</td><td>Retrieval evaluation set</td></tr>
          <tr><td>Routing</td><td>Overlapping capabilities</td><td>Narrow MCP tools</td><td>Tool-selection matrix</td></tr>
          <tr><td>Contracts</td><td>Invalid arguments</td><td>Typed schemas and bounds</td><td>Negative-path tests</td></tr>
          <tr><td>Side effects</td><td>Duplicate action</td><td>State machine and idempotency</td><td>Replay and timeout tests</td></tr>
        </tbody></table>
      </section>
    </main>
    <dialog class="modal" data-role="modal"><header><div><span data-role="modal-category"></span><h3 data-role="modal-title"></h3></div><button data-action="close-modal">×</button></header><div class="modal-grid"><section><h4>What I identified</h4><p data-role="modal-observation"></p><h4>Runtime contract</h4><dl><dt>Input</dt><dd data-role="modal-input"></dd><dt>Output</dt><dd data-role="modal-output"></dd></dl></section><section><h4>Design decision</h4><p data-role="modal-decision"></p><h4>Failure behavior</h4><p data-role="modal-failure"></p><aside data-role="modal-signal"></aside></section></div></dialog>
  `;
}
