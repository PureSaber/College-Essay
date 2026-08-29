# College Essay · 港新申请文书案例库

一个面向香港、新加坡本科申请的**可核验文书案例索引与拆解库**，首批重点覆盖：

- 香港大学（HKU）
- 香港科技大学（HKUST）
- 香港中文大学（CUHK）
- 新加坡国立大学（NUS）
- 南洋理工大学（NTU）

当前版本收录 **17 个公开来源记录、22 个学校关联、9 个高置信度重点案例**。最后核验日期：**2026-08-29**。

> 本仓库不是“网传满分范文全文搬运库”。大学通常不公开文书分数，公开渠道中的“高分”也很少可验证。本项目使用的是**策展优先级分数 `quality_score`**，衡量来源证据、录取/奖学金结果、文书细节、可学习性和路径清晰度；它不等于学校官方评分，也不代表文书单独导致录取。

## 首批重点案例

| 学校 | 案例 | 结果 | 策展分 |
|---|---|---|---:|
| NUS | [Real Estate 第一志愿直接录取短答](docs/case-notes.md#nus-real-estate-direct-offer-2023) | 直接录取 | 97 |
| HKUST | [二次申请重写主线 + BAAS](docs/case-notes.md#hkust-russia-full-tuition-baas) | 全额学费 + HKD 50,000 BAAS | 96 |
| HKU | [“家”与建筑作品集联动](docs/case-notes.md#hku-architecture-full-tuition-2025) | 建筑录取 + 全额学费 | 94 |
| HKUST | [Personal / Impact Statement 分工](docs/case-notes.md#hkust-nigeria-full-ride-impact-statement) | 学费、住宿、生活费全奖 | 94 |
| NUS | [计算机科学与社会影响目标](docs/case-notes.md#nus-cs-goals-social-impact) | 录取 | 91 |
| HKUST | [CS + Economics 直接式动机信](docs/case-notes.md#hkust-almaty-cs-econ-scholarship-ps) | 录取 | 90 |
| NTU | [生物学重申请证据链](docs/case-notes.md#ntu-biology-structural-biology-reapplication-2026) | Biology + Structural Biology 录取 | 90 |

CUHK 的公开“完整文书 + 明确录取结果”材料目前明显少于其他四校，因此仓库不会用来源不明的营销范文填数量。现有 CUHK 记录会明确区分“录取结果样本”“匿名社区经验”和“未核验视频入口”。

## 目录

```text
.
├── data/
│   └── catalog.json              # 唯一事实源；新增案例优先改这里
├── docs/
│   ├── case-notes.md             # 由脚本生成的人类可读索引
│   ├── methodology.md            # 证据等级、评分与版权规则
│   └── school-requirements.md    # 五校当前文书要求与官方链接
├── schema/
│   └── catalog.schema.json       # 数据结构规范
├── scripts/
│   ├── build_index.py            # 从 JSON 重建 Markdown 索引
│   └── validate.py               # 零依赖校验
├── .github/
│   ├── ISSUE_TEMPLATE/
│   │   └── essay-submission.yml  # 新来源提交模板
│   └── workflows/
│       └── validate.yml          # CI：校验数据和生成文件一致性
├── CONTRIBUTING.md
└── LICENSE.md
```

## 使用

```bash
python scripts/validate.py
python scripts/build_index.py
```

新增记录后先运行两个命令，再提交 `data/catalog.json` 与重建后的 `docs/case-notes.md`。CI 会阻止字段缺失、重复 ID、非法链接、分数越界、学校覆盖缺失，以及生成文件未同步等问题。

## 阅读顺序

1. 先看 [`docs/school-requirements.md`](docs/school-requirements.md)，确认自己属于哪条申请路径。
2. 再看 [`docs/case-notes.md`](docs/case-notes.md)，优先参考 `B+ / B` 且与目标专业、路径相近的案例。
3. 用 [`docs/methodology.md`](docs/methodology.md) 的检查表拆解结构，不要复制句子。
4. 当年申请前回到学校官网和申请门户再次确认题目、字数及材料要求。

## 版权与学术诚信

第三方文书默认只保留**链接、元数据、中文转述和原创分析**。只有作者本人投稿且明确授权，或材料带有兼容开放许可证时，仓库才接收全文。请勿把任何案例改几个词后作为自己的申请文书；这既削弱真实性，也可能违反学校的诚信要求。

提交新来源见 [`CONTRIBUTING.md`](CONTRIBUTING.md)。
