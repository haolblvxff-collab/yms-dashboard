# 半导体 YE 专业术语表

**创建日期**: 2026-03-22  
**最后更新**: 2026-03-22  
**当前数量**: 11 个  
**目标数量**: 200+ 个

---

## 📋 术语表结构说明

每个术语包含：
- **术语**: 中文名称（英文缩写/全称）
- **中文解释**: 详细的中文说明
- **英文解释**: Detailed English explanation
- **来源/分类**: 所属领域或学习阶段
- **备注**: 补充说明、公式、示例等

---

## A

### APC - 高级工艺控制

| 项目 | 内容 |
|------|------|
| **全称** | Advanced Process Control |
| **中文解释** | 使用自动化和统计方法对半导体制造工艺进行实时监控和调整，以提高工艺稳定性和产品良率 |
| **英文解释** | Automated and statistical methods for real-time monitoring and adjustment of semiconductor manufacturing processes to improve process stability and product yield |
| **来源/分类** | YMS 架构 / 工艺控制 |
| **备注** | 包括 FDC（故障检测）、SPC（统计过程控制）、R2R（逐件控制）等 |

---

### ANOVA - 方差分析

| 项目 | 内容 |
|------|------|
| **全称** | Analysis of Variance |
| **中文解释** | 一种统计方法，用于分析两个或多个样本均值之间的差异是否具有统计学意义，常用于实验设计（DOE）中 |
| **英文解释** | A statistical method used to analyze whether the differences between two or more sample means are statistically significant, commonly used in Design of Experiments (DOE) |
| **来源/分类** | Phase 3 / 统计分析 |
| **备注** | 用于识别影响良率的关键因素，判断不同工艺条件是否有显著差异 |

---

## C

### CD - 关键尺寸

| 项目 | 内容 |
|------|------|
| **全称** | Critical Dimension |
| **中文解释** | 半导体制造中最小的图形尺寸，通常指晶体管栅极长度或金属线宽，是衡量工艺精度的关键指标 |
| **英文解释** | The smallest feature size in semiconductor manufacturing, typically referring to transistor gate length or metal line width, a key metric for process precision |
| **来源/分类** | CMOS 工艺 / 光刻 |
| **备注** | 控制要求：±3σ < 5%，先进节点已达 5nm 以下 |

---

### CMP - 化学机械抛光

| 项目 | 内容 |
|------|------|
| **全称** | Chemical Mechanical Polishing / Planarization |
| **中文解释** | 结合化学腐蚀和机械研磨的全局平坦化工艺，用于去除多余材料并使晶圆表面达到原子级平整 |
| **英文解释** | A global planarization process combining chemical etching and mechanical abrasion to remove excess material and achieve atomic-level surface flatness |
| **来源/分类** | CMOS 工艺 / 平坦化 |
| **备注** | 关键参数：去除速率、均匀性（WIWNU < 2%）、缺陷密度 |

---

### Cp - 过程能力指数

| 项目 | 内容 |
|------|------|
| **全称** | Process Capability Index |
| **中文解释** | 衡量过程潜在能力的指标，表示规格范围与过程变异的比值，不考虑过程中心偏移 |
| **英文解释** | A metric measuring process potential capability, representing the ratio of specification range to process variation, without considering process center shift |
| **来源/分类** | SPC / 过程能力 |
| **备注** | 公式：Cp = (USL - LSL) / (6σ)；评价：<1.0 不足，>1.33 良好，>1.67 优秀 |

---

### Cpk - 过程能力指数（考虑偏移）

| 项目 | 内容 |
|------|------|
| **全称** | Process Capability Index (considering shift) |
| **中文解释** | 考虑过程中心偏移的实际过程能力指标，反映过程在规格范围内的实际表现 |
| **英文解释** | Actual process capability index considering process center shift, reflecting the actual performance within specification limits |
| **来源/分类** | SPC / 过程能力 |
| **备注** | 公式：Cpk = min(CPU, CPL) = min[(USL-μ)/3σ, (μ-LSL)/3σ]；通常 Cpk < Cp |

---

### CP - 晶圆探针测试

| 项目 | 内容 |
|------|------|
| **全称** | Circuit Probing / Chip Probing |
| **中文解释** | 在晶圆切割前，使用探针卡对每个芯片进行电性测试，识别不良芯片并标记（ink mark） |
| **英文解释** | Electrical testing of each die on a wafer before dicing, using a probe card to identify and mark defective chips (ink mark) |
| **来源/分类** | YMS 架构 / 测试 |
| **备注** | 测试项目：开路/短路、功能测试、参数测试；输出 CP 良率图 |

---

## D

### DOE - 实验设计

| 项目 | 内容 |
|------|------|
| **全称** | Design of Experiments |
| **中文解释** | 一种系统化的实验方法，通过合理安排实验组合来识别影响结果的关键因素及其交互作用 |
| **英文解释** | A systematic experimental method to identify key factors affecting results and their interactions through合理安排 experimental combinations |
| **来源/分类** | Phase 3 / 统计分析 |
| **备注** | 常用方法：全因子设计、部分因子设计、响应曲面法（RSM）、田口方法 |

