"""
YMS FastAPI Backend — REST API for query, upload, and analysis.
"""
import os
import io
import datetime
import tempfile
from typing import Optional, List

import pandas as pd
import numpy as np
from fastapi import FastAPI, File, UploadFile, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse, JSONResponse
from pydantic import BaseModel
import sqlite3

from database import get_connection, run_query, insert_query, init_db

app = FastAPI(
    title="YMS API",
    description="Yield Management System — Query, Upload, and Analysis API",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = os.path.join(os.path.dirname(__file__), "yms_data.db")
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ─── Models ────────────────────────────────────────────────

class QueryRequest(BaseModel):
    sql: str


class GRRStudyCreate(BaseModel):
    study_name: str
    description: Optional[str] = ""
    method: str = "ANOVA"
    gauge_name: Optional[str] = None
    usl: Optional[float] = None
    lsl: Optional[float] = None
    tolerance: Optional[float] = None


class GRRMeasurement(BaseModel):
    part_id: str
    operator_id: str
    trial: int
    value: float


class LotCreate(BaseModel):
    lot_id: str
    product_id: Optional[str] = None
    status: str = "In Progress"


class MeasurementCreate(BaseModel):
    lot_id: str
    parameter_name: str
    value: float
    recipe: Optional[str] = None
    timestamp: Optional[str] = None


class DefectCreate(BaseModel):
    lot_id: str
    wafer_id: str
    defect_type: str
    count: int
    severity: Optional[str] = "Medium"


# ─── Health ────────────────────────────────────────────────

@app.get("/api/health")
def health():
    return {"status": "ok", "version": "2.0.0", "timestamp": str(datetime.datetime.now())}


# ─── File Upload ───────────────────────────────────────────

@app.post("/api/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    """Upload CSV or Excel files. Auto-detects table type from column names."""
    results = []
    for file in files:
        content = await file.read()
        ext = os.path.splitext(file.filename)[1].lower()

        try:
            if ext == ".csv":
                df = pd.read_csv(io.BytesIO(content))
            elif ext in (".xlsx", ".xls"):
                df = pd.read_excel(io.BytesIO(content))
            else:
                results.append({"file": file.filename, "status": "error", "msg": "Unsupported format"})
                continue
        except Exception as e:
            results.append({"file": file.filename, "status": "error", "msg": str(e)})
            continue

        # Auto-detect table
        cols = [c.lower().strip() for c in df.columns]
        table = _detect_table(cols)

        if table is None:
            results.append({"file": file.filename, "status": "skipped", "msg": "Cannot detect table type from columns", "columns": list(df.columns)})
            continue

        count = _import_dataframe(df, table)
        results.append({"file": file.filename, "status": "imported", "table": table, "rows": count})

    return {"results": results}


def _detect_table(cols: List[str]):
    """Detect target table from column names."""
    if any(k in cols for k in ("lot_id", "lot", "lot_no")):
        if any(k in cols for k in ("parameter_name", "param", "parameter", "measurement")):
            return "Measurements"
        if any(k in cols for k in ("wafer_id", "wafer", "defect_type", "defect")):
            return "Defects"
        if any(k in cols for k in ("start_time", "end_time", "status", "product_id")):
            return "Lots"
    if any(k in cols for k in ("wafer_id", "wafer", "defect_type")):
        return "Defects"
    return None


def _import_dataframe(df: pd.DataFrame, table: str) -> int:
    """Import DataFrame into SQLite table."""
    conn = get_connection()
    try:
        if table == "Lots":
            mapping = {
                "lot_id": _find_col(df, ["lot_id", "lot", "lot_no"]),
                "product_id": _find_col(df, ["product_id", "product", "device"]),
                "start_time": _find_col(df, ["start_time", "start"]),
                "end_time": _find_col(df, ["end_time", "end"]),
                "status": _find_col(df, ["status"]),
            }
            count = 0
            for _, row in df.iterrows():
                vals = {
                    "Lot_ID": str(row.get(mapping["lot_id"], "")),
                    "Product_ID": str(row.get(mapping["product_id"], "")),
                    "Start_Time": str(row.get(mapping["start_time"], "")),
                    "End_Time": str(row.get(mapping["end_time"], "")),
                    "Status": str(row.get(mapping["status"], "In Progress")),
                }
                conn.execute(
                    "INSERT OR REPLACE INTO Lots (Lot_ID, Product_ID, Start_Time, End_Time, Status) VALUES (?,?,?,?,?)",
                    [vals["Lot_ID"], vals["Product_ID"], vals["Start_Time"], vals["End_Time"], vals["Status"]],
                )
                count += 1

        elif table == "Measurements":
            mapping = {
                "lot_id": _find_col(df, ["lot_id", "lot"]),
                "timestamp": _find_col(df, ["timestamp", "time", "date"]),
                "parameter_name": _find_col(df, ["parameter_name", "param", "parameter"]),
                "value": _find_col(df, ["value", "measurement", "result"]),
                "recipe": _find_col(df, ["recipe"]),
            }
            count = 0
            for _, row in df.iterrows():
                conn.execute(
                    "INSERT INTO Measurements (Lot_ID, Timestamp, Parameter_Name, Value, Recipe) VALUES (?,?,?,?,?)",
                    [
                        str(row.get(mapping["lot_id"], "")),
                        str(row.get(mapping["timestamp"], datetime.datetime.now().isoformat())),
                        str(row.get(mapping["parameter_name"], "")),
                        float(row.get(mapping["value"], 0)),
                        str(row.get(mapping["recipe"], "")),
                    ],
                )
                count += 1

        elif table == "Defects":
            mapping = {
                "lot_id": _find_col(df, ["lot_id", "lot"]),
                "wafer_id": _find_col(df, ["wafer_id", "wafer"]),
                "defect_type": _find_col(df, ["defect_type", "defect", "type"]),
                "count": _find_col(df, ["count", "cnt", "quantity"]),
                "severity": _find_col(df, ["severity", "level"]),
                "timestamp": _find_col(df, ["timestamp", "time", "date"]),
            }
            count = 0
            for _, row in df.iterrows():
                conn.execute(
                    "INSERT INTO Defects (Lot_ID, Wafer_ID, Defect_Type, Count, Severity, Timestamp) VALUES (?,?,?,?,?,?)",
                    [
                        str(row.get(mapping["lot_id"], "")),
                        str(row.get(mapping["wafer_id"], "")),
                        str(row.get(mapping["defect_type"], "")),
                        int(row.get(mapping["count"], 1)),
                        str(row.get(mapping["severity"], "Medium")),
                        str(row.get(mapping["timestamp"], datetime.datetime.now().isoformat())),
                    ],
                )
                count += 1

        conn.commit()
        return count
    finally:
        conn.close()


def _find_col(df: pd.DataFrame, candidates: List[str]) -> Optional[str]:
    """Find first matching column name (case-insensitive)."""
    for c in candidates:
        for col in df.columns:
            if c.lower() in col.lower().strip():
                return col
    return None


# ─── Template Download ─────────────────────────────────────

@app.get("/api/template/{table}")
def download_template(table: str):
    """Download CSV template for data upload."""
    templates = {
        "measurements": pd.DataFrame(columns=["Lot_ID", "Timestamp", "Parameter_Name", "Value", "Recipe"]),
        "defects": pd.DataFrame(columns=["Lot_ID", "Wafer_ID", "Defect_Type", "Count", "Severity", "Timestamp"]),
        "lots": pd.DataFrame(columns=["Lot_ID", "Product_ID", "Start_Time", "End_Time", "Status"]),
    }
    if table not in templates:
        raise HTTPException(404, f"Unknown template: {table}. Use: measurements, defects, lots")

    buf = io.BytesIO()
    templates[table].to_csv(buf, index=False)
    buf.seek(0)
    return StreamingResponse(buf, media_type="text/csv", headers={"Content-Disposition": f"attachment; filename=yms_{table}_template.csv"})


# ─── CRUD: Lots ────────────────────────────────────────────

@app.get("/api/lots")
def list_lots(status: Optional[str] = None, limit: int = 100):
    sql = "SELECT * FROM Lots"
    params = {}
    if status:
        sql += " WHERE Status = :status"
        params["status"] = status
    sql += f" ORDER BY Start_Time DESC LIMIT {limit}"
    df = run_query(sql, params if params else None)
    return df.to_dict(orient="records")


@app.get("/api/lots/{lot_id}")
def get_lot(lot_id: str):
    df = run_query("SELECT * FROM Lots WHERE Lot_ID = ?", [lot_id])
    if df.empty:
        raise HTTPException(404, f"Lot {lot_id} not found")
    md = run_query("SELECT * FROM Measurements WHERE Lot_ID = ? ORDER BY Timestamp", [lot_id])
    df_defects = run_query("SELECT * FROM Defects WHERE Lot_ID = ?", [lot_id])
    return {
        "lot": df.to_dict(orient="records")[0],
        "measurements": md.to_dict(orient="records"),
        "defects": df_defects.to_dict(orient="records"),
    }


@app.post("/api/lots")
def create_lot(lot: LotCreate):
    insert_query(
        "INSERT OR REPLACE INTO Lots (Lot_ID, Product_ID, Status) VALUES (?,?,?)",
        [lot.lot_id, lot.product_id, lot.status],
    )
    return {"status": "created", "lot_id": lot.lot_id}


# ─── CRUD: Measurements ────────────────────────────────────

@app.get("/api/measurements")
def query_measurements(
    lot_id: Optional[str] = None,
    parameter: Optional[str] = None,
    recipe: Optional[str] = None,
    limit: int = 500,
):
    sql = "SELECT * FROM Measurements WHERE 1=1"
    params = []
    if lot_id:
        sql += " AND Lot_ID = ?"
        params.append(lot_id)
    if parameter:
        sql += " AND Parameter_Name = ?"
        params.append(parameter)
    if recipe:
        sql += " AND Recipe = ?"
        params.append(recipe)
    sql += f" ORDER BY Timestamp DESC LIMIT {limit}"
    df = run_query(sql, params if params else None)
    return df.to_dict(orient="records")


@app.post("/api/measurements")
def create_measurement(m: MeasurementCreate):
    ts = m.timestamp or datetime.datetime.now().isoformat()
    insert_query(
        "INSERT INTO Measurements (Lot_ID, Timestamp, Parameter_Name, Value, Recipe) VALUES (?,?,?,?,?)",
        [m.lot_id, ts, m.parameter_name, m.value, m.recipe],
    )
    return {"status": "created"}


# ─── CRUD: Defects ─────────────────────────────────────────

@app.get("/api/defects")
def query_defects(
    lot_id: Optional[str] = None,
    defect_type: Optional[str] = None,
    severity: Optional[str] = None,
    limit: int = 500,
):
    sql = "SELECT * FROM Defects WHERE 1=1"
    params = []
    if lot_id:
        sql += " AND Lot_ID = ?"
        params.append(lot_id)
    if defect_type:
        sql += " AND Defect_Type = ?"
        params.append(defect_type)
    if severity:
        sql += " AND Severity = ?"
        params.append(severity)
    sql += f" ORDER BY Timestamp DESC LIMIT {limit}"
    df = run_query(sql, params if params else None)
    return df.to_dict(orient="records")


# ─── Analysis ──────────────────────────────────────────────

@app.get("/api/analysis/yield")
def yield_summary(lot_id: Optional[str] = None):
    """Yield summary: total, passed, yield rate."""
    sql = "SELECT Lot_ID, COUNT(*) as total_defects, SUM(Count) as defect_sum FROM Defects"
    params = []
    if lot_id:
        sql += " WHERE Lot_ID = ?"
        params.append(lot_id)
    sql += " GROUP BY Lot_ID ORDER BY Lot_ID"
    df = run_query(sql, params if params else None)
    return df.to_dict(orient="records")


@app.get("/api/analysis/pareto")
def pareto_analysis(lot_id: Optional[str] = None):
    """Pareto analysis of defect types."""
    sql = "SELECT Defect_Type, SUM(Count) as Total FROM Defects"
    params = []
    if lot_id:
        sql += " WHERE Lot_ID = ?"
        params.append(lot_id)
    sql += " GROUP BY Defect_Type ORDER BY Total DESC"
    df = run_query(sql, params if params else None)
    return df.to_dict(orient="records")


@app.get("/api/analysis/spc")
def spc_stats(
    parameter: str,
    lot_id: Optional[str] = None,
    usl: Optional[float] = None,
    lsl: Optional[float] = None,
    subgroup_size: Optional[int] = None,
):
    """Enhanced SPC analysis for a measurement parameter.

    Returns control limits, capability indices (Pp/Ppk/Cp/Cpk/PPM),
    and comprehensive alarm detection (OOC, OOS, trends, same-side runs).
    """
    params = [parameter]
    sql = "SELECT * FROM Measurements WHERE Parameter_Name = ?"
    if lot_id:
        sql += " AND Lot_ID = ?"
        params.append(lot_id)
    sql += " ORDER BY Timestamp"
    df = run_query(sql, params)
    if df.empty:
        return {"error": "No data for parameter"}

    values = df["Value"].dropna().values
    n = len(values)

    # Import SPC engine
    import importlib.util
    _spc_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                              "src", "yms", "analysis", "spc_control_charts.py")
    _spc_spec = importlib.util.spec_from_file_location("spc_control_charts", os.path.abspath(_spc_path))
    _spc_mod = importlib.util.module_from_spec(_spc_spec)
    _spc_spec.loader.exec_module(_spc_mod)
    spc = _spc_mod.SPCControlCharts()

    # Control limits
    limits = spc.calculate_control_limits(values)
    mean_v = limits["mean"]
    std_v = limits["std"]

    # Spec limits: use provided or auto-infer
    _usl = usl if usl is not None else (mean_v + 4 * std_v)
    _lsl = lsl if lsl is not None else (mean_v - 4 * std_v)

    # Capability indices
    sg = int(subgroup_size) if subgroup_size and subgroup_size >= 2 else None
    cap = spc.calculate_capability_indices(values, _usl, _lsl, subgroup_size=sg)

    # Alarm detection
    alarm_result = spc.detect_alarms(values, limits, usl=usl, lsl=lsl)

    return {
        "parameter": parameter,
        "lot_id": lot_id,
        "count": n,
        "control_limits": {
            "mean": round(mean_v, 4),
            "std": round(std_v, 4),
            "ucl": round(limits["UCL"], 4),
            "lcl": round(limits["LCL"], 4),
        },
        "capability": cap,
        "alarms": {
            "summary": alarm_result["summary"],
            "violated_rules": alarm_result["violated_rules"],
            "alarm_count": len(alarm_result["alarms"]),
            "alarms": alarm_result["alarms"],
        },
        "statistics": {
            "min": float(values.min()),
            "max": float(values.max()),
            "median": float(np.median(values)),
            "q1": float(np.percentile(values, 25)),
            "q3": float(np.percentile(values, 75)),
        },
    }


# ─── MSA / GR&R Endpoints ─────────────────────────────────

@app.get("/api/grr/studies")
def grr_studies():
    """List all GR&R studies."""
    return run_query("SELECT * FROM GRR_Studies ORDER BY Created_At DESC").to_dict(orient="records")


@app.get("/api/grr/studies/{study_id}")
def grr_study_detail(study_id: int):
    """Get single GR&R study metadata."""
    df = run_query("SELECT * FROM GRR_Studies WHERE ID = ?", [study_id])
    if df.empty:
        raise HTTPException(404, "Study not found")
    return df.iloc[0].to_dict()


@app.post("/api/grr/studies")
def grr_create_study(req: GRRStudyCreate):
    """Create a new GR&R study."""
    study_id = insert_query(
        """INSERT INTO GRR_Studies (Study_Name, Description, Method, Gauge_Name, USL, LSL, Tolerance)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (req.study_name, req.description, req.method, req.gauge_name,
         req.usl, req.lsl, req.tolerance)
    )
    return {"id": study_id, "study_name": req.study_name, "status": "created"}


@app.get("/api/grr/studies/{study_id}/measurements")
def grr_measurements(study_id: int):
    """Get all measurements for a GR&R study."""
    df = run_query(
        """SELECT Part_ID AS Part, Operator_ID AS Operator, Trial, Value
           FROM GRR_Measurements WHERE Study_ID = ? ORDER BY Part_ID, Operator_ID, Trial""",
        [study_id]
    )
    return df.to_dict(orient="records")


@app.post("/api/grr/studies/{study_id}/measurements")
def grr_add_measurements(study_id: int, measurements: List[GRRMeasurement]):
    """Add measurements to a GR&R study."""
    for m in measurements:
        insert_query(
            """INSERT INTO GRR_Measurements (Study_ID, Part_ID, Operator_ID, Trial, Value)
               VALUES (?, ?, ?, ?, ?)""",
            (study_id, m.part_id, m.operator_id, m.trial, m.value)
        )
    return {"status": "added", "count": len(measurements)}


@app.get("/api/grr/analysis/{study_id}")
def grr_analysis(study_id: int, method: Optional[str] = None):
    """Run full GR&R analysis for a study."""
    study_df = run_query("SELECT * FROM GRR_Studies WHERE ID = ?", [study_id])
    if study_df.empty:
        raise HTTPException(404, "Study not found")
    srow = study_df.iloc[0]

    df = run_query(
        """SELECT Part_ID AS Part, Operator_ID AS Operator, Trial, Value
           FROM GRR_Measurements WHERE Study_ID = ? ORDER BY Part_ID, Operator_ID, Trial""",
        [study_id]
    )
    if df.empty:
        raise HTTPException(400, "No measurement data for this study")

    import importlib.util
    _msa_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                              "src", "yms", "analysis", "msa_gauge_rr.py")
    _msa_spec = importlib.util.spec_from_file_location("msa_gauge_rr", os.path.abspath(_msa_path))
    _msa_mod = importlib.util.module_from_spec(_msa_spec)
    _msa_spec.loader.exec_module(_msa_mod)
    msa = _msa_mod.MSAGaugeRR()

    use_method = method or srow.get("Method", "ANOVA")
    usl = srow.get("USL")
    lsl = srow.get("LSL")
    tol = srow.get("Tolerance")

    result = msa.analyze(df, method=use_method, usl=usl, lsl=lsl, tolerance=tol)

    return {
        "study_id": study_id,
        "study_name": srow["Study_Name"],
        "method": result.method,
        "n_parts": result.n_parts,
        "n_operators": result.n_operators,
        "n_trials": result.n_trials,
        "n_measurements": len(df),
        "variance_components": {
            "repeatability": result.var_repeatability,
            "reproducibility": result.var_reproducibility,
            "operator": result.var_operator,
            "interaction": result.var_interaction,
            "grr": result.var_grr,
            "part": result.var_part,
            "total": result.var_total,
        },
        "standard_deviations": {
            "repeatability": result.sigma_repeatability,
            "reproducibility": result.sigma_reproducibility,
            "grr": result.sigma_grr,
            "part": result.sigma_part,
            "total": result.sigma_total,
        },
        "pct_study_variation": {
            "repeatability": result.pct_repeatability,
            "reproducibility": result.pct_reproducibility,
            "grr": result.pct_grr,
            "part": result.pct_part,
        },
        "pct_tolerance": {
            "repeatability": result.pct_tol_repeatability,
            "reproducibility": result.pct_tol_reproducibility,
            "grr": result.pct_tol_grr,
            "part": result.pct_tol_part,
        },
        "ndc": result.ndc,
        "grade_grr": result.grade_grr,
        "grade_ndc": result.grade_ndc,
    }


