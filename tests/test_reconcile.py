import json
import tempfile
import unittest
from pathlib import Path

from csv_evidence.reconcile import reconcile


class ReconcileTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.aion = self.root / "aion.json"
        self.nexus = self.root / "nexus.json"

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, aion_members, nexus_streams):
        self.aion.write_text(json.dumps({"members": aion_members}), encoding="utf-8")
        self.nexus.write_text(json.dumps({"streams": nexus_streams}), encoding="utf-8")

    def test_missing_hash_and_duplicate_multiplicity(self):
        a, b = "a" * 64, "b" * 64
        self.write(
            [{"status": "parsed", "member_sha256": a, "data_rows": 10},
             {"status": "parsed", "member_sha256": a, "data_rows": 10},
             {"status": "parsed", "member_sha256": b, "data_rows": 4}],
            [{"identity": {"raw_sha256": a}, "row_count": 10, "quality_flags": []}],
        )
        result = reconcile(self.aion, self.nexus)
        self.assertEqual(result["aion_entries"], 3)
        self.assertEqual(result["aion_only_hashes"], [b])
        self.assertEqual(result["multiplicity_difference_hashes"], [a])
        self.assertFalse(result["coverage_claim_allowed"])

    def test_row_count_semantics_are_not_assumed_equal(self):
        a = "a" * 64
        self.write(
            [{"status": "parsed", "member_sha256": a, "data_rows": 11}],
            [{"identity": {"raw_sha256": a}, "row_count": 10, "quality_flags": []}],
        )
        result = reconcile(self.aion, self.nexus)
        self.assertEqual(result["row_count_difference_hashes"], [a])
        self.assertFalse(result["coverage_claim_allowed"])

    def test_invalid_hash_is_rejected(self):
        self.write([{"status": "parsed", "member_sha256": "wrong", "data_rows": 1}], [])
        with self.assertRaises(ValueError):
            reconcile(self.aion, self.nexus)

    def test_identical_inventory_does_not_grant_market_authority(self):
        a = "a" * 64
        self.write(
            [{"status": "parsed", "member_sha256": a, "data_rows": 10}],
            [{"identity": {"raw_sha256": a}, "row_count": 10, "quality_flags": []}],
        )
        result = reconcile(self.aion, self.nexus)
        self.assertTrue(result["inventory_equivalent"])
        self.assertFalse(result["coverage_claim_allowed"])


if __name__ == "__main__":
    unittest.main()
