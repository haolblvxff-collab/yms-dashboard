# YMS 相关性分析工具

## 📋 概述

`correlation_analysis.py` 是一个用于半导体良率管理系统的工艺参数与良率相关性分析工具。

**功能特点**:
- ✅ 支持 Pearson 和 Spearman 两种相关分析方法
- ✅ 自动识别关键影响参数（|r| >= 0.3 且 p < 0.05）
- ✅ 生成交互式热力图可视化（HTML 格式）
- ✅ 显著性标记（*** p<0.001, ** p<0.01, * p<0.05）
- ✅ 内置示例数据用于演示

**推荐使用方法**: 对于半导体工艺数据，**推荐使用 Spearman 方法**，因为：
- 对异常值更稳健
- 不要求数据服从正态分布
- 适用于单调关系（不一定是线性）

---

## 🚀 快速开始

### 1. 运行示例演示

```bash
cd /home/admin/openclaw/workspace/yms-project/scripts
python3 correlation_analysis.py --demo
```

**输出**:
- 控制台显示相关性分析结果
- 生成 `correlation_demo_report.html` 交互式热力图

### 2. 分析实际数据

```bash
python3 correlation_analysis.py wafer_data.csv report.html spearman
```

**参数说明**:
- `wafer_data.csv` - 输入数据文件（CSV 格式）
- `report.html` - 输出文件名（可选，默认：correlation_report.html）
- `spearman` - 相关方法（可选，默认：spearman，可选值：spearman|pearson）

---

## 📊 数据格式要求

### CSV 文件格式

```csv
wafer_id,etch_temperature,deposition_pressure,implant_dose,anneal_time,oxide_thickness,yield_rate
1,248.5,0.49,1.02e15,29.8,99.2,0.87
2,251.2,0.51,0.98e15,30.5,101.3,0.82
3,249.8,0.50,1.01e15,30.1,100.1,0.85
...
```

**要求**:
- 第一行是列名（header）
- 至少包含 2 列数值数据
- **最后一列数值列**会被自动识别为良率指标
- 其他数值列被视为工艺参数

### 常见工艺参数列名示例

| 工艺步骤 | 参数示例 |
|----------|----------|
| 刻蚀 | etch_temperature, etch_pressure, etch_time |
| 沉积 | deposition_pressure, deposition_temperature, film_thickness |
| 离子注入 | implant_dose, implant_energy, tilt_angle |
| 退火 | anneal_temperature, anneal_time, ambient_gas |
| 氧化 | oxide_thickness, oxidation_temperature |
| 光刻 | exposure_dose, focus_offset, line_width |
| 清洗 | particle_count, contamination_level |

---

## 📈 输出说明

### 1. 控制台输出

```
============================================================
YMS 相关性分析报告
============================================================
分析方法：SPEARMAN
数据量：100 条记录
参数数量：8
良率指标：yield_rate
============================================================

📊 工艺参数与良率的相关性分析:
------------------------------------------------------------
          Parameter  Correlation  P_value Significance  Abs_Correlation
   etch_temperature    -0.385743 0.000074          ***         0.385743
         line_width     0.226331 0.023554            *         0.226331
       implant_dose    -0.157312 0.118032           ns         0.157312
...

============================================================
🔑 关键影响参数 (|r| >= 0.3 且 p < 0.05):
============================================================
       Parameter  Correlation  P_value Significance
etch_temperature    -0.385743 0.000074          ***
```

### 2. 显著性标记说明

| 标记 | p 值范围 | 含义 |
|------|----------|------|
| `***` | p < 0.001 | 极显著 |
| `**` | 0.001 ≤ p < 0.01 | 很显著 |
| `*` | 0.01 ≤ p < 0.05 | 显著 |
| `ns` | p ≥ 0.05 | 不显著 |

### 3. 相关性强度解释

| |r| 范围 | 相关性强度 |
|---------|----------|------------|
| 0.0-0.3 | 弱相关或无相关 |
| 0.3-0.5 | 中等相关 |
| 0.5-0.7 | 强相关 |
| 0.7-1.0 | 极强相关 |

**注意**: 相关性不等于因果性！需要结合工艺知识判断。

---

## 🔧 高级用法

### 1. 使用 Pearson 方法

