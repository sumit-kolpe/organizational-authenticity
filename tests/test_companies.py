"""Test metadata failures with temporary synthetic CSVs; no network access."""
import csv
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest

from shared.utils.companies import CompanyMetadataError, load_companies, validate_assignment_sample


class CompanyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.file = Path(self.temp.name) / "companies.csv"

    def write(self, text):
        self.file.write_text(text, encoding="utf-8")
        return self.file

    def test_assignment_matches(self):
        rows = load_companies()
        validate_assignment_sample(rows)
        self.assertEqual(len(rows), 50)

    def test_order_does_not_matter(self):
        validate_assignment_sample(list(reversed(load_companies())))

    def test_ticker_punctuation_preserved(self):
        rows = load_companies(self.write("ticker,company_name,sector\nBRK.B,Example,Financials\n"))
        self.assertEqual(rows[0]["ticker"], "BRK.B")

    def test_bom_and_quoted_comma(self):
        rows = load_companies(self.write('\ufeffticker,company_name,sector\nTEST,"Example, Inc.",Example sector\n'))
        self.assertEqual(rows[0]["company_name"], "Example, Inc.")

    def test_invalid_csv_cases(self):
        header = "ticker,company_name,sector\n"
        cases = ["", header, "ticker,sector,company_name\nA,S,N\n",
                 header + "A,Name,Sector\nA,Other,Sector\n",
                 header + "A,,Sector\n", header + "A,Name\n",
                 header + "A,Name,Sector,Extra\n", header + " A,Name,Sector\n"]
        for text in cases:
            with self.subTest(text=text), self.assertRaises(CompanyMetadataError):
                load_companies(self.write(text))

    def test_missing_file(self):
        with self.assertRaises(CompanyMetadataError):
            load_companies(self.file)

    def test_missing_and_extra_assignment_tickers(self):
        rows = load_companies()
        for candidate in (rows[:-1], rows + [dict(ticker="EXTRA", company_name="Example", sector="Energy")]):
            with self.subTest(count=len(candidate)), self.assertRaises(CompanyMetadataError):
                validate_assignment_sample(candidate)

    def test_substitution_even_with_same_count(self):
        rows = load_companies()
        rows[0]["ticker"] = "OTHER"
        with self.assertRaises(CompanyMetadataError):
            validate_assignment_sample(rows)

    def test_incorrect_name_or_sector(self):
        for field in ("company_name", "sector"):
            rows = load_companies()
            rows[0][field] = "Incorrect"
            with self.subTest(field=field), self.assertRaises(CompanyMetadataError):
                validate_assignment_sample(rows)

    def test_generic_loader_allows_other_samples(self):
        rows = load_companies(self.write("ticker,company_name,sector\nTEST,Example,Example sector\n"))
        self.assertEqual(len(rows), 1)
        with self.assertRaises(CompanyMetadataError):
            validate_assignment_sample(rows)


if __name__ == "__main__":
    unittest.main()
