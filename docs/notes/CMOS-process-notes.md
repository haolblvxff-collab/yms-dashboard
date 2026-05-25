# CMOS 工艺流程学习笔记

**学习日期**: 2026-03-22  
**学习阶段**: Phase 1 - 建立整体框架  
**参考资料**: YMS 架构文档、semiconductor-yms skill

---

## 📋 学习目标

1. ✅ 建立 CMOS 工艺的整体框架
2. ⏳ 理解各工艺步骤的作用和顺序
3. ⏳ 掌握关键工艺参数（KPP）
4. ⏳ 了解前后工序的联系

---

## 🔄 CMOS 工艺流程总览

```
硅片制备 → 氧化 → 光刻 → 刻蚀 → 离子注入 → 薄膜沉积 → CMP → 金属化 → 测试
   ↓         ↓        ↓        ↓          ↓          ↓         ↓       ↓        ↓
 Wafer    Gate     Active   Contact    S/D       Inter    Via     Pad     CP/FT
         Oxide    Pattern   Etch      Implant   Metal1   Metal2  Metal   Test
```

---

## 📊 详细工艺流程

### 1. 硅片制备 (Wafer Preparation)

**目的**: 准备高质量的硅衬底

**主要步骤**:
1. 单晶硅生长 (Czochralski 法)
2. 切割 (Slicing)
3. 倒角 (Edge Grinding)
4. 研磨 (Lapping)
5. 腐蚀 (Etching)
6. 抛光 (Polishing)
7. 清洗 (Cleaning)

**关键参数**:
- 晶圆尺寸：200mm / 300mm / 450mm
- 晶体取向：<100> / <111>
- 电阻率：根据掺杂浓度
- 平整度：TTV < 1μm

**YMS 关注点**:
- 硅片缺陷密度
- 表面粗糙度
- 厚度均匀性

---

### 2. 氧化 (Oxidation)

**目的**: 生长二氧化硅层（SiO₂）

**类型**:
- **干氧氧化**: O₂ ambient，质量好，速度慢
- **湿氧氧化**: H₂O ambient，速度快，质量稍差
- **LOCOS**: 局部氧化隔离

**反应方程式**:
```
Si + O₂ → SiO₂  (干氧)
Si + 2H₂O → SiO₂ + 2H₂  (湿氧)
```

**关键参数**:
- 温度：800-1200°C
- 时间：30min - 2hr
- 氧化层厚度：10nm - 1μm
- 均匀性：±2%

**YMS 关注点**:
- 氧化层厚度均匀性
- 界面态密度
- 击穿电压

---

### 3. 光刻 (Photolithography)

**目的**: 将掩膜版图形转移到晶圆表面

**主要步骤**:
1. 表面准备 (HMDS 处理)
2. 涂胶 (Spin Coating)
3. 前烘 (Soft Bake)
4. 对准 (Alignment)
5. 曝光 (Exposure)
6. 后烘 (PEB)
7. 显影 (Development)
8. 坚膜 (Hard Bake)
9. 显影检查 (ADI)

**关键参数**:
- 光刻胶厚度：0.5-2μm
- 曝光剂量：mJ/cm²
- 焦距：±0.1μm
- 套刻精度：< 10nm (先进节点)
- CD 均匀性：±3σ < 5%

**YMS 关注点**:
- CD (Critical Dimension) 均匀性
- 套刻误差 (Overlay)
- 缺陷密度
- 光刻胶残留

---

### 4. 刻蚀 (Etching)

**目的**: 去除未被光刻胶保护的材料

**类型**:
- **湿法刻蚀**: 化学溶液，各向同性
- **干法刻蚀**: 等离子体，各向异性

**干法刻蚀类型**:
- RIE (反应离子刻蚀)
- ICP (电感耦合等离子体)
- CCP (电容耦合等离子体)

**关键参数**:
- 刻蚀速率：Å/min
- 选择比：目标材料/掩膜材料
- 均匀性：±3%
- 侧壁角度：85-90°
- 刻蚀深度控制：±2%

**YMS 关注点**:
- 刻蚀速率均匀性
- 选择比
- 微负载效应
- 残留物
- 侧壁粗糙度

---

### 5. 离子注入 (Ion Implantation)

**目的**: 将掺杂离子注入硅中，改变电学特性

**主要步骤**:
1. 离子源产生
2. 质量分析
3. 加速
4. 扫描注入
5. 退火激活

**关键参数**:
- 注入能量：1-200 keV
- 注入剂量：1e11 - 1e16 ions/cm²
- 注入角度：0-60° (tilt/rotate)
- 结深：根据能量和剂量

**退火工艺**:
- 温度：800-1100°C
- 时间：秒级 (RTA) - 分钟级
- 氛围：N₂/Ar

**YMS 关注点**:
- 剂量均匀性
- 结深控制
- 激活率
- 注入损伤

---

### 6. 薄膜沉积 (Thin Film Deposition)

**目的**: 在晶圆表面沉积各种功能薄膜

**类型**:

#### PVD (物理气相沉积)
- 溅射 (Sputtering)
- 蒸发 (Evaporation)
- 应用：金属层 (Al, Cu, Ti, Ta)

#### CVD (化学气相沉积)
- APCVD (常压)
- LPCVD (低压)
- PECVD (等离子体增强)
- 应用：介质层 (SiO₂, Si₃N₄)

#### ALD (原子层沉积)
- 单层沉积，极好的均匀性
- 应用：High-k 介质、阻挡层

