"""
YMS DOE Enhanced Module v2.0
JMP-style Design of Experiments: Design generation, ANOVA, effect screening,
residual diagnostics, response surface, prediction profiler.

Supports: Full Factorial, Fractional Factorial, Plackett-Burman,
          Central Composite (CCD), Box-Behnken, D-Optimal
"""
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from itertools import product, combinations
from scipy import stats
from scipy.linalg import lstsq
import streamlit as st
import json


# ═══════════════════════════════════════════════════════════
#  DESIGN GENERATORS
# ═══════════════════════════════════════════════════════════

def generate_full_factorial(n_factors: int, center_points: int = 0,
                            replicates: int = 1, factor_names: list = None):
    """2^k full factorial with optional center points and replicates."""
    if factor_names is None:
        factor_names = [f"X{i+1}" for i in range(n_factors)]
    levels = [-1, 1]
    base = list(product(levels, repeat=n_factors))
    # Replicates
    runs = base * replicates
    # Center points
    for _ in range(center_points):
        runs.append(tuple([0] * n_factors))
    df = pd.DataFrame(runs, columns=factor_names)
    df["RunOrder"] = np.random.permutation(len(df))
    df = df.sort_values("RunOrder").reset_index(drop=True)
    df["StdOrder"] = range(1, len(df) + 1)
    return df


def generate_fractional_factorial(n_factors: int, resolution: str = "V",
                                   factor_names: list = None):
    """2^(k-p) fractional factorial using generator-based aliasing.
    Resolution III/IV/V supported for k <= 8."""
    if factor_names is None:
        factor_names = [f"X{i+1}" for i in range(n_factors)]

    # Use standard generator tables from Montgomery
    generators = {
        3: {"III": ("C", "AB"), "IV": None, "V": None},
        4: {"III": ("D", "AB"), "IV": ("D", "ABC"), "V": None},
        5: {"III": ("E", "AB"), "IV": ("E", "ABCD"), "V": ("E", "ABC")},
        6: {"III": ("F", "AB"), "IV": ("F", "ABCD"), "V": ("F", "ABC")},
        7: {"III": ("G", "AB"), "IV": ("G", "ABCD"), "V": ("G", "ABCDE")},
        8: {"III": ("H", "AB"), "IV": ("H", "ABCD"), "V": ("H", "ABCDE")},
    }

    if n_factors < 3:
        return generate_full_factorial(n_factors, factor_names=factor_names)

    gen_info = generators.get(n_factors, {}).get(resolution)
    if gen_info is None:
        # Fallback: use full factorial
        return generate_full_factorial(n_factors, factor_names=factor_names)

    gen_name, alias = gen_info
    base_k = ord(gen_name) - ord('A')  # e.g. 'E' -> 4 (factors A,B,C,D)

    # Generate base factorial (k-1 factors)
    base_runs = list(product([-1, 1], repeat=base_k))
    runs = []
    for r in base_runs:
        row = list(r)
        # Compute generator column
        sign = 1
        for ch in alias:
            idx = ord(ch) - ord('A')
            if idx < len(r):
                sign *= r[idx]
        row.append(sign)
        runs.append(tuple(row))

    df = pd.DataFrame(runs, columns=[chr(65+i) for i in range(n_factors)])
    # Rename to X1, X2, ...
    mapping = {chr(65+i): factor_names[i] for i in range(n_factors)}
    df.rename(columns=mapping, inplace=True)
    df["RunOrder"] = np.random.permutation(len(df))
    df = df.sort_values("RunOrder").reset_index(drop=True)
    df["StdOrder"] = range(1, len(df) + 1)
    return df


