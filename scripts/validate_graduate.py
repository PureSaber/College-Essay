#!/usr/bin/env python3
"""Validate data/graduate-catalog.json using only the Python standard library."""

from __future__ import annotations

import datetime as dt
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "data" / "graduate-catalog.json"

SCHOOLS = ("HKU", "HKUST", "CUHK", "NUS", "NTU")
ALLOWED_UNIVERSITIES = set(SCHOOLS)
ALLOWED_REGIONS = {"Hong Kong", "Singapore"}
ALLOWED_PROGRAMME_TYPES = {
    "coursework_master",
    "research_master",
    "phd",
    "mba_or_executive",
    "mixed_research_postgraduate",
    "multiple_programmes",
}
RESEARCH_TYPES = {"research_master", "phd", "mixed_research_postgraduate"}
ALLOWED_RECORD_TYPES = {
    "official_requirement",
    "official_guidance",
    "official_exception",
    "admitted_case",
    "community_case",
}
OFFICIAL_TYPES = {
    "official_requirement",
    "official_guidance",
    "official_exception",
}
ALLOWED_REQUIREMENT_STATUS = {
    "current",
    "cycle_specific",
    "historical",
    "not_applicable",
}
ALLOWED_TIERS = {"A", "A-", "B+", "B", "C+", "C", "D+", "D"}
FEATURED_OFFICIAL_TIERS = {"A", "A-"}
FEATURED_CASE_TIERS = {"A", "A-", "B+", "B"}
ID_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
TOKEN_PATTERN = re.compile(r"^[a-z0-9_]+$")

REQUIRED_RECORD_FIELDS = {
    "id",
    "record_type",
    "universities",
    "primary_university",
    "region",
    "degree_level",
    "programme_type",
    "application_route",
    "program",
    "cycle",
    "requirement_status",
    "outcome",
    "scholarship",
    "evidence_tier",
    "quality_score",
    "featured",
    "document_types",
    "source",
    "copyright",
    "summary_zh",
    "strengths",
    "limitations",
    "tags",
}


def add(errors: list[str], message: str) -> None:
    errors.append(message)


def is_iso_date(value: object) -> bool:
    if value is None:
        return True
    if not isinstance(value, str):
        return False
    try:
        dt.date.fromisoformat(value)
    except ValueError:
        return False
    return True


def is_https_url(value: object) -> bool:
    if not isinstance(value, str):
        return False
    parsed = urlparse(value)
    return parsed.scheme == "https" and bool(parsed.netloc)


def is_nonempty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_string_list(
    errors: list[str],
    prefix: str,
    value: object,
    *,
    token_pattern: re.Pattern[str] | None = None,
) -> None:
    if (
        not isinstance(value, list)
        or not value
        or any(not is_nonempty_string(item) for item in value)
    ):
        add(errors, f"{prefix}: must be a non-empty string array")
        return
    if len(value) != len(set(value)):
        add(errors, f"{prefix}: duplicate values are not allowed")
    if token_pattern is not None:
        for item in value:
            if isinstance(item, str) and not token_pattern.fullmatch(item):
                add(errors, f"{prefix}: {item!r} must use lowercase snake_case")


