from __future__ import annotations

import argparse
import json
from datetime import date, datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

from .assistant import ManufacturingAssistant
from .loader import load_dataset

DASHBOARD_HTML = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Manufacturing Assistant Dashboard</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&family=IBM+Plex+Mono:wght@400;600&display=swap" rel="stylesheet" />
  <style>
    :root {
      --bg: #f0ede6;
      --bg-accent: #e6f0ef;
      --panel: #fffffff0;
      --card: #ffffff;
      --ink: #10212b;
      --muted: #4f6674;
      --line: #d7e0e5;
      --teal: #006d77;
      --amber: #d97706;
      --red: #d1495b;
      --green: #2a9d8f;
      --shadow: 0 10px 30px rgba(16, 33, 43, 0.08);
    }

    * {
      box-sizing: border-box;
    }

    body {
      margin: 0;
      font-family: "Space Grotesk", "Segoe UI", sans-serif;
      color: var(--ink);
      background:
        radial-gradient(circle at 85% 10%, rgba(0, 109, 119, 0.18), transparent 35%),
        radial-gradient(circle at 15% 95%, rgba(217, 119, 6, 0.2), transparent 30%),
        linear-gradient(135deg, var(--bg), var(--bg-accent));
      min-height: 100vh;
    }

    .shell {
      max-width: 1200px;
      margin: 0 auto;
      padding: 24px;
      display: grid;
      gap: 18px;
    }

    .header {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 16px;
      padding: 20px;
      box-shadow: var(--shadow);
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 14px;
      animation: rise 450ms ease forwards;
    }

    .title {
      margin: 0;
      font-size: 1.45rem;
      letter-spacing: 0.01em;
    }

    .subtitle {
      margin: 6px 0 0;
      color: var(--muted);
      font-size: 0.94rem;
    }

    .timestamp {
      font-family: "IBM Plex Mono", monospace;
      font-size: 0.82rem;
      background: #f6faf9;
      border: 1px solid #d1ebe7;
      border-radius: 999px;
      padding: 8px 12px;
    }

    .kpi-grid {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 12px;
    }

    .kpi {
      background: var(--card);
      border-radius: 14px;
      padding: 14px 16px;
      border: 1px solid var(--line);
      box-shadow: var(--shadow);
      opacity: 0;
      transform: translateY(8px);
      animation: rise 450ms ease forwards;
    }

    .kpi:nth-child(2) { animation-delay: 70ms; }
    .kpi:nth-child(3) { animation-delay: 120ms; }
    .kpi:nth-child(4) { animation-delay: 170ms; }

    .kpi-label {
      margin: 0;
      color: var(--muted);
      font-size: 0.82rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }

    .kpi-value {
      margin: 6px 0 0;
      font-size: 1.6rem;
      font-family: "IBM Plex Mono", monospace;
    }

    .grid {
      display: grid;
      grid-template-columns: 1.35fr 1fr;
      gap: 14px;
    }

    .panel {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 16px;
      box-shadow: var(--shadow);
      padding: 16px;
      animation: rise 500ms ease forwards;
    }

    .panel h2 {
      margin: 0 0 10px;
      font-size: 1.05rem;
    }

    table {
      width: 100%;
      border-collapse: collapse;
      font-size: 0.92rem;
    }

    th, td {
      text-align: left;
      padding: 9px 8px;
      border-bottom: 1px solid #ebeff2;
      vertical-align: top;
    }

    th {
      color: var(--muted);
      font-weight: 500;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      font-size: 0.76rem;
    }

    .health {
      border-radius: 999px;
      padding: 3px 10px;
      display: inline-block;
      font-size: 0.74rem;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      font-weight: 700;
      color: white;
    }

    .health.stable { background: var(--green); }
    .health.watch { background: var(--amber); }
    .health.critical { background: var(--red); }

    .progress-wrap {
      background: #edf3f5;
      border-radius: 999px;
      width: 120px;
      height: 9px;
      overflow: hidden;
    }

    .progress {
      height: 9px;
      border-radius: 999px;
      transition: width 400ms ease;
    }

    .progress.stable { background: var(--green); }
    .progress.watch { background: var(--amber); }
    .progress.critical { background: var(--red); }

    .stack {
      display: grid;
      gap: 14px;
    }

    .list {
      margin: 0;
      padding: 0;
      list-style: none;
      display: grid;
      gap: 8px;
    }

    .list-item {
      border: 1px solid #e8edf0;
      background: #fafcfc;
      border-radius: 10px;
      padding: 10px 12px;
      font-size: 0.92rem;
    }

    .list-item strong {
      font-family: "IBM Plex Mono", monospace;
      font-size: 0.84rem;
    }

    .issue-actions {
      margin-top: 8px;
      display: flex;
      justify-content: flex-end;
    }

    .issue-btn {
      padding: 7px 10px;
      border-radius: 999px;
      font-size: 0.76rem;
      background: #0b7285;
      letter-spacing: 0.02em;
    }

    .issue-btn:hover {
      filter: brightness(1.08);
    }

    .ghost-btn {
      background: transparent;
      color: var(--muted);
      border: 1px solid #cfdae1;
      font-weight: 500;
      padding: 8px 10px;
    }

    .solution-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      margin-bottom: 6px;
    }

    .solution-actions {
      margin-top: 8px;
    }

    .solution-actions .list-item {
      background: #ffffff;
    }

    .solution-impact {
      margin-top: 8px;
      font-size: 0.88rem;
    }

    .ask {
      display: grid;
      gap: 9px;
    }

    .ask-row {
      display: grid;
      grid-template-columns: 1fr auto;
      gap: 10px;
    }

    input[type="text"] {
      width: 100%;
      border: 1px solid #d9e2e8;
      border-radius: 10px;
      padding: 10px 12px;
      font: inherit;
      background: white;
    }

    button {
      border: none;
      border-radius: 10px;
      padding: 10px 14px;
      background: var(--teal);
      color: white;
      font: inherit;
      font-weight: 600;
      cursor: pointer;
    }

    button:hover {
      filter: brightness(1.06);
    }

    .answer {
      border: 1px dashed #c8d4dc;
      border-radius: 10px;
      padding: 10px;
      font-size: 0.9rem;
      background: #f9fbfc;
      white-space: pre-wrap;
      min-height: 56px;
    }

    .muted {
      color: var(--muted);
    }

    @keyframes rise {
      from { opacity: 0; transform: translateY(10px); }
      to { opacity: 1; transform: translateY(0); }
    }

    @media (max-width: 960px) {
      .kpi-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }

      .grid {
        grid-template-columns: 1fr;
      }
    }

    @media (max-width: 640px) {
      .shell {
        padding: 14px;
      }

      .kpi-grid {
        grid-template-columns: 1fr;
      }

      .ask-row {
        grid-template-columns: 1fr;
      }

      table {
        display: block;
        overflow-x: auto;
      }
    }
  </style>