# ─── Correlation Analysis Endpoint ────────────────────────

@app.get("/api/analysis/correlation")
def correlation_analysis(
    method: str = "spearman",
    min_corr: float = 0.3,
    max_p: float = 0.05,
):
    """Correlation analysis between measurement parameters and yield."""
    import importlib.util

    # Load measurements pivoted
    raw = run_query(
        """SELECT Lot_ID, Parameter_Name, AVG(Value) as Mean_Value
           FROM Measurements GROUP BY Lot_ID, Parameter_Name ORDER BY Lot_ID"""
    )
    if raw.empty:
        return {"error": "No measurement data"}

    df = raw.pivot(index="Lot_ID", columns="Parameter_Name", values="Mean_Value").reset_index()
    lots = run_query("SELECT Lot_ID, Yield FROM Lots")
    if not lots.empty:
        df = df.merge(lots[["Lot_ID", "Yield"]], on="Lot_ID", how="left")
        df["Yield"] = df["Yield"].fillna(0.85)

    numeric_cols = [c for c in df.columns if c not in ("Lot_ID",) and df[c].dtype in ("float64", "int64")]
    yield_col = "Yield" if "Yield" in df.columns else numeric_cols[-1]
    param_cols = [c for c in numeric_cols if c != yield_col]

    _eng_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                              "src", "yms", "analysis", "correlation_engine.py")
    _spec = importlib.util.spec_from_file_location("correlation_engine", os.path.abspath(_eng_path))
    _mod = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_mod)
    eng = _mod.CorrelationAnalysis()

    ranking = eng.analyze(df, param_cols, yield_col, method=method)
    key_params = eng.find_key_params(ranking, min_corr=min_corr, max_p=max_p)

    return {
        "method": method,
        "n_parameters": len(param_cols),
        "yield_column": yield_col,
        "n_lots": len(df),
        "ranking": ranking.to_dict(orient="records"),
        "key_parameters": key_params.to_dict(orient="records") if len(key_params) > 0 else [],
    }


