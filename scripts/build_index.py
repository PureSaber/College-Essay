#!/usr/bin/env python3
"""Generate docs/case-notes.md from data/catalog.json."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "data" / "catalog.json"
OUTPUT_PATH = ROOT / "docs" / "case-notes.md"

SCHOOL_ORDER = ["HKU", "HKUST", "CUHK", "NUS", "NTU"]
TYPE_LABELS = {
    "admitted_case": "录取案例",
    "outcome_reference": "结果样本",
    "community_advice": "社区经验",
    "public_walkthrough": "公开视频入口",
}


def text(value: object, fallback: str = "未公开") -> str:
    if value is None:
        return fallback
    value = str(value).strip()
    return value or fallback


def render() -> str:
    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    records = catalog["records"]

    by_university: dict[str, list[dict]] = defaultdict(list)
    by_primary: dict[str, list[dict]] = defaultdict(list)
    for record in records:
        for university in record["universities"]:
            by_university[university].append(record)
        by_primary[record["primary_university"]].append(record)

    lines: list[str] = [
        "# 公开文书案例与拆解",
        "",
        f"> 自动生成自 `data/catalog.json`。请勿直接编辑本文件。数据版本："
        f"`{catalog['version']}`；最后更新：`{catalog['last_updated']}`。",
        "",
        "本页只收录来源链接、元数据、中文转述与原创分析，不镜像未经授权的第三方完整文书。"
        "`quality_score` 是策展优先级，不是大学官方文书分数。",
        "",
        "## 按学校导航",
        "",
    ]

    for university in SCHOOL_ORDER:
        items = sorted(
            by_university[university],
            key=lambda r: (-r["quality_score"], r["id"]),
        )
        lines += [
            f"### {university}",
            "",
            "| 案例 | 类型 | 结果 | 证据 | 策展分 |",
            "|---|---|---|---:|---:|",
        ]
        for record in items:
            star = " ⭐" if record["featured"] else ""
            lines.append(
                f"| [`{record['id']}`](#{record['id']}){star} | "
                f"{TYPE_LABELS[record['record_type']]} | "
                f"{text(record['outcome'])} | {record['evidence_tier']} | "
                f"{record['quality_score']} |"
            )
        lines.append("")

    lines += [
        "## 详细记录",
        "",
        "记录按主要学校和策展分排序；涉及多校的来源只展开一次，并在“涉及学校”中交叉标注。",
        "",
    ]

    for university in SCHOOL_ORDER:
        items = sorted(
            by_primary[university],
            key=lambda r: (-r["quality_score"], r["id"]),
        )
        lines += [f"## {university} 详细记录", ""]
        for record in items:
            lines += [
                f"### {record['id']}",
                "",
                f"- **类型：** {TYPE_LABELS[record['record_type']]}",
                f"- **涉及学校：** {', '.join(record['universities'])}",
                f"- **申请路径：** {text(record['application_route'])}",
                f"- **专业 / 项目：** {text(record['program'])}",
                f"- **入学年份：** {text(record['intake_year'])}",
                f"- **结果：** {text(record['outcome'])}",
                f"- **奖学金：** {text(record['scholarship'], '无公开信息')}",
                f"- **证据等级 / 策展分：** {record['evidence_tier']} / {record['quality_score']}",
                f"- **文书形态：** {', '.join(record['essay_format'])}",
                f"- **原始来源：** [{record['source']['title']}]({record['source']['url']})"
                f"（{record['source']['platform']}）",
                f"- **版权处理：** {record['copyright']['policy']}；不在仓库收录第三方全文",
                "",
                "**案例摘要**",
                "",
                record["summary_zh"],
                "",
                "**值得学习**",
                "",
            ]
            lines.extend(f"- {item}" for item in record["strengths"])
            lines += ["", "**局限与风险**", ""]
            lines.extend(f"- {item}" for item in record["limitations"])
            lines += [
                "",
                f"**标签：** `{'` `'.join(record['tags'])}`",
                "",
                "---",
                "",
            ]

    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    OUTPUT_PATH.write_text(render(), encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
