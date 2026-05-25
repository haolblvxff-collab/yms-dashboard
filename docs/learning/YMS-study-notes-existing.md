# YMS 系统学习笔记 - 现有资料深度学习

**学习时间**: 2026-03-21 11:35-12:00  
**资料来源**: semiconductor-yms skill  
**学习者**: lamber

---

## 📚 知识体系总览

```
半导体 YMS 系统
│
├── 1️⃣ 系统架构 (architecture-patterns.md)
│   ├── 4 层架构设计
│   ├── 部署模式
│   └── 数据流设计
│
├── 2️⃣ 数据模型 (data-model.md)
│   ├── 6 大核心实体
│   ├── 数据表设计
│   └── 索引与分区
│
├── 3️⃣ 工艺控制 (spc-rules.md)
│   ├── SPC 控制图
│   ├── 告警规则
│   └── 过程能力指数
│
├── 4️⃣ 根因分析 (rca-methods.md)
│   ├── 5 Why 分析法
│   ├── 鱼骨图
│   ├── 故障树
│   └── 统计方法
│
├── 5️⃣ 技术栈 (tech-stack.md)
│   ├── 数据采集层
│   ├── 数据存储层
│   ├── 分析引擎
│   └── 可视化层
│
├── 6️⃣ 集成接口 (integration-guide.md)
│   ├── MES 集成
│   ├── 测试机台集成
│   ├── 缺陷检测集成
│   └── 设备 Sensor 采集
│
├── 7️⃣ 实施路线 (implementation-roadmap.md)
│   ├── 3 个 Phase
│   ├── 关键里程碑
│   └── 风险管理
│
└── 8️⃣ 需求调研 (requirements-checklist.md)
    ├── 工厂信息
    ├── 数据源清单
    ├── 功能需求
    └── 性能要求
```

---

## 1️⃣ 系统架构详解

### 4 层架构设计

```
┌─────────────────────────────────────────────────────────┐
│                    展示层 (Presentation)                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Grafana    │  │   Reports    │  │   Alerts     │  │
│  │  Dashboard   │  │  PDF/Excel   │  │  WebSocket   │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                   应用层 (Application)                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Yield        │  │ SPC Engine   │  │ RCA          │  │
│  │ Analysis     │  │              │  │              │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ FDC Engine   │  │ APC Engine   │  │ Report       │  │
│  │              │  │              │  │ Generator    │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                 处理层 (Data Processing)                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Stream       │  │ Batch        │  │ Data         │  │
│  │ Processing   │  │ Processing   │  │ Quality      │  │
│  │ (Kafka)      │  │ (Airflow)    │  │              │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                   存储层 (Data Storage)                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ PostgreSQL   │  │ InfluxDB     │  │ MinIO/S3     │  │
│  │ (Relational) │  │ (Time-series)│  │ (Objects)    │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### 部署模式对比

| 规模 | 设备数 | 架构 | 配置 |
|------|--------|------|------|
| **小型 Fab** | <100 台 | 单机 Docker Compose | 32C/128G |
| **中型 Fab** | 100-500 台 | 负载均衡 + 集群 | PG 集群 + Influx 集群 |
| **大型 Fab** | >500 台 | Kubernetes 微服务 | 独立扩展各服务 |

### 数据流设计

**实时数据流**（FDC 场景）:
```
Equipment → SECS/GEM → EAP → Kafka → Stream Processing
                                     │
                    ┌────────────────┼────────────────┐
                    ▼                ▼                ▼
               InfluxDB         FDC Engine      Real-time
               (Time-series)    (Anomaly)        Alerts
```

**批量数据流**（良率分析场景）:
```
MES/Test Data → ETL → PostgreSQL → Batch Processing
                                       │
                       ┌───────────────┼───────────────┐
                       ▼               ▼               ▼
                  Yield Analysis   SPC Charts     Daily Reports
```

---

## 2️⃣ 数据模型详解

### 6 大核心实体关系

```
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│   Product   │───┬───│    Route    │───┬───│ ProcessStep │
└─────────────┘   │   └─────────────┘   │   └─────────────┘
                  │                     │
                  ▼                     ▼
┌─────────────┐   │   ┌─────────────┐   │   ┌─────────────┐
│     Lot     │───┘   │   Wafer     │───┘   │  Defect     │
└─────────────┘       └─────────────┘       └─────────────┘
      │                     │
      │                     │
      ▼                     ▼
