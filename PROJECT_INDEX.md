# YMS Project - 完整项目索引

**最后更新**: 2026-03-31  
**项目版本**: 1.0.0

---

## 📁 完整目录结构

```
yms-project/
├── 📄 核心文件
│   ├── README.md                     # 项目说明
│   ├── PYCHARM_SETUP.md              # PyCharm 配置指南
│   ├── requirements.txt              # Python 依赖
│   ├── pyproject.toml                # 项目配置
│   ├── setup.py                      # 安装脚本
│   └── .gitignore                    # Git 忽略
│
├── 🐍 源代码 (src/yms/)
│   ├── __init__.py                   # 包初始化
│   ├── core/                         # 核心模块
│   │   ├── __init__.py
│   │   ├── config.py                 # 配置管理
│   │   └── database.py               # 数据库连接
│   ├── analysis/                     # 分析模块
│   │   ├── __init__.py
│   │   ├── correlation_analysis.py   # 相关性分析
│   │   └── spc_control_charts.py     # SPC 控制图
│   ├── visualization/                # 可视化模块
│   │   ├── __init__.py
│   │   └── wafer_map_viz.py          # Wafer Map 可视化
│   └── utils/                        # 工具模块
│       ├── __init__.py
│       └── helpers.py                # 辅助函数
│
├── 🧪 测试 (tests/)
│   ├── __init__.py
│   ├── test_correlation.py           # 相关性分析测试
│   └── test_spc.py                   # SPC 控制图测试
│
├── 🗄️ 数据库 (schema/)
│   └── defect_module.sql             # 缺陷数据模型 (~16.7KB)
│
├── ⚙️ 配置 (config/)
│   └── config.yaml                   # 项目配置
│
├── 📊 数据 (data/)
│   ├── raw/                          # 原始数据
│   └── processed/                    # 处理后数据
│
├── 📚 文档 (docs/)
│   ├── learning/                     # 学习资料
│   │   ├── YMS-learning-plan.md      # YMS 学习计划
│   │   ├── YMS-phase1-plan.md        # Phase 1 计划
│   │   ├── YMS-resources.md          # 学习资源
│   │   ├── YMS-resources-direct-links.md  # 资源直链
│   │   └── YMS-study-notes-existing.md    # 已有笔记
│   │
│   ├── notes/                        # 学习笔记
│   │   ├── CMOS-process-map.md       # CMOS 工艺流程图
│   │   ├── CMOS-process-notes.md     # CMOS 工艺笔记
│   │   ├── Metallization-notes.md    # 金属化工艺笔记
│   │   ├── Handbook-Ch1-notes.md     # Handbook 第 1 章
│   │   └── Handbook-notes.md         # Handbook 笔记
│   │
│   ├── plans/                        # 计划文档
│   │   └── YMS-linux-migration-plan.md  # Linux 移植计划
│   │
│   ├── tests/                        # 测试题
│   │   └── phase1-test.md            # Phase 1 综合测试
│   │
│   └── skills/                       # Skills
│       └── semiconductor-yms.skill   # 半导体 YMS skill
│
├── 📖 知识库 (knowledge/)
│   ├── terminology.md                # 术语表 (77 个术语)
│   ├── yms/                          # YMS 知识
│   ├── cmos/                         # CMOS 知识
│   └── spc/                          # SPC 知识
│
├── 📜 脚本 (scripts/)
│   ├── correlation_analysis.py       # 相关性分析脚本
│   ├── legacy_correlation_analysis.py # 旧版脚本
│   └── correlation_demo_report.html  # 示例报告
│
└── 📝 日志
    └── yms.log                       # 运行日志
```

---

## 📊 文件统计

| 类别 | 文件数 | 总大小 |
|------|--------|--------|
| **源代码** | 10+ | ~30KB |
| **数据库 Schema** | 1 | ~17KB |
| **文档** | 15+ | ~100KB |
| **知识库** | 10+ | ~200KB |
| **测试** | 3+ | ~20KB |
| **配置** | 5+ | ~5KB |
| **总计** | **44+** | **~372KB** |

---

## 🎯 核心功能模块

### 1. 相关性分析 (`src/yms/analysis/correlation_analysis.py`)

**功能**:
- Pearson/Spearman 两种相关分析方法
- 自动识别关键影响参数 (|r|>=0.3, p<0.05)
- 生成交互式热力图 (Plotly HTML)
- 显著性标记 (*** p<0.001, ** p<0.01, * p<0.05)

**使用示例**:
```python
from yms.analysis import CorrelationAnalysis

analysis = CorrelationAnalysis()
analysis.run_demo()
```

