#!/usr/bin/env python3
"""Validate the curated college-essay catalog with only the Python standard library."""

from __future__ import annotations

import datetime as dt
import json
import re
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "data" / "catalog.json"

ALLOWED_UNIVERSITIES = {"HKU", "HKUST", "CUHK", "NUS", "NTU"}
ALLOWED_TIERS = {"A", "A-", "B+", "B", "C+", "C", "D+", "D"}
ALLOWED_RECORD_TYPES = {
    "admitted_case",
    "outcome_reference",
    "community_advice",
    "public_walkthrough",
}
FEATURED_TIERS = {"A", "A-", "B+", "B"}
ID_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
TAG_PATTERN = re.compile(r"^[a-z0-9_]+$")

REQUIRED_RECORD_FIELDS = {
    "id",
    "record_type",
    "universities",
    "primary_university",
    "region",
    "degree_level",
    "application_route",
    "program",
    "intake_year",
    "outcome",
    "scholarship",
    "evidence_tier",
    "quality_score",
    "featured",
    "essay_format",
    "source",
    "copyright",
    "summary_zh",
    "strengths",
    "limitations",
    "tags",
}


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def valid_iso_date(value: object) -> bool:
    if value is None:
        return True
    if not isinstance(value, str):
        return False
    try:
        dt.date.fromisoformat(value)
    except ValueError:
        return False
    return True


def valid_https_url(value: object) -> bool:
    if not isinstance(value, str):
        return False
    parsed = urlparse(value)
    return parsed.scheme == "https" and bool(parsed.netloc)