┌─────────────┐       ┌─────────────┐
│  Equipment  │       │ Measurement │
└─────────────┘       └─────────────┘
```

### 实体定义速查

#### Lot（批次）
- **主键**: lot_id
- **核心字段**: product_id, route_id, status, wafer_count
- **状态**: ACTIVE / HOLD / COMPLETE / SCRAP
- **批次类型**: PROD (生产) / ENG (工程) / TEST (测试)

#### Wafer（晶圆）
- **主键**: wafer_id
- **外键**: lot_id
- **核心字段**: wafer_number, cp_yield, ft_yield, bin1_count
- **关键指标**: 
  - CP Yield = (Bin1 / Total Die) × 100%
  - FT Yield = (Pass / Total) × 100%

#### Defect（缺陷）
- **主键**: defect_id
- **外键**: wafer_id
- **核心字段**: defect_type, x_coord, y_coord, layer, severity
- **缺陷分类**: Particle, Scratch, Stain, Bridge, Void

#### Measurement（量测）
- **主键**: measurement_id
- **外键**: wafer_id
- **核心字段**: param_name, param_value, target, lsl, usl, ucl, lcl
- **关键参数**: CD (关键尺寸), Film Thickness, Sheet Resistance

#### Equipment（设备）
- **主键**: equipment_id
- **核心字段**: equipment_type, vendor, model, status
- **状态**: RUN / IDLE / DOWN / PM
- **关键指标**: MTBA (平均故障间隔时间)

#### ProcessStep（工艺步骤）
- **主键**: step_id
- **外键**: route_id
- **核心字段**: step_sequence, step_name, operation_type
- **工艺类型**: Lithography, Etch, Deposition, Implant, CMP

### 关键索引设计

```sql
-- 提高查询性能
CREATE INDEX idx_lot_product ON lot(product_id);
CREATE INDEX idx_wafer_lot ON wafer(lot_id);
CREATE INDEX idx_defect_wafer ON defect(wafer_id);
CREATE INDEX idx_measurement_param ON measurement(param_name, measurement_time);
```

### 数据分区策略

```sql
-- 大数据量表按月分区
CREATE TABLE defect_partitioned (
    LIKE defect INCLUDING ALL
) PARTITION BY RANGE (inspection_time);

CREATE TABLE defect_2024_01 PARTITION OF defect_partitioned
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
```

---

## 3️⃣ SPC 控制图与告警规则

### 控制图选型表

| 数据类型 | 子组大小 | 控制图 | 适用场景 |
|----------|----------|--------|----------|
| 连续变量 | n=1 | I-MR Chart | 单个测量值 |
| 连续变量 | 2≤n≤9 | X-bar R Chart | 小样本 |
| 连续变量 | n≥10 | X-bar S Chart | 大样本 |
| 不合格品率 | 可变 | P-Chart | 良率监控 |
| 不合格品数 | 固定 | NP-Chart | 缺陷计数 |
| 缺陷数 | 固定 | C-Chart | 缺陷密度 |
| 单位缺陷数 | 可变 | U-Chart | 缺陷率 |

### Western Electric Rules（6 条）

| 规则 | 检测条件 | 严重程度 | 可能原因 |
|------|----------|----------|----------|
| **Rule 1** | 单点超出±3σ | 🔴 高 | 设备故障、材料异常 |
| **Rule 2** | 连续 9 点同侧 | 🟡 中 | 工艺偏移、校准问题 |
| **Rule 3** | 连续 6 点上升/下降 | 🟡 中 | 工具磨损、化学品老化 |
| **Rule 4** | 连续 14 点交替 | 🟢 低 | 过度调整、数据源混合 |
| **Rule 5** | 3 点中 2 点超出±2σ | 🟡 中 | 工艺变异增大 |
| **Rule 6** | 5 点中 4 点超出±1σ | 🟢 低 | 轻微偏移 |

### 控制限计算公式

**X-bar R Chart**:
```
CL = X̿ (总平均值)
UCL = X̿ + A2 × R̄
LCL = X̿ - A2 × R̄

其中 A2 查表（取决于子组大小 n）
```

**I-MR Chart**:
```
Individual Chart:
  CL = X̄
  UCL = X̄ + 2.66 × MR̄
  LCL = X̄ - 2.66 × MR̄

Moving Range Chart:
  CL = MR̄
  UCL = 3.267 × MR̄
  LCL = 0
```

### 过程能力指数

**Cp（过程潜力）**:
```
Cp = (USL - LSL) / (6σ)

评价:
  Cp < 1.0:  能力不足
  Cp = 1.0:  刚好满足
  Cp > 1.33: 良好
  Cp > 1.67: 优秀
```

**Cpk（实际能力，考虑偏移）**:
```
Cpk = min(CPU, CPL)

其中:
  CPU = (USL - μ) / (3σ)
  CPL = (μ - LSL) / (3σ)
