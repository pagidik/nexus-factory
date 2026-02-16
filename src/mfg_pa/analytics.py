from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from statistics import mean

from .models import MaintenanceRisk, OrderRecord, ProductionRecord, ShipmentRecord


@dataclass(frozen=True)
class LineStatus:
    line: str
    throughput_pct: float
    downtime_minutes: int
    projected_downtime_minutes: int
    defect_rate: float
    health: str


@dataclass(frozen=True)
class Bottleneck:
    line: str
    reason: str
    severity: int


@dataclass(frozen=True)
class OrderRisk:
    order_id: str
    due_date: date
    reason: str
    priority: str


def build_line_statuses(
    production: list[ProductionRecord], maintenance: list[MaintenanceRisk]
) -> list[LineStatus]:
    maintenance_by_line = {
        risk.line: risk.additional_downtime_minutes for risk in maintenance
    }
    statuses: list[LineStatus] = []

    for record in production:
        projected_downtime = record.downtime_minutes + maintenance_by_line.get(
            record.line, 0
        )
        throughput_pct = record.throughput_ratio * 100
        health = "stable"
        if throughput_pct < 85 or record.defect_rate >= 4 or projected_downtime >= 70:
            health = "critical"
        elif throughput_pct < 92 or record.defect_rate >= 3 or projected_downtime >= 45:
            health = "watch"

        statuses.append(
            LineStatus(
                line=record.line,
                throughput_pct=throughput_pct,
                downtime_minutes=record.downtime_minutes,
                projected_downtime_minutes=projected_downtime,
                defect_rate=record.defect_rate,
                health=health,
            )
        )

    return sorted(statuses, key=lambda item: item.line)


def identify_bottlenecks(statuses: list[LineStatus]) -> list[Bottleneck]:
    bottlenecks: list[Bottleneck] = []
    for status in statuses:
        if status.health == "stable":
            continue
        severity = 2 if status.health == "critical" else 1
        reasons: list[str] = []
        if status.throughput_pct < 92:
            reasons.append(f"throughput {status.throughput_pct:.1f}%")
        if status.defect_rate >= 3:
            reasons.append(f"defects {status.defect_rate:.1f}%")
        if status.projected_downtime_minutes >= 45:
            reasons.append(
                f"projected downtime {status.projected_downtime_minutes} min"
            )
        bottlenecks.append(
            Bottleneck(
                line=status.line,
                reason=", ".join(reasons) if reasons else "general performance drift",
                severity=severity,
            )
        )
    return sorted(bottlenecks, key=lambda item: (-item.severity, item.line))


def delayed_shipments(shipments: list[ShipmentRecord]) -> list[ShipmentRecord]:
    return sorted(
        [shipment for shipment in shipments if shipment.delay_hours > 0],
        key=lambda shipment: shipment.delay_hours,
        reverse=True,
    )


def assess_order_risks(
    orders: list[OrderRecord],
    delayed: list[ShipmentRecord],
    as_of: date,
) -> list[OrderRisk]:
    delayed_hours = max((shipment.delay_hours for shipment in delayed), default=0)
    risks: list[OrderRisk] = []

    for order in orders:
        days_to_due = (order.due_date - as_of).days
        if order.status in {"at_risk", "blocked"}:
            risks.append(
                OrderRisk(
                    order_id=order.order_id,
                    due_date=order.due_date,
                    reason=f"explicit status is {order.status}",
                    priority=order.priority,
                )
            )
            continue

        high_priority_due_soon = order.priority == "high" and days_to_due <= 2
        if high_priority_due_soon and delayed_hours >= 8:
            risks.append(
                OrderRisk(
                    order_id=order.order_id,
                    due_date=order.due_date,
                    reason=f"high-priority due in {days_to_due} day(s) with {delayed_hours}h inbound delay",
                    priority=order.priority,
                )
            )

    return sorted(risks, key=lambda item: (item.due_date, item.order_id))


def snapshot_kpis(statuses: list[LineStatus], delayed: list[ShipmentRecord]) -> dict[str, float | int]:
    avg_throughput = mean([status.throughput_pct for status in statuses]) if statuses else 0.0
    return {
        "lines_monitored": len(statuses),
        "avg_throughput_pct": round(avg_throughput, 1),
        "delayed_shipments": len(delayed),
        "critical_lines": sum(1 for status in statuses if status.health == "critical"),
    }


def due_soon_window(as_of: date) -> date:
    return as_of + timedelta(days=2)