def generate_plackett_burman(n_runs: int, factor_names: list = None):
    """Plackett-Burman screening design. n_runs must be multiple of 4."""
    # Standard PB design generators (first row for N=12)
    pb_generators = {
        8:  [1, 1, 1, -1, 1, -1, -1],
        12: [1, 1, -1, 1, 1, 1, -1, -1, -1, 1, -1],
        16: [1, 1, 1, 1, -1, 1, -1, 1, 1, -1, -1, 1, -1, -1, -1],
        20: [1, 1, -1, -1, 1, 1, 1, 1, -1, 1, -1, 1, -1, -1, -1, -1, 1, 1, -1],
        24: [1, 1, 1, 1, 1, -1, 1, -1, 1, 1, -1, -1, 1, 1, -1, -1, 1, -1, 1, -1, -1, -1, -1],
    }
    n_runs = max(8, n_runs)
    n_runs = ((n_runs + 3) // 4) * 4  # round up to multiple of 4
    if n_runs > 24:
        n_runs = 24

    n_factors = n_runs - 1
    if factor_names is None:
        factor_names = [f"X{i+1}" for i in range(n_factors)]

    gen = pb_generators.get(n_runs, pb_generators[12])
    gen = gen[:n_factors]

    # Cyclic generation
    design = [gen]
    for i in range(1, n_runs - 1):
        row = [gen[-1]] + gen[:-1]
        design.append(row)
        gen = row
    # Last row: all -1
    design.append([-1] * n_factors)

    df = pd.DataFrame(design, columns=factor_names[:n_factors])
    df["RunOrder"] = np.random.permutation(len(df))
    df = df.sort_values("RunOrder").reset_index(drop=True)
    df["StdOrder"] = range(1, len(df) + 1)
    return df


def generate_ccd(n_factors: int, alpha: str = "rotatable",
                 center_points: int = 2, factor_names: list = None):
    """Central Composite Design: 2^k factorial + axial points + center."""
    if factor_names is None:
        factor_names = [f"X{i+1}" for i in range(n_factors)]

    if alpha == "rotatable":
        a = 2 ** (n_factors / 4)
    elif alpha == "spherical":
        a = np.sqrt(n_factors)
    else:  # face-centered
        a = 1.0

    # Factorial portion
    factorial = list(product([-1, 1], repeat=n_factors))
    runs = [list(r) for r in factorial]

    # Axial points
    for i in range(n_factors):
        row = [0] * n_factors
        row[i] = a
        runs.append(row)
        row2 = [0] * n_factors
        row2[i] = -a
        runs.append(row2)

    # Center points
    for _ in range(center_points):
        runs.append([0] * n_factors)

    df = pd.DataFrame(runs, columns=factor_names)
    df["RunOrder"] = np.random.permutation(len(df))
    df = df.sort_values("RunOrder").reset_index(drop=True)
    df["StdOrder"] = range(1, len(df) + 1)
    # Normalize axial points back to coded units for display
    for col in factor_names:
        df[col] = df[col].round(4)
    return df, {"alpha": a, "design_type": f"CCD ({alpha})"}


def generate_box_behnken(n_factors: int, center_points: int = 2,
                          factor_names: list = None):
    """Box-Behnken design for 3-7 factors."""
    if factor_names is None:
        factor_names = [f"X{i+1}" for i in range(n_factors)]
    if n_factors < 3:
        n_factors = 3

    runs = []
    # All 2-factor combinations at ±1, others at 0
    for i, j in combinations(range(n_factors), 2):
        for vi, vj in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
            row = [0] * n_factors
            row[i] = vi
            row[j] = vj
            runs.append(row)

    # Center points
    for _ in range(center_points):
        runs.append([0] * n_factors)

    df = pd.DataFrame(runs, columns=factor_names)
    df["RunOrder"] = np.random.permutation(len(df))
    df = df.sort_values("RunOrder").reset_index(drop=True)
    df["StdOrder"] = range(1, len(df) + 1)
    return df


# ═══════════════════════════════════════════════════════════
#  MODEL FITTING & ANOVA
# ═══════════════════════════════════════════════════════════

def build_model_matrix(df: pd.DataFrame, factor_cols: list,
                       include_2fi: bool = True, include_quadratic: bool = False):
    """Build design matrix with intercept, main effects, 2FIs, optional quadratics."""
    X_mat = df[factor_cols].values
    terms = ["Intercept"]
    cols = [np.ones(len(df))]

    # Main effects
    for col in factor_cols:
        terms.append(col)
        cols.append(X_mat[:, factor_cols.index(col)])

    # Two-factor interactions
    if include_2fi and len(factor_cols) >= 2:
        for i, j in combinations(range(len(factor_cols)), 2):
            name = f"{factor_cols[i]}×{factor_cols[j]}"
            terms.append(name)
            cols.append(X_mat[:, i] * X_mat[:, j])

    # Quadratic terms
    if include_quadratic:
        for col in factor_cols:
            terms.append(f"{col}²")
            cols.append(X_mat[:, factor_cols.index(col)] ** 2)

    X = np.column_stack(cols)
    return X, terms


def fit_doe_model(df: pd.DataFrame, factor_cols: list, response_col: str = "Response",
                  include_2fi: bool = True, include_quadratic: bool = False):
    """Fit linear model and return comprehensive ANOVA + effect statistics.

    Returns dict with: coefficients, ANOVA table, effects, R², adjusted R²,
    predicted R² (PRESS), half-normal effects, model matrix.
    """
    X, terms = build_model_matrix(df, factor_cols, include_2fi, include_quadratic)
    y = df[response_col].values
    n, p = X.shape

    # Least squares fit
    coeffs, residuals, rank, singular = lstsq(X, y)
    y_pred = X @ coeffs
    residuals_vec = y - y_pred

    # Sum of squares
    ss_total = np.sum((y - y.mean()) ** 2)
    ss_regression = np.sum((y_pred - y.mean()) ** 2)
    ss_residual = np.sum(residuals_vec ** 2)

    # Degrees of freedom
    df_reg = p - 1
    df_res = n - p
    df_tot = n - 1

    # Mean squares
    ms_reg = ss_regression / df_reg if df_reg > 0 else 0
    ms_res = ss_residual / df_res if df_res > 0 else 0

    # F-statistic & p-value
    f_val = ms_reg / ms_res if ms_res > 0 else 0
    f_p = 1 - stats.f.cdf(f_val, df_reg, df_res) if ms_res > 0 else 1

    # R²
    r2 = 1 - ss_residual / ss_total if ss_total > 0 else 0
    r2_adj = 1 - (1 - r2) * (n - 1) / (n - p) if n > p else 0

    # Standard errors, t-stats, p-values per coefficient
    XtX_inv = np.linalg.pinv(X.T @ X)
    se = np.sqrt(np.maximum(np.diag(XtX_inv) * ms_res, 0))

    t_stats = coeffs / np.maximum(se, 1e-15)
    p_values = 2 * (1 - stats.t.cdf(np.abs(t_stats), df_res))
    # VIF
    vif = np.full(p, np.nan)
    for i in range(1, p):  # skip intercept
        mask = np.ones(p, dtype=bool)
        mask[i] = False
        if np.sum(mask) > 1:
            X_rest = X[:, mask]
            r2_i = 1 - np.sum((X[:, i] - X_rest @ lstsq(X_rest, X[:, i])[0]) ** 2) / \
                   np.sum((X[:, i] - X[:, i].mean()) ** 2) if np.sum((X[:, i] - X[:, i].mean()) ** 2) > 0 else 0
            vif[i] = 1 / (1 - r2_i) if r2_i < 1 else np.inf

    coeff_table = pd.DataFrame({
        "Term": terms,
        "Coef": coeffs.round(4),
        "SE": se.round(4),
        "t": t_stats.round(3),
        "p": p_values.round(4),
        "VIF": vif.round(2),
    })
    coeff_table["Sig"] = coeff_table["p"].apply(
        lambda x: "***" if x < 0.001 else ("**" if x < 0.01 else ("*" if x < 0.05 else ""))
    )

    # Effects (2 * coefficient for coded -1/+1 factors, except intercept and quadratics)
    effects = []
    for i, term in enumerate(terms):
        if term == "Intercept":
            effects.append({"Term": term, "Effect": coeffs[i]})
        elif "²" in term:
            effects.append({"Term": term, "Effect": coeffs[i]})
        else:
            effects.append({"Term": term, "Effect": 2 * coeffs[i]})

    effects_df = pd.DataFrame(effects)

    # ANOVA table
    anova = pd.DataFrame([
        {"Source": "Model", "SS": round(ss_regression, 2), "df": df_reg,
         "MS": round(ms_reg, 2), "F": round(f_val, 2), "p": round(f_p, 4)},
        {"Source": "Residual", "SS": round(ss_residual, 2), "df": df_res,
         "MS": round(ms_res, 2), "F": "", "p": ""},
        {"Source": "Total", "SS": round(ss_total, 2), "df": df_tot,
         "MS": "", "F": "", "p": ""},
    ])

    # PRESS (leave-one-out cross-validation)
    press = 0
    for i in range(n):
        mask = np.ones(n, dtype=bool)
        mask[i] = False
        X_loo = X[mask]
        y_loo = y[mask]
        b_loo = lstsq(X_loo, y_loo)[0]
        e_i = y[i] - X[i] @ b_loo
        press += e_i ** 2
    r2_pred = 1 - press / ss_total if ss_total > 0 else 0

    return {
        "coefficients": coeff_table,
        "anova": anova,
        "effects": effects_df,
        "r2": r2,
        "r2_adj": r2_adj,
        "r2_pred": r2_pred,
        "n": n,
        "p": p,
        "X": X,
        "y": y,
        "y_pred": y_pred,
        "residuals": residuals_vec,
        "terms": terms,
        "factor_cols": factor_cols,
        "X_mat": X,
        "coeffs_raw": coeffs,
    }


# ═══════════════════════════════════════════════════════════
#  VISUALIZATION FUNCTIONS
# ═══════════════════════════════════════════════════════════

def plot_half_normal(effects_df: pd.DataFrame):
    """Half-normal probability plot of effects (JMP-style)."""
    eff = effects_df[effects_df["Term"] != "Intercept"]["Effect"].abs().sort_values().values
    n = len(eff)
    if n == 0:
        return go.Figure()

    # Half-normal quantiles
    ranks = np.arange(1, n + 1)
    quantiles = stats.halfnorm.ppf((ranks - 0.5) / n)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=quantiles, y=eff,
        mode="markers+text",
        text=effects_df[effects_df["Term"] != "Intercept"]["Term"].values[
            np.argsort(effects_df[effects_df["Term"] != "Intercept"]["Effect"].abs().values)
        ],
        textposition="top center",
        marker=dict(size=10, color=["red" if e > np.percentile(eff, 50) else "steelblue" for e in eff]),
        name="Effects"
    ))
    # Reference line
    fig.add_trace(go.Scatter(
        x=[0, max(quantiles) * 1.1], y=[0, 0],
        mode="lines", line=dict(color="gray", dash="dash"), showlegend=False
    ))
    # Lenth's PSE line (approximation)
    if n >= 3:
        sorted_eff = np.sort(eff)
        s0 = 1.5 * np.median(sorted_eff)
        pse = 1.5 * np.median(sorted_eff[sorted_eff < 2.5 * s0]) if np.any(sorted_eff < 2.5 * s0) else s0
        fig.add_hline(y=pse * stats.t.ppf(0.975, n//3), line_dash="dot",
                      line_color="orange", annotation_text="ME (Lenth)")

    fig.update_layout(
        title="Half-Normal Plot of Effects",
        xaxis_title="Half-Normal Quantiles",
        yaxis_title="|Effect|",
        height=400,
    )
    return fig


def plot_pareto_effects(effects_df: pd.DataFrame):
    """Pareto chart of standardized effects."""
    eff = effects_df[effects_df["Term"] != "Intercept"].copy()
    eff["AbsEffect"] = eff["Effect"].abs()
    eff = eff.sort_values("AbsEffect", ascending=True)

    fig = go.Figure()
    colors = ["#e74c3c" if v > 0 else "#3498db" for v in eff["Effect"]]
    fig.add_trace(go.Bar(
        y=eff["Term"], x=eff["AbsEffect"],
        orientation="h", marker_color=colors,
        text=eff["Effect"].round(3), textposition="outside",
    ))
    # Bonferroni limit line
    t_crit = stats.t.ppf(1 - 0.025 / len(eff), max(len(eff), 2))
    fig.add_vline(x=t_crit, line_dash="dash", line_color="red",
                  annotation_text=f"t={t_crit:.2f}")
    fig.update_layout(
        title="Pareto Chart of Effects",
        xaxis_title="|Effect|", yaxis_title="",
        height=max(300, len(eff) * 30),
        showlegend=False,
    )
    return fig


def plot_interaction(df: pd.DataFrame, factor_cols: list, response_col: str = "Response"):
    """Interaction plots for all 2-factor pairs."""
    if len(factor_cols) < 2:
        return go.Figure()

    pairs = list(combinations(factor_cols, 2))
    n_pairs = len(pairs)
    n_cols = min(3, n_pairs)
    n_rows = (n_pairs + n_cols - 1) // n_cols

    fig = make_subplots(rows=n_rows, cols=n_cols,
                        subplot_titles=[f"{a} × {b}" for a, b in pairs])

    for idx, (f1, f2) in enumerate(pairs):
        row = idx // n_cols + 1
        col = idx % n_cols + 1
        # Group by both factors
        for level in sorted(df[f1].unique()):
            subset = df[df[f1] == level]
            means = subset.groupby(f2)[response_col].mean()
            fig.add_trace(
                go.Scatter(x=list(means.index), y=means.values, mode="lines+markers",
                           name=f"{f1}={level}", legendgroup=f"{f1}",
                           showlegend=(idx == 0)),
                row=row, col=col
            )
    fig.update_layout(height=300 * n_rows, title="Interaction Plots")
    return fig


def plot_contour(model_result: dict, x_factor: str, y_factor: str):
    """Contour plot for two factors (hold others at 0)."""
    factor_cols = model_result["factor_cols"]
    terms = model_result["terms"]
    coeffs = model_result["coeffs_raw"]

    xi = factor_cols.index(x_factor)
    yi = factor_cols.index(y_factor)

    grid_size = 50
    x_range = np.linspace(-1.5, 1.5, grid_size)
    y_range = np.linspace(-1.5, 1.5, grid_size)
    xx, yy = np.meshgrid(x_range, y_range)

    zz = np.zeros_like(xx)
    # Intercept
    zz += coeffs[0]
    # Main effects
    for i, col in enumerate(factor_cols):
        idx = terms.index(col)
        if col == x_factor:
            zz += coeffs[idx] * xx
        elif col == y_factor:
            zz += coeffs[idx] * yy

    # 2FIs
    for term, coef in zip(terms, coeffs):
        if "×" in term:
            parts = term.split("×")
            if set(parts) == {x_factor, y_factor}:
                zz += coef * xx * yy

    fig = go.Figure()
    fig.add_trace(go.Contour(
        x=x_range, y=y_range, z=zz,
        colorscale="RdBu_r", contours=dict(showlabels=True),
        colorbar=dict(title="Response"),
    ))
    # Design points
    fig.add_trace(go.Scatter(
        x=model_result["X"][:, xi + 1], y=model_result["X"][:, yi + 1],
        mode="markers", marker=dict(color="black", size=6, symbol="x"),
        name="Design Points",
    ))
    fig.update_layout(
        title=f"Contour Plot: {x_factor} × {y_factor}",
        xaxis_title=x_factor, yaxis_title=y_factor,
        height=450,
    )
    return fig


def plot_surface(model_result: dict, x_factor: str, y_factor: str):
    """3D response surface plot."""
    factor_cols = model_result["factor_cols"]
    terms = model_result["terms"]
    coeffs = model_result["coeffs_raw"]

    xi = factor_cols.index(x_factor)
    yi = factor_cols.index(y_factor)

    grid_size = 40
    x_range = np.linspace(-1.5, 1.5, grid_size)
    y_range = np.linspace(-1.5, 1.5, grid_size)
    xx, yy = np.meshgrid(x_range, y_range)

    zz = np.zeros_like(xx)
    zz += coeffs[0]
    for i, col in enumerate(factor_cols):
        idx = terms.index(col)
        if col == x_factor:
            zz += coeffs[idx] * xx
        elif col == y_factor:
            zz += coeffs[idx] * yy
    for term, coef in zip(terms, coeffs):
        if "×" in term and set(term.split("×")) == {x_factor, y_factor}:
            zz += coef * xx * yy

    fig = go.Figure()
    fig.add_trace(go.Surface(
        x=x_range, y=y_range, z=zz,
        colorscale="RdBu_r", opacity=0.85,
    ))
    fig.update_layout(
        title=f"Response Surface: {x_factor} × {y_factor}",
        scene=dict(
            xaxis_title=x_factor, yaxis_title=y_factor, zaxis_title="Response"
        ),
        height=500,
    )
    return fig


def plot_residual_diagnostics(model_result: dict):
    """Residual diagnostic plots: normal Q-Q, residuals vs predicted, residuals vs run order."""
    residuals = model_result["residuals"]
    y_pred = model_result["y_pred"]
    n = len(residuals)

    fig = make_subplots(rows=1, cols=3,
                        subplot_titles=["Normal Q-Q Plot", "Residuals vs Predicted", "Residuals vs Run Order"])

    # Normal Q-Q
    sorted_res = np.sort(residuals)
    quantiles = stats.norm.ppf((np.arange(1, n + 1) - 0.5) / n)
    fig.add_trace(go.Scatter(x=quantiles, y=sorted_res, mode="markers",
                             marker=dict(size=6), name="Q-Q"), row=1, col=1)
    # Reference line
    slope, intercept = np.polyfit(quantiles, sorted_res, 1)
    x_line = np.array([min(quantiles), max(quantiles)])
    fig.add_trace(go.Scatter(x=x_line, y=slope * x_line + intercept,
                             mode="lines", line=dict(color="red", dash="dash"),
                             showlegend=False), row=1, col=1)

    # Residuals vs Predicted
    fig.add_trace(go.Scatter(x=y_pred, y=residuals, mode="markers",
                             marker=dict(size=6), name="Res vs Pred"), row=1, col=2)
    fig.add_hline(y=0, line_dash="dash", line_color="gray", row=1, col=2)

    # Residuals vs Run Order
    fig.add_trace(go.Scatter(x=list(range(1, n + 1)), y=residuals, mode="lines+markers",
                             marker=dict(size=6), name="Run Order"), row=1, col=3)
    fig.add_hline(y=0, line_dash="dash", line_color="gray", row=1, col=3)

    fig.update_layout(height=350, showlegend=False,
                      title="Residual Diagnostics")
    return fig


def plot_prediction_profiler(model_result: dict, default_settings: dict = None):
    """Interactive prediction profiler with sliders (Streamlit-native, not Plotly)."""
    # This function returns HTML/JS data for Streamlit to render interactively
    factor_cols = model_result["factor_cols"]
    terms = model_result["terms"]
    coeffs = model_result["coeffs_raw"]

    if default_settings is None:
        default_settings = {c: 0.0 for c in factor_cols}

    return {
        "factors": factor_cols,
        "terms": terms,
        "coeffs": [float(c) for c in coeffs],
        "defaults": default_settings,
    }


def make_prediction(model_result: dict, settings: dict) -> float:
    """Compute prediction from model given factor settings."""
    terms = model_result["terms"]
    coeffs = model_result["coeffs_raw"]
    factor_cols = model_result["factor_cols"]

    pred = coeffs[0]  # intercept
    for i, col in enumerate(factor_cols):
        idx = terms.index(col)
        pred += coeffs[idx] * settings[col]

    for term, coef in zip(terms, coeffs):
        if "×" in term:
            a, b = term.split("×")
            pred += coef * settings[a] * settings[b]
        if "²" in term:
            col = term.replace("²", "")
            pred += coef * settings[col] ** 2

    return pred


# ═══════════════════════════════════════════════════════════
#  STREAMLIT UI
# ═══════════════════════════════════════════════════════════

def render_doe_page(db_run_query=None, db_insert_query=None):
    """Render the complete DOE page. Pass DB functions from main.py for persistence."""
    st.title("🧪 Design of Experiments (DOE)")

    # ═══ Workflow State ═══
    if "doe_design" not in st.session_state:
        st.session_state.doe_design = None
    if "doe_response" not in st.session_state:
        st.session_state.doe_response = None
    if "doe_result" not in st.session_state:
        st.session_state.doe_result = None
    if "doe_factor_cols" not in st.session_state:
        st.session_state.doe_factor_cols = None

    # ═══ SIDEBAR: Design Type ═══
    st.sidebar.header("🔧 DOE Workflow")

    design_type = st.sidebar.selectbox("Design Type", [
        "Full Factorial (2^k)",
        "Fractional Factorial (2^(k-p))",
        "Plackett-Burman (Screening)",
        "Central Composite (CCD)",
        "Box-Behnken",
    ])

    if design_type == "Full Factorial (2^k)":
        k = st.sidebar.slider("Number of Factors (k)", 2, 6, 3)
        cp = st.sidebar.slider("Center Points", 0, 5, 2)
        reps = st.sidebar.slider("Replicates", 1, 3, 1)

        factor_names = []
        st.sidebar.caption("Factor Names (optional)")
        for i in range(k):
            name = st.sidebar.text_input(f"Factor {i+1}", f"X{i+1}", key=f"ff_name_{i}")
            factor_names.append(name)

        if st.sidebar.button("📐 Generate Design", type="primary"):
            df = generate_full_factorial(k, cp, reps, factor_names)
            st.session_state.doe_design = df
            st.session_state.doe_factor_cols = factor_names
            st.session_state.doe_response = None
            st.session_state.doe_result = None
            st.rerun()

    elif design_type == "Fractional Factorial (2^(k-p))":
        k = st.sidebar.slider("Number of Factors (k)", 3, 8, 5)
        res = st.sidebar.selectbox("Resolution", ["III", "IV", "V"], index=1)
        factor_names = []
        st.sidebar.caption("Factor Names (optional)")
        for i in range(k):
            name = st.sidebar.text_input(f"Factor {i+1}", f"X{i+1}", key=f"ffrac_name_{i}")
            factor_names.append(name)

        if st.sidebar.button("📐 Generate Design", type="primary"):
            df = generate_fractional_factorial(k, res, factor_names)
            st.session_state.doe_design = df
            st.session_state.doe_factor_cols = factor_names
            st.session_state.doe_response = None
            st.session_state.doe_result = None
            st.rerun()

    elif design_type == "Plackett-Burman (Screening)":
        n_runs = st.sidebar.selectbox("Number of Runs", [8, 12, 16, 20, 24], index=1)
        n_factors = n_runs - 1
        st.sidebar.caption(f"Factors: {n_factors}")
        factor_names = []
        for i in range(n_factors):
            name = st.sidebar.text_input(f"Factor {i+1}", f"X{i+1}", key=f"pb_name_{i}")
            factor_names.append(name)

        if st.sidebar.button("📐 Generate Design", type="primary"):
            df = generate_plackett_burman(n_runs, factor_names)
            st.session_state.doe_design = df
            st.session_state.doe_factor_cols = factor_names[:n_factors]
            st.session_state.doe_response = None
            st.session_state.doe_result = None
            st.rerun()

    elif design_type == "Central Composite (CCD)":
        k = st.sidebar.slider("Number of Factors (k)", 2, 5, 2)
        alpha_type = st.sidebar.selectbox("Alpha Type", ["rotatable", "spherical", "face-centered"])
        cp = st.sidebar.slider("Center Points", 1, 5, 3)
        factor_names = []
        for i in range(k):
            name = st.sidebar.text_input(f"Factor {i+1}", f"X{i+1}", key=f"ccd_name_{i}")
            factor_names.append(name)

        if st.sidebar.button("📐 Generate Design", type="primary"):
            df, info = generate_ccd(k, alpha_type, cp, factor_names)
            st.session_state.doe_design = df
            st.session_state.doe_factor_cols = factor_names
            st.session_state.doe_response = None
            st.session_state.doe_result = None
            st.sidebar.info(f"Alpha = {info['alpha']:.3f}")
            st.rerun()

    elif design_type == "Box-Behnken":
        k = st.sidebar.slider("Number of Factors (k)", 3, 7, 3)
        cp = st.sidebar.slider("Center Points", 1, 5, 3)
        factor_names = []
        for i in range(k):
            name = st.sidebar.text_input(f"Factor {i+1}", f"X{i+1}", key=f"bb_name_{i}")
            factor_names.append(name)

        if st.sidebar.button("📐 Generate Design", type="primary"):
            df = generate_box_behnken(k, cp, factor_names)
            st.session_state.doe_design = df
            st.session_state.doe_factor_cols = factor_names
            st.session_state.doe_response = None
            st.session_state.doe_result = None
            st.rerun()

    # ═══ MAIN CONTENT ═══
    if st.session_state.doe_design is None:
        st.info("👈 请在侧边栏选择 DOE 设计类型并点击 **Generate Design** 开始。")
        st.markdown("""
        ### 支持的实验设计类型
        | 类型 | 用途 | 特点 |
        |------|------|------|
        | **Full Factorial** | 全面因子效应估计 | 2^k 全因子，可加中心点和重复 |
        | **Fractional Factorial** | 因子筛选 | 2^(k-p) 部分因子，支持 Resolution III/IV/V |
        | **Plackett-Burman** | 主效应筛选 | 高效筛选设计，N=8/12/16/20/24 |
        | **Central Composite (CCD)** | 响应曲面优化 | 因子+轴点+中心，支持可旋转/球面/面心 |
        | **Box-Behnken** | 响应曲面优化 | 3-7 因子，避免极端组合 |
        """)
        return

    # ═══ Display Design Matrix ═══
    df = st.session_state.doe_design
    factor_cols = st.session_state.doe_factor_cols

    st.subheader(f"📋 Design Matrix ({len(df)} runs)")
    display_df = df.copy()
    if "RunOrder" in display_df.columns:
        display_df = display_df.drop(columns=["RunOrder", "StdOrder"], errors="ignore")
    st.dataframe(display_df, use_container_width=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("Runs", len(df))
    c2.metric("Factors", len(factor_cols))
    if "Response" not in df.columns:
        c3.metric("Response Status", "⚠️ Not entered")

    # ═══ Response Entry ═══
    st.markdown("---")
    st.subheader("📝 Response Data Entry")

    entry_mode = st.radio("Entry Mode", ["📝 Manual Entry (per row)", "📊 Simulate for Demo", "📤 Bulk Paste"], horizontal=True)

    if entry_mode == "📊 Simulate for Demo":
        st.caption("Generate synthetic response with interaction effects for quick demo.")
        noise = st.slider("Noise Level (σ)", 0.0, 5.0, 1.0, 0.1)

        if st.button("🎲 Generate Demo Response"):
            coeff = [50]
            for i, col in enumerate(factor_cols):
                coeff.append(np.random.uniform(5, 15) * np.random.choice([1, -1]))
            if len(factor_cols) >= 2:
                for _ in range(min(3, len(factor_cols) * (len(factor_cols) - 1) // 2)):
                    coeff.append(np.random.uniform(3, 10) * np.random.choice([1, -1]))

            terms_list = ["Intercept"] + factor_cols
            combos = list(combinations(factor_cols, 2))
            for a, b in combos[:len(coeff) - len(factor_cols) - 1]:
                terms_list.append(f"{a}×{b}")

            y = np.zeros(len(df))
            y += coeff[0]
            for i, col in enumerate(factor_cols):
                y += coeff[i + 1] * df[col].values
            for j, (a, b) in enumerate(combos[:len(coeff) - len(factor_cols) - 1]):
                y += coeff[len(factor_cols) + 1 + j] * df[a].values * df[b].values
            y += np.random.normal(0, noise, len(df))

            df["Response"] = y.round(3)
            st.session_state.doe_design = df
            st.session_state.doe_response = True
            st.rerun()

    elif entry_mode == "📝 Manual Entry (per row)":
        st.caption("Enter response values for each experimental run.")
        response_values = []
        if "Response" in df.columns:
            default_vals = df["Response"].tolist()
        else:
            default_vals = [0.0] * len(df)

        for i in range(len(df)):
            val = st.number_input(
                f"Run {i+1}: " + ", ".join([f"{c}={df[c].iloc[i]:.0f}" for c in factor_cols]),
                value=float(default_vals[i]), key=f"resp_{i}",
                format="%.3f"
            )
            response_values.append(val)

        if st.button("✅ Save Responses"):
            df["Response"] = response_values
            st.session_state.doe_design = df
            st.session_state.doe_response = True
            st.rerun()

    elif entry_mode == "📤 Bulk Paste":
        st.caption("Paste response values (one per line, one value per run).")
        text = st.text_area("Response Values", height=150,
                           placeholder="85.2\n92.1\n78.6\n...")
        if st.button("📥 Parse & Apply"):
            lines = [l.strip() for l in text.split("\n") if l.strip()]
            try:
                vals = [float(l) for l in lines]
                if len(vals) != len(df):
                    st.error(f"Expected {len(df)} values, got {len(vals)}")
                else:
                    df["Response"] = vals
                    st.session_state.doe_design = df
                    st.session_state.doe_response = True
                    st.success(f"Applied {len(vals)} values!")
                    st.rerun()
            except ValueError as e:
                st.error(f"Parse error: {e}")

    # ═══ Export ═══
    if st.session_state.doe_response:
        csv = df.to_csv(index=False)
        st.download_button("📥 Download CSV", csv, "doe_experiment.csv", "text/csv")

    # ═══ ANALYSIS ═══
    if st.session_state.doe_response and "Response" in df.columns:
        st.markdown("---")
        st.header("📊 Model Analysis")

        col1, col2 = st.columns(2)
        with col1:
            include_2fi = st.checkbox("Include 2-Factor Interactions", value=len(factor_cols) >= 2)
        with col2:
            include_quad = st.checkbox("Include Quadratic Terms", value=False,
                                       help="Only meaningful for CCD/Box-Behnken with center points")

        if st.button("🔬 Fit Model", type="primary"):
            result = fit_doe_model(df, factor_cols, "Response", include_2fi, include_quad)
            st.session_state.doe_result = result
            st.rerun()

        if st.session_state.doe_result is not None:
            r = st.session_state.doe_result

            # ── Model Summary ──
            st.subheader("📋 Model Summary")
            sm1, sm2, sm3, sm4 = st.columns(4)
            sm1.metric("R²", f"{r['r2']:.4f}")
            sm2.metric("R² Adjusted", f"{r['r2_adj']:.4f}")
            sm3.metric("R² Predicted", f"{r['r2_pred']:.4f}")
            sm4.metric("Observations", r['n'])

            # ── ANOVA ──
            st.subheader("📊 ANOVA Table")
            st.dataframe(r["anova"], use_container_width=True, hide_index=True)

            # ── Coefficient Table ──
            st.subheader("📈 Parameter Estimates")
            coef_df = r["coefficients"].copy()
            styled = coef_df.style.apply(
                lambda row: ['background-color: #e8f5e9' if row['p'] < 0.05 else ''
                            for _ in row], axis=1, subset=['p']
            )
            st.dataframe(coef_df, use_container_width=True, hide_index=True)

            # ── Effect Screening ──
            st.markdown("---")
            st.subheader("🎯 Effect Screening")

            eff_tab1, eff_tab2 = st.tabs(["Half-Normal Plot", "Pareto Chart"])
            with eff_tab1:
                st.plotly_chart(plot_half_normal(r["effects"]), use_container_width=True)
            with eff_tab2:
                st.plotly_chart(plot_pareto_effects(r["effects"]), use_container_width=True)

            # ── Main Effects & Interactions ──
            st.markdown("---")
            st.subheader("📈 Main Effects & Interactions")

            if len(factor_cols) >= 2:
                st.plotly_chart(plot_interaction(df, factor_cols), use_container_width=True)

            # Main effects
            main_cols = st.columns(len(factor_cols))
            for i, factor in enumerate(factor_cols):
                effect_data = df.groupby(factor)["Response"].agg(["mean", "std"]).reset_index()
                with main_cols[i]:
                    fig = go.Figure()
                    fig.add_trace(go.Bar(
                        x=["Low (-1)", "High (+1)"],
                        y=effect_data["mean"].values,
                        error_y=dict(type="data", array=effect_data["std"].values),
                        marker_color=["#3498db", "#e74c3c"],
                    ))
                    fig.update_layout(title=f"Main Effect: {factor}", height=300,
                                     yaxis_title="Mean Response")
                    st.plotly_chart(fig, use_container_width=True)

            # ── Response Surface ──
            if len(factor_cols) >= 2:
                st.markdown("---")
                st.subheader("🌐 Response Surface Explorer")

                csf1, csf2 = st.columns(2)
                with csf1:
                    x_surf = st.selectbox("X-Axis Factor", factor_cols, key="surf_x")
                with csf2:
                    remaining = [c for c in factor_cols if c != x_surf]
                    y_surf = st.selectbox("Y-Axis Factor", remaining, key="surf_y")

                surf_tab1, surf_tab2 = st.tabs(["Contour Plot", "3D Surface"])
                with surf_tab1:
                    st.plotly_chart(plot_contour(r, x_surf, y_surf), use_container_width=True)
                with surf_tab2:
                    st.plotly_chart(plot_surface(r, x_surf, y_surf), use_container_width=True)

            # ── Prediction Profiler ──
            st.markdown("---")
            st.subheader("🎛️ Prediction Profiler")

            st.caption("Adjust factor settings and see predicted response.")
            profiler_settings = {}
            pcols = st.columns(len(factor_cols))
            for i, factor in enumerate(factor_cols):
                with pcols[i]:
                    min_v = float(df[factor].min())
                    max_v = float(df[factor].max())
                    profiler_settings[factor] = st.slider(
                        factor, min_v, max_v, 0.0, 0.1, key=f"prof_{factor}"
                    )

            pred_val = make_prediction(r, profiler_settings)
            st.metric("📌 Predicted Response", f"{pred_val:.4f}")

            # ── Residual Diagnostics ──
            st.markdown("---")
            st.subheader("🔍 Residual Diagnostics")
            st.plotly_chart(plot_residual_diagnostics(r), use_container_width=True)

            # Residual statistics
            res = r["residuals"]
            rcol1, rcol2, rcol3, rcol4 = st.columns(4)
            rcol1.metric("Mean Residual", f"{np.mean(res):.4f}")
            rcol2.metric("Std Residual", f"{np.std(res):.4f}")
            rcol3.metric("Shapiro-Wilk p", f"{stats.shapiro(res)[1]:.4f}" if len(res) >= 3 else "N/A")
            rcol4.metric("Durbin-Watson", f"{np.sum(np.diff(res)**2)/np.sum(res**2):.3f}" if len(res) > 1 else "N/A")

            # ── Save to DB ──
            st.markdown("---")
            if db_insert_query is not None:
                if st.button("💾 Save Experiment to Database"):
                    exp_name = f"DOE_{design_type.replace(' ', '_')}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}"
                    data_json = json.dumps({
                        "design_type": design_type,
                        "factor_names": factor_cols,
                        "design": df.to_dict(orient="records"),
                        "model_r2": r["r2"],
                        "coefficients": r["coefficients"].to_dict(orient="records"),
                    })
                    try:
                        db_insert_query(
                            "INSERT INTO DOE_Experiments (Experiment_Name, Factor_1, Factor_2, Response_Variable, Data_JSON) VALUES (?,?,?,?,?)",
                            [exp_name, factor_cols[0] if len(factor_cols) > 0 else "",
                             factor_cols[1] if len(factor_cols) > 1 else "",
                             "Response", data_json]
                        )
                        st.success(f"Saved: {exp_name}")
                    except Exception as e:
                        st.error(f"Save failed: {e}")