---

### 2. SPC 控制图 (`src/yms/analysis/spc_control_charts.py`)

**功能**:
- X-bar R 图 (均值 - 极差图)
- I-MR 图 (单值 - 移动极差图)
- P-Chart (不合格品率图)
- C-Chart (缺陷数图)
- U-Chart (单位缺陷数图)
- Western Electric Rules (6 条判异规则)

**使用示例**:
```python
from yms.analysis import SPCControlCharts

spc = SPCControlCharts()
spc.plot_xbar_r(data, output_path='xbar_r.html')
```

---

### 3. Wafer Map 可视化 (`src/yms/visualization/wafer_map_viz.py`)

**功能**:
- 圆形晶圆模板 (300mm)
- 缺陷坐标 plotting
- 按缺陷类型着色 (8 种预设颜色)
- 图例和统计信息
- 按工艺层分组显示

**使用示例**:
```python
from yms.visualization import WaferMapViz

viz = WaferMapViz()
viz.plot_wafer_map(defect_data, output_path='wafer_map.html')
```

---

### 4. 缺陷数据模型 (`schema/defect_module.sql`)

**数据表** (10 张):
1. `defect_category` - 缺陷分类表 (11 大类，30+ 子类)
2. `defect_inspection` - 检测记录表
3. `defect_detail` - 缺陷明细表
4. `v_defect_pareto` - Pareto 分析视图
5. `v_defect_density_trend` - 密度趋势视图
6. `defect_spc_control` - SPC 控制表
7. `defect_alert` - 告警记录表
8. `defect_wafer_map` - Wafer Map 数据表
9. `defect_electrical_corr` - 缺陷 - 电测关联表

**核心功能**:
- 缺陷自动分类 + 人工复检
- Pareto 分析 (Top N 缺陷)
- SPC 控制 (Western Electric Rules)
- 告警管理 (OPEN/ACKNOWLEDGED/CLOSED)
- 缺陷 - 电测关联分析

---

## 📚 知识库内容

### 术语表 (77 个术语)

**分类统计**:
- CMOS 工艺：30+ 个
- YMS 架构：15+ 个
- SPC/统计：10+ 个
- 质量管理：10+ 个
- 其他：12+ 个

**位置**: `knowledge/terminology.md`

---

### CMOS 工艺笔记

| 文件 | 内容 |
|------|------|
| `CMOS-process-map.md` | 8 大工艺流程图、KPP 汇总 |
| `CMOS-process-notes.md` | 各工艺详细笔记 |
| `Metallization-notes.md` | 金属化工艺专项 |

**状态**: ✅ 8/8 工艺全部完成

---

### YMS 学习资料

| 文件 | 内容 |
|------|------|
| `YMS-learning-plan.md` | 完整学习计划 |
| `YMS-phase1-plan.md` | Phase 1 详细规划 |
| `YMS-resources.md` | 学习资源索引 |
| `YMS-study-notes-existing.md` | 已有学习笔记 |

---

## 🧪 测试与验证

### Phase 1 综合测试

**文件**: `docs/tests/phase1-test.md`

**内容**:
- Part 1: CMOS 工艺 (40 分)
- Part 2: YMS 模型 (30 分)
- Part 3: 术语表 (30 分)
- Part 4: 综合应用 (20 分)

**成绩**: 108/120 分 (90%) ✅ 通过

---

## 🚀 快速开始

### 1. 安装依赖

```bash
cd yms-project/
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. 运行 Demo

```bash
# 相关性分析
python src/yms/analysis/correlation_analysis.py --demo

# SPC 控制图
python src/yms/analysis/spc_control_charts.py --demo

# Wafer Map 可视化
python src/yms/visualization/wafer_map_viz.py --demo
```

### 3. 运行测试

```bash
pytest tests/ -v
```

---

## 📈 项目进度

| Phase | 主题 | 进度 | 状态 |
|-------|------|------|------|
| **Phase 1** | 基础建立 | **100%** | ✅ 完成 |
| Phase 2 | YE 核心技能 | 10% | 🟢 进行中 |
| Phase 3 | 异常分析 | 0% | ⏳ 待开始 |
| Phase 4 | 系统集成 | 0% | ⏳ 待开始 |
| Phase 5 | 实战演练 | 10% | 🟢 进行中 |

---

## 📞 联系方式

- **项目维护者**: lamber
- **项目起始**: 2026-03-20
- **最后更新**: 2026-03-31
- **项目位置**: `/home/admin/openclaw/workspace/yms-project/`

---

**完整项目已整理完毕！** 🎉
