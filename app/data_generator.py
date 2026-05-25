import pandas as pd
import numpy as np
import datetime

def generate_trend_data():
    """Generate consistent trend data for SPC analysis."""
    np.random.seed(42)
    dates = pd.date_range(start="2026-04-01", periods=100, freq="H")
    data = {
        "Date": dates,
        "Etch Rate (A/min)": np.random.normal(1000, 15, 100),
        "Pressure (mTorr)": np.random.normal(50, 0.5, 100),
        "CD (nm)": np.random.normal(45, 0.3, 100),
        "Thickness (A)": np.random.normal(5000, 20, 100),
        "Recipe": np.random.choice(["ETCH_001", "ETCH_002"], 100)
    }
    df = pd.DataFrame(data)
    # Inject OOC
    df.loc[20, "Etch Rate (A/min)"] = 1060
    df.loc[80, "Pressure (mTorr)"] = 48.0
    return df

def generate_lot_data(lot_id="LOT-2026-001"):
    """Generate Gantt chart data for a specific lot."""
    np.random.seed(hash(lot_id) % 2**32)
    steps = ["Oxidation", "Lithography", "Etch", "Deposition", "CMP", "Metrology"]
    base_time = datetime.datetime(2026, 4, 20, 8, 0, 0)
    current_time = base_time
    data = []
    for i, step in enumerate(steps):
        process_time = pd.Timedelta(hours=np.random.uniform(1, 4))
        wait_time = pd.Timedelta(hours=np.random.uniform(0, 2))
        if i == 3: # Bottleneck
            wait_time += pd.Timedelta(hours=5)
        start = current_time
        end = start + process_time + wait_time
        data.append({
            "Step": step,
            "Start Time": start,
            "End Time": end,
            "Process Time": process_time,
            "Wait Time": wait_time,
            "Status": "Completed"
        })
        current_time = end + pd.Timedelta(minutes=np.random.uniform(15, 60))
    return pd.DataFrame(data)

def generate_doe_data(num_factors=2):
    """Generate DOE data."""
    np.random.seed(42)
    levels = [-1, 1]
    factors = [f"Factor_{i+1}" for i in range(num_factors)]
    design = list(__import__('itertools').product(levels, repeat=num_factors))
    df = pd.DataFrame(design, columns=factors)
    # Response model with interaction
    y = 50 + 10 * df[factors[0]] + 5 * df[factors[1]] 
    if len(factors) > 1:
        y += 8 * df[factors[0]] * df[factors[1]]
    y += np.random.normal(0, 1, len(df))
    df["Response"] = y
    return df

def generate_dashboard_data():
    """Generate high-level dashboard metrics."""
    dates = pd.date_range(start="2026-04-10", periods=10, freq="D")
    return pd.DataFrame({
        "Date": dates,
        "Yield (%)": np.random.normal(92, 1, 10),
        "Defect Density": np.random.normal(0.4, 0.05, 10)
    })
