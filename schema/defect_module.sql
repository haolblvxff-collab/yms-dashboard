-- ============================================================
-- YMS 缺陷分类模块 (Defect Classification Module)
-- ============================================================
-- 创建日期：2026-03-26
-- 作者：lamber
-- 描述：缺陷检测数据模型，支持缺陷采集、分类、分析和追溯
-- ============================================================

-- ============================================================
-- 1. 缺陷类型分类表 (Defect Type Classification)
-- ============================================================
-- 参考 SEMI 标准和行业通用缺陷分类体系

CREATE TABLE defect_category (
    category_id         SERIAL PRIMARY KEY,
    category_code       VARCHAR(20) NOT NULL UNIQUE,  -- 分类代码：PARTICLE, SCRATCH, VOID, etc.
    category_name_cn    VARCHAR(100) NOT NULL,         -- 中文名称
    category_name_en    VARCHAR(100) NOT NULL,         -- 英文名称
    parent_category_id  INTEGER REFERENCES defect_category(category_id),  -- 父分类 (支持层级)
    description         TEXT,                          -- 详细描述
    severity_level      INTEGER DEFAULT 3,             -- 严重度等级 (1-5, 5 最严重)
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 预置缺陷分类数据 (SEMATECH 标准)
INSERT INTO defect_category (category_code, category_name_cn, category_name_en, severity_level, description) VALUES
-- 颗粒类缺陷
('PARTICLE', '颗粒', 'Particle', 3, '表面附着的微小颗粒，可能来自设备、环境或工艺副产物'),
('CONTAMINATION', '污染', 'Contamination', 3, '表面化学污染，包括有机物、金属离子等'),

-- 图形类缺陷
('PATTERN_DEFECT', '图形缺陷', 'Pattern Defect', 4, '光刻或刻蚀导致的图形异常'),
('BRIDGE', '桥接', 'Bridge', 5, '两条本应分开的导线连接在一起'),
('OPEN', '开路', 'Open', 5, '导线断开导致电路不通'),
('SHORT', '短路', 'Short', 5, '不同电位的导体意外连接'),
('LINE_BREAK', '断线', 'Line Break', 5, '金属线或poly 线断裂'),
('LINE_THIN', '线宽过细', 'Line Thinning', 4, '导线宽度低于规格下限'),
('LINE_THICK', '线宽过粗', 'Line Thickening', 4, '导线宽度超出规格上限'),

-- 表面类缺陷
('SCRATCH', '划伤', 'Scratch', 4, '机械划伤，通常呈线性'),
('DENT', '凹坑', 'Dent', 3, '表面凹陷'),
('HILLOCK', '凸起', 'Hillock', 3, '表面突起，常见于金属层'),
('PIT', '针孔', 'Pit', 4, '薄膜上的小孔，可能导致短路'),
('VOID', '空洞', 'Void', 4, '材料内部或界面的空腔'),
('PEELING', '剥离', 'Peeling', 5, '薄膜从基底剥离'),
('CRACK', '裂纹', 'Crack', 5, '材料开裂，可能延伸至内部'),

-- 刻蚀类缺陷
('UNDERCUT', '底切', 'Undercut', 4, '刻蚀横向过度，形成凹陷'),
('RESIDUE', '残留', 'Residue', 4, '刻蚀后未完全去除的材料'),
('MICRO_TRENCH', '微沟槽', 'Micro-Trench', 3, '刻蚀底部形成的 V 型沟槽'),
('NOTCHING', '缺口', 'Notching', 4, '刻蚀侧壁的不规则缺口'),

-- 光刻类缺陷
('FOCUS_ERROR', '聚焦误差', 'Focus Error', 3, '光刻聚焦不良导致的图形模糊'),
('EXPOSURE_ERROR', '曝光误差', 'Exposure Error', 3, '曝光剂量不当导致的 CD 偏差'),
('ALIGNMENT_ERROR', '套刻误差', 'Alignment Error', 4, '层间对准偏差'),

-- 薄膜类缺陷
('THICKNESS_VAR', '厚度不均', 'Thickness Variation', 3, '薄膜厚度超出均匀性规格'),
('STRESS_DEFECT', '应力缺陷', 'Stress Defect', 4, '薄膜应力过大导致的翘曲或裂纹'),
('DELAMINATION', '分层', 'Delamination', 5, '薄膜层间分离'),

-- 注入类缺陷
('IMPLANT_ERROR', '注入误差', 'Implant Error', 4, '离子注入剂量或能量偏差'),
('CHANNELING', '沟道效应', 'Channeling', 4, '离子沿晶格方向深入，导致分布异常'),

-- CMP 类缺陷
('DISHING', '碟形缺陷', 'Dishing', 3, 'Cu CMP 后金属表面凹陷'),
('EROSION', '侵蚀', 'Erosion', 3, '介质层 CMP 后过度去除'),
('CORROSION', '腐蚀', 'Corrosion', 4, 'Cu 互连的化学腐蚀'),

-- 其他
('OTHER', '其他', 'Other', 2, '未分类的缺陷'),
('FALSE_ALARM', '误报', 'False Alarm', 1, '检测系统误判，实际无缺陷');

-- ============================================================
-- 2. 缺陷检测记录表 (Defect Inspection Records)
-- ============================================================

CREATE TABLE defect_inspection (
    inspection_id     SERIAL PRIMARY KEY,
    inspection_code   VARCHAR(50) NOT NULL UNIQUE,  -- 检测批次代码
    lot_id            VARCHAR(50) NOT NULL,          -- 批次 ID
    wafer_id          VARCHAR(50) NOT NULL,          -- 晶圆 ID
    layer_name        VARCHAR(50),                   -- 工艺层名称 (e.g., M1, POLY, AA)
    process_step      VARCHAR(100),                  -- 工艺步骤 (e.g., "Photo_M1", "Etch_M1")
    equipment_id      VARCHAR(50),                   -- 检测设备 ID
    recipe_id         VARCHAR(50),                   -- 检测配方 ID
    inspection_time   TIMESTAMP NOT NULL,            -- 检测时间
    inspector         VARCHAR(50),                   -- 操作员
    total_defects     INTEGER DEFAULT 0,             -- 总缺陷数
    defect_density    DECIMAL(10,4),                 -- 缺陷密度 (defects/cm²)
    inspection_area   DECIMAL(10,4),                 -- 检测面积 (cm²)
    sensitivity       VARCHAR(20),                   -- 检测灵敏度 (e.g., "0.1um", "0.2um")
    status            VARCHAR(20) DEFAULT 'COMPLETED', -- 状态：PENDING, COMPLETED, REVIEWED
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- 外键约束
    CONSTRAINT fk_lot FOREIGN KEY (lot_id) REFERENCES lot_tracking(lot_id),
    CONSTRAINT fk_wafer FOREIGN KEY (wafer_id) REFERENCES wafer_info(wafer_id)
);

-- 索引优化
CREATE INDEX idx_defect_inspection_lot ON defect_inspection(lot_id);
CREATE INDEX idx_defect_inspection_wafer ON defect_inspection(wafer_id);
CREATE INDEX idx_defect_inspection_layer ON defect_inspection(layer_name);
CREATE INDEX idx_defect_inspection_time ON defect_inspection(inspection_time);

-- ============================================================
-- 3. 缺陷明细表 (Defect Details)
-- ============================================================
-- 记录每个缺陷的详细信息

CREATE TABLE defect_detail (
    defect_id         BIGSERIAL PRIMARY KEY,
    inspection_id     INTEGER NOT NULL REFERENCES defect_inspection(inspection_id),
    defect_number     INTEGER NOT NULL,              -- 缺陷序号 (within inspection)
    category_id       INTEGER REFERENCES defect_category(category_id),
    
    -- 位置信息
    wafer_x           DECIMAL(10,4) NOT NULL,        -- X 坐标 (mm, 以晶圆中心为原点)
    wafer_y           DECIMAL(10,4) NOT NULL,        -- Y 坐标 (mm)
    die_x             INTEGER,                       -- Die 列号
    die_y             INTEGER,                       -- Die 行号
    
    -- 缺陷特征
    size              DECIMAL(10,4),                 -- 缺陷尺寸 (um)
    height            DECIMAL(10,4),                 -- 缺陷高度 (um, 3D 检测)
    shape             VARCHAR(50),                   -- 形状描述
    brightness        INTEGER,                       -- 亮度值 (0-255)
    contrast          INTEGER,                       -- 对比度
    
    -- 分类信息
    auto_class        VARCHAR(50),                   -- 自动分类结果
    manual_class      VARCHAR(50),                   -- 人工复检分类
    review_status     VARCHAR(20) DEFAULT 'PENDING', -- PENDING, REVIEWED, SKIPPED
    reviewer          VARCHAR(50),                   -- 复检员
    review_time       TIMESTAMP,                     -- 复检时间
    confidence        DECIMAL(5,4),                  -- 分类置信度 (0-1)
    
    -- 图像信息
    defect_image_path VARCHAR(500),                  -- 缺陷图像路径
    reference_path    VARCHAR(500),                  -- 参考图像路径
    
    -- 影响评估
    kill_ratio        DECIMAL(5,4),                  -- 致死率 (0-1, 导致芯片失效的概率)
    electrical_impact VARCHAR(20),                   -- 电学影响：NONE, MINOR, MAJOR, FATAL
    
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 索引优化 (关键查询性能)
CREATE INDEX idx_defect_detail_inspection ON defect_detail(inspection_id);
CREATE INDEX idx_defect_detail_category ON defect_detail(category_id);
CREATE INDEX idx_defect_detail_wafer_pos ON defect_detail(wafer_x, wafer_y);
CREATE INDEX idx_defect_detail_die_pos ON defect_detail(die_x, die_y);
CREATE INDEX idx_defect_detail_review_status ON defect_detail(review_status);

-- ============================================================
-- 4. 缺陷 Pareto 分析视图 (Defect Pareto View)
-- ============================================================

CREATE VIEW v_defect_pareto AS
SELECT 
    dc.category_code,
    dc.category_name_cn,
    dc.category_name_en,
    dc.severity_level,
    COUNT(dd.defect_id) AS defect_count,
    ROUND(100.0 * COUNT(dd.defect_id) / SUM(COUNT(dd.defect_id)) OVER (), 2) AS percentage,
    ROUND(100.0 * SUM(COUNT(dd.defect_id)) OVER (ORDER BY COUNT(dd.defect_id) DESC ROWS UNBOUNDED PRECEDING) 
          / SUM(COUNT(dd.defect_id)) OVER (), 2) AS cumulative_percentage
FROM defect_detail dd
JOIN defect_category dc ON dd.category_id = dc.category_id
WHERE dd.review_status = 'REVIEWED'
GROUP BY dc.category_id, dc.category_code, dc.category_name_cn, dc.category_name_en, dc.severity_level
ORDER BY defect_count DESC;

-- ============================================================
-- 5. 缺陷密度趋势视图 (Defect Density Trend View)
-- ============================================================

CREATE VIEW v_defect_density_trend AS
SELECT 
    layer_name,
    process_step,
    DATE(inspection_time) AS inspection_date,
    COUNT(DISTINCT inspection_id) AS inspection_count,
    AVG(defect_density) AS avg_defect_density,
    STDDEV(defect_density) AS stddev_defect_density,
    MAX(defect_density) AS max_defect_density,
    MIN(defect_density) AS min_defect_density,
    AVG(total_defects) AS avg_total_defects
FROM defect_inspection
GROUP BY layer_name, process_step, DATE(inspection_time)
ORDER BY inspection_date DESC, layer_name;

-- ============================================================
-- 6. 缺陷 SPC 控制表 (Defect SPC Control)
-- ============================================================
-- 用于缺陷密度的统计过程控制

CREATE TABLE defect_spc_control (
    spc_id            SERIAL PRIMARY KEY,
    layer_name        VARCHAR(50) NOT NULL,
    process_step      VARCHAR(100) NOT NULL,
    category_id       INTEGER REFERENCES defect_category(category_id),
    
    -- 控制限
    ucl               DECIMAL(10,4),                 -- 上控制限 (Upper Control Limit)
    cl                DECIMAL(10,4),                 -- 中心线 (Center Line)
    lcl               DECIMAL(10,4),                 -- 下控制限 (Lower Control Limit)
    
    -- 规格限
    usl               DECIMAL(10,4),                 -- 上规格限 (Upper Specification Limit)
    lsl               DECIMAL(10,4),                 -- 下规格限 (Lower Specification Limit)
    
    -- 统计参数
    sample_size       INTEGER DEFAULT 30,            -- 样本数量
    mean_value        DECIMAL(10,4),                 -- 均值
    stddev_value      DECIMAL(10,4),                 -- 标准差
    cp_value          DECIMAL(5,4),                  -- Cp (过程能力指数)
    cpk_value         DECIMAL(5,4),                  -- Cpk (实际过程能力指数)
    
    -- 控制规则 (Western Electric Rules)
    rule1_enabled     BOOLEAN DEFAULT TRUE,          -- 单点超出±3σ
    rule2_enabled     BOOLEAN DEFAULT TRUE,          -- 连续 9 点同侧
    rule3_enabled     BOOLEAN DEFAULT TRUE,          -- 连续 6 点上升/下降
    rule4_enabled     BOOLEAN DEFAULT TRUE,          -- 连续 14 点交替
    rule5_enabled     BOOLEAN DEFAULT TRUE,          -- 连续 3 点中 2 点超出±2σ
    rule6_enabled     BOOLEAN DEFAULT TRUE,          -- 连续 5 点中 4 点超出±1σ
    
    -- 状态
    is_active         BOOLEAN DEFAULT TRUE,
    last_calculation  TIMESTAMP,
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- 唯一约束
    UNIQUE(layer_name, process_step, category_id)
);

-- ============================================================
-- 7. 缺陷告警记录表 (Defect Alert Records)
-- ============================================================

CREATE TABLE defect_alert (
    alert_id          SERIAL PRIMARY KEY,
    inspection_id     INTEGER REFERENCES defect_inspection(inspection_id),
    spc_id            INTEGER REFERENCES defect_spc_control(spc_id),
    alert_type        VARCHAR(50) NOT NULL,          -- 告警类型：SPC_VIOLATION, HIGH_DENSITY, EXCURSION
    alert_level       VARCHAR(20) NOT NULL,          -- 告警等级：INFO, WARNING, CRITICAL, FATAL
    alert_message     TEXT NOT NULL,                 -- 告警消息
    triggered_value   DECIMAL(10,4),                 -- 触发值
    threshold_value   DECIMAL(10,4),                 -- 阈值
    rule_violated     VARCHAR(100),                  -- 违反的规则
    triggered_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    acknowledged_by   VARCHAR(50),                   -- 确认人
    acknowledged_at   TIMESTAMP,                     -- 确认时间
    action_taken      TEXT,                          -- 采取的措施
    status            VARCHAR(20) DEFAULT 'OPEN',    -- OPEN, ACKNOWLEDGED, CLOSED
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 索引优化
CREATE INDEX idx_defect_alert_inspection ON defect_alert(inspection_id);
CREATE INDEX idx_defect_alert_status ON defect_alert(status);
CREATE INDEX idx_defect_alert_triggered_at ON defect_alert(triggered_at);

-- ============================================================
-- 8. 缺陷 Wafer Map 数据表 (Defect Wafer Map)
-- ============================================================
-- 用于快速生成 Wafer Map 可视化

CREATE TABLE defect_wafer_map (
    map_id            SERIAL PRIMARY KEY,
    inspection_id     INTEGER NOT NULL REFERENCES defect_inspection(inspection_id),
    wafer_id          VARCHAR(50) NOT NULL,
    layer_name        VARCHAR(50),
    
    -- 分 bin 统计 (按缺陷类型或尺寸)
    bin1_count        INTEGER DEFAULT 0,             -- Bin 1: Particle (<0.5um)
    bin2_count        INTEGER DEFAULT 0,             -- Bin 2: Particle (0.5-1um)
    bin3_count        INTEGER DEFAULT 0,             -- Bin 3: Particle (>1um)
    bin4_count        INTEGER DEFAULT 0,             -- Bin 4: Scratch
    bin5_count        INTEGER DEFAULT 0,             -- Bin 5: Pattern Defect
    bin6_count        INTEGER DEFAULT 0,             -- Bin 6: Other
    
    -- 区域统计
    center_count      INTEGER DEFAULT 0,             -- 中心区域缺陷数
    edge_count        INTEGER DEFAULT 0,             -- 边缘区域缺陷数
    total_count       INTEGER DEFAULT 0,             -- 总缺陷数
    
    -- 良率影响评估
    estimated_yield_loss DECIMAL(5,4),              -- 预估良率损失 (%)
    
    -- 图像数据
    wafer_map_image   BYTEA,                         -- Wafer Map 图像 (可选)
    wafer_map_path    VARCHAR(500),                  -- Wafer Map 文件路径
    
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 9. 缺陷与电测关联表 (Defect-Electrical Correlation)
-- ============================================================
-- 用于分析缺陷对电测良率的影响

CREATE TABLE defect_electrical_corr (
    corr_id           SERIAL PRIMARY KEY,
    wafer_id          VARCHAR(50) NOT NULL,
    lot_id            VARCHAR(50) NOT NULL,
    
    -- 缺陷数据
    inspection_id     INTEGER REFERENCES defect_inspection(inspection_id),
    total_defects     INTEGER,
    critical_defects  INTEGER,                     -- 关键缺陷数 (kill_ratio > 0.8)
    defect_density    DECIMAL(10,4),
    
    -- 电测数据
    cp_test_yield     DECIMAL(5,4),                -- CP 测试良率 (%)
    ft_test_yield     DECIMAL(5,4),                -- FT 测试良率 (%)
    total_die         INTEGER,                     -- 总芯片数
    pass_die          INTEGER,                     -- 通过芯片数
    fail_die          INTEGER,                     -- 失效芯片数
    
    -- 关联分析
    correlation_coeff DECIMAL(5,4),                -- 相关系数 (Pearson r)
    p_value           DECIMAL(10,6),               -- 显著性 p 值
    yield_loss_model  VARCHAR(100),                -- 良率损失模型 (Poisson/Exponential/Seeds)
    
    -- 分析结论
    impact_assessment VARCHAR(500),                -- 影响评估
    recommendation    TEXT,                        -- 改进建议
    
    analyzed_by       VARCHAR(50),
    analyzed_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 10. 数据更新触发器 (Update Triggers)
-- ============================================================

-- 自动更新 updated_at 时间戳
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_defect_category_updated_at
    BEFORE UPDATE ON defect_category
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trg_defect_detail_updated_at
    BEFORE UPDATE ON defect_detail
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trg_defect_spc_control_updated_at
    BEFORE UPDATE ON defect_spc_control
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================
-- 11. 常用查询示例 (Query Examples)
-- ============================================================

-- 查询 1: 获取某批次的缺陷 Pareto 分析
-- SELECT * FROM v_defect_pareto;

-- 查询 2: 获取某层的缺陷密度趋势
-- SELECT * FROM v_defect_density_trend WHERE layer_name = 'M1';

-- 查询 3: 获取某晶圆的 Wafer Map 数据
-- SELECT * FROM defect_wafer_map WHERE wafer_id = 'W001234';

-- 查询 4: 获取未处理的告警
-- SELECT * FROM defect_alert WHERE status = 'OPEN' ORDER BY triggered_at DESC;

-- 查询 5: 获取某缺陷类型的 SPC 状态
-- SELECT * FROM defect_spc_control WHERE category_id = 1 AND is_active = TRUE;

-- ============================================================
-- 文档结束
-- ============================================================