```bash
python3 correlation_analysis.py wafer_data.csv report.html pearson
```

**适用场景**:
- 数据服从正态分布
- 变量之间是线性关系
- 没有明显异常值

### 2. 在 Python 脚本中调用

```python
import pandas as pd
from correlation_analysis import generate_correlation_report

# 读取数据
df = pd.read_csv('wafer_data.csv')

# 定义参数列和良率列
param_cols = ['etch_temperature', 'deposition_pressure', 'implant_dose']
yield_col = 'yield_rate'

# 生成报告
results, corr_matrix = generate_correlation_report(
    df, param_cols, yield_col,
    output_file='my_report.html',
    method='spearman'
)

# 查看结果
print(results)
```

### 3. 自定义分析

```python
from correlation_analysis import (
    analyze_parameter_yield_correlation,
    generate_correlation_matrix,
    plot_correlation_heatmap
)

# 1. 分析参数与良率的相关性
results = analyze_parameter_yield_correlation(
    df, param_cols, yield_col, method='spearman'
)

# 2. 生成相关性矩阵
corr_matrix = generate_correlation_matrix(df, method='spearman')

# 3. 绘制热力图
plot_correlation_heatmap(
    corr_matrix, 
    title='Custom Heatmap',
    output_file='custom_heatmap.html'
)
```

---

## 📊 示例数据说明

运行 `--demo` 时使用的示例数据包含以下列：

| 列名 | 含义 | 类型 | 范围 |
|------|------|------|------|
| wafer_id | 晶圆编号 | 整数 | 1-100 |
| etch_temperature | 刻蚀温度 | 浮点数 | 240-260°C |
| deposition_pressure | 沉积压力 | 浮点数 | 0.46-0.54 Torr |
| implant_dose | 注入剂量 | 浮点数 | ~1e15 ions/cm² |
| anneal_time | 退火时间 | 浮点数 | 26-34 min |
| oxide_thickness | 氧化层厚度 | 浮点数 | 94-106 nm |
| line_width | 线宽 | 浮点数 | 0.17-0.19 μm |
| particle_count | 颗粒数 | 整数 | 泊松分布 |
| yield_rate | 良率 | 浮点数 | 0-1 |

**示例数据中的相关性**:
- `etch_temperature` 与 `yield_rate` 负相关（温度越高，良率越低）
- `particle_count` 与 `yield_rate` 负相关（颗粒越多，良率越低）
- `deposition_pressure` 与 `yield_rate` 正相关（压力适中，良率较高）

---

## ⚠️ 注意事项

### 1. 数据质量

- **缺失值**: 自动跳过含有缺失值的样本
- **异常值**: Spearman 方法对异常值更稳健
- **样本量**: 建议至少 30 个样本，最好 100+ 样本

### 2. 相关性解释

- **相关性 ≠ 因果性**: 高相关不代表因果关系
- **混淆变量**: 可能存在未测量的第三变量影响
- **非线性关系**: Pearson 只能检测线性关系

### 3. 工艺知识结合

相关性分析结果需要结合工艺知识解释：

```
示例：
- etch_temperature 与 yield_rate 负相关 (r=-0.39, p<0.001)

工艺解释:
✅ 可能原因：高温导致光刻胶硬化，影响刻蚀精度
✅ 验证方法：检查高温批次的 CD-SEM 数据
✅ 改进措施：优化刻蚀温度窗口，加强温度控制
```

---

## 🔗 相关文件

- `correlation_analysis.py` - 主脚本
- `correlation_demo_report.html` - 示例输出（运行 --demo 生成）
- `../YMS-Architecture.md` - YMS 系统架构文档
- `../YMS-用户手册.md` - YMS 用户手册

---

## 📝 更新日志

### 2026-03-22
- ✅ 创建 correlation_analysis.py
- ✅ 支持 Pearson 和 Spearman 两种方法
- ✅ 添加 --demo 参数运行示例
- ✅ 生成交互式 HTML 热力图
- ✅ 自动识别关键影响参数
- ✅ 添加显著性标记

---

## 🙏 反馈与建议

如有问题或建议，请联系：
- Email: [your-email@example.com]
- Issue: [GitHub Issues]

---

**最后更新**: 2026-03-22  
**作者**: lamber
