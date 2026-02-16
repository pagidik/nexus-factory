from __future__ import annotations

import re
from datetime import date

from .models import MaintenanceRisk, OrderRecord, ProductionRecord, ShipmentRecord

PRODUCTION_RE = re.compile(
    r"Line (?P<line>[\w-]+) produced (?P<actual>\d+) units against target (?P<target>\d+)\. "
    r"Downtime (?P<downtime>\d+) min .*?Defect rate (?P<defect>[\d.]+)%\.?$",
    re.IGNORECASE,
)

SHIPMENT_DELAYED_RE = re.compile(
    r"Shipment (?P<shipment_id>[\w-]+) for route (?P<route>\S+->\S+) carrying "
    r"(?P<component>.+?) is delayed by (?P<delay>\d+) hours \(status: (?P<status>[\w_]+)\) "
    r"because of (?P<cause>[^.]+)\.",
    re.IGNORECASE,
)

SHIPMENT_ONTIME_RE = re.compile(
    r"Shipment (?P<shipment_id>[\w-]+) for route (?P<route>\S+->\S+) carrying "
    r"(?P<component>.+?) is on time with ETA (?P<eta>\d+) hours \(status: (?P<status>[\w_]+)\)\.",
    re.IGNORECASE,
)

ORDER_RE = re.compile(
    r"Order (?P<order_id>[\w-]+) model (?P<model>[\w-]+) quantity (?P<quantity>\d+) "
    r"due (?P<due_date>\d{4}-\d{2}-\d{2}) priority (?P<priority>\w+) status (?P<status>[\w_]+)\.",
    re.IGNORECASE,
)

MAINTENANCE_RE = re.compile(
    r"(?P<line>[\w-]+).*?expected additional (?P<minutes>\d+) minutes downtime next shift\.",
    re.IGNORECASE,
)


def parse_production_records(text: str, source: str) -> list[ProductionRecord]:
    records: list[ProductionRecord] = []
    for raw_line in text.splitlines():
        match = PRODUCTION_RE.search(raw_line.strip())
        if not match:
            continue
        records.append(
            ProductionRecord(
                line=match.group("line"),
                target_units=int(match.group("target")),
                actual_units=int(match.group("actual")),
                downtime_minutes=int(match.group("downtime")),
                defect_rate=float(match.group("defect")),
                source=source,
            )
        )
    return records


def parse_shipment_records(text: str, source: str) -> list[ShipmentRecord]:
    records: list[ShipmentRecord] = []
    for raw_line in text.splitlines():
        normalized = raw_line.strip()
        if not normalized:
            continue

        delayed = SHIPMENT_DELAYED_RE.search(normalized)
        if delayed:
            records.append(
                ShipmentRecord(
                    shipment_id=delayed.group("shipment_id"),
                    route=delayed.group("route"),
                    component=delayed.group("component"),
                    status=delayed.group("status"),
                    delay_hours=int(delayed.group("delay")),
                    eta_hours=None,
                    cause=delayed.group("cause"),
                    source=source,
                )
            )
            continue

        on_time = SHIPMENT_ONTIME_RE.search(normalized)
        if on_time:
            records.append(
                ShipmentRecord(
                    shipment_id=on_time.group("shipment_id"),
                    route=on_time.group("route"),
                    component=on_time.group("component"),
                    status=on_time.group("status"),
                    delay_hours=0,
                    eta_hours=int(on_time.group("eta")),
                    cause="none",
                    source=source,
                )
            )

    return records


def parse_order_records(text: str, source: str) -> list[OrderRecord]:
    records: list[OrderRecord] = []
    for raw_line in text.splitlines():
        match = ORDER_RE.search(raw_line.strip())
        if not match:
            continue
        records.append(
            OrderRecord(
                order_id=match.group("order_id"),
                model=match.group("model"),
                quantity=int(match.group("quantity")),
                due_date=date.fromisoformat(match.group("due_date")),
                priority=match.group("priority").lower(),
                status=match.group("status").lower(),
                source=source,
            )
        )
    return records


def parse_maintenance_risks(text: str, source: str) -> list[MaintenanceRisk]:
    records: list[MaintenanceRisk] = []
    for raw_line in text.splitlines():
        match = MAINTENANCE_RE.search(raw_line.strip())
        if not match:
            continue
        records.append(
            MaintenanceRisk(
                line=match.group("line"),
                additional_downtime_minutes=int(match.group("minutes")),
                detail=raw_line.strip(),
                source=source,
            )
        )
    return records