</head>
<body>
  <main class="shell">
    <section class="header">
      <div>
        <h1 class="title">Manufacturing Assistant Dashboard</h1>
        <p class="subtitle">Live POC view for line health, inbound logistics, and fulfillment risk.</p>
      </div>
      <div class="timestamp" id="timestamp">Loading...</div>
    </section>

    <section class="kpi-grid" id="kpis"></section>

    <section class="grid">
      <article class="panel">
        <h2>Line Performance</h2>
        <table>
          <thead>
            <tr>
              <th>Line</th>
              <th>Health</th>
              <th>Throughput</th>
              <th>Downtime</th>
              <th>Defects</th>
            </tr>
          </thead>
          <tbody id="lineRows"></tbody>
        </table>
      </article>

      <section class="stack">
        <article class="panel">
          <h2>Bottlenecks</h2>
          <ul class="list" id="bottlenecks"></ul>
        </article>

        <article class="panel">
          <h2>Delayed Shipments</h2>
          <ul class="list" id="shipments"></ul>
        </article>

        <article class="panel">
          <h2>Order Risk</h2>
          <ul class="list" id="orders"></ul>
        </article>
      </section>
    </section>

    <section class="panel ask">
      <h2>Ask the Assistant</h2>
      <div class="ask-row">
        <input id="questionInput" type="text" value="where are bottlenecks?" />
        <button id="askBtn" type="button">Ask</button>
      </div>
      <div class="answer" id="answerBox">Type a question and click Ask.</div>
      <div class="muted">Try: "status summary", "logistics delays", "order risks"</div>
    </section>

    <section class="panel" id="solutionPanel" hidden>
      <div class="solution-header">
        <h2 id="solutionTitle">AI Resolution</h2>
        <button id="solutionClose" type="button" class="ghost-btn">Close</button>
      </div>
      <div class="muted" id="solutionMeta">Choose an issue and click "We have an answer".</div>
      <div class="answer" id="solutionSummary">AI plans will appear here.</div>
      <ul class="list solution-actions" id="solutionActions"></ul>
      <div class="muted solution-impact" id="solutionImpact"></div>
    </section>
  </main>

  <script>
    const byId = (id) => document.getElementById(id);

    const fmtPct = (value) => `${Number(value).toFixed(1)}%`;

    const healthClass = (health) => {
      const normalized = (health || "").toLowerCase();
      if (normalized === "critical") return "critical";
      if (normalized === "watch") return "watch";
      return "stable";
    };

    const escapeHtml = (raw) =>
      String(raw)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;");

    const escapeAttr = (raw) =>
      String(raw)
        .replaceAll("&", "&amp;")
        .replaceAll("\"", "&quot;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;");

    const issueAction = (issueType, issueId) => `
      <div class="issue-actions">
        <button
          type="button"
          class="issue-btn"
          data-issue-type="${escapeAttr(issueType)}"
          data-issue-id="${escapeAttr(issueId)}"
        >
          We have an answer
        </button>
      </div>
    `;

    const renderKpis = (snapshot) => {
      const kpis = snapshot.kpis;
      const cards = [
        ["Lines Monitored", kpis.lines_monitored],
        ["Avg Throughput", `${kpis.avg_throughput_pct}%`],
        ["Critical Lines", kpis.critical_lines],
        ["Delayed Shipments", kpis.delayed_shipments],
      ];
      byId("kpis").innerHTML = cards
        .map(
          ([label, value]) =>
            `<article class="kpi"><p class="kpi-label">${label}</p><p class="kpi-value">${value}</p></article>`
        )
        .join("");
    };

    const renderLines = (snapshot) => {
      const rows = snapshot.line_statuses
        .map((line) => {
          const cls = healthClass(line.health);
          const width = Math.max(0, Math.min(100, Number(line.throughput_pct)));
          return `
            <tr>
              <td><strong>${escapeHtml(line.line)}</strong></td>
              <td><span class="health ${cls}">${escapeHtml(line.health)}</span></td>
              <td>
                <div class="progress-wrap"><div class="progress ${cls}" style="width:${width}%"></div></div>
                <div class="muted">${fmtPct(line.throughput_pct)}</div>
              </td>
              <td>${line.projected_downtime_minutes} min <span class="muted">(raw ${line.downtime_minutes})</span></td>
              <td>${fmtPct(line.defect_rate)}</td>
            </tr>
          `;
        })
        .join("");
      byId("lineRows").innerHTML = rows || '<tr><td colspan="5">No line data available.</td></tr>';
    };

    const renderList = (id, items, mapper, emptyText) => {
      if (!items || items.length === 0) {
        byId(id).innerHTML = `<li class="list-item">${emptyText}</li>`;
        return;
      }
      byId(id).innerHTML = items.map((item) => `<li class="list-item">${mapper(item)}</li>`).join("");
    };

    const renderSolution = (payload) => {
      byId("solutionPanel").hidden = false;
      byId("solutionTitle").textContent = payload.title;
      byId("solutionMeta").textContent = `Issue: ${payload.issue_type} / ${payload.issue_id} | Confidence: ${payload.confidence}`;
      byId("solutionSummary").textContent = payload.summary;
      byId("solutionActions").innerHTML = (payload.actions || [])
        .map((action, index) => `<li class="list-item"><strong>Step ${index + 1}</strong><br>${escapeHtml(action)}</li>`)
        .join("");
      byId("solutionImpact").textContent = payload.expected_impact || "";
    };

    const fetchSolution = async (issueType, issueId) => {
      byId("solutionPanel").hidden = false;
      byId("solutionTitle").textContent = "AI Resolution";
      byId("solutionMeta").textContent = `Issue: ${issueType} / ${issueId}`;
      byId("solutionSummary").textContent = "Analyzing issue context...";
      byId("solutionActions").innerHTML = "";
      byId("solutionImpact").textContent = "";

      const response = await fetch(
        `/api/solution?issue_type=${encodeURIComponent(issueType)}&issue_id=${encodeURIComponent(issueId)}`,
        { cache: "no-store" }
      );
      if (!response.ok) {
        byId("solutionSummary").textContent = `Unable to generate solution (${response.status}).`;
        return;
      }
      const payload = await response.json();
      renderSolution(payload);
    };

    const refresh = async () => {
      const response = await fetch("/api/snapshot", { cache: "no-store" });
      if (!response.ok) throw new Error(`snapshot request failed: ${response.status}`);
      const snapshot = await response.json();
      byId("timestamp").textContent = `As of ${snapshot.as_of} | Updated ${snapshot.generated_at}`;
      renderKpis(snapshot);
      renderLines(snapshot);
      renderList(
        "bottlenecks",
        snapshot.bottlenecks,
        (item) =>
          `<strong>${escapeHtml(item.line)}</strong><br>${escapeHtml(item.reason)} <span class="muted">(severity ${item.severity})</span>${issueAction("bottleneck", item.line)}`,
        "No active bottlenecks."
      );
      renderList(
        "shipments",
        snapshot.delayed_shipments,
        (item) =>
          `<strong>${escapeHtml(item.shipment_id)}</strong> ${escapeHtml(item.component)}<br>${escapeHtml(item.route)} | ${item.delay_hours}h delay (${escapeHtml(item.cause)})${issueAction("shipment", item.shipment_id)}`,
        "All tracked shipments are on time."
      );
      renderList(
        "orders",
        snapshot.order_risks,
        (item) =>
          `<strong>${escapeHtml(item.order_id)}</strong> due ${escapeHtml(item.due_date)} (${escapeHtml(item.priority)})<br>${escapeHtml(item.reason)}${issueAction("order_risk", item.order_id)}`,
        "No at-risk orders."
      );
    };

    const ask = async () => {
      const question = byId("questionInput").value.trim();
      if (!question) return;
      byId("answerBox").textContent = "Thinking...";
      const response = await fetch(`/api/ask?q=${encodeURIComponent(question)}`, { cache: "no-store" });
      if (!response.ok) {
        byId("answerBox").textContent = `Request failed (${response.status})`;
        return;
      }
      const payload = await response.json();
      byId("answerBox").textContent = payload.answer;
    };

    byId("askBtn").addEventListener("click", () => {
      ask().catch((err) => {
        byId("answerBox").textContent = `Error: ${err.message}`;
      });
    });

    byId("questionInput").addEventListener("keydown", (event) => {
      if (event.key === "Enter") {
        event.preventDefault();
        byId("askBtn").click();
      }
    });

    byId("solutionClose").addEventListener("click", () => {
      byId("solutionPanel").hidden = true;
    });

    document.addEventListener("click", (event) => {
      const btn = event.target.closest(".issue-btn");
      if (!btn) return;
      const issueType = btn.getAttribute("data-issue-type") || "";
      const issueId = btn.getAttribute("data-issue-id") || "";
      fetchSolution(issueType, issueId).catch((err) => {
        byId("solutionPanel").hidden = false;
        byId("solutionSummary").textContent = `Error: ${err.message}`;
      });
    });

    refresh().catch((err) => {
      byId("timestamp").textContent = `Failed to load: ${err.message}`;
    });
    setInterval(() => {
      refresh().catch((err) => {
        byId("timestamp").textContent = `Failed to refresh: ${err.message}`;
      });
    }, 15000);
  </script>