```

---

## 4️⃣ 根因分析方法（RCA）

### 5 Why 分析法

**步骤**:
1. 定义问题
2. 问第一个 Why
3. 问第二个 Why
4. 继续追问（通常 5 次）
5. 找到根本原因
6. 制定对策

**经典案例**:
```
问题：CP 良率下降 5%

Why 1: 为什么良率下降？
→ 某层缺陷密度增加

Why 2: 为什么缺陷密度增加？
→ 沉积设备 Particle 超标

Why 3: 为什么 Particle 超标？
→ 腔体清洁不彻底

Why 4: 为什么清洁不彻底？
→ 清洁程序参数设置错误

Why 5: 为什么参数设置错误？
→ 工程师更换后未培训新程序

根本原因：培训流程缺失
对策：建立工程师变更管理流程
```

### 鱼骨图（6M 分类）

```
                    良率下降
                       │
    ┌──────────────────┼──────────────────┐
    │                  │                  │
    ▼                  ▼                  ▼
  Manpower          Machine            Material
    │                  │                  │
    ├─ 培训不足        ├─ 设备老化        ├─ 来料变异
    ├─ 操作失误        ├─ 校准偏移        ├─ 批次差异
    └─ 人员变更        └─ 备件更换        └─ 供应商变更
    
    │                  │                  │
    ▼                  ▼                  ▼
  Method            Measurement         Mother Nature
    │                  │                  │
    ├─ SOP 不完善      ├─ 量测误差        ├─ 温湿度变化
    ├─ 参数设置错误    ├─ 仪器漂移        ├─ 电压波动
    └─ 工艺窗口窄      └─ 采样不足        └─ 洁净度异常
```

### 统计方法

**t 检验**（比较两组）:
```python
from scipy import stats
t_stat, p_value = stats.ttest(normal_lot_params, abnormal_lot_params)
# p < 0.05 → 差异显著
```

**ANOVA**（比较多组）:
```python
f_stat, p_value = stats.f_oneway(eq_A_params, eq_B_params, eq_C_params)
# p < 0.05 → 至少有一组不同
```

**相关性分析**:
```python
correlation = df[['param1', 'param2', 'yield']].corr(method='spearman')
# |r| > 0.7 → 强相关
```

---

## 5️⃣ 技术栈选型

### 完整技术栈

| 层级 | 组件 | 推荐方案 | 说明 |
|------|------|----------|------|
| **数据采集** | 设备接口 | SECS/GEM Gateway | 行业标准 |
| | 消息队列 | Apache Kafka | 高吞吐 |
| **数据存储** | 关系型 DB | PostgreSQL 14+ | 复杂查询 |
| | 时序 DB | InfluxDB 2.x | Sensor 数据 |
| | 对象存储 | MinIO | Wafer Map/图像 |
| **数据处理** | 流处理 | Kafka Streams | 实时 FDC |
| | 批处理 | Apache Airflow | ETL |
| **分析引擎** | 统计分析 | Python (scipy) | SPC 计算 |
| | 机器学习 | scikit-learn | 缺陷分类 |
| **可视化** | Dashboard | Grafana 9.x | 实时监控 |
| | Web 框架 | React + TS | 自定义页面 |
| | 图表库 | Plotly | Wafer Map |

### Python 核心依赖

```requirements.txt
# 数据处理
pandas>=2.0.0
numpy>=1.24.0
scipy>=1.10.0

# 统计分析
statsmodels>=0.14.0
scikit-learn>=1.3.0

# 可视化
plotly>=5.15.0
matplotlib>=3.7.0

# 数据库
sqlalchemy>=2.0.0
psycopg2-binary>=2.9.0
influxdb-client>=1.36.0

# Web 框架
fastapi>=0.100.0
uvicorn>=0.23.0
```

---

## 6️⃣ 集成接口

### MES 集成方式

**方式 1: 数据库视图**（推荐）:
```sql
CREATE VIEW yms_lot_vw AS
SELECT lot_id, product_id, route_id, status, start_time, end_time
FROM lot
WHERE create_time > SYSDATE - 365;

GRANT SELECT ON yms_lot_vw TO yms_user;
```

**方式 2: REST API**:
```python
def get_lot_info(lot_id):
    response = requests.get(
        f"http://mes-api/lot/{lot_id}",
        headers={"Authorization": "Bearer <token>"}
    )
    return response.json()
```

### 测试机台集成

**CP 测试数据格式**:
```csv
Wafer_ID,X_Coord,Y_Coord,Bin_Code,Test_Time,Tester_ID
W001,0,0,1,2024-01-01 10:00:00,T001
W001,1,0,1,2024-01-01 10:00:00,T001
W001,2,0,5,2024-01-01 10:00:00,T001
```

### 缺陷检测集成

**KLA 缺陷数据**:
```json
{
  "wafer_id": "W001",
  "layer": "M1",
  "defects": [
    {
      "defect_id": 1,
      "x": 10.5,
      "y": 20.3,
      "type": "Particle",
      "size": 0.5,
      "severity": 2
    }
  ]
}
```

### 设备 Sensor 采集

**Kafka 消费者**:
```python
from kafka import KafkaConsumer

