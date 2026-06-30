"use client";

import { useMemo, useState } from "react";
import { api, Approval, AuditEvent, BrainRule } from "../lib/api";

type DemoState = "idle" | "running" | "ready" | "error";

const priya = "Priya Sharma joins as a Sales Engineer in Dubai.";
const omar = "Omar Reyes joins as a Sales Engineer in Dubai.";

export default function Home() {
  const [demoState, setDemoState] = useState<DemoState>("idle");
  const [rules, setRules] = useState<BrainRule[]>([]);
  const [approvals, setApprovals] = useState<Approval[]>([]);
  const [events, setEvents] = useState<AuditEvent[]>([]);
  const [activeStep, setActiveStep] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [input, setInput] = useState(priya);

  const learnedRule = rules[0];
  const pendingApproval = approvals.find((approval) => approval.status === "pending");

  async function refresh() {
    const [ruleRes, approvalRes, auditRes] = await Promise.all([api.rules(), api.approvals(), api.audit()]);
    setRules(ruleRes.rules);
    setApprovals(approvalRes.approvals);
    setEvents(auditRes.events.slice(-8).reverse());
  }

  async function runGuidedDemo() {
    setDemoState("running");
    setError(null);
    setActiveStep(0);
    try {
      await api.reset();
      setRules([]);
      setApprovals([]);
      setEvents([]);
      await sleep(500);
      setActiveStep(1);
      await api.intake(priya);
      await refresh();
      await sleep(700);
      setActiveStep(2);
      const approvalRes = await api.approvals();
      const approval = approvalRes.approvals.find((item) => item.status === "pending");
      if (!approval) throw new Error("Guided demo expected a pending approval.");
      await api.resolve(approval.id, "Sales");
      await refresh();
      await sleep(700);
      setActiveStep(3);
      await api.intake(omar);
      await refresh();
      setActiveStep(4);
      setDemoState("ready");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
      setDemoState("error");
    }
  }

  async function resetDemo() {
    setDemoState("idle");
    setActiveStep(0);
    setError(null);
    await api.reset();
    await refresh();
  }

  async function submitCase() {
    setError(null);
    try {
      await api.intake(input);
      await refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    }
  }

  const statusCopy = useMemo(() => {
    if (demoState === "running") return "Running guided demo";
    if (demoState === "ready") return "Company Brain rule created and applied";
    if (demoState === "error") return "Demo needs attention";
    return "Ready for guided demo";
  }, [demoState]);

  return (
    <main className="shell">
      <section className="hero">
        <div className="eyebrow">Company Brain Workbench</div>
        <div className="heroGrid">
          <div>
            <h1>Corrected once. Never asks again.</h1>
            <p className="lede">
              A full-stack AI employee workbench where human corrections become structured company memory and future workflows resolve automatically.
            </p>
            <div className="actions">
              <button className="primary" onClick={runGuidedDemo} disabled={demoState === "running"}>
                {demoState === "running" ? "Running…" : "Run guided demo"}
              </button>
              <button className="secondary" onClick={resetDemo}>Reset</button>
            </div>
            {error ? <p className="error">{error}</p> : <p className="status">{statusCopy}</p>}
          </div>
          <div className="brainCard">
            <span className="cardLabel">Company Brain</span>
            <div className={learnedRule ? "brainOrb learned" : "brainOrb"}>{learnedRule ? "1" : "0"}</div>
            <p>{learnedRule ? "Rule active: Sales Engineer + Dubai → Sales" : "No learned rules yet"}</p>
          </div>
        </div>
      </section>

      <section className="comparison">
        <article className={`compareCard ${activeStep >= 1 ? "active" : ""}`}>
          <span className="cardLabel">Before learning</span>
          <h2>Priya Sharma</h2>
          <p>Sales Engineer · Dubai</p>
          <div className="stateLine warning">Ambiguity detected</div>
          <ul>
            <li>Could map to Sales or Engineering</li>
            <li>IT access and finance tier change downstream</li>
            <li>Human resolution required</li>
          </ul>
        </article>
        <article className={`compareCard learned ${activeStep >= 4 ? "active" : ""}`}>
          <span className="cardLabel">After learning</span>
          <h2>Omar Reyes</h2>
          <p>Sales Engineer · Dubai</p>
          <div className="stateLine success">Rule matched</div>
          <ul>
            <li>Mapped to Sales automatically</li>
            <li>CRM and sales-core access selected</li>
            <li>No human escalation needed</li>
          </ul>
        </article>
      </section>

      <section className="grid three">
        <Panel title="Workbench" kicker="Intake">
          <textarea value={input} onChange={(event) => setInput(event.target.value)} maxLength={2000} />
          <div className="chipRow">
            <button onClick={() => setInput(priya)}>Priya case</button>
            <button onClick={() => setInput(omar)}>Omar case</button>
          </div>
          <button className="secondary wide" onClick={submitCase}>Submit case</button>
        </Panel>

        <Panel title="Approvals" kicker="Human in the loop">
          {pendingApproval ? (
            <div className="approvalBox">
              <strong>{pendingApproval.question}</strong>
              <p>{pendingApproval.facts.name} · {pendingApproval.facts.role} · {pendingApproval.facts.location}</p>
              <button className="primary small" onClick={() => api.resolve(pendingApproval.id, "Sales").then(refresh)}>Resolve as Sales</button>
            </div>
          ) : (
            <Empty text="No pending approvals." />
          )}
        </Panel>

        <Panel title="Company Brain" kicker="Learned rules">
          {rules.length ? rules.map((rule) => (
            <div className="rule" key={rule.id}>
              <strong>{rule.pattern.role} + {rule.pattern.location}</strong>
              <span>→ {rule.decision.department}</span>
              <small>Applied {rule.times_applied} time{rule.times_applied === 1 ? "" : "s"}</small>
            </div>
          )) : <Empty text="Rules appear here after a human correction." />}
        </Panel>
      </section>

      <section className="grid two">
        <Panel title="Audit Trail" kicker="Trust layer">
          <div className="timeline">
            {events.length ? events.map((event) => (
              <div className="event" key={event.id}>
                <span>{event.event_type}</span>
                <p>{event.summary}</p>
              </div>
            )) : <Empty text="Run the demo to populate the audit trail." />}
          </div>
        </Panel>
        <Panel title="Demo Sequence" kicker="Phase 7">
          <ol className="steps">
            <li className={activeStep >= 1 ? "done" : ""}>Priya case escalates</li>
            <li className={activeStep >= 2 ? "done" : ""}>Human resolves Sales Engineer as Sales</li>
            <li className={activeStep >= 3 ? "done" : ""}>Company Brain stores rule</li>
            <li className={activeStep >= 4 ? "done" : ""}>Omar auto-resolves from rule</li>
          </ol>
        </Panel>
      </section>
    </main>
  );
}

function Panel({ title, kicker, children }: { title: string; kicker: string; children: React.ReactNode }) {
  return <article className="panel"><span className="cardLabel">{kicker}</span><h3>{title}</h3>{children}</article>;
}

function Empty({ text }: { text: string }) {
  return <p className="empty">{text}</p>;
}

function sleep(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