def main() -> int:
    errors: list[str] = []

    try:
        catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: cannot read {CATALOG_PATH}: {exc}", file=sys.stderr)
        return 1

    if not isinstance(catalog, dict):
        print("ERROR: catalog root must be an object", file=sys.stderr)
        return 1

    expected_top = {"version", "last_updated", "scope", "records"}
    missing_top = expected_top - catalog.keys()
    extra_top = catalog.keys() - expected_top
    if missing_top:
        add(errors, f"catalog: missing top-level keys {sorted(missing_top)}")
    if extra_top:
        add(errors, f"catalog: unsupported top-level keys {sorted(extra_top)}")

    if not is_nonempty_string(catalog.get("version")):
        add(errors, "catalog.version must be a non-empty string")
    if not is_iso_date(catalog.get("last_updated")):
        add(errors, "catalog.last_updated must be an ISO date")

    scope = catalog.get("scope")
    if not isinstance(scope, dict):
        add(errors, "catalog.scope must be an object")
        scope = {}

    expected_scope = {
        "regions",
        "priority_universities",
        "degree_levels",
        "programme_types",
        "full_text_policy",
    }
    if set(scope) != expected_scope:
        add(errors, f"catalog.scope fields must be exactly {sorted(expected_scope)}")

    if set(scope.get("regions", [])) != ALLOWED_REGIONS:
        add(errors, "scope.regions must contain Hong Kong and Singapore exactly once")
    if set(scope.get("priority_universities", [])) != ALLOWED_UNIVERSITIES:
        add(errors, "scope.priority_universities must contain HKU, HKUST, CUHK, NUS and NTU")
    if scope.get("degree_levels") != ["graduate"]:
        add(errors, "scope.degree_levels must be exactly ['graduate']")
    if set(scope.get("programme_types", [])) != ALLOWED_PROGRAMME_TYPES:
        add(errors, "scope.programme_types does not match the supported programme types")
    if not is_nonempty_string(scope.get("full_text_policy")):
        add(errors, "scope.full_text_policy must be a non-empty string")

    records = catalog.get("records")
    if not isinstance(records, list) or not records:
        add(errors, "catalog.records must be a non-empty array")
        records = []

    ids: set[str] = set()
    source_urls: Counter[str] = Counter()
    school_coverage: Counter[str] = Counter()
    official_coverage: Counter[str] = Counter()
    programme_coverage: dict[str, set[str]] = defaultdict(set)

    for index, record in enumerate(records):
        prefix = f"records[{index}]"
        if not isinstance(record, dict):
            add(errors, f"{prefix}: must be an object")
            continue

        missing = REQUIRED_RECORD_FIELDS - record.keys()
        extra = record.keys() - REQUIRED_RECORD_FIELDS
        if missing:
            add(errors, f"{prefix}: missing fields {sorted(missing)}")
        if extra:
            add(errors, f"{prefix}: unsupported fields {sorted(extra)}")

        record_id = record.get("id")
        if not isinstance(record_id, str) or not ID_PATTERN.fullmatch(record_id):
            add(errors, f"{prefix}.id must be lowercase kebab-case")
            record_id = f"<invalid-{index}>"
        elif record_id in ids:
            add(errors, f"{prefix}.id duplicates {record_id!r}")
        else:
            ids.add(record_id)

        record_type = record.get("record_type")
        if record_type not in ALLOWED_RECORD_TYPES:
            add(errors, f"{record_id}.record_type: unsupported value {record_type!r}")

        universities = record.get("universities")
        if (
            not isinstance(universities, list)
            or not universities
            or any(school not in ALLOWED_UNIVERSITIES for school in universities)
            or len(universities) != len(set(universities))
        ):
            add(errors, f"{record_id}.universities: invalid or duplicated school codes")
            universities = []
        else:
            school_coverage.update(universities)
            for school in universities:
                programme_coverage[school].add(str(record.get("programme_type")))
                if record_type in OFFICIAL_TYPES:
                    official_coverage[school] += 1

        primary = record.get("primary_university")
        if primary not in universities:
            add(errors, f"{record_id}.primary_university must appear in universities")

        region = record.get("region")
        if region not in ALLOWED_REGIONS:
            add(errors, f"{record_id}.region: unsupported value {region!r}")
        elif primary in {"HKU", "HKUST", "CUHK"} and region != "Hong Kong":
            add(errors, f"{record_id}.region must be Hong Kong for {primary}")
        elif primary in {"NUS", "NTU"} and region != "Singapore":
            add(errors, f"{record_id}.region must be Singapore for {primary}")

        if record.get("degree_level") != "graduate":
            add(errors, f"{record_id}.degree_level must be 'graduate'")

        programme_type = record.get("programme_type")
        if programme_type not in ALLOWED_PROGRAMME_TYPES:
            add(errors, f"{record_id}.programme_type: unsupported value {programme_type!r}")

        if not is_nonempty_string(record.get("application_route")):
            add(errors, f"{record_id}.application_route must be a non-empty string")

        for nullable_field in ("program", "cycle", "outcome", "scholarship"):
            value = record.get(nullable_field)
            if value is not None and not is_nonempty_string(value):
                add(errors, f"{record_id}.{nullable_field} must be null or a non-empty string")

        status = record.get("requirement_status")
        if status not in ALLOWED_REQUIREMENT_STATUS:
            add(errors, f"{record_id}.requirement_status: unsupported value {status!r}")

        tier = record.get("evidence_tier")
        if tier not in ALLOWED_TIERS:
            add(errors, f"{record_id}.evidence_tier: unsupported value {tier!r}")

        score = record.get("quality_score")
        if not isinstance(score, int) or isinstance(score, bool) or not 0 <= score <= 100:
            add(errors, f"{record_id}.quality_score must be an integer from 0 to 100")

        featured = record.get("featured")
        if not isinstance(featured, bool):
            add(errors, f"{record_id}.featured must be boolean")
        elif featured:
            official_ok = (
                record_type in OFFICIAL_TYPES
                and tier in FEATURED_OFFICIAL_TIERS
                and isinstance(score, int)
                and score >= 97
            )
            case_ok = (
                record_type == "admitted_case"
                and tier in FEATURED_CASE_TIERS
                and isinstance(score, int)
                and score >= 91
                and is_nonempty_string(record.get("outcome"))
            )
            if not (official_ok or case_ok):
                add(
                    errors,
                    f"{record_id}: featured requires an A/A- official record scoring >=97 "
                    "or a verified admitted case scoring >=91",
                )

        if record_type == "admitted_case" and not is_nonempty_string(record.get("outcome")):
            add(errors, f"{record_id}: admitted_case requires a non-empty outcome")
        if record_type in OFFICIAL_TYPES and status == "not_applicable":
            add(errors, f"{record_id}: official records need a current, cycle-specific or historical status")

        validate_string_list(
            errors,
            f"{record_id}.document_types",
            record.get("document_types"),
            token_pattern=TOKEN_PATTERN,
        )
        validate_string_list(errors, f"{record_id}.strengths", record.get("strengths"))
        validate_string_list(errors, f"{record_id}.limitations", record.get("limitations"))
        validate_string_list(
            errors,
            f"{record_id}.tags",
            record.get("tags"),
            token_pattern=TOKEN_PATTERN,
        )

        summary = record.get("summary_zh")
        if not isinstance(summary, str) or len(summary.strip()) < 20:
            add(errors, f"{record_id}.summary_zh must contain a substantive summary")

        source = record.get("source")
        source_fields = {"title", "url", "platform", "source_type", "published_at"}
        if not isinstance(source, dict):
            add(errors, f"{record_id}.source must be an object")
            source = {}
        if set(source) != source_fields:
            add(errors, f"{record_id}.source fields must be exactly {sorted(source_fields)}")
        for field in ("title", "platform"):
            if not is_nonempty_string(source.get(field)):
                add(errors, f"{record_id}.source.{field} must be a non-empty string")
        source_type = source.get("source_type")
        if not isinstance(source_type, str) or not TOKEN_PATTERN.fullmatch(source_type):
            add(errors, f"{record_id}.source.source_type must use lowercase snake_case")
        source_url = source.get("url")
        if not is_https_url(source_url):
            add(errors, f"{record_id}.source.url must be an absolute HTTPS URL")
        elif isinstance(source_url, str):
            source_urls[source_url] += 1
        if not is_iso_date(source.get("published_at")):
            add(errors, f"{record_id}.source.published_at must be null or an ISO date")

        rights = record.get("copyright")
        rights_fields = {"full_text_in_repo", "policy", "license"}
        if not isinstance(rights, dict):
            add(errors, f"{record_id}.copyright must be an object")
            rights = {}
        if set(rights) != rights_fields:
            add(errors, f"{record_id}.copyright fields must be exactly {sorted(rights_fields)}")
        if not isinstance(rights.get("full_text_in_repo"), bool):
            add(errors, f"{record_id}.copyright.full_text_in_repo must be boolean")
        if rights.get("full_text_in_repo") and not any(
            token in str(rights.get("policy", "")).lower()
            for token in ("permission", "open", "author")
        ):
            add(errors, f"{record_id}: full text requires explicit permission or open licensing")
        for field in ("policy", "license"):
            if not is_nonempty_string(rights.get(field)):
                add(errors, f"{record_id}.copyright.{field} must be a non-empty string")

    for school in SCHOOLS:
        if school_coverage[school] < 4:
            add(errors, f"catalog needs at least four graduate records for {school}")
        if official_coverage[school] < 3:
            add(errors, f"catalog needs at least three official graduate records for {school}")
        types = programme_coverage[school]
        if "coursework_master" not in types and "multiple_programmes" not in types:
            add(errors, f"catalog needs coursework-master coverage for {school}")
        if not (types & RESEARCH_TYPES) and "multiple_programmes" not in types:
            add(errors, f"catalog needs research-postgraduate coverage for {school}")

    repeated = {url: count for url, count in source_urls.items() if count > 2}
    if repeated:
        add(errors, f"source URLs repeated more than twice: {repeated}")

    if errors:
        print(f"Validation failed with {len(errors)} error(s):", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    featured_count = sum(bool(record["featured"]) for record in records)
    coverage = ", ".join(f"{school}={school_coverage[school]}" for school in SCHOOLS)
    print(
        f"OK: {len(records)} graduate records; {featured_count} featured; "
        f"coverage {coverage}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
