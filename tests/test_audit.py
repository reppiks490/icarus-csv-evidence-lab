import json
import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from csv_evidence import audit_file, audit_paths
from csv_evidence import audit as audit_module
from csv_evidence.fixtures import CASES, write_fixtures


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.manifest = json.loads(write_fixtures(self.root).read_text(encoding="utf-8"))

    def tearDown(self):
        self.tmp.cleanup()

    def test_every_fixture_has_expected_structural_result(self):
        self.assertEqual(len(self.manifest), len(CASES) + 1)
        for item in self.manifest:
            with self.subTest(item=item["file"]):
                report = audit_file(self.root / item["file"])
                expected = item["expected_finding"]
                if expected:
                    self.assertIn(expected, report["finding_counts"])
                else:
                    self.assertTrue(report["parse_complete"])
                    self.assertEqual(report["rows"], 1)
                self.assertEqual(report["eligibility"], "quarantined_pending_source_verification")
                self.assertEqual(report["provenance"]["chart_type"], "unverified")

    def test_quoted_comma_is_one_row(self):
        report = audit_file(self.root / "SYNTHETIC_quoted_comma.csv", delimiter=",")
        self.assertEqual(report["rows"], 1)
        self.assertEqual(report["columns"], 6)
        self.assertNotIn("ragged_row", report["finding_counts"])

    def test_identical_content_is_grouped_by_hash(self):
        original = self.root / "SYNTHETIC_clean_ohlc.csv"
        copy = self.root / "SYNTHETIC_copy.csv"
        copy.write_bytes(original.read_bytes())
        report = audit_paths([original, copy])
        self.assertEqual(report["file_count"], 2)
        self.assertEqual(len(report["identical_content_groups"]), 1)
        self.assertEqual(len(report["identical_content_groups"][0]), 2)

    def test_does_not_modify_input(self):
        path = self.root / "SYNTHETIC_bom.csv"
        before = path.read_bytes()
        audit_file(path)
        self.assertEqual(path.read_bytes(), before)

    def test_invalid_delimiter_rejected(self):
        with self.assertRaises(ValueError):
            audit_file(self.root / "SYNTHETIC_clean_ohlc.csv", delimiter="|")

    def test_invalid_and_duplicate_times_are_detected(self):
        path = self.root / "times.csv"
        path.write_text(
            "time,open,high,low,close\n"
            "not-a-time,100,101,99,100\n"
            "2026-01-01T10:01:00Z,100,101,99,100\n"
            "2026-01-01T10:01:00Z,100,101,99,100\n"
            "2026-01-01T10:00:00Z,100,101,99,100\n",
            encoding="utf-8",
        )
        counts = audit_file(path, delimiter=",")["finding_counts"]
        self.assertEqual(counts["invalid_timestamp"], 1)
        self.assertEqual(counts["duplicate_timestamp"], 1)
        self.assertEqual(counts["timestamp_out_of_order"], 1)

    def test_header_only_is_not_clean(self):
        path = self.root / "header_only.csv"
        path.write_text("time,open,high,low,close\n", encoding="utf-8")
        self.assertIn("no_data_rows", audit_file(path, delimiter=",")["finding_counts"])

    def test_missing_timestamp_column_is_not_clean(self):
        path = self.root / "no_time.csv"
        path.write_text("open,high,low,close\n100,101,99,100\n", encoding="utf-8")
        self.assertIn("missing_or_ambiguous_timestamp_column", audit_file(path, delimiter=",")["finding_counts"])

    def test_digest_and_parse_use_same_snapshot(self):
        path = self.root / "changing.csv"
        original = b"time,open,high,low,close\n2026-01-01T10:00:00Z,100,101,99,100\n"
        path.write_bytes(original)
        sniff = audit_module._dialect

        def mutate_after_snapshot(sample, delimiter):
            path.write_text("time,open,high,low,close\nBROKEN,100,101,99,100\n", encoding="utf-8")
            return sniff(sample, delimiter)

        with patch.object(audit_module, "_dialect", side_effect=mutate_after_snapshot):
            report = audit_file(path, delimiter=",")
        self.assertEqual(report["sha256"], hashlib.sha256(original).hexdigest())
        self.assertNotIn("invalid_timestamp", report["finding_counts"])
        self.assertIn("source_path_changed_during_audit", report["finding_counts"])

    def test_fixtures_do_not_overwrite_nonempty_directory(self):
        with self.assertRaises(FileExistsError):
            write_fixtures(self.root)

    def test_long_header_is_preserved(self):
        path = self.root / "long_header.csv"
        long_name = "x" * 150
        path.write_text(f"{long_name},another\n1,2\n", encoding="utf-8")
        self.assertEqual(audit_file(path, delimiter=",")["header"][0], long_name)

    def test_directory_scan_includes_every_csv_extension_case_recursively(self):
        corpus = self.root / 'SYNTHETIC_CASE_COVERAGE'
        nested = corpus / 'nested'
        nested.mkdir(parents=True)
        source = b'time,open,high,low,close\n2026-01-01T10:00:00Z,100,101,99,100\n'
        paths = [corpus / 'first.csv', nested / 'second.CSV', nested / 'third.CsV']
        for path in paths: path.write_bytes(source)
        (nested / 'notes.txt').write_bytes(source)
        report = audit_paths([corpus], delimiter=',')
        self.assertEqual(report['file_count'], 3)
        self.assertEqual({row['path'] for row in report['files']}, {str(p.resolve()) for p in paths})
        self.assertTrue(all(row['rows'] == 1 for row in report['files']))
        self.assertEqual(len(report['identical_content_groups'][0]), 3)
        for path in paths: self.assertEqual(path.read_bytes(), source)

    def test_csv_named_directory_does_not_abort_recursive_file_audit(self):
        corpus = self.root / 'SYNTHETIC_DIRECTORY_COVERAGE'
        misleading = corpus / 'directory.csv'
        misleading.mkdir(parents=True)
        path = misleading / 'actual.csv'
        path.write_text('time,open,high,low,close\n2026-01-01T10:00:00Z,100,101,99,100\n', encoding='utf-8')
        report = audit_paths([corpus], delimiter=',')
        self.assertEqual(report['file_count'], 1)
        self.assertEqual(report['files'][0]['path'], str(path.resolve()))


if __name__ == "__main__":
    unittest.main()