**关键参数**:
- 厚度：10nm - 1μm
- 均匀性：±1-3%
- 应力：压应力/张应力
- 台阶覆盖率：>90%
- 颗粒污染：< 0.1 个/cm²

**YMS 关注点**:
- 厚度均匀性
- 薄膜应力
- 针孔缺陷
- 颗粒污染

---

### 7. 化学机械抛光 (CMP)

**目的**: 全局平坦化晶圆表面

**原理**: 化学腐蚀 + 机械研磨

**主要步骤**:
1. 抛光 (Polishing)
2. 清洗 (Cleaning)
3. 干燥 (Drying)
4. 膜厚测量 (Metrology)

**关键参数**:
- 去除速率：Å/min
- 均匀性：±3%
- 平整度：WIWNU < 2%
- 缺陷密度：< 0.1 个/cm²

**YMS 关注点**:
- 碟形缺陷 (Dishing)
- 侵蚀 (Erosion)
- 残留 (Residue)
- 划痕 (Scratch)

---

### 8. 金属化 (Metallization)

**目的**: 形成互连结构

**工艺顺序**:
```
接触孔 → 阻挡层 → 种子层 → 电镀 → CMP → 钝化
Contact  Barrier  Seed    Plating  CMP    Passivation
```

**金属材料**:
- 接触/通孔：W (钨)
- 互连：Al (铝) / Cu (铜)
- 阻挡层：Ti/TiN, Ta/TaN
- 种子层：Cu seed

**关键参数**:
- 线宽/线距：根据节点
- 电阻率：μΩ·cm
- 电迁移寿命：>10 年
- 粘附性：>10 MPa

**YMS 关注点**:
- 空洞 (Void)
- 缝隙 (Seam)
- 电迁移
- 应力迁移

---

## 📈 典型 CMOS 工艺流程顺序

```
1.  硅片准备
2.  初始氧化
3.  有源区光刻
4.  有源区刻蚀 / STI 形成
5.  阱区注入 (N-well/P-well)
6.  栅氧化
7.  多晶硅沉积
8.  栅极光刻
9.  栅极刻蚀
10. 源漏注入 (LDD)
11. 侧墙形成
12. 源漏注入 (S/D)
13. 退火激活
14. 接触孔形成
15. 金属 1 沉积
16. 金属 1 光刻
17. 金属 1 刻蚀
18. 层间介质沉积
19. 通孔形成
20. 金属 2 沉积
... (重复多层金属)
21. 钝化层
22. 焊盘开口
23. 测试
```

---

## 🔍 关键工艺控制点 (KPP)

| 工艺步骤 | 关键参数 | 控制范围 | 检测方法 |
|----------|----------|----------|----------|
| 光刻 | CD 均匀性 | ±3σ < 5% | CD-SEM |
| 光刻 | 套刻精度 | < 10nm | Overlay Metrology |
| 刻蚀 | 刻蚀速率 | ±3% | Ellipsometry |
| 刻蚀 | 选择比 | > 10:1 | SEM |
| 注入 | 剂量均匀性 | ±1% | 4-point Probe |
| 注入 | 结深 | ±5% | SIMS |
| CVD | 厚度均匀性 | ±1.5% | Ellipsometry |
| CMP | 去除速率 | ±5% | Profilometry |
| 金属 | 电阻率 | ±5% | 4-point Probe |

---

## 📊 YMS 数据模型映射

### Lot (批次)
```
lot_id: L20240322.001
product_id: CMOS_180nm
route_id: ROUTE_001
wafer_count: 25
status: ACTIVE
```

### Wafer (晶圆)
```
wafer_id: W001
lot_id: L20240322.001
wafer_number: 1
cp_yield: 0.92
ft_yield: 0.89
```

### Defect (缺陷)
```
defect_id: D00001
wafer_id: W001
layer: METAL1
defect_type: Particle
x_coord: 125.5
y_coord: 89.3
size: 0.5μm
```

### Measurement (量测)
```
meas_id: M00001
wafer_id: W001
param: OXIDE_THICKNESS
value: 100.5
unit: nm
spec_min: 98.0
spec_max: 102.0
```

### Equipment (设备)
```
equip_id: EQP_ETCH_01
equip_type: ETCH
model: LAM TCP
status: RUNNING
mtba: 150hr
```

---

## 🎯 良率影响因素

### 1. 缺陷类
- 颗粒污染
- 划痕
- 残留
- 针孔
- 桥接

### 2. 工艺偏差类
- CD 偏差
- 厚度偏差
- 注入剂量偏差
- 刻蚀深度偏差

### 3. 设备类
- 设备漂移
- 腔室匹配
- 备件寿命

### 4. 环境类
- 温度波动
- 湿度波动
- 振动

---

## 📝 学习总结

### 已掌握
- ✅ CMOS 工艺整体流程框架
- ✅ 各主要工艺步骤的目的和作用
- ✅ 关键工艺参数 (KPP)
- ✅ YMS 数据模型与工艺的映射

### 待深入
- ⏳ 每个工艺步骤的详细物理/化学原理
- ⏳ 工艺整合 (PI) 知识
- ⏳ 失效模式分析
- ⏳ 先进节点工艺差异

### 下一步
1. 结合实际产品流程实例学习
2. 学习缺陷分类和根因分析
3. 深入 SPC 控制图应用
4. 实践 YMS 相关性分析

---

**参考资料**:
- YMS-Architecture.md
- semiconductor-yms skill
- 《Semiconductor Manufacturing Handbook》

**最后更新**: 2026-03-22  
**作者**: lamber
