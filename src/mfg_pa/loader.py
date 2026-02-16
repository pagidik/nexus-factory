from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .models import MaintenanceRisk, OrderRecord, ProductionRecord, ShipmentRecord
from .parsers import (
    parse_maintenance_risks,
    parse_order_records,
    parse_production_records,
    parse_shipment_records,
)


@dataclass
class ParsedDataset:
    production: list[ProductionRecord]
    shipments: list[ShipmentRecord]
    orders: list[OrderRecord]
    maintenance_risks: list[MaintenanceRisk]


def load_dataset(data_dir: str | Path) -> ParsedDataset:
    root = Path(data_dir)
    if not root.exists():
        raise FileNotFoundError(f"Data directory not found: {root}")

    production: list[ProductionRecord] = []
    shipments: list[ShipmentRecord] = []
    orders: list[OrderRecord] = []
    maintenance_risks: list[MaintenanceRisk] = []

    for path in sorted(root.glob("*.txt")):
        text = path.read_text(encoding="utf-8")
        source = str(path)
        production.extend(parse_production_records(text, source))
        shipments.extend(parse_shipment_records(text, source))
        orders.extend(parse_order_records(text, source))
        maintenance_risks.extend(parse_maintenance_risks(text, source))

    return ParsedDataset(
        production=production,
        shipments=shipments,
        orders=orders,
        maintenance_risks=maintenance_risks,
    )

