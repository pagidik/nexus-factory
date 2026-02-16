from __future__ import annotations

import sys
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mfg_pa.assistant import ManufacturingAssistant  # noqa: E402
from mfg_pa.loader import load_dataset  # noqa: E402


class AssistantTests(unittest.TestCase):
    def setUp(self) -> None:
        dataset = load_dataset(ROOT / "data" / "unstructured")
        self.assistant = ManufacturingAssistant(dataset, as_of=date(2026, 2, 16))

    def test_overview_contains_expected_metrics(self) -> None:
        overview = self.assistant.overview()
        self.assertIn("Lines monitored: 3", overview)
        self.assertIn("Delayed shipments: 2", overview)

    def test_bottleneck_question_mentions_paint_line(self) -> None:
        answer = self.assistant.ask("Where are bottlenecks?")
        self.assertIn("Paint-02", answer)
        self.assertIn("Logistics update", answer)

    def test_order_risk_question_mentions_known_risky_order(self) -> None:
        answer = self.assistant.ask("Any order risks?")
        self.assertIn("ORD-2203", answer)


if __name__ == "__main__":
    unittest.main()

