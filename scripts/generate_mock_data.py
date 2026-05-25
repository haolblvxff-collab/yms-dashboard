"""Generate mock data for YMS database — Lots, Measurements, Defects, DOE."""
import sqlite3
import numpy as np
import random
import datetime
import json
import os
import sys

# 确保能导入 app 模块
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "app", "yms_data.db")
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

np.random.seed(42)
random.seed(42)

# ─── 清空旧数据 ───
for t in ["Measurements", "Defects", "Lots", "DOE_Experiments"]:
    cursor.execute(f"DELETE FROM {t}")
conn.commit()
print("已清空旧数据")

# ═══════════════════════════════════════════════════════════
# 1. Lots — 20个批次
# ═══════════════════════════════════════════════════════════
products = ["DEVICE-A", "DEVICE-B", "DEVICE-C", "MEMS-SENSOR", "POWER-IC"]
statuses = ["Completed", "In Progress", "On Hold"]
lots = []
for i in range(1, 21):
    lot_id = f"LOT-2026-{i:03d}"
    product = random.choice(products)
    start = datetime.datetime(2026, 4, 1) + datetime.timedelta(days=random.randint(0, 35))
    end = start + datetime.timedelta(hours=random.randint(12, 72))
    status = "Completed" if i <= 15 else random.choice(["In Progress", "On Hold"])
    lots.append((lot_id, product, start.isoformat(), end.isoformat(), status))

cursor.executemany(
    "INSERT INTO Lots (Lot_ID, Product_ID, Start_Time, End_Time, Status) VALUES (?,?,?,?,?)",
    lots
)
print(f"Lots: {len(lots)} 条")

# ═══════════════════════════════════════════════════════════
# 2. Measurements — 每个 Lot 多个参数
# ═══════════════════════════════════════════════════════════
params_config = {
    "Etch Rate (A/min)":  (1000, 15),    # mean, std
    "CD (nm)":            (45,   0.3),
    "Thickness (A)":      (5000, 20),
    "Pressure (mTorr)":   (50,   0.5),
    "RF Power (W)":       (300,  5),
    "Temperature (C)":    (200,  2),
}
recipes = ["ETCH_001", "ETCH_002", "DEP_001", "LITHO_001", "CMP_001"]

measurements = []
for i in range(1, 16):  # completed lots only
    lot = f"LOT-2026-{i:03d}"
    for param, (mean, std) in params_config.items():
        n = random.randint(8, 15)
        base_time = datetime.datetime(2026, 4, 1, 8, 0, 0) + datetime.timedelta(days=random.randint(0, 30))
        for j in range(n):
            ts = base_time + datetime.timedelta(hours=j * random.randint(2, 6))
            val = np.random.normal(mean, std)
            # 注入 OOC (约5%概率)
            if (hash(lot + param + str(j)) % 100 < 5):
                val = mean + random.choice([4.5, -4.5]) * std
            recipe = random.choice(recipes)
            measurements.append((lot, ts.isoformat(), param, round(float(val), 3), recipe))

cursor.executemany(
    "INSERT INTO Measurements (Lot_ID, Timestamp, Parameter_Name, Value, Recipe) VALUES (?,?,?,?,?)",
    measurements
)
print(f"Measurements: {len(measurements)} 条")

# ═══════════════════════════════════════════════════════════
# 3. Defects — 缺陷记录
# ═══════════════════════════════════════════════════════════
defect_types = [
    ("Particle", 0.35), ("Scratch", 0.20), ("Pattern Collapse", 0.12),
    ("Void", 0.10), ("Residue", 0.08), ("Bridging", 0.06),
    ("Notch", 0.04), ("Contamination", 0.03), ("Micro-crack", 0.02),
]
severities = ["Low", "Medium", "High", "Critical"]
sev_weights = [0.40, 0.35, 0.18, 0.07]
cnt_vals = [1, 2, 3, 5, 8, 12, 20, 50]
cnt_weights = [0.30, 0.25, 0.15, 0.10, 0.08, 0.06, 0.04, 0.02]

defects = []
for _ in range(350):
    lot = f"LOT-2026-{random.randint(1, 17):03d}"
    wafer = f"W{random.randint(1,25):02d}"
    dtype = random.choices([d[0] for d in defect_types],
                           weights=[d[1] for d in defect_types])[0]
    count = random.choices(cnt_vals, weights=cnt_weights)[0]
    sev = random.choices(severities, weights=sev_weights)[0]
    ts = datetime.datetime(2026, 4, 1) + datetime.timedelta(
        days=random.randint(0, 40), hours=random.randint(0, 23), minutes=random.randint(0, 59))
    defects.append((lot, wafer, dtype, count, sev, ts.isoformat()))

cursor.executemany(
    "INSERT INTO Defects (Lot_ID, Wafer_ID, Defect_Type, Count, Severity, Timestamp) VALUES (?,?,?,?,?,?)",
    defects
)
print(f"Defects: {len(defects)} 条")

# ═══════════════════════════════════════════════════════════
# 4. DOE_Experiments
# ═══════════════════════════════════════════════════════════
doe_data = json.dumps({
    "factors": {"Pressure": [-1, 0, 1], "RF_Power": [-1, 0, 1]},
    "response": [[50, 55, 62], [58, 65, 70], [60, 68, 75]],
    "interaction": True,
})
cursor.execute(
    "INSERT INTO DOE_Experiments (Experiment_Name, Factor_1, Factor_2, Response_Variable, Data_JSON) VALUES (?,?,?,?,?)",
    ("Etch Rate DOE", "Pressure (mTorr)", "RF Power (W)", "Etch Rate (A/min)", doe_data)
)
cursor.execute(
    "INSERT INTO DOE_Experiments (Experiment_Name, Factor_1, Factor_2, Response_Variable, Data_JSON) VALUES (?,?,?,?,?)",
    ("CD Uniformity DOE", "Temperature (C)", "Gas Flow (sccm)", "CD (nm)",
     json.dumps({"factors": {"Temperature": [-1, 0, 1], "Gas_Flow": [-1, 0, 1]},
                 "response": [[30, 35, 40], [38, 45, 52], [40, 50, 60]], "interaction": True}))
)
print("DOE_Experiments: 2 条")

conn.commit()

# ─── 汇总 ───
print("\n" + "="*50)
print("数据库汇总:")
for t in ["Lots", "Measurements", "Defects", "DOE_Experiments"]:
    cursor.execute(f"SELECT COUNT(*) FROM {t}")
    count = cursor.fetchone()[0]
    print(f"  {t:20s}: {count:5d} 条")
conn.close()
print("\n✅ 模拟数据已写入 yms_data.db")
print("   刷新 Dashboard 即可看到数据")
