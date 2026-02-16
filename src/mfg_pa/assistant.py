from __future__ import annotations

from datetime import date
from typing import Any

from .analytics import (
    assess_order_risks,
    build_line_statuses,
    delayed_shipments,
    identify_bottlenecks,
    snapshot_kpis,
)
from .loader import ParsedDataset


class ManufacturingAssistant:
    def __init__(self, dataset: ParsedDataset, as_of: date | None = None) -> None:
        self.dataset = dataset
        self.as_of = as_of or date.today()

        self.statuses = build_line_statuses(
            dataset.production,
            dataset.maintenance_risks,
        )
        self.delayed = delayed_shipments(dataset.shipments)
        self.bottlenecks = identify_bottlenecks(self.statuses)
        self.order_risks = assess_order_risks(
            dataset.orders,
            self.delayed,
            self.as_of,
        )

    def ask(self, question: str) -> str:
        prompt = question.strip().lower()
        if not prompt:
            return self.help_text()
        if any(token in prompt for token in ("bottleneck", "delay", "blocked", "issue")):
            return f"{self.bottleneck_update()}\n\n{self.logistics_update()}"
        if any(token in prompt for token in ("shipment", "logistics", "inbound")):
            return self.logistics_update()
        if any(token in prompt for token in ("order", "delivery", "customer", "due")):
            return self.order_update()
        if any(token in prompt for token in ("status", "summary", "line", "overview")):
            return self.overview()
        if "help" in prompt:
            return self.help_text()
        return f"{self.overview()}\n\n{self.help_text()}"

    def overview(self) -> str:
        kpis = snapshot_kpis(self.statuses, self.delayed)
        header = (
            "Manufacturing Assistant Snapshot\n"
            f"As of: {self.as_of.isoformat()}\n"
            f"Lines monitored: {kpis['lines_monitored']}, "
            f"Average throughput: {kpis['avg_throughput_pct']}%, "
            f"Critical lines: {kpis['critical_lines']}, "
            f"Delayed shipments: {kpis['delayed_shipments']}"
        )
        line_rows = [
            (
                f"- {status.line}: {status.health.upper()} | "
                f"throughput {status.throughput_pct:.1f}% | "
                f"downtime {status.projected_downtime_minutes} min projected | "
                f"defects {status.defect_rate:.1f}%"
            )
            for status in self.statuses
        ]
        return "\n".join([header, "Line status:", *line_rows])

    def bottleneck_update(self) -> str:
        if not self.bottlenecks:
            return "Bottleneck update: no bottlenecks detected."
        rows = [
            f"- {item.line}: {item.reason} (severity {item.severity})"
            for item in self.bottlenecks
        ]
        return "\n".join(["Bottleneck update:", *rows])

    def logistics_update(self) -> str:
        if not self.delayed:
            return "Logistics update: all tracked shipments are on time."
        rows = [
            (
                f"- {shipment.shipment_id} ({shipment.component}) on {shipment.route}: "
                f"{shipment.delay_hours}h delay, cause: {shipment.cause}"
            )
            for shipment in self.delayed
        ]
        return "\n".join(["Logistics update:", *rows])

    def order_update(self) -> str:
        if not self.order_risks:
            return "Order risk update: no at-risk orders."
        rows = [
            (
                f"- {risk.order_id} due {risk.due_date.isoformat()} "
                f"({risk.priority}): {risk.reason}"
            )
            for risk in self.order_risks
        ]
        return "\n".join(["Order risk update:", *rows])

    def snapshot(self) -> dict[str, Any]:
        kpis = snapshot_kpis(self.statuses, self.delayed)
        return {
            "as_of": self.as_of.isoformat(),
            "kpis": kpis,
            "line_statuses": [
                {
                    "line": status.line,
                    "health": status.health,
                    "throughput_pct": round(status.throughput_pct, 1),
                    "downtime_minutes": status.downtime_minutes,
                    "projected_downtime_minutes": status.projected_downtime_minutes,
                    "defect_rate": status.defect_rate,
                }
                for status in self.statuses
            ],
            "bottlenecks": [
                {
                    "line": bottleneck.line,
                    "reason": bottleneck.reason,
                    "severity": bottleneck.severity,
                }
                for bottleneck in self.bottlenecks
            ],
            "delayed_shipments": [
                {
                    "shipment_id": shipment.shipment_id,
                    "route": shipment.route,
                    "component": shipment.component,
                    "delay_hours": shipment.delay_hours,
                    "cause": shipment.cause,
                }
                for shipment in self.delayed
            ],
            "order_risks": [
                {
                    "order_id": risk.order_id,
                    "due_date": risk.due_date.isoformat(),
                    "priority": risk.priority,
                    "reason": risk.reason,
                }
                for risk in self.order_risks
            ],
        }

    @staticmethod
    def help_text() -> str:
        return (
            "Try queries like: 'status summary', 'where are bottlenecks?', "
            "'logistics delays', or 'order risks'."
        )