---

## E

### EAP - 设备自动化程序

| 项目 | 内容 |
|------|------|
| **全称** | Equipment Automation Program |
| **中文解释** | 实现半导体生产设备自动化控制的软件系统，负责设备与 MES 系统之间的数据通信和指令执行 |
| **英文解释** | Software system for automated control of semiconductor production equipment, responsible for data communication and command execution between equipment and MES |
| **来源/分类** | YMS 架构 / 系统集成 |
| **备注** | 支持 SECS/GEM 协议，实现自动上料、参数下载、数据采集等功能 |

---

### EDA - 电子设计自动化

| 项目 | 内容 |
|------|------|
| **全称** | Electronic Design Automation |
| **中文解释** | 用于设计集成电路和印刷电路板的软件工具集合，包括电路设计、仿真、验证、布局布线等 |
| **英文解释** | A collection of software tools for designing integrated circuits and printed circuit boards, including circuit design, simulation, verification, place and route |
| **来源/分类** | 设计 / 工具 |
| **备注** | 主要厂商：Synopsys、Cadence、Mentor Graphics（Siemens） |

---

## F

### FDC - 故障检测与分类

| 项目 | 内容 |
|------|------|
| **全称** | Fault Detection and Classification |
| **中文解释** | 通过实时监控工艺参数和设备状态，自动检测异常情况并对故障进行分类的系统 |
| **英文解释** | A system that automatically detects abnormalities and classifies faults by real-time monitoring of process parameters and equipment status |
| **来源/分类** | YMS 架构 / 质量控制 |
| **备注** | 检测方法：SPC 控制图、多变量分析、机器学习；响应：告警、停机、通知 |

---

### FPY - 一次通过率

| 项目 | 内容 |
|------|------|
| **全称** | First Pass Yield |
| **中文解释** | 产品首次通过整个制造流程而无需返工或修复的良率，反映工艺的整体稳定性和质量水平 |
| **英文解释** | Yield of products passing through the entire manufacturing process on the first attempt without rework or repair, reflecting overall process stability and quality level |
| **来源/分类** | YMS 架构 / 良率指标 |
| **备注** | FPY = (投入晶圆数 - 不良品数) / 投入晶圆数 × 100% |

---

### FT - 最终测试

| 项目 | 内容 |
|------|------|
| **全称** | Final Test |
| **中文解释** | 在芯片封装完成后进行的全面电性测试，验证芯片功能和性能是否符合规格要求 |
| **英文解释** | Comprehensive electrical testing performed after chip packaging to verify whether chip function and performance meet specification requirements |
| **来源/分类** | YMS 架构 / 测试 |
| **备注** | 测试项目：功能测试、速度测试、功耗测试、可靠性测试；输出 FT 良率 |

---

### FTA - 故障树分析

| 项目 | 内容 |
|------|------|
| **全称** | Fault Tree Analysis |
| **中文解释** | 一种自上而下的演绎分析方法，从故障事件出发，逐层分析导致故障的可能原因及其逻辑关系 |
| **英文解释** | A top-down deductive analysis method that starts from a fault event and analyzes possible causes and their logical relationships layer by layer |
| **来源/分类** | Phase 3 / 根因分析 |
| **备注** | 使用逻辑门（AND/OR）构建故障树，计算故障发生概率，识别关键路径 |

---

## K

### KPP - 关键工艺参数

| 项目 | 内容 |
|------|------|
| **全称** | Key Process Parameter |
| **中文解释** | 对产品质量和良率有重大影响的工艺参数，需要重点监控和控制 |
| **英文解释** | Process parameters that have significant impact on product quality and yield, requiring focused monitoring and control |
| **来源/分类** | CMOS 工艺 / 工艺控制 |
| **备注** | 示例：光刻的 CD 均匀性、刻蚀的选择比、CVD 的厚度均匀性 |

---

## L

### Lot - 批次

| 项目 | 内容 |
|------|------|
| **全称** | Lot |
| **中文解释** | 半导体生产的基本管理单位，通常包含 25 片晶圆，同一批次的晶圆在同一工艺条件下加工 |
| **英文解释** | Basic management unit in semiconductor manufacturing, typically containing 25 wafers processed under the same process conditions |
| **来源/分类** | YMS 架构 / 生产管理 |
| **备注** | 批次追踪：Lot ID、产品型号、工艺路线、开始/结束时间、设备历史 |

---

## M

### MES - 制造执行系统

| 项目 | 内容 |
|------|------|
| **全称** | Manufacturing Execution System |
| **中文解释** | 用于管理和跟踪半导体制造过程的信息系统，包括生产调度、物料追踪、工艺管理、数据采集等功能 |
| **英文解释** | Information system for managing and tracking semiconductor manufacturing processes, including production scheduling, material tracking, process management, data collection |
| **来源/分类** | YMS 架构 / 系统集成 |
| **备注** | 与 YMS 集成：提供 Lot/Wafer 信息、工艺路线、设备状态等数据 |

