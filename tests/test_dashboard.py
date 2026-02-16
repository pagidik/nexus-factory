from __future__ import annotations

import sys
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mfg_pa.dashboard import DashboardService  # noqa: E402


class DashboardServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = DashboardService(
            data_dir=ROOT / "data" / "unstructured",
            as_of=date(2026, 2, 16),
        )

    def test_snapshot_contains_expected_sections(self) -> None:
        snapshot = self.service.snapshot()
        self.assertEqual(snapshot["as_of"], "2026-02-16")
        self.assertIn("generated_at", snapshot)
        self.assertEqual(snapshot["kpis"]["lines_monitored"], 3)
        self.assertEqual(len(snapshot["line_statuses"]), 3)
        self.assertEqual(len(snapshot["delayed_shipments"]), 2)
        self.assertEqual(len(snapshot["order_risks"]), 2)

    def test_ask_uses_assistant_logic(self) -> None:
        answer = self.service.ask("where are bottlenecks?")
        self.assertIn("Bottleneck update", answer)
        self.assertIn("Paint-02", answer)

    def test_solution_returns_action_plan_for_each_issue_type(self) -> None:
        bottleneck_plan = self.service.solution("bottleneck", "Paint-02")
        shipment_plan = self.service.solution("shipment", "SHP-778")
        order_plan = self.service.solution("order_risk", "ORD-2203")

        self.assertIn("actions", bottleneck_plan)
        self.assertGreaterEqual(len(bottleneck_plan["actions"]), 3)
        self.assertIn("AI Resolution Plan", bottleneck_plan["title"])

        self.assertIn("actions", shipment_plan)
        self.assertIn("SHP-778", shipment_plan["title"])
        self.assertIn("Expected impact", shipment_plan["expected_impact"])

        self.assertIn("actions", order_plan)
        self.assertIn("ORD-2203", order_plan["title"])
        self.assertIn("confidence", order_plan)

    def test_solution_raises_for_unknown_issue(self) -> None:
        with self.assertRaises(KeyError):
            self.service.solution("bottleneck", "Unknown-Line")


if __name__ == "__main__":
    unittest.main()
