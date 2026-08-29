# College Essay · 港新本科与研究生申请文书案例库

一个面向香港、新加坡大学申请的**可核验文书要求、公开案例索引与结构拆解库**，重点覆盖：

- 香港大学（HKU）
- 香港科技大学（HKUST）
- 香港中文大学（CUHK）
- 新加坡国立大学（NUS）
- 南洋理工大学（NTU）

当前版本分为两套互不混淆的数据集：

- **本科：**17 个公开来源记录，9 个重点案例；
- **研究生：**36 条要求或案例记录，17 条重点记录，其中 4 条公开录取案例；
- **合计：**53 条结构化记录，最后核验日期为 **2026-08-29**。

> 本仓库不是“网传满分范文全文搬运库”。大学通常不公开文书单项分数，研究生项目还经常因学院、学位类型和申请轮次而改变题目。`quality_score` 是**策展优先级**，衡量来源证据、要求清晰度、录取结果、公开细节和教学价值；它不是学校官方评分，也不表示文书单独导致录取。

## 研究生部分已经覆盖什么

研究生库不会把所有材料统称为 Personal Statement，而是区分：

- 授课型硕士 SOP / Personal Statement；
- MPhil / PhD research proposal、research plan、research-interest statement；
- academic / professional writing sample；
- MBA compulsory essays 与 scholarship essay；
- 明确 **不要求** 或只把文书列为可选的项目。

首批高价值记录包括：

| 学校 | 记录 | 价值 | 策展分 |
|---|---|---|---:|
| HKU | [研究型申请的 proposal / research-interest 分工](docs/graduate-case-notes.md#hku-rpg-proposal-or-research-interest) | 研究背景、目标、方法与 HKU 动机的最低框架 | 99 |
| HKUST | [研究计划 + 既往研究经历](docs/graduate-case-notes.md#hkust-rpg-research-plan-and-experience) | 把过去证据与未来课题连成连续研究路径 | 99 |
| CUHK | [中文系 PhD：proposal、PS、writing sample、硕士论文](docs/graduate-case-notes.md#cuhk-chinese-phd-proposal-ps-writing-sample) | 展示研究型材料组合及各自分工 | 99 |
| NUS | [Geography PhD 1,900 词组合式 SOP](docs/graduate-case-notes.md#nus-geography-phd-combined-sop-proposal) | 400 词背景动机 + 1,500 词研究计划 | 99 |
| NTU | [NBS PhD proposal + Statement of Objectives](docs/graduate-case-notes.md#ntu-nbs-phd-proposal-objectives) | 区分研究设计、研究动机和个人准备 | 99 |
| NTU | [MSBA 录取者的两问式 SOP](docs/graduate-case-notes.md#ntu-msba-admitted-sop-two-questions-2020) | 经验/接触 + 为什么读项目与选择 NTU | 96 |

研究生公开材料中，官方要求远多于“完整文书 + 可核验录取结果”。仓库因此把 `official_requirement`、`official_guidance`、`official_exception`、`admitted_case` 和 `community_case` 分开标记，而不是用来源不明的中介范文填充数量。

## 本科重点案例

| 学校 | 案例 | 结果 | 策展分 |
|---|---|---|---:|
| NUS | [Real Estate 第一志愿直接录取短答](docs/case-notes.md#nus-real-estate-direct-offer-2023) | 直接录取 | 97 |
| HKUST | [二次申请重写主线 + BAAS](docs/case-notes.md#hkust-russia-full-tuition-baas) | 全额学费 + HKD 50,000 BAAS | 96 |
| HKU | [“家”与建筑作品集联动](docs/case-notes.md#hku-architecture-full-tuition-2025) | 建筑录取 + 全额学费 | 94 |
| HKUST | [Personal / Impact Statement 分工](docs/case-notes.md#hkust-nigeria-full-ride-impact-statement) | 学费、住宿、生活费全奖 | 94 |
| NUS | [计算机科学与社会影响目标](docs/case-notes.md#nus-cs-goals-social-impact) | 录取 | 91 |
| NTU | [生物学重申请证据链](docs/case-notes.md#ntu-biology-structural-biology-reapplication-2026) | Biology + Structural Biology 录取 | 90 |

## 目录

```text
.
├── data/
│   ├── catalog.json                  # 本科唯一事实源
│   └── graduate-catalog.json         # 研究生唯一事实源
├── docs/
│   ├── case-notes.md                 # 自动生成：本科案例索引
│   ├── school-requirements.md        # 本科五校要求
│   ├── graduate-case-notes.md        # 自动生成：研究生要求与案例索引
│   ├── graduate-school-requirements.md
│   ├── graduate-writing-framework.md
│   └── methodology.md
├── schema/
│   ├── catalog.schema.json
│   └── graduate-catalog.schema.json
├── scripts/
│   ├── build_index.py
│   ├── validate.py
│   ├── build_graduate_index.py
│   └── validate_graduate.py
├── .github/
│   ├── ISSUE_TEMPLATE/essay-submission.yml
│   └── workflows/validate.yml
├── CONTRIBUTING.md
└── LICENSE.md
```

## 使用

```bash
# 本科
python scripts/validate.py
python scripts/build_index.py

# 研究生
python scripts/validate_graduate.py
python scripts/build_graduate_index.py
```

新增记录后，修改对应 JSON 唯一事实源，再重建相应 Markdown。CI 会检查：

- 字段完整性与枚举；
- 重复 ID、重复标签和非法链接；
- 学校与项目类型覆盖；
- `featured` 与证据等级是否匹配；
- 录取案例是否提供结果；
- 全文版权状态；
- 自动生成索引是否已同步提交。

## 阅读顺序

### 本科申请

1. [`docs/school-requirements.md`](docs/school-requirements.md)
2. [`docs/case-notes.md`](docs/case-notes.md)
3. [`docs/methodology.md`](docs/methodology.md)

### 研究生申请

1. [`docs/graduate-school-requirements.md`](docs/graduate-school-requirements.md)：先确认目标项目要求什么；
2. [`docs/graduate-case-notes.md`](docs/graduate-case-notes.md)：查看官方要求、录取案例和例外；
3. [`docs/graduate-writing-framework.md`](docs/graduate-writing-framework.md)：拆解 SOP、PS、proposal、writing sample 和 MBA essays 的分工。

当年提交前，必须回到项目官网和申请门户再次确认题目、字数、语言、文件格式、是否需要导师同意及截止时间。

## 版权与学术诚信

第三方材料默认只保留**链接、元数据、中文转述和原创分析**。只有作者本人明确授权、材料带兼容开放许可证，或已进入公有领域时，仓库才接收全文。

请勿：

- 把案例改几个词后作为自己的申请文书；
- 使用泄露、付费盗版或来源不明的文书包；
- 把他人的研究计划、经历或职业目标写成自己的；
- 将 `quality_score` 宣传成学校官方评分；
- 让生成式 AI 编造课程、导师、项目成果或个人经历。

提交新来源见 [`CONTRIBUTING.md`](CONTRIBUTING.md)。
