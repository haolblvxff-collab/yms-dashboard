# YMS - Yield Management System (良率管理系统)

**版本**: 1.0.0  
**创建日期**: 2026-03-20  
**作者**: lamber  
**Python 版本**: 3.9+

---

## 📖 项目简介

YMS (Yield Management System) 是半导体良率管理系统，用于收集、分析和可视化半导体制造过程中的良率相关数据。

### 核心功能

- **相关性分析**: Pearson/Spearman 方法，自动识别关键工艺参数
- **Wafer Map 可视化**: 交互式缺陷分布图
- **缺陷 Pareto 分析**: Top N 缺陷类型排序
- **SPC 控制图**: X-bar R、I-MR、P-Chart、C-Chart、U-Chart
- **缺陷分类**: 11 大类，30+ 子行业标准分类

---

## 🚀 快速开始

### 1. 环境要求

- Python 3.9+
- pip 21.0+
- PyCharm 2023.1+ (推荐)

### 2. 克隆/复制项目

```bash
cd /path/to/your/workspace
# 项目已在 /home/admin/openclaw/workspace/yms-project/
```

### 3. 创建虚拟环境

```bash
# 在项目根目录
python3 -m venv venv

# 激活虚拟环境
# Linux/macOS:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

### 4. 安装依赖

```bash
pip install -r requirements.txt
```

### 5. 运行示例

```bash
# 运行相关性分析示例
python src/yms/analysis/correlation_analysis.py --demo

# 运行 Wafer Map 可视化示例
python src/yms/visualization/wafer_map_viz.py --demo

# 运行 SPC 控制图示例
python src/yms/analysis/spc_control_charts.py --demo
```

---

## 📁 项目结构

```
yms-project/
├── src/
│   └── yms/                      # 主包
│       ├── __init__.py
│       ├── core/                 # 核心模块
│       │   ├── __init__.py
│       │   ├── config.py         # 配置管理
│       │   └── database.py       # 数据库连接
│       ├── analysis/             # 分析模块
│       │   ├── __init__.py
│       │   ├── correlation_analysis.py   # 相关性分析
│       │   └── spc_control_charts.py     # SPC 控制图
│       ├── visualization/        # 可视化模块
│       │   ├── __init__.py
│       │   └── wafer_map_viz.py  # Wafer Map 可视化
│       └── utils/                # 工具模块
│           ├── __init__.py
│           └── helpers.py        # 辅助函数
├── tests/                        # 测试目录
│   ├── __init__.py
│   ├── test_correlation.py
│   └── test_spc.py
├── data/                         # 数据目录
│   ├── raw/                      # 原始数据
│   └── processed/                # 处理后数据
├── schema/                       # 数据库 Schema
│   └── defect_module.sql         # 缺陷数据模型
├── config/                       # 配置文件
│   └── config.yaml               # 项目配置
├── docs/                         # 文档目录
├── requirements.txt              # Python 依赖
├── pyproject.toml                # 项目配置
├── setup.py                      # 安装脚本
├── .gitignore                    # Git 忽略文件
└── README.md                     # 项目说明
```

---

## 📦 依赖说明

### 核心依赖

| 包名 | 版本 | 用途 |
|------|------|------|
| numpy | >=1.21.0 | 数值计算 |
| pandas | >=1.3.0 | 数据处理 |
| scipy | >=1.7.0 | 科学计算 (相关性分析) |
| plotly | >=5.0.0 | 交互式可视化 |

### 可选依赖

| 包名 | 版本 | 用途 |
|------|------|------|
| matplotlib | >=3.4.0 | 静态图表 |
| seaborn | >=0.11.0 | 统计图表 |
| sqlalchemy | >=1.4.0 | 数据库 ORM |
| psycopg2 | >=2.9.0 | PostgreSQL 驱动 |

---

## 🔧 PyCharm 配置

### 1. 打开项目

1. 启动 PyCharm
2. File → Open
3. 选择 `yms-project` 目录
4. 点击 OK

### 2. 配置 Python 解释器

1. File → Settings → Project → Python Interpreter
2. 点击齿轮图标 → Add
3. 选择 "Existing environment"
4. 选择项目中的 `venv/bin/python`
5. 点击 OK

### 3. 标记目录

1. 右键 `src/` 目录 → Mark Directory as → Sources Root
2. 右键 `tests/` 目录 → Mark Directory as → Tests Root

### 4. 运行配置

1. Run → Edit Configurations
2. 点击 + → Python
3. 配置:
   - Name: Correlation Analysis Demo
   - Script path: `src/yms/analysis/correlation_analysis.py`
   - Parameters: `--demo`
   - Working directory: `$ProjectFileDir$`
4. 点击 OK

---

## 📊 功能模块

### 相关性分析 (correlation_analysis.py)

```python
from yms.analysis import CorrelationAnalysis

# 创建分析对象
analysis = CorrelationAnalysis()

# 运行示例
analysis.run_demo()

# 或分析自定义数据
df = pd.read_csv('wafer_data.csv')
report = analysis.analyze(df, method='spearman')
report.save_html('report.html')
```

### Wafer Map 可视化 (wafer_map_viz.py)

```python
from yms.visualization import WaferMapViz

# 创建可视化对象
viz = WaferMapViz()

# 生成 Wafer Map
viz.plot_wafer_map(defect_data, output_path='wafer_map.html')
```

### SPC 控制图 (spc_control_charts.py)

```python
from yms.analysis import SPCControlCharts

# 创建 SPC 对象
spc = SPCControlCharts()

# 生成 X-bar R 图
spc.plot_xbar_r(data, output_path='xbar_r_chart.html')

# 生成 P-Chart
spc.plot_p_chart(defect_counts, sample_sizes, output_path='p_chart.html')
```

---

## 🧪 测试

```bash
# 运行所有测试
pytest tests/

# 运行特定测试
pytest tests/test_correlation.py -v

# 生成覆盖率报告
pytest --cov=src/yms tests/
```

---

## 📝 数据库配置

### PostgreSQL 配置

1. 创建数据库:
```sql
CREATE DATABASE yms_db;
```

2. 导入 Schema:
```bash
psql -U postgres -d yms_db -f schema/defect_module.sql
```

3. 更新配置文件 `config/config.yaml`:
```yaml
database:
  host: localhost
  port: 5432
  name: yms_db
  user: postgres
  password: your_password
```

---

## 🤝 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📄 许可证

MIT License

---

## 📧 联系方式

- 项目维护者：lamber
- 项目日期：2026-03-20 ~ 2026-03-30

---

**祝使用愉快！** 🎉