---

### MTBA - 平均中止间隔时间

| 项目 | 内容 |
|------|------|
| **全称** | Mean Time Between Abort |
| **中文解释** | 设备两次异常中止之间的平均运行时间，用于衡量设备稳定性和可靠性 |
| **英文解释** | Average operating time between two equipment aborts, used to measure equipment stability and reliability |
| **来源/分类** | YMS 架构 / 设备管理 |
| **备注** | MTBA 越长，设备越稳定；目标：>150 小时 |

---

## P

### PVD - 物理气相沉积

| 项目 | 内容 |
|------|------|
| **全称** | Physical Vapor Deposition |
| **中文解释** | 通过物理方法（如溅射、蒸发）将材料从源转移到晶圆表面形成薄膜的工艺 |
| **英文解释** | A process of transferring material from a source to the wafer surface through physical methods (such as sputtering, evaporation) to form a thin film |
| **来源/分类** | CMOS 工艺 / 薄膜沉积 |
| **备注** | 应用：金属层（Al、Cu、Ti、Ta）、阻挡层；特点：台阶覆盖率较差 |

---

## R

### RCA - 根因分析

| 项目 | 内容 |
|------|------|
| **全称** | Root Cause Analysis |
| **中文解释** | 一种系统化的问题解决方法，通过深入分析找到问题的根本原因，而非仅仅处理表面症状 |
| **英文解释** | A systematic problem-solving method that finds the root cause of a problem through in-depth analysis, rather than just addressing surface symptoms |
| **来源/分类** | YMS 架构 / 质量改进 |
| **备注** | 常用工具：5 Why、鱼骨图、FTA、关联图；目标：防止问题复发 |

---

### RIE - 反应离子刻蚀

| 项目 | 内容 |
|------|------|
| **全称** | Reactive Ion Etching |
| **中文解释** | 一种干法刻蚀技术，利用等离子体中的活性离子与材料发生化学反应并物理轰击，实现各向异性刻蚀 |
| **英文解释** | A dry etching technique that uses reactive ions in plasma to chemically react with materials and physically bombard, achieving anisotropic etching |
| **来源/分类** | CMOS 工艺 / 刻蚀 |
| **备注** | 特点：各向异性好、选择比高；应用：接触孔、通孔、栅极刻蚀 |

---

## S

### SPC - 统计过程控制

| 项目 | 内容 |
|------|------|
| **全称** | Statistical Process Control |
| **中文解释** | 使用统计方法（如控制图）监控和控制制造过程，及时发现异常并采取措施，确保过程稳定 |
| **英文解释** | Using statistical methods (such as control charts) to monitor and control manufacturing processes, detect abnormalities timely and take measures to ensure process stability |
| **来源/分类** | YMS 架构 / 质量控制 |
| **备注** | 控制图类型：X-bar R、I-MR、P-Chart、C-Chart；告警规则：Western Electric Rules |

---

### SEM - 扫描电子显微镜

| 项目 | 内容 |
|------|------|
| **全称** | Scanning Electron Microscope |
| **中文解释** | 使用聚焦电子束扫描样品表面，通过检测二次电子或背散射电子成像的高分辨率显微镜 |
| **英文解释** | A high-resolution microscope that scans the sample surface with a focused electron beam and images by detecting secondary electrons or backscattered electrons |
| **来源/分类** | 检测设备 / 失效分析 |
| **备注** | 分辨率：可达 1nm 以下；应用：缺陷观察、CD 测量、截面分析 |

---

### SECS/GEM - 半导体设备通信协议

| 项目 | 内容 |
|------|------|
| **全称** | SECS/GEM (SEMI Equipment Communications Standard / Generic Equipment Model) |
| **中文解释** | 半导体行业标准的设备通信协议，定义设备与主机系统之间的数据格式和通信规则 |
| **英文解释** | Semiconductor industry standard equipment communication protocol that defines data formats and communication rules between equipment and host systems |
| **来源/分类** | Phase 4 / 系统集成 |
| **备注** | SECS-I：物理层；SECS-II：消息层；GEM：设备行为模型 |

---

## W

### Wafer - 晶圆

