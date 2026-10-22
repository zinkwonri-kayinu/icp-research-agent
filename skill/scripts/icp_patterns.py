"""Turn a table of customer evidence into an ICP with counted confidence.

The agent collects evidence (case studies, reviews, logos) into a CSV. This
script does the part LLMs are bad at: counting. A trait only makes the ICP if
at least 2 customers share it, and confidence comes from the share, not vibes.

Usage:
    python skill/scripts/icp_patterns.py examples/evidence.csv
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

SIZE_BANDS = [(1, 10), (11, 50), (51, 200), (201, 500), (501, 1000), (1001, 5000), (5001, 10**9)]
SENIORITY = [
    ("C-level / Founder", r"\b(ceo|cfo|coo|cto|cro|cmo|chief|founder|co-founder|owner|president)\b"),
    ("VP", r"\b(vp|vice president)\b"),
    ("Head / Director", r"\b(head|director)\b"),
    ("Manager", r"\b(manager|lead)\b"),
]
DEPARTMENTS = [
    ("RevOps / Sales Ops", r"\b(revops|revenue operations|sales ops|sales operations|gtm ops)\b"),
    ("Sales", r"\b(sales|account executive|sdr|bdr|business development)\b"),
    ("Marketing / Growth", r"\b(marketing|growth|demand gen|demand generation)\b"),
    ("Operations", r"\b(operations|ops)\b"),
    ("Engineering", r"\b(engineer|engineering|developer|technical)\b"),
    ("Executive", r"\b(ceo|founder|co-founder|president|owner)\b"),
]


@dataclass
class Trait:
    field: str
    value: str
    count: int
    total: int

    @property
    def share(self) -> float:
        return self.count / self.total if self.total else 0.0

    @property
    def confidence(self) -> str:
        if self.count >= 3 and self.share >= 0.6:
            return "H"
        if self.share >= 0.4:
            return "M"
        return "L"

    def evidence(self) -> str:
        return f"{self.count} of {self.total}"


def size_band(raw: str) -> str | None:
    digits = re.sub(r"[^\d]", "", raw or "")
    if not digits:
        return None
    n = int(digits)
    for lo, hi in SIZE_BANDS:
        if lo <= n <= hi:
            return f"{lo}-{hi}" if hi < 10**9 else f"{lo}+"
    return None


def classify(title: str, rules: list[tuple[str, str]]) -> str | None:
    title = (title or "").lower()
    for label, pattern in rules:
        if re.search(pattern, title):
            return label
    return None


def split_multi(value: str) -> list[str]:
    return [v.strip() for v in re.split(r"[;|]", value or "") if v.strip()]


def derive(rows: list[dict]) -> dict[str, list[Trait]]:
    fields: dict[str, Counter] = {
        "industry": Counter(),
        "employees": Counter(),
        "stage": Counter(),
        "geography": Counter(),
        "business_model": Counter(),
        "tech_stack": Counter(),
        "seniority": Counter(),
        "department": Counter(),
    }
    for row in rows:
        for key in ("industry", "stage", "geography", "business_model"):
            if row.get(key, "").strip():
                fields[key][row[key].strip()] += 1
        if band := size_band(row.get("employees", "")):
            fields["employees"][band] += 1
        for tool in set(split_multi(row.get("tech_stack", ""))):
            fields["tech_stack"][tool] += 1
        if s := classify(row.get("title", ""), SENIORITY):
            fields["seniority"][s] += 1
        if d := classify(row.get("title", ""), DEPARTMENTS):
            fields["department"][d] += 1

    total = len(rows)
    return {
        name: [Trait(name, value, n, total) for value, n in counter.most_common() if n >= 2]
        for name, counter in fields.items()
    }


def render(traits: dict[str, list[Trait]], total: int) -> str:
    def line(label: str, key: str) -> str:
        items = traits.get(key, [])
        if not items:
            return f"- {label}: no pattern (fewer than 2 customers share a value)"
        values = ", ".join(t.value for t in items)
        top = items[0]
        return f"- {label}: {values} (Confidence: {top.confidence} - {top.evidence()} customers match \"{top.value}\")"

    return "\n".join(
        [
            f"## ICP: Clay list-building format ({total} customers analysed)",
            "**Company filters**",
            line("Industry", "industry"),
            line("Company size (employees)", "employees"),
            line("Growth stage / funding", "stage"),
            line("Geography", "geography"),
            line("Business model", "business_model"),
            line("Tech stack", "tech_stack"),
            "",
            "**People filters (buyer persona)**",
            line("Seniority", "seniority"),
            line("Department", "department"),
        ]
    )


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Count ICP patterns in a customer evidence CSV.")
    p.add_argument("evidence", type=Path)
    args = p.parse_args(argv)
    with open(args.evidence, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        sys.exit("evidence file is empty")
    print(render(derive(rows), len(rows)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
