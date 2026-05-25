"""Generate GR&R demo data and run quick validation."""
import sys, os, importlib.util
import numpy as np

proj_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(proj_dir, "app"))

from database import init_db, insert_query, run_query
init_db()

# Check if study exists
existing = run_query("SELECT ID FROM GRR_Studies WHERE Study_Name = ?", ["CD-SEM CD GR&R 2026-Q2"])
if existing.empty:
    study_id = insert_query(
        """INSERT INTO GRR_Studies (Study_Name, Description, Method, Gauge_Name, USL, LSL, Tolerance)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        ("CD-SEM CD GR&R 2026-Q2", "CD-SEM #3 daily", "ANOVA", "CD-SEM #3", 105.0, 95.0, 10.0)
    )
    print(f"Study created: ID={study_id}")

    np.random.seed(42)
    n_parts, n_ops, n_trials = 10, 3, 3
    parts = [f"Wafer-{i+1:02d}" for i in range(n_parts)]
    ops = [f"Op-{i+1}" for i in range(n_ops)]
    grand_mean = 100.0
    part_effects = np.random.normal(0, 1.2, n_parts)
    op_biases = np.array([-0.2, 0.15, 0.05])
    saved = 0
    for pi, part in enumerate(parts):
        for oi, op in enumerate(ops):
            for trial in range(1, n_trials + 1):
                value = grand_mean + part_effects[pi] + op_biases[oi] + np.random.normal(0, 0.25)
                value = round(float(value), 3)
                insert_query(
                    """INSERT INTO GRR_Measurements (Study_ID, Part_ID, Operator_ID, Trial, Value)
                       VALUES (?, ?, ?, ?, ?)""",
                    (study_id, part, op, trial, value)
                )
                saved += 1
    print(f"Saved {saved} measurements")
else:
    study_id = int(existing.iloc[0]["ID"])
    print(f"Study exists: ID={study_id}")

# Test engine
df = run_query(
    """SELECT Part_ID AS Part, Operator_ID AS Operator, Trial, Value
       FROM GRR_Measurements WHERE Study_ID = ?""", [study_id])
print(f"Loaded {len(df)} rows")

_msa_path = os.path.join(proj_dir, "src", "yms", "analysis", "msa_gauge_rr.py")
_msa_spec = importlib.util.spec_from_file_location("msa_gauge_rr", os.path.abspath(_msa_path))
_msa_mod = importlib.util.module_from_spec(_msa_spec)
_msa_spec.loader.exec_module(_msa_mod)
msa = _msa_mod.MSAGaugeRR()

result = msa.analyze(df, method="ANOVA", usl=105.0, lsl=95.0)

print(f"\n=== GR&R Results ===")
print(f"%GR&R = {result.pct_grr:.1f}%  ({result.grade_grr})")
print(f"%EV   = {result.pct_repeatability:.1f}%")
print(f"%AV   = {result.pct_reproducibility:.1f}%")
print(f"%PV   = {result.pct_part:.1f}%")
print(f"ndc   = {result.ndc:.1f}  ({result.grade_ndc})")
print(f"%Tol  = {result.pct_tol_grr:.1f}%")
print("OK")