| 项目 | 内容 |
|------|------|
| **全称** | Wafer |
| **中文解释** | 由高纯度单晶硅制成的圆形薄片，是半导体制造的基底材料，在其上制造集成电路 |
| **英文解释** | A circular thin slice made of high-purity single crystal silicon, serving as the substrate material for semiconductor manufacturing, on which integrated circuits are fabricated |
| **来源/分类** | YMS 架构 / 基础材料 |
| **备注** | 常见尺寸：150mm(6")、200mm(8")、300mm(12")；厚度：约 725μm (300mm) |

---

## Y

### YE - 良率工程

| 项目 | 内容 |
|------|------|
| **全称** | Yield Engineering |
| **中文解释** | 通过分析、监控和改进制造工艺来提高产品良率的工程学科，涉及数据分析、工艺优化、缺陷控制等 |
| **英文解释** | An engineering discipline focused on improving product yield through analysis, monitoring, and improvement of manufacturing processes, involving data analysis, process optimization, defect control |
| **来源/分类** | 目标 / 专业领域 |
| **备注** | 核心技能：良率分析、异常处理、根因分析、工艺整合 |

---

### YMS - 良率管理系统

| 项目 | 内容 |
|------|------|
| **全称** | Yield Management System |
| **中文解释** | 用于收集、分析和可视化半导体制造过程中的良率相关数据的综合系统，支持良率改进决策 |
| **英文解释** | A comprehensive system for collecting, analyzing, and visualizing yield-related data in semiconductor manufacturing processes, supporting yield improvement decisions |
| **来源/分类** | YMS 架构 / 系统 |
| **备注** | 核心功能：相关性分析、Wafer Map、SPC、Pareto 分析、趋势分析、根因分析 |

---

## 📊 进度统计

| 分类 | 数量 | 目标 |
|------|------|------|
| 总术语 | 40 | 200+ |
| 本月新增 | 40 | 50 |
| 本周目标 | 40 → 50 | +10 |
| 今日新增 | 29 | - |

**更新记录**:
- 10:30: 新增 10 个（氧化、光刻、刻蚀、离子注入、CVD、ALD、光刻胶、掩膜版、缺陷、良率）
- 13:30: 新增 9 个（Wafer Map、Bin Map、Pareto Chart、Control Chart、Correlation、Excursion、Hold、Scrap、Rework）
- 16:15: 新增 10 个（FEOL、BEOL、洁净室、颗粒污染、套刻精度、CD 均匀性、台阶覆盖率、选择比、激活率、表面粗糙度）

---

## O

### 氧化 - 氧化工艺

| 项目 | 内容 |
|------|------|
| **全称** | Oxidation |
| **中文解释** | 在硅片表面生长二氧化硅（SiO₂）薄膜的工艺，用于形成栅极氧化层、场氧化层或掩膜层，可分为干氧氧化和湿氧氧化 |
| **英文解释** | A process of growing silicon dioxide (SiO₂) film on wafer surface, used to form gate oxide, field oxide, or mask layer, can be dry oxidation or wet oxidation |
| **来源/分类** | CMOS 工艺 / Phase 1 |
| **备注** | 反应式：Si + O₂ → SiO₂（干氧）、Si + 2H₂O → SiO₂ + 2H₂（湿氧）；温度：800-1200°C；厚度：10nm-1μm |

---

### 光刻 - 光刻工艺

| 项目 | 内容 |
|------|------|
| **全称** | Lithography / Photolithography |
| **中文解释** | 使用光学方法将掩膜版上的图形转移到涂有光刻胶的晶圆表面的工艺，是半导体制造中最关键的图形化技术 |
| **英文解释** | Using optical methods to transfer patterns from mask to photoresist-coated wafer surface, the most critical patterning technology in semiconductor manufacturing |
| **来源/分类** | CMOS 工艺 / Phase 1 |
| **备注** | 9 步骤：涂胶→前烘→对准→曝光→后烘→显影→坚膜→检查；关键参数：CD 均匀性、套刻精度 |

---

## E

### 刻蚀 - 刻蚀工艺

| 项目 | 内容 |
|------|------|
| **全称** | Etching |
| **中文解释** | 去除未被光刻胶保护的材料，将光刻图形永久转移到晶圆表面的工艺，分为湿法刻蚀（各向同性）和干法刻蚀（各向异性） |
| **英文解释** | Removing unprotected materials to permanently transfer photoresist patterns to wafer surface, divided into wet etching (isotropic) and dry etching (anisotropic) |
| **来源/分类** | CMOS 工艺 / Phase 1 |
| **备注** | 干法刻蚀：RIE、ICP；关键参数：刻蚀速率、选择比（>10:1）、均匀性（±3%）、侧壁角度 |

---

## I

### 离子注入 - 离子注入工艺

| 项目 | 内容 |
|------|------|
| **全称** | Ion Implantation |
| **中文解释** | 将掺杂离子加速并注入硅片中，改变半导体电学特性的工艺，用于形成源漏区、阱区等 |
| **英文解释** | Accelerating and implanting dopant ions into silicon wafer to change electrical properties, used to form source/drain regions, wells, etc. |
| **来源/分类** | CMOS 工艺 / Phase 1 |
| **备注** | 关键参数：注入能量（1-200 keV）、剂量（1e11-1e16 ions/cm²）、退火激活（800-1100°C） |

---

## C

### 化学气相沉积 - CVD

| 项目 | 内容 |
|------|------|
| **全称** | Chemical Vapor Deposition |
| **中文解释** | 通过气态前驱体在晶圆表面发生化学反应，沉积固态薄膜的工艺，用于沉积介质层（SiO₂、Si₃N₄）等 |
| **英文解释** | Depositing solid thin films through chemical reactions of gaseous precursors on wafer surface, used to deposit dielectric layers (SiO₂, Si₃N₄), etc. |
| **来源/分类** | CMOS 工艺 / Phase 1 |
| **备注** | 类型：APCVD（常压）、LPCVD（低压）、PECVD（等离子体增强）；关键参数：厚度均匀性（±1.5%）、台阶覆盖率 |

---

### 原子层沉积 - ALD

| 项目 | 内容 |
|------|------|
| **全称** | Atomic Layer Deposition |
| **中文解释** | 通过交替通入不同前驱体，以原子层为单位逐层沉积薄膜的工艺，具有极好的均匀性和台阶覆盖率 |
| **英文解释** | Depositing thin films layer by layer at atomic level by alternately introducing different precursors, with excellent uniformity and step coverage |
| **来源/分类** | CMOS 工艺 / Phase 1 |
| **备注** | 应用：High-k 介质、阻挡层；特点：单原子层控制、保形性好；缺点：沉积速率慢 |

---

## P

### 光刻胶 - 光刻胶材料

| 项目 | 内容 |
|------|------|
| **全称** | Photoresist |
| **中文解释** | 一种对光敏感的高分子材料，涂覆在晶圆表面，经曝光和显影后形成图形，分为正胶（曝光部分溶解）和负胶（曝光部分不溶解） |
| **英文解释** | A light-sensitive polymer material coated on wafer surface, forming patterns after exposure and development, divided into positive resist (exposed part dissolves) and negative resist (exposed part remains) |
| **来源/分类** | CMOS 工艺 / 材料 |
| **备注** | 厚度：0.5-2μm；关键参数：感光度、对比度、粘附性、抗刻蚀性 |

---

## M

### 掩膜版 - 掩膜版/光罩

| 项目 | 内容 |
|------|------|
| **全称** | Mask / Reticle |
| **中文解释** | 包含电路图形的光学模板，用于光刻过程中将图形投影到晶圆上，通常由石英玻璃和铬膜制成 |
| **英文解释** | An optical template containing circuit patterns, used to project patterns onto wafer during lithography, typically made of quartz glass and chromium film |
| **来源/分类** | CMOS 工艺 / 光刻 |
| **备注** | 尺寸：6 英寸方形；图形缩小倍率：4:1（步进式）；关键参数：CD 精度、缺陷密度 |

---

## D

### 缺陷 - 缺陷

| 项目 | 内容 |
|------|------|
| **全称** | Defect |
| **中文解释** | 晶圆表面或内部的异常情况，包括颗粒、划痕、残留、针孔等，会影响芯片性能和良率 |
| **英文解释** | Abnormalities on wafer surface or inside, including particles, scratches, residues, pinholes, etc., which can affect chip performance and yield |
| **来源/分类** | 质量 / Phase 1 |
| **备注** | 检测方法：光学检测、电子束检测；分类：致命缺陷、可修复缺陷；目标：缺陷密度 < 0.1 个/cm² |

---

## Y

### 良率 - 良率

| 项目 | 内容 |
|------|------|
| **全称** | Yield |
| **中文解释** | 合格芯片数量与总芯片数量的比率，是衡量半导体制造过程质量和效率的核心指标 |
| **英文解释** | The ratio of good chips to total chips, a core metric for measuring quality and efficiency of semiconductor manufacturing process |
| **来源/分类** | YMS 架构 / 质量指标 |
| **备注** | 类型：CP 良率（晶圆测试）、FT 良率（最终测试）、FPY（一次通过率）；目标：>90%（成熟工艺） |

---

## 📝 待添加术语（按优先级）

### 🔴 高优先级（Phase 1 - 本周）✅ 已完成

~~| 术语 | 英文 | 分类 |~~
~~|------|------|------|~~
~~| 氧化 | Oxidation | 工艺 |~~
~~| 光刻 | Lithography / Photolithography | 工艺 |~~
~~| 刻蚀 | Etching | 工艺 |~~
~~| 离子注入 | Ion Implantation | 工艺 |~~
~~| 化学气相沉积 | Chemical Vapor Deposition (CVD) | 工艺 |~~
~~| 原子层沉积 | Atomic Layer Deposition (ALD) | 工艺 |~~
~~| 光刻胶 | Photoresist | 材料 |~~
~~| 掩膜版 | Mask / Reticle | 光刻 |~~
~~| 缺陷 | Defect | 质量 |~~
~~| 良率 | Yield | 指标 |~~

**状态**: ✅ 10 个术语已添加（2026-03-22 10:30）

### 🟡 中优先级（Phase 2 - 下周）

## W

### 晶圆图 - 缺陷分布图

| 项目 | 内容 |
|------|------|
| **全称** | Wafer Map |
| **中文解释** | 以图形方式展示晶圆表面缺陷位置分布的图表，用于识别缺陷模式和工艺问题，是 YE 工程师的核心分析工具 |
| **英文解释** | A graphical representation showing the spatial distribution of defects on wafer surface, used to identify defect patterns and process issues, a core analysis tool for YE engineers |
| **来源/分类** | YMS 架构 / Phase 2 |
| **备注** | 常见模式：环形、随机、簇状、边缘集中；颜色编码：按缺陷类型或严重度区分 |

---

## B

### 良率分布图 - Bin Map

| 项目 | 内容 |
|------|------|
| **全称** | Bin Map |
| **中文解释** | 显示晶圆上每个芯片测试结果的分布图，不同 Bin 代表不同的失效模式，用于分析良率损失的空间分布 |
| **英文解释** | A distribution map showing test results of each die on wafer, different bins represent different failure modes, used to analyze spatial distribution of yield loss |
| **来源/分类** | YMS 架构 / Phase 2 |
| **备注** | Bin 分类：Bin 1（良品）、Bin 2-10（各类失效）；与 Wafer Map 叠加分析可定位根因 |

---

## P

### 帕累托图 - 排列图

| 项目 | 内容 |
|------|------|
| **全称** | Pareto Chart |
| **中文解释** | 按发生频率排序的柱状图，结合累积百分比曲线，基于 80/20 法则识别主要缺陷类型或失效模式 |
| **英文解释** | A bar chart sorted by occurrence frequency with cumulative percentage curve, based on 80/20 rule to identify major defect types or failure modes |
| **来源/分类** | YMS 架构 / Phase 2 |
| **备注** | 应用：缺陷 Pareto、失效模式 Pareto、设备 Pareto；优先解决前 20% 的主要问题 |

---

## C

### 控制图 - 管制图

| 项目 | 内容 |
|------|------|
| **全称** | Control Chart |
| **中文解释** | 用于监控过程稳定性的统计图表，包含中心线（CL）、上控制限（UCL）和下控制限（LCL），用于检测异常波动 |
| **英文解释** | A statistical chart for monitoring process stability, containing center line (CL), upper control limit (UCL), and lower control limit (LCL), used to detect abnormal variations |
| **来源/分类** | SPC / Phase 2 |
| **备注** | 类型：X-bar R（小样本）、I-MR（单值）、P-Chart（不合格率）、C-Chart（缺陷数）；告警规则：Western Electric Rules |

---

### 相关性 - 相关分析

| 项目 | 内容 |
|------|------|
| **全称** | Correlation |
| **中文解释** | 衡量两个变量之间关系强度和方向的统计指标，范围 -1 到 +1，用于识别工艺参数与良率的关联关系 |
| **英文解释** | A statistical metric measuring the strength and direction of relationship between two variables, ranging from -1 to +1, used to identify correlations between process parameters and yield |
| **来源/分类** | 统计 / Phase 3 |
| **备注** | Pearson（线性关系）、Spearman（单调关系）；|r|≥0.3 且 p<0.05 认为显著相关 |

---

## E

### 异常 - 工艺异常

| 项目 | 内容 |
|------|------|
| **全称** | Excursion |
| **中文解释** | 工艺参数或良率超出正常范围的异常情况，通常由设备故障、材料问题或操作失误引起，需要立即调查和处理 |
| **英文解释** | An abnormal situation where process parameters or yield exceed normal ranges, usually caused by equipment failure, material issues, or operator errors, requiring immediate investigation and handling |
| **来源/分类** | 质量 / Phase 2 |
| **备注** | 响应流程：Hold Lot → 根因分析 → 纠正措施 → 预防措施 → Release Lot |

---

## H

### 扣留 - 批次扣留

| 项目 | 内容 |
|------|------|
| **全称** | Hold |
| **中文解释** | 因质量异常或工艺问题暂停批次流转的管理措施，等待调查和决策，防止不良品流入下道工序 |
| **英文解释** | A management measure to suspend lot flow due to quality abnormalities or process issues, awaiting investigation and decision, preventing defective products from flowing to next process |
| **来源/分类** | 质量管理 / Phase 2 |
| **备注** | Hold 类型：质量 Hold、工程 Hold、设备 Hold；释放条件：问题解决 + 风险评估通过 |

---

### 报废 - 批次报废

| 项目 | 内容 |
|------|------|
| **全称** | Scrap |
| **中文解释** | 因严重质量问题无法修复而判定为废品的批次，是良率损失的主要来源之一，需要严格控制和根因分析 |
| **英文解释** | Batches judged as waste due to serious quality issues that cannot be repaired, one of the main sources of yield loss, requiring strict control and root cause analysis |
| **来源/分类** | 质量管理 / Phase 2 |
| **备注** | Scrap 率 = 报废批次 / 总投入批次 × 100%；目标：<1%（成熟工艺） |

---

### 返工 - 批次返工

| 项目 | 内容 |
|------|------|
| **全称** | Rework |
| **中文解释** | 对不合格的批次进行重新加工或修复的工艺，如去除光刻胶重新曝光、去除薄膜重新沉积等 |
| **英文解释** | A process of reprocessing or repairing non-conforming batches, such as removing photoresist for re-exposure, removing thin film for re-deposition, etc. |
| **来源/分类** | 质量管理 / Phase 2 |
| **备注** | 限制：每批次最多返工 2 次；风险：增加生产周期、可能引入新缺陷 |

---

## 📝 待添加术语（按优先级）

### 🔴 高优先级（Phase 1 - 本周）✅ 已完成

~~| 术语 | 英文 | 分类 |~~
~~|------|------|------|~~
~~| 氧化 | Oxidation | 工艺 |~~
~~| 光刻 | Lithography / Photolithography | 工艺 |~~
~~| 刻蚀 | Etching | 工艺 |~~
~~| 离子注入 | Ion Implantation | 工艺 |~~
~~| 化学气相沉积 | Chemical Vapor Deposition (CVD) | 工艺 |~~
~~| 原子层沉积 | Atomic Layer Deposition (ALD) | 工艺 |~~
~~| 光刻胶 | Photoresist | 材料 |~~
~~| 掩膜版 | Mask / Reticle | 光刻 |~~
~~| 缺陷 | Defect | 质量 |~~
~~| 良率 | Yield | 指标 |~~

**状态**: ✅ 10 个术语已添加（2026-03-22 10:30）

### 🟡 中优先级（Phase 2 - 本周）✅ 已完成

~~| 术语 | 英文 | 分类 |~~
~~|------|------|------|~~
~~| 晶圆图 | Wafer Map | 分析 |~~
~~| 良率分布图 | Bin Map | 分析 |~~
~~| 帕累托图 | Pareto Chart | 分析 |~~
~~| 控制图 | Control Chart | SPC |~~
~~| 相关性 | Correlation | 统计 |~~
~~| 异常 | Excursion | 质量 |~~
~~| 扣留 | Hold | 管理 |~~
~~| 报废 | Scrap | 管理 |~~
~~| 返工 | Rework | 管理 |~~

**状态**: ✅ 9 个术语已添加（2026-03-22 13:30）

## F

### 前道工序 - FEOL

| 项目 | 内容 |
|------|------|
| **全称** | Front End of Line |
| **中文解释** | 半导体制造的前段工艺，包括从硅片准备到金属互连之前的所有工艺步骤，主要形成晶体管等有源器件 |
| **英文解释** | The front segment of semiconductor manufacturing, including all process steps from wafer preparation to before metal interconnection, mainly forming active devices such as transistors |
| **来源/分类** | CMOS 工艺 / Phase 3 |
| **备注** | 主要工艺：氧化、光刻、刻蚀、离子注入、薄膜沉积；结束标志：晶体管完成 |

---

## B

### 后道工序 - BEOL

| 项目 | 内容 |
|------|------|
| **全称** | Back End of Line |
| **中文解释** | 半导体制造的后段工艺，包括金属互连、钝化层沉积、焊盘形成等，将晶体管连接成完整电路 |
| **英文解释** | The back segment of semiconductor manufacturing, including metal interconnection, passivation layer deposition, pad formation, etc., connecting transistors into complete circuits |
| **来源/分类** | CMOS 工艺 / Phase 3 |
| **备注** | 主要工艺：金属沉积、CMP、通孔形成、多层互连；结束标志：晶圆测试前 |

---

## C

### 洁净室 - 无尘室

| 项目 | 内容 |
|------|------|
| **全称** | Clean Room |
| **中文解释** | 控制空气中颗粒污染物浓度的特殊环境，用于半导体制造，防止颗粒污染影响芯片良率 |
| **英文解释** | A special environment that controls the concentration of airborne particulate contaminants, used in semiconductor manufacturing to prevent particle contamination from affecting chip yield |
| **来源/分类** | 设施 / Phase 3 |
| **备注** | 等级：Class 1/10/100/1000（每立方英尺颗粒数）；先进厂：Class 1 或更高 |

---

### 颗粒污染 - 颗粒污染

| 项目 | 内容 |
|------|------|
| **全称** | Particle Contamination |
| **中文解释** | 晶圆表面的微小颗粒污染物，可能来自空气、设备、人员或化学品，会导致电路短路、断路或缺陷 |
| **英文解释** | Tiny particulate contaminants on wafer surface, which may come from air, equipment, personnel, or chemicals, and can cause circuit shorts, opens, or defects |
| **来源/分类** | 质量 / Phase 3 |
| **备注** | 控制标准：<0.1μm 颗粒密度 < 1 个/cm²；检测方法：光学表面扫描 |

---

## O

### 套刻精度 - 套刻误差

| 项目 | 内容 |
|------|------|
| **全称** | Overlay Accuracy / Overlay Error |
| **中文解释** | 光刻工艺中，不同层之间图形对准的精度，是衡量多层互连质量的关键指标 |
| **英文解释** | The accuracy of pattern alignment between different layers in lithography process, a key metric for measuring multi-layer interconnection quality |
| **来源/分类** | 光刻 / Phase 3 |
| **备注** | 先进节点要求：<5nm；测量方法：套刻标记（Overlay Mark） |

---

### 临界尺寸均匀性 - CD 均匀性

| 项目 | 内容 |
|------|------|
| **全称** | Critical Dimension Uniformity |
| **中文解释** | 晶圆上或晶圆间关键尺寸（如栅极长度、线宽）的一致性，影响器件性能和良率 |
| **英文解释** | The consistency of critical dimensions (such as gate length, line width) across a wafer or between wafers, affecting device performance and yield |
| **来源/分类** | 光刻 / Phase 3 |
| **备注** | 控制要求：±3σ < 5%；测量工具：CD-SEM |

---

## S

### 台阶覆盖率 - 阶梯覆盖率

| 项目 | 内容 |
|------|------|
| **全称** | Step Coverage |
| **中文解释** | 薄膜沉积工艺中，薄膜在台阶或沟槽表面的覆盖能力，影响互连可靠性和器件性能 |
| **英文解释** | The coverage ability of thin film on step or trench surfaces in thin film deposition process, affecting interconnection reliability and device performance |
| **来源/分类** | 薄膜沉积 / Phase 3 |
| **备注** | ALD 台阶覆盖率最好（>95%）；PVD 较差（<50%）；CVD 中等（70-90%） |

---

### 选择比 - 刻蚀选择比

| 项目 | 内容 |
|------|------|
| **全称** | Selectivity / Etch Selectivity |
| **中文解释** | 刻蚀工艺中，目标材料与掩膜材料或下层材料的刻蚀速率比值，高选择比可保护不需要刻蚀的区域 |
| **英文解释** | The ratio of etch rates between target material and mask material or underlying layer in etching process, high selectivity can protect areas that do not need to be etched |
| **来源/分类** | 刻蚀 / Phase 3 |
| **备注** | 要求：>10:1（理想>50:1）；高选择比是干法刻蚀的关键优势 |

---

## A

### 激活率 - 掺杂激活率

| 项目 | 内容 |
|------|------|
| **全称** | Activation Rate / Dopant Activation Rate |
| **中文解释** | 离子注入后，经过退火工艺，掺杂原子进入晶格位置并贡献载流子的比例 |
| **英文解释** | After ion implantation, the proportion of dopant atoms that enter lattice positions and contribute carriers through annealing process |
| **来源/分类** | 离子注入 / Phase 3 |
| **备注** | 目标：>90%；退火温度：800-1100°C；快速退火（RTA）可提高激活率 |

---

## S

### 表面粗糙度 - 晶圆表面粗糙度

| 项目 | 内容 |
|------|------|
| **全称** | Surface Roughness |
| **中文解释** | 晶圆表面的微观不平整度，影响薄膜沉积质量、光刻胶附着力和器件性能 |
| **英文解释** | The microscopic unevenness of wafer surface, affecting thin film deposition quality, photoresist adhesion, and device performance |
| **来源/分类** | 硅片制备 / Phase 3 |
| **备注** | 抛光后要求：Ra < 0.5nm；测量方法：AFM（原子力显微镜） |

---

## 📝 待添加术语（按优先级）

### 🔴 高优先级（Phase 1 - 本周）✅ 已完成

**状态**: ✅ 10 个术语已添加（2026-03-22 10:30）

### 🟡 中优先级（Phase 2 - 本周）✅ 已完成

**状态**: ✅ 9 个术语已添加（2026-03-22 13:30）

### 🟢 低优先级（Phase 3 - 本周补充）✅ 已完成

**状态**: ✅ 10 个术语已添加（2026-03-22 16:15）

**当前总计**: 40 个术语（本周目标 50 个，还需 +10 个）

### 🟢 低优先级（Phase 3 - 后续）

| 术语 | 英文 | 分类 |
|------|------|------|
| 相关性 | Correlation | 统计 |
| 回归 | Regression | 统计 |
| 聚类 | Clustering | 机器学习 |
| 分类 | Classification | 机器学习 |
| 神经网络 | Neural Network | 机器学习 |

---

## 📚 术语来源

- **YMS 架构**: YMS 系统设计和实现相关
- **CMOS 工艺**: 半导体制造工艺相关
- **SPC**: 统计过程控制相关
- **Phase X**: 学习计划第 X 阶段
- **质量**: 质量控制和良率管理
- **统计**: 统计分析方法
- **系统集成**: MES/EAP/SECS-GEM等

---

**最后更新**: 2026-03-22  
**下次更新**: 每日添加新术语（目标：本周 50 个）  
**维护人**: lamber
