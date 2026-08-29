#!/usr/bin/env python3
"""Generate docs/graduate-case-notes.md from data/graduate-catalog.json."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "data" / "graduate-catalog.json"
OUTPUT_PATH = ROOT / "docs" / "graduate-case-notes.md"

SCHOOLS = ("HKU", "HKUST", "CUHK", "NUS", "NTU")
TYPE_LABELS = {
    "official_requirement": "官方要求",
    "official_guidance": "官方写作指导",
    "official_exception": "官方例外 / 可选或替代材料",
    "admitted_case": "录取案例",
    "community_case": "社区经验",
}
PROGRAMME_LABELS = {
    "coursework_master": "授课型硕士",
    "research_master": "研究型硕士 / MPhil",
    "phd": "博士",
    "mba_or_executive": "MBA / 专业管理项目",
    "mixed_research_postgraduate": "研究型硕博",
    "multiple_programmes": "多项目",
}
STATUS_LABELS = {
    "current": "当前页面",
    "cycle_specific": "特定申请轮次",
    "historical": "历史材料",
    "not_applicable": "案例记录",
}


def shown(value: object, fallback: str = "未公开") -> str:
    if value is None:
        return fallback
    text = str(value).strip()
    return text or fallback


def render() -> str:
    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    records = catalog["records"]

    by_school: dict[str, list[dict]] = defaultdict(list)
    by_primary: dict[str, list[dict]] = defaultdict(list)
    for record in records:
        for school in record["universities"]:
            by_school[school].append(record)
        by_primary[record["primary_university"]].append(record)

    featured = sorted(
        (record for record in records if record["featured"]),
        key=lambda record: (-record["quality_score"], record["id"]),
    )
    admitted = sorted(
        (record for record in records if record["record_type"] == "admitted_case"),
        key=lambda record: (-record["quality_score"], record["id"]),
    )

    lines: list[str] = [
        "# 港新研究生申请文书要求、案例与拆解",
        "",
        f"> 自动生成自 `data/graduate-catalog.json`。请勿直接编辑本文件。"
        f"数据版本：`{catalog['version']}`；最后更新：`{catalog['last_updated']}`。",
        "",
        f"当前收录 **{len(records)} 条研究生文书记录**，其中 "
        f"**{len(featured)} 条重点记录**、**{len(admitted)} 条公开录取案例**。"
        "`quality_score` 是策展优先级，不是大学官方文书分数。",
        "",
        "研穵生公开材料中，官方题目与格式要求远多于“完整文书 + 可核验录取结果”。"
        "因此本页将官方要求、录取案例和社区经验分开标注；不会因为来源自称“成功范文”就提高证据等级。",
        "",
        "## 重点记录",
        "",
        "| 学校 | 记录 | 路径 | 类型 | 文书组件 | 证据 | 策展分 |",
        "|---|---|---|---|---|---:|---:|",
    ]

    for record in featured:
        lines.append(
            f"| {record['primary_university']} | "
            f"[`{record['id']}`](#{record['id']}) | "
            f"{PROGRAMME_LABELS[record['programme_type']]} | "
            f"{TYPE_LABELS[record['record_type']]} | "
            f"{', '.join(record['document_types'])} | "
            f"{record['evidence_tier']} | {record['quality_score']} |"
        )

    lines += [
        "",
        "## 可核验程度较高的录取案例",
        "",
    ]
    if admitted:
        lines += [
            "| 学校 | 案例 | 项目 | 结果 | 证据 | 策展分 |",
            "|---|---|---|---|---:|---:|",
        ]
        for record in admitted:
            lines.append(
                f"| {record['primary_university']} | "
                f"[`{record['id']}`](#{record['id']}) | "
                f"{shown(record['program'])} | {shown(record['outcome'])} | "
                f"{record['evidence_tier']} | {record['quality_score']} |"
            )
    else:
        lines.append("当前没有满足收录标准的研究生录取案例。")

    lines += [
        "",
        "## 按学校导航",
        "",
    ]

    for school in SCHOOLS:
        items = sorted(
            by_school[school],
            key=lambda record: (-record["quality_score"], record["id"]),
        )
        lines += [
            f"### {school}",
            "",
            "| 记录 | 路径 | 类型 | 项目 | 状态 | 证据 | 策展分 |",
            "|---|---|---|---|---|---:|---:|",
        ]
        for record in items:
            star = " ⭐" if record["featured"] else ""
            lines.append(
                f"| [`{record['id']}`](#{record['id']}){star} | "
                f"{PROGRAMME_LABELS[record['programme_type']]} | "
                f"{TYPE_LABELS[record['record_type']]} | "
                f"{shown(record['program'])} | "
                f"{STATUS_LABELS[record['requirement_status']]} | "
                f"{record['evidence_tier']} | {record['quality_score']} |"
            )
        lines.append("")

    lines += [
        "## 详细记录",
        "",
        "记录按主要学校和策展分排序。官方要求说明“该项目要求写什么”；"
        "录取案例只说明公开材料中可确认的写法与结果，不能证明文书单独导致录取。",
        "",
    ]

    for school in SCHOOLS:
        items = sorted(
            by_primary[school],
            key=lambda record: (-record["quality_score"], record["id"]),
        )
        lines += [f"## {school} 详细记录", ""]
        for record in items:
            lines += [
                f"### {record['id']}",
                "",
                f"- **记录类型：** {TYPE_LABELS[record['record_type']]}",
                f"- **研究生路径：** {PROGRAMME_LABELS[record['programme_type']]}",
                f"- **申请路径：** {shown(record['application_route'])}",
                f"- **专业 / 项目：** {shown(record['program'])}",
                f"- **申请轮次：** {shown(record['cycle'])}",
                f"- **要求状态：** {STATUS_LABELS[record['requirement_status']]}",
                f"- **结果：** {shown(record['outcome'], '不适用 / 未公开')}",
                f"- **奖学金：** {shown(record['scholarship'], '无公开信息')}",
                f"- **证据等级 / 策展分：** {record['evidence_tier']} / {record['quality_score']}",
                f"- **文书组件：** {', '.join(record['document_types'])}",
                f"- **原始来源：** [{record['source']['title']}]({record['source']['url']})"
                f"（{record['source']['platform']}）",
                f"- **版权处理：** {record['copyright']['policy']}；不在仓库镜像第三方全文",
                "",
                "**摘要与拆解**",
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