# ─── Yield Analysis Endpoint ───────────────────────────────

@app.get("/api/analysis/yield-detail")
def yield_detail_analysis(
    dice_per_wafer: int = 1000,
    wafers_per_lot: int = 25,
):
    """Full yield analysis: Pareto, loss decomposition, density trend, kill ratio."""
    import importlib.util

    lots_df = run_query("SELECT * FROM Lots")
    defects_df = run_query("SELECT * FROM Defects")

    _eng_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                              "src", "yms", "analysis", "yield_analysis.py")
    _spec = importlib.util.spec_from_file_location("yield_analysis", os.path.abspath(_eng_path))
    _mod = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_mod)
    eng = _mod.YieldAnalysis()

    report = eng.analyze(lots_df, defects_df,
                          total_dice_per_wafer=dice_per_wafer,
                          n_wafers_per_lot=wafers_per_lot)

    return {
        "total_lots": report.total_lots,
        "total_defects": report.total_defects,
        "overall_yield": round(report.overall_yield, 1),
        "kill_ratio": report.kill_ratio,
        "pareto": report.pareto_df.to_dict(orient="records") if report.pareto_df is not None else [],
        "yield_loss_by_type": report.loss_by_type.to_dict(orient="records") if report.loss_by_type is not None else [],
        "density_trend": report.density_trend.to_dict(orient="records") if report.density_trend is not None else [],
        "kill_by_type": report.kill_by_type.to_dict(orient="records") if report.kill_by_type is not None else [],
    }


