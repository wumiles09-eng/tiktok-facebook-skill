# CLAUDE.md — TikTok × Facebook 海外短剧投放自动化

> 这是项目的**单一事实源**。所有 agent（Claude / Codex）在本仓库工作前必须先读完本文件。
> 项目级规则覆盖全局个人规则；冲突以本文件为准。

## 1. 项目定位（先读这一段）

这是一个**投放知识 + 可复用 skill** 仓库，不是软件产品。

**核心产出三件事：**
1. **自动化投放方案** —— 把"批量建计划 / 调优 / 创意轮换 / 复盘"做成确定性、可审计、人在环的 skill 工作流。
2. **投放策略沉淀** —— 把短剧出海投放的方法论、KPI 体系、市场差异固化成文档（`references/`）。
3. **skill 提炼** —— 从 TikTok Agentic Hub agents、飞书 wiki、Ss78we 自动化项目、clawhub.ai、实战经验中提炼可复用 skill。

**明确不做（边界）：**
- ❌ 不新建广告投放平台 / SaaS / 后端服务 / 从零的 UI。
- ❌ 不重写 TikTok / Meta 的 SDK 或 MCP。
- ❌ 不造"自主花钱"的 autonomous agent —— 花钱动作永远 read-first + 人工审批。
- ❌ 不在 Ads Manager 上跑浏览器自动化（Selenium/Playwright 录制操作广告后台）—— 违反平台 ToS、封号风险。公开页面（Creative Center / Ad Library）可用浏览器调研 skill。
- ❌ 不为了"能用"而硬编码 secrets、跳过审批门、弱化安全/合规校验。

**判断新工作是否属于本项目，问一句：** 它是在"固化投放方法/skill"，还是在"造新软件"？前者做，后者停。

## 2. 仓库结构

```
.
├── README.md                       # 面向使用者的总览
├── AGENTIC-HUB-MAPPING.md          # TT Agentic Hub agents → 本仓 skill 的映射
├── references/                     # 策略与领域知识（文档，不是代码）
│   ├── design-patterns.md          # 9 条核心设计模式（safety/架构底线）
│   ├── shortdrama-domain.md        # 短剧出海投放领域知识 + KPI 体系
│   ├── tt-mcp-tool-catalog.md      # TikTok 官方 MCP/API 工具目录
│   └── meta-sdk-quickstart.md      # Meta Marketing API 接入速查
└── skills/                         # 可复用 skill（每个一目录）
    ├── tt-ads-bridge/              # TT 官方 API 桥接（read-first）
    ├── meta-ads-bridge/            # Meta 官方 API 桥接（read-first）
    ├── batch-campaign-builder/     # 矩阵批量建计划 + matrix_expand.py
    ├── delivery-optimizer/         # 百分位基准 + 节奏预测 + percentile_bench.py / pacing_forecast.py
    ├── creative-fatigue-rotation/  # 只读疲劳检测 + fatigue_classify.py
    ├── shortdrama-creative-pipeline/ # 创意工厂（hook 剪辑/本地化/合规）
    ├── competitor-creative-recon/  # 竞品创意侦察（公开数据）
    └── automation-runlog-cockpit/  # 唯一审计日志（每个 skill 上报）
```

**约定：** 一个 skill = 一个目录 = 一个 `SKILL.md`（带 frontmatter）+ 可选 `scripts/`（纯计算 Python）。脚本只做确定性计算，不发真实 API 写请求；写请求由 bridge skill 在审批后发。

## 3. 硬性安全底线（不可破，来自 references/design-patterns.md）

1. **Read-first, mutate-with-approval.** 任何 create / update / pause / delete 动作前：先 read → 出 plan → 用户审批 → 执行 → 回读校验。全过程写 `automation-runlog-cockpit`。
2. **确定性本地算术.** 预算、出价、百分位、排期、idempotency key 全部本地确定性计算。**绝不让 LLM 算钱或决定金额。**
3. **只读 detector + 独立 actor.** 检测（fatigue/optimizer/recon）与执行（bridge/builder）职责分离；detector 永不直接 mutate。
4. **right-metric-per-objective.** `app_install` 看 CPI/首次付费；付费留存看 D0/D7 ROAS。不对齐的 KPI 不进同一基准池。
5. **Apples-to-apples 基准.** 同 `platform × objective × market` 的同侪百分位，不跨池比。
6. **永远不在 Ads Manager 上浏览器自动化.** 只用官方 API/MCP；公开调研页可用浏览器 skill。
7. **人在环 + runlog 是唯一真相源.** 没有 prior `approval` 条目，actor skill 不发写请求；同 `idem_key` 重复动作跳过不重放。

## 4. 短剧投放领域要点（详见 references/shortdrama-domain.md）

- 60–120s/集，paywall 通常在 ep10–15；矩阵投放 = 集数 × 市场 × 受众 × objective。
- 创意半衰期 3–7 天，需持续轮换。
- 核心 KPI：3s view、首集完播、CPI、付费集2 CVR、D0/D7 ROAS、hook rate、频次。
- 平台主推：TT Smart+/Spark + GMV Max；Meta Advantage+ App Promotion + CBO。CAPI 两边强制。

## 5. 工作方式

**验证脚本（不联网）：**
```bash
python3 -m py_compile skills/*/scripts/*.py          # 语法
python3 skills/delivery-optimizer/scripts/percentile_bench.py < sample.json
```

**提炼新 skill 的标准结构：**
```
skills/<kebab-name>/
├── SKILL.md          # frontmatter(name,description) + When/Inputs/Workflow/Safety gates/Example
└── scripts/*.py      # 可选；纯计算；可独立 py_compile + sample 跑
```
加 skill 前先确认：它是**可复用模式**（≥2 场景/项目会用），不是一次性脚本或未验证假设。

**改 skill 行为 = 改 SKILL.md + 脚本**，不引入新的 ad platform 抽象层。

## 6. Git / 发布

- 远端：`github.com/wumiles09-eng/tiktok-facebook-skill`（PUBLIC）
- 推送前必须切到正确账号（多账号防错）：
  ```bash
  gh-as wumiles09-eng && git push
  ```
- `.gitignore` 已排除 `__pycache__/`、`*.pyc`、`runlog/`、`plans/`、`*.sample.json` —— 真实广告数据/凭据不入库。
- 提交粒度：一个 skill / 一篇策略文档 = 一个 commit；commit message 用 `feat/fix/docs(<scope>): <desc>`。

## 7. 不要做的事（再次强调）

- 不要在本仓造 web 后端、数据库、前端、CLI 框架、新的 LLM 编排引擎。
- 不要把 wdrama / AutoYT / Novle 等其他项目的代码搬进来 —— 本仓只放**投放方法与 skill**。
- 不要用"为了跑通"理由删测试、弱校验、跳审批门、硬编码凭据。
- 不要在没读 `references/design-patterns.md` 的情况下改任何 skill 的 Safety gates。
