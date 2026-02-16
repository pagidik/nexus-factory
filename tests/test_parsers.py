from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mfg_pa.parsers import (  # noqa: E402
    parse_maintenance_risks,
    parse_order_records,
    parse_production_records,
    parse_shipment_records,
)


class ParserTests(unittest.TestCase):
    def test_production_parser_extracts_all_lines(self) -> None:
        text = (ROOT / "data" / "unstructured" / "shift_report_morning.txt").read_text(
            encoding="utf-8"
        )
        records = parse_production_records(text, "test")
        self.assertEqual(len(records), 3)
        self.assertEqual(records[0].line, "Assembly-01")
        self.assertAlmostEqual(records[1].defect_rate, 4.2)

    def test_shipment_parser_extracts_delayed_and_on_time(self) -> None:
        text = (ROOT / "data" / "unstructured" / "logistics_update.txt").read_text(
            encoding="utf-8"
        )
        records = parse_shipment_records(text, "test")
        self.assertEqual(len(records), 3)
        delayed = [record for record in records if record.delay_hours > 0]
        self.assertEqual(len(delayed), 2)

    def test_order_and_maintenance_parsers(self) -> None:
        orders_text = (ROOT / "data" / "unstructured" / "orders_digest.txt").read_text(
            encoding="utf-8"
        )
        maintenance_text = (
            ROOT / "data" / "unstructured" / "maintenance_note.txt"
        ).read_text(encoding="utf-8")
        orders = parse_order_records(orders_text, "test")
        risks = parse_maintenance_risks(maintenance_text, "test")
        self.assertEqual(len(orders), 4)
        self.assertEqual(orders[2].status, "at_risk")
        self.assertEqual(len(risks), 1)
        self.assertEqual(risks[0].line, "Paint-02")


if __name__ == "__main__":
    unittest.main()

