# Contributing

感谢补充港新本科或研究生申请文书来源。请优先通过 **Essay source submission** Issue 模板提交，维护者核验后再修改结构化目录。

## 应修改哪个数据文件

- 本科：`data/catalog.json`
- 研究生：`data/graduate-catalog.json`

不要直接编辑自动生成的 `docs/case-notes.md` 或 `docs/graduate-case-notes.md`。

## 最低信息要求

每条来源至少需要：

- 学校、学位层级、项目类型和申请路径；
- 原始公开链接，而非二手截图、聚合转载或网盘转存；
- 申请年份、当前页面或“未知”；
- 课程 / 专业（如公开）；
- 文书组件及限制；
- 录取与奖学金结果，以及结果证据类型；
- 你能从来源中确认的题目、主题、结构或修改过程；
- 版权状态与全文授权情况；
- 已删除的个人敏感信息说明。

### 研究生记录还应标明

- `coursework_master`、`research_master`、`phd`、`mba_or_executive`、`mixed_research_postgraduate` 或 `multiple_programmes`；
- SOP、Personal Statement、Research Proposal、Research Plan、Writing Sample、MBA essays 等具体组件；
- 项目是否要求申请前联系导师或取得 supervisor endorsement；
- 要求是 `current`、`cycle_specific`、`historical` 还是仅为案例记录；
- 项目明确不要求文书或把文书列为可选时，也应作为 `official_exception` 保存，而不是忽略。

## 全文提交规则

只有以下情形可以提交全文：

1. 你是原作者，并在 Issue 中明确同意以 CC BY 4.0、CC BY-SA 4.0 或 CC0 发布；或
2. 原始材料本身带有兼容开放许可证，并提供许可证链接；或
3. 材料已进入公有领域。

“公开可见”不等于“可以整篇转载”。没有授权时，只提交链接、元数据和你自己的概括分析。

全文必须脱敏，至少删除：

- 姓名、邮箱、电话、地址、生日；
- 申请号、证件号、学校内部账号；
- 推荐人和拟联系导师的私人联系方式；
- 能识别未成年人的具体个人信息；
- 未经同意的家庭健康、财务或法律信息；
- 未发表研究中不应公开的数据、合作方信息或保密内容。

## 证据升级

把案例从 C/D 升到 B/A，需要补充下列证据之一：

- 作者本人可核验的录取、在读或毕业信息；
- 录取或奖学金结果截图的脱敏版本；
- 学校官方展示页；
- 作者明确说明来源、年份、路径及对应文书组件。

官方要求只有在来源为大学、学院、项目或可核验官方账号时，才能评为 A / A-。中介网页不能因为写着“成功案例”而升级。

不得伪造、编辑或选择性裁剪结果证据。

## 修改流程

```bash
# 本科
python scripts/validate.py
python scripts/build_index.py

# 研究生
python scripts/validate_graduate.py
python scripts/build_graduate_index.py

git diff --check
```

提交时应同时包含：

- 对应 JSON 事实源的修改；
- 自动重建后的对应 Markdown 索引；
- 如字段结构变化，更新 schema、校验脚本、生成脚本和说明文档；
- 官方要求发生变化时，更新核验日期和 `requirement_status`。

## 学术诚信

本项目用于研究写作结构、材料分工和学校差异。禁止：

- 代写、出售或交换申请文书；
- 复制案例句子后仅做同义替换；
- 把他人经历、研究问题、数据或成果写成自己的；
- 发布通过泄露、付费盗版或未授权渠道获得的文书；
- 把策展分数宣传成学校官方评分；
- 使用生成式 AI 编造导师匹配、课程信息、发表记录或录取结果。