def main() -> int:
    errors: list[str] = []

    try:
        catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: cannot read {CATALOG_PATH}: {exc}", file=sys.stderr)
        return 1

    for top_key in ("version", "last_updated", "scope", "records"):
        if top_key not in catalog:
            fail(errors, f"catalog: missing top-level key {top_key!r}")

    if not valid_iso_date(catalog.get("last_updated")):
        fail(errors, "catalog.last_updated must be an ISO date")

    scope = catalog.get("scope")
    if not isinstance(scope, dict):
        fail(errors, "catalog.scope must be an object")
        scope = {}

    priority = scope.get("priority_universities")
    if not isinstance(priority, list) or set(priority) != ALLOWED_UNIVERSITIES:
        fail(
            errors,
            "scope.priority_universities must contain HKU, HKUST, CUHK, NUS and NTU exactly once",
        )

    records = catalog.get("records")
    if not isinstance(records, list) or not records:
        fail(errors, "catalog.records must be a non-empty array")
        records = []

    ids: set[str] = set()
    source_urls: Counter[str] = Counter()
    university_coverage: Counter[str] = Counter()

    for index, record in enumerate(records):
        prefix = f"records[{index}]"
        if not isinstance(record, dict):
            fail(errors, f"{prefix}: must be an object")
            continue

        missing = REQUIRED_RECORD_FIELDS - record.keys()
        extra = record.keys() - REQUIRED_RECORD_FIELDS
        if missing:
            fail(errors, f"{prefix}: missing fields {sorted(missing)}")
        if extra:
            fail(errors, f"{prefix}: unsupported fields {sorted(extra)}")

        record_id = record.get("id")
        if not isinstance(record_id, str) or not ID_PATTERN.fullmatch(record_id):
            fail(errors, f"{prefix}.id: must be lowercase kebab-case")
            record_id = f"<invalid-{index}>"
        elif record_id in ids:
            fail(errors, f"{prefix}.id: duplicate id {record_id!r}")
        else:
            ids.add(record_id)

        record_type = record.get("record_type")
        if record_type not in ALLOWED_RECORD_TYPES:
            fail(errors, f"{record_id}.record_type: unsupported value {record_type!r}")

        universities = record.get("universities")
        if (
            not isinstance(universities, list)
            or not universities
            or any(u not in ALLOWED_UNIVERSITIES for u in universities)
            or len(universities) != len(set(universities))
        ):
            fail(errors, f"{record_id}.universities: invalid or duplicated school codes")
            universities = []
        else:
            university_coverage.update(universities)

        primary = record.get("primary_university")
        if primary not in universities:
            fail(errors, f"{record_id}.primary_university must appear in universities")

        if record.get("degree_level") != "undergraduate":
            fail(errors, f"{record_id}.degree_level: first release supports undergraduate only")

        intake_year = record.get("intake_year")
        if intake_year is not None and (
            not isinstance(intake_year, int) or not 2000 <= intake_year <= 2100
        ):
            fail(errors, f"{record_id}.intake_year: must be null or 2000..2100")

        tier = record.get("evidence_tier")
        if tier not in ALLOWED_TIERS:
            fail(errors, f"{record_id}.evidence_tier: unsupported value {tier!r}")

        score = record.get("quality_score")
        if not isinstance(score, int) or isinstance(score, bool) or not 0 <= score <= 100:
            fail(errors, f"{record_id}.quality_score: must be an integer from 0 to 100")

        featured = record.get("featured")
        if not isinstance(featured, bool):
            fail(errors, f"{record_id}.featured: must be boolean")
        elif featured and not (
            record_type == "admitted_case"
            and isinstance(score, int)
            and score >= 85
            and tier in FEATURED_TIERS
        ):
            fail(
                errors,
                f"{record_id}: featured requires admitted_case, score >= 85 and evidence tier B or above",
            )

        for field in ("essay_format", "strengths", "limitations", "tags"):
            value = record.get(field)
            if not isinstance(value, list) or not value or any(
                not isinstance(item, str) or not item.strip() for item in value
            ):
                fail(errors, f"{record_id}.{field}: must be a non-empty string array")
            elif len(value) != len(set(value)):
                fail(errors, f"{record_id}.{field}: duplicate values are not allowed")

        tags = record.get("tags")
        if isinstance(tags, list):
            for tag in tags:
                if isinstance(tag, str) and not TAG_PATTERN.fullmatch(tag):
                    fail(errors, f"{record_id}.tags: {tag!r} is not snake_case")

        summary = record.get("summary_zh")
        if not isinstance(summary, str) or len(summary.strip()) < 20:
            fail(errors, f"{record_id}.summary_zh: must contain a substantive Chinese summary")

        source = record.get("source")
        if not isinstance(source, dict):
            fail(errors, f"{record_id}.source: must be an object")
            source = {}
        source_required = {"title", "url", "platform", "source_type", "published_at"}
        if set(source) != source_required:
            fail(errors, f"{record_id}.source: fields must be exactly {sorted(source_required)}")
        url = source.get("url")
        if not valid_https_url(url):
            fail(errors, f"{record_id}.source.url: must be an absolute HTTPS URL")
        elif isinstance(url, str):
            source_urls[url] += 1
        if not valid_iso_date(source.get("published_at")):
            fail(errors, f"{record_id}.source.published_at: must be null or ISO date")

        copyright_data = record.get("copyright")
        if not isinstance(copyright_data, dict):
            fail(errors, f"{record_id}.copyright: must be an object")
            copyright_data = {}
        copyright_required = {"full_text_in_repo", "policy", "license"}
        if set(copyright_data) != copyright_required:
            fail(
                errors,
                f"{record_id}.copyright: fields must be exactly {sorted(copyright_required)}",
            )
        full_text = copyright_data.get("full_text_in_repo")
        if not isinstance(full_text, bool):
            fail(errors, f"{record_id}.copyright.full_text_in_repo: must be boolean")
        if full_text and (
            "permission" not in str(copyright_data.get("policy", "")).lower()
            and "open" not in str(copyright_data.get("policy", "")).lower()
        ):
            fail(
                errors,
                f"{record_id}: full text requires explicit permission or open-license policy",
            )

    uncovered = ALLOWED_UNIVERSITIES - university_coverage.keys()
    if uncovered:
        fail(errors, f"catalog has no coverage for {sorted(uncovered)}")

    # Reusing one first-person source for multiple school-specific outcomes is allowed,
    # but it should be uncommon and visible.
    repeated = {url: count for url, count in source_urls.items() if count > 2}
    if repeated:
        fail(errors, f"source URLs repeated more than twice: {repeated}")

    if errors:
        print(f"Validation failed with {len(errors)} error(s):", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    featured_count = sum(bool(record["featured"]) for record in records)
    coverage_text = ", ".join(
        f"{university}={university_coverage[university]}"
        for university in ("HKU", "HKUST", "CUHK", "NUS", "NTU")
    )
    print(
        f"OK: {len(records)} records; {featured_count} featured; coverage {coverage_text}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
