"""Regenerate YMS mock data with richer defects for Yield Analysis demo."""
import sys, os, numpy as np

os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "app"))
sys.path.insert(0, ".")
from database import init_db, insert_query, run_query

init_db()

# Clear old data
for tbl in ["GRR_Measurements", "GRR_Studies", "DOE_Experiments", "Defects", "Measurements", "Lots"]:
    try:
        insert_query(f"DELETE FROM {tbl}", [])
    except:
        pass

np.random.seed(42)

# ── Lots (20 lots, 5 products) ──
products = ["A100", "B200", "C300", "D400", "E500"]
lot_ids = []
for i in range(20):
    lid = f"LOT-{i+1:04d}"
    prod = products[i % 5]
    status = "Completed" if i < 16 else ("In Progress" if i < 18 else "On Hold")
    insert_query("INSERT INTO Lots (Lot_ID, Product_ID, Status) VALUES (?, ?, ?)",
                 (lid, prod, status))
    lot_ids.append(lid)
print(f"Created {len(lot_ids)} lots")

# ── Measurements (6 params × 16 completed lots ≈ 1000 points) ──
params = ["CD_nm", "THK_A", "ETCH_Rate", "Pressure_mT", "Temp_C", "Uniformity_pct"]
param_means = {"CD_nm": 100, "THK_A": 5000, "ETCH_Rate": 1000, "Pressure_mT": 50, "Temp_C": 250, "Uniformity_pct": 2.0}
param_std = {"CD_nm": 1.5, "THK_A": 30, "ETCH_Rate": 25, "Pressure_mT": 0.8, "Temp_C": 3, "Uniformity_pct": 0.15}
param_corr_with_yield = {"CD_nm": -0.55, "THK_A": 0.20, "ETCH_Rate": -0.40, "Pressure_mT": 0.35, "Temp_C": -0.30, "Uniformity_pct": -0.60}

# Generate measurements with realistic correlations to yield
base_yield = np.random.uniform(0.85, 0.98, 16)
for i, lid in enumerate(lot_ids[:16]):  # completed lots
    ly = base_yield[i]
    for param in params:
        mu = param_means[param]
        sd = param_std[param]
        corr = param_corr_with_yield[param]
        # Induce correlation: shift mean based on lot yield
        adjusted_mu = mu + corr * (ly - 0.91) * sd * 3
        value = np.random.normal(adjusted_mu, sd)
        insert_query(
            "INSERT INTO Measurements (Lot_ID, Parameter_Name, Value, Recipe) VALUES (?, ?, ?, ?)",
            (lid, param, round(value, 3), f"RECIPE_{products[i%5]}")
        )
print(f"Created {16 * len(params)} measurements for {16} lots")

# ── Defects (rich: 9 types, 4 severities, ~400 defects across 16 lots) ──
defect_types = [
    "Particle_Fall-on", "Pattern_Bridge", "Scratch_Surface",
    "Residue_Organic", "Void_Metal", "Thickness_NonUniform",
    "CD_Deviation", "Overlay_Shift", "Contamination_Edge"
]
severities = ["Critical", "Major", "Minor", "Cosmetic"]
# Kill ratios by defect type (for realistic yield loss)
defect_kr = {
    "Particle_Fall-on": 0.35, "Pattern_Bridge": 0.75, "Scratch_Surface": 0.90,
    "Residue_Organic": 0.40, "Void_Metal": 0.80, "Thickness_NonUniform": 0.50,
    "CD_Deviation": 0.70, "Overlay_Shift": 0.85, "Contamination_Edge": 0.30,
}
defect_base_rate = {
    "Particle_Fall-on": 30, "Pattern_Bridge": 8, "Scratch_Surface": 3,
    "Residue_Organic": 12, "Void_Metal": 5, "Thickness_NonUniform": 15,
    "CD_Deviation": 10, "Overlay_Shift": 6, "Contamination_Edge": 20,
}

for i, lid in enumerate(lot_ids[:16]):
    for dtype in defect_types:
        # Lower-yield lots have more defects
        ly = base_yield[i]
        base_count = defect_base_rate[dtype]
        adj_count = max(0, int(np.random.poisson(base_count * (1.2 - ly))))
        if adj_count > 0:
            sev = np.random.choice(severities, p=[0.15, 0.35, 0.30, 0.20])
            insert_query(
                "INSERT INTO Defects (Lot_ID, Wafer_ID, Defect_Type, Count, Severity) VALUES (?, ?, ?, ?, ?)",
                (lid, f"W{i+1:02d}", dtype, adj_count, sev)
            )
print("Created rich defect data with realistic distributions")
print("Done")