consumer = KafkaConsumer(
    'equipment-data',
    bootstrap_servers=['localhost:9092']
)

for message in consumer:
    process_sensor_data(message.value)
```

---

## 7️⃣ 实施路线图

### 3 个 Phase

```
Phase 1 (4-6 周)        Phase 2 (6-8 周)        Phase 3 (8-12 周)
基础平台建设            核心功能开发            高级分析与优化
    │                       │                       │
    ▼                       ▼                       ▼
- 数据采集              - SPC 引擎               - 机器学习模型
- 数据存储              - FDC 功能               - 良率预测
- 基础可视化            - 良率分析              - APC 集成
- 用户管理              - 报告系统              - 优化建议
```

### 关键里程碑

| 里程碑 | 时间 | 验收标准 |
|--------|------|----------|
| M1: 数据采集完成 | Week 4 | 所有数据源接入，数据质量>99% |
| M2: 基础可视化完成 | Week 6 | Dashboard 上线，用户培训完成 |
| M3: SPC 功能完成 | Week 9 | Control Chart 正常运行，告警准确 |
| M4: 良率分析完成 | Week 12 | 分析功能满足用户需求 |
| M5: FDC 功能完成 | Week 18 | 实时异常检测准确率>95% |
| M6: 项目验收 | Week 26 | 所有功能验收通过 |

---

## 8️⃣ 需求调研清单

### 工厂基本信息
- 工厂类型：晶圆厂 / 封装厂 / 测试厂
- 工艺节点：_______ nm
- 产品类型：逻辑 / 存储 / 功率器件 / 模拟
- 产能：_______ 片/月
- 设备数量：_______ 台

### 数据源清单
| 系统/设备 | 数据类型 | 接口方式 | 优先级 |
|-----------|----------|----------|--------|
| MES | Lot/Wafer 追踪 | API/DB/File | 高 |
| CP 测试机 | Bin Map | SECS/GEM | 高 |
| FT 测试机 | 测试结果 | SECS/GEM | 高 |
| 缺陷检测 | 缺陷坐标 | SECS/GEM | 高 |
| 量测设备 | CD/膜厚 | SECS/GEM | 中 |
| 工艺设备 | Sensor 数据 | EDA | 中 |

### 功能需求优先级
- Wafer Map: □高 □中 □低
- Pareto 分析：□高 □中 □低
- SPC Control Chart: □高 □中 □低
- 相关性分析：□高 □中 □低
- 良率预测：□高 □中 □低

---

## 📝 学习总结

### 已掌握知识点

✅ **系统架构**: 4 层架构设计、部署模式、数据流  
✅ **数据模型**: 6 大实体、关系、索引设计  
✅ **SPC 控制**: 控制图选型、告警规则、Cp/Cpk 计算  
✅ **根因分析**: 5 Why、鱼骨图、统计方法  
✅ **技术栈**: 完整技术选型、Python 依赖  
✅ **集成接口**: MES/测试机台/缺陷检测集成  
✅ **实施路线**: 3 Phase、里程碑、风险管理  
✅ **需求调研**: 工厂信息、数据源、功能需求

### 待深入学习

🔄 **工艺流程**: 需要结合产品实例学习各工艺步骤  
🔄 **SECS/GEM 协议**: 需要学习协议层细节  
🔄 **机器学习模型**: 缺陷分类、良率预测算法  
🔄 **APC 系统**: 高级工艺控制原理

### 与学习计划的对应

| Phase | 对应内容 | 状态 |
|-------|----------|------|
| Phase 1 | 系统架构、数据模型、术语 | ✅ 已掌握 |
| Phase 2 | 工艺流程实例 | 🔄 待学习（等待资料） |
| Phase 3 | YMS 功能实现 | ✅ 相关性分析已完成 |

---

## 🎯 下一步计划

**等待用户下载资料期间**:
1. ✅ 复习术语表（glossary.md）
2. ✅ 整理系统架构笔记
3. ✅ 理解 SPC 告警规则
4. ✅ 掌握 RCA 方法

**收到资料后**:
1. 开始 Phase 1: 通读 Handbook 第 1 章
2. 学习 CMOS 工艺流程实例
3. 绘制完整工艺流程图

---

**笔记创建时间**: 2026-03-21 11:45  
**最后更新**: 2026-03-21 12:00  
**状态**: 现有资料学习完成，等待外部资料