# ─── SQL Query (read-only + sandboxed) ─────────────────────

READONLY_TABLES = {"Lots", "Measurements", "Defects", "DOE_Experiments", "GRR_Studies", "GRR_Measurements"}


@app.post("/api/query")
def execute_query(req: QueryRequest):
    """Execute a read-only SQL query against the YMS database."""
    sql = req.sql.strip().upper()
    # Block dangerous operations
    dangerous = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "CREATE", "VACUUM", "ATTACH"]
    for kw in dangerous:
        if sql.startswith(kw):
            raise HTTPException(403, f"Read-only queries only. Detected: {kw}")

    try:
        df = run_query(req.sql)
        return {"columns": list(df.columns), "rows": df.to_dict(orient="records"), "count": len(df)}
    except Exception as e:
        raise HTTPException(400, str(e))


# ─── Process Flow API ──────────────────────────────────────

@app.get("/api/process-flow")
def get_process_flow(flow_id: str = None):
    """获取工艺流程数据"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        if flow_id:
            cursor.execute("""
                SELECT Flow_ID, Route_ID, Step_ID, Step_Description, Target, 
                       Recipe_ID, Equipment_Group, EDC_Param_Set, QTime, Seq_No
                FROM Process_Flow WHERE Flow_ID = ? ORDER BY Seq_No
            """, (flow_id,))
        else:
            cursor.execute("""
                SELECT Flow_ID, Route_ID, Step_ID, Step_Description, Target,
                       Recipe_ID, Equipment_Group, EDC_Param_Set, QTime, Seq_No
                FROM Process_Flow ORDER BY Seq_No
            """)
        
        rows = cursor.fetchall()
        result = []
        for r in rows:
            result.append({
                "flow_id": r[0], "route": r[1], "step_id": r[2],
                "description": r[3], "target": r[4] or "",
                "recipe_id": r[5] or "", "equip_group": r[6] or "",
                "edc_param_set": r[7] or "", "qtime": r[8] or "",
                "seq_no": r[9]
            })
        return {"status": "ok", "count": len(result), "data": result}
    finally:
        conn.close()


@app.get("/api/process-flow/routes")
def get_process_flow_routes(flow_id: str = None):
    """获取工艺流程路径列表"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        if flow_id:
            cursor.execute("""
                SELECT Route_ID, COUNT(*) as step_count 
                FROM Process_Flow 
                WHERE Flow_ID = ? AND Route_ID != ''
                GROUP BY Route_ID ORDER BY Route_ID
            """, (flow_id,))
        else:
            cursor.execute("""
                SELECT Route_ID, COUNT(*) as step_count 
                FROM Process_Flow 
                WHERE Route_ID != ''
                GROUP BY Route_ID ORDER BY Route_ID
            """)
        routes = [{"route": r[0], "steps": r[1]} for r in cursor.fetchall()]
        return {"status": "ok", "count": len(routes), "routes": routes}
    finally:
        conn.close()


# ─── Main ──────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    init_db()
    print("Starting YMS API on http://0.0.0.0:8000")
    print("Docs: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
