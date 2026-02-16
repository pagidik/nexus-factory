from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class ProductionRecord:
    line: str
    target_units: int
    actual_units: int
    downtime_minutes: int
    defect_rate: float
    source: str

    @property
    def throughput_ratio(self) -> float:
        if self.target_units <= 0:
            return 0.0
        return self.actual_units / self.target_units


@dataclass(frozen=True)
class ShipmentRecord:
    shipment_id: str
    route: str
    component: str
    status: str
    delay_hours: int
    eta_hours: int | None
    cause: str
    source: str


@dataclass(frozen=True)
class OrderRecord:
    order_id: str
    model: str
    quantity: int
    due_date: date
    priority: str
    status: str
    source: str


@dataclass(frozen=True)
class MaintenanceRisk:
    line: str
    additional_downtime_minutes: int
    detail: str
    source: str

