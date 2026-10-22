import csv
from pathlib import Path

from icp_patterns import Trait, classify, derive, render, size_band, SENIORITY, DEPARTMENTS

ROWS = list(csv.DictReader(open(Path(__file__).parent.parent / "examples" / "evidence.csv", encoding="utf-8")))


def test_size_bands():
    assert size_band("180") == "51-200"
    assert size_band("1,200 employees") == "1001-5000"
    assert size_band("") is None


def test_title_classification():
    assert classify("Co-Founder & CEO", SENIORITY) == "C-level / Founder"
    assert classify("Head of Revenue Operations", DEPARTMENTS) == "RevOps / Sales Ops"
    assert classify("Director of Sales Operations", DEPARTMENTS) == "RevOps / Sales Ops"


def test_confidence_from_counts():
    assert Trait("x", "y", 5, 7).confidence == "H"
    assert Trait("x", "y", 3, 7).confidence == "M"
    assert Trait("x", "y", 2, 7).confidence == "L"


def test_only_shared_traits_survive():
    traits = derive(ROWS)
    industries = {t.value: t.count for t in traits["industry"]}
    assert industries == {"B2B SaaS": 5}  # Fintech and Marketplace appear once
    assert traits["tech_stack"][0].value == "HubSpot"
    assert {t.value for t in traits["department"]} >= {"RevOps / Sales Ops"}


def test_render_cites_evidence():
    out = render(derive(ROWS), len(ROWS))
    assert "Industry: B2B SaaS (Confidence: H - 5 of 7 customers match \"B2B SaaS\")" in out