</body>
</html>
"""


def parse_as_of(value: str | None) -> date | None:
    if not value:
        return None
    return date.fromisoformat(value)


class DashboardService:
    def __init__(self, data_dir: str | Path, as_of: date | None = None) -> None:
        self.data_dir = Path(data_dir)
        self.as_of = as_of

    def _assistant(self) -> ManufacturingAssistant:
        dataset = load_dataset(self.data_dir)
        return ManufacturingAssistant(dataset, as_of=self.as_of)

    def snapshot(self) -> dict[str, object]:
        payload = self._assistant().snapshot()
        payload["generated_at"] = datetime.now(timezone.utc).isoformat(
            timespec="seconds"
        )
        return payload

    def ask(self, question: str) -> str:
        return self._assistant().ask(question)

    def solution(self, issue_type: str, issue_id: str) -> dict[str, Any]:
        issue_kind = issue_type.strip().lower()
        issue_key = issue_id.strip()
        if not issue_kind or not issue_key:
            raise KeyError("issue_type and issue_id are required")

        assistant = self._assistant()

        if issue_kind == "bottleneck":
            return self._bottleneck_solution(assistant, issue_key)
        if issue_kind == "shipment":
            return self._shipment_solution(assistant, issue_key)
        if issue_kind == "order_risk":
            return self._order_risk_solution(assistant, issue_key)

        raise KeyError(f"Unsupported issue type: {issue_type}")

    def _bottleneck_solution(
        self, assistant: ManufacturingAssistant, line: str
    ) -> dict[str, Any]:
        bottleneck = next(
            (
                item
                for item in assistant.bottlenecks
                if item.line.lower() == line.lower()
            ),
            None,
        )
        if bottleneck is None:
            raise KeyError(f"Bottleneck not found for line {line}")

        status = next(
            (item for item in assistant.statuses if item.line.lower() == line.lower()),
            None,
        )
        if status is None:
            raise KeyError(f"Line status not found for line {line}")

        actions = [
            f"Dispatch maintenance to {line} now and clear the dominant loss source: {bottleneck.reason}.",
            f"Rebalance operators for the next shift on {line} to recover throughput above 92%.",
            f"Apply hourly checkpoint for downtime; trigger escalation if projected downtime stays above 45 minutes.",
        ]
        if status.defect_rate >= 3:
            actions.append(
                f"Enable tightened quality gate on {line} and verify first 25 units after restart."
            )

        impact = (
            "Expected impact: recover 10-15% throughput and cut 20-35 minutes of shift downtime "
            "if executed in the current shift window."
        )
        confidence = "high" if bottleneck.severity >= 2 else "medium"
        return {
            "issue_type": "bottleneck",
            "issue_id": line,
            "title": f"AI Resolution Plan for {line}",
            "summary": (
                f"{line} is constrained by {bottleneck.reason}. "
                "The recommendation focuses on immediate containment plus shift-level rebalance."
            ),
            "actions": actions,
            "expected_impact": impact,
            "confidence": confidence,
            "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        }

    def _shipment_solution(
        self, assistant: ManufacturingAssistant, shipment_id: str
    ) -> dict[str, Any]:
        shipment = next(
            (
                item
                for item in assistant.delayed
                if item.shipment_id.lower() == shipment_id.lower()
            ),
            None,
        )
        if shipment is None:
            raise KeyError(f"Shipment not found: {shipment_id}")

        impacted_orders = [risk.order_id for risk in assistant.order_risks]
        actions = [
            f"Trigger expedited logistics with carrier and supplier for {shipment.shipment_id} ({shipment.component}).",
            f"Re-sequence production to consume available material while {shipment.shipment_id} is delayed by {shipment.delay_hours}h.",
            "Launch a 4-hourly ETA checkpoint until the shipment reaches dock.",
        ]
        if shipment.delay_hours >= 10:
            actions.append(
                f"Activate alternate source buffer for {shipment.component} to protect the next 24-hour build plan."
            )
        if impacted_orders:
            actions.append(
                f"Prioritize inbound allocation to at-risk orders: {', '.join(impacted_orders)}."
            )

        return {
            "issue_type": "shipment",
            "issue_id": shipment_id,
            "title": f"AI Resolution Plan for Shipment {shipment.shipment_id}",
            "summary": (
                f"{shipment.shipment_id} on route {shipment.route} is delayed due to {shipment.cause}. "
                "The plan reduces material starvation risk while transit normalizes."
            ),
            "actions": actions,
            "expected_impact": (
                "Expected impact: prevent line stops caused by missing material and limit customer-delivery slippage."
            ),
            "confidence": "high" if shipment.delay_hours >= 8 else "medium",
            "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        }

    def _order_risk_solution(
        self, assistant: ManufacturingAssistant, order_id: str
    ) -> dict[str, Any]:
        order_risk = next(
            (
                item
                for item in assistant.order_risks
                if item.order_id.lower() == order_id.lower()
            ),
            None,
        )
        if order_risk is None:
            raise KeyError(f"Order risk not found: {order_id}")

        primary_bottleneck = assistant.bottlenecks[0].line if assistant.bottlenecks else "critical line"
        worst_delay = assistant.delayed[0].delay_hours if assistant.delayed else 0
        actions = [
            f"Lock dedicated production slots for {order_risk.order_id} on the next two shifts.",
            f"Protect component allocation for {order_risk.order_id} ahead of lower-priority work orders.",
            f"Use {primary_bottleneck} as managed constraint and run hourly output checks against order promise.",
        ]
        if worst_delay >= 8:
            actions.append(
                "Prepare customer communication for revised ETA only if recovery misses the next shift checkpoint."
            )

        return {
            "issue_type": "order_risk",
            "issue_id": order_id,
            "title": f"AI Fulfillment Plan for {order_risk.order_id}",
            "summary": (
                f"{order_risk.order_id} is at risk because {order_risk.reason}. "
                "The plan prioritizes schedule protection and material gating to preserve due-date confidence."
            ),
            "actions": actions,
            "expected_impact": (
                "Expected impact: improve on-time delivery probability by concentrating capacity on the highest-risk commitment."
            ),
            "confidence": "high" if order_risk.priority == "high" else "medium",
            "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        }


def _handler_factory(service: DashboardService) -> type[BaseHTTPRequestHandler]:
    class DashboardHandler(BaseHTTPRequestHandler):
        def _send_json(self, payload: dict[str, object], status: HTTPStatus) -> None:
            body = json.dumps(payload).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def _send_html(self, html: str, status: HTTPStatus) -> None:
            body = html.encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)
            if parsed.path == "/":
                self._send_html(DASHBOARD_HTML, HTTPStatus.OK)
                return

            if parsed.path == "/api/snapshot":
                self._send_json(service.snapshot(), HTTPStatus.OK)
                return

            if parsed.path == "/api/ask":
                query = parse_qs(parsed.query)
                question = query.get("q", [""])[0]
                self._send_json(
                    {"question": question, "answer": service.ask(question)},
                    HTTPStatus.OK,
                )
                return

            if parsed.path == "/api/solution":
                query = parse_qs(parsed.query)
                issue_type = query.get("issue_type", [""])[0]
                issue_id = query.get("issue_id", [""])[0]
                if not issue_type or not issue_id:
                    self._send_json(
                        {
                            "error": "Missing required query parameters: issue_type and issue_id"
                        },
                        HTTPStatus.BAD_REQUEST,
                    )
                    return
                try:
                    self._send_json(
                        service.solution(issue_type, issue_id),
                        HTTPStatus.OK,
                    )
                except KeyError as exc:
                    self._send_json({"error": str(exc)}, HTTPStatus.NOT_FOUND)
                return

            self._send_json({"error": "Not Found"}, HTTPStatus.NOT_FOUND)

        def log_message(self, _format: str, *_args: object) -> None:
            return

    return DashboardHandler


def serve_dashboard(
    data_dir: str | Path,
    host: str = "127.0.0.1",
    port: int = 8787,
    as_of: date | None = None,
) -> int:
    service = DashboardService(data_dir=data_dir, as_of=as_of)
    handler = _handler_factory(service)
    server = ThreadingHTTPServer((host, port), handler)
    url = f"http://{host}:{port}/"
    print(f"Dashboard running at {url}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down dashboard...")
    finally:
        server.server_close()
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Manufacturing Personal Assistant dashboard"
    )
    parser.add_argument(
        "--data",
        default="data/unstructured",
        help="Path to unstructured text files (default: data/unstructured)",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host to bind the dashboard server (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8787,
        help="Port to bind the dashboard server (default: 8787)",
    )
    parser.add_argument(
        "--as-of",
        help="Optional YYYY-MM-DD date for deterministic risk calculations.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    as_of = parse_as_of(args.as_of)
    return serve_dashboard(
        data_dir=args.data,
        host=args.host,
        port=args.port,
        as_of=as_of,
    )


if __name__ == "__main__":
    raise SystemExit(main())
