"""
MSA Gauge R&R (GR&R) Analysis Engine
=====================================
Semiconductor-grade Measurement System Analysis.
Implements ANOVA (gold standard) and Xbar-R (simpler) methods.

AIAG MSA 4th Edition compliance:
  - %GR&R < 10%  → Acceptable
  - 10%–30%      → Conditionally Acceptable
  - > 30%         → Unacceptable
  - ndc ≥ 5       → Adequate resolution
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import warnings


@dataclass
class GRRResult:
    """Complete GR&R analysis result."""
    method: str  # "ANOVA" or "Xbar-R"
    n_parts: int
    n_operators: int
    n_trials: int

    # ── Variance Components ──
    var_repeatability: float = 0.0      # σ²_EV (Equipment Variation)
    var_reproducibility: float = 0.0    # σ²_AV (Appraiser Variation)
    var_operator: float = 0.0           # Operator-only portion
    var_interaction: float = 0.0        # Part×Operator interaction
    var_grr: float = 0.0                # Total GR&R variance
    var_part: float = 0.0               # Part-to-part variance
    var_total: float = 0.0              # Total variance

    # ── Standard Deviations ──
    sigma_repeatability: float = 0.0
    sigma_reproducibility: float = 0.0
    sigma_operator: float = 0.0
    sigma_interaction: float = 0.0
    sigma_grr: float = 0.0
    sigma_part: float = 0.0
    sigma_total: float = 0.0

    # ── % Study Variation (%SV) ──
    pct_repeatability: float = 0.0
    pct_reproducibility: float = 0.0
    pct_operator: float = 0.0
    pct_interaction: float = 0.0
    pct_grr: float = 0.0
    pct_part: float = 0.0

    # ── % Tolerance ──
    pct_tol_repeatability: float = 0.0
    pct_tol_reproducibility: float = 0.0
    pct_tol_grr: float = 0.0
    pct_tol_part: float = 0.0

    # ── Capability ──
    ndc: float = 0.0                     # Number of Distinct Categories

    # ── Classification ──
    grade_grr: str = ""                  # "✅ Acceptable" / "⚠️ Marginal" / "❌ Unacceptable"
    grade_ndc: str = ""                  # "✅ Adequate" / "❌ Inadequate"

    # ── ANOVA Table (only for ANOVA method) ──
    anova_table: Optional[pd.DataFrame] = None

    # ── Study-level statistics ──
    part_means: Optional[pd.DataFrame] = None
    operator_means: Optional[pd.DataFrame] = None
    part_op_means: Optional[pd.DataFrame] = None
    range_stats: Optional[pd.DataFrame] = None

    # ── Raw data (pivoted for charting) ──
    data_long: Optional[pd.DataFrame] = None


class MSAGaugeRR:
    """
    MSA Gauge Repeatability & Reproducibility Analysis.

    Two methods:
      - ANOVA: Two-way crossed ANOVA with interaction (gold standard, AIAG preferred)
      - Xbar-R: Average & Range method (simpler, classic, no interaction estimate)

    Usage:
        msa = MSAGaugeRR()
        result = msa.analyze(df, method="ANOVA", usl=10.0, lsl=5.0)
        # df columns: ['Part', 'Operator', 'Trial', 'Value']
    """

    # ── d2* constants for estimating σ from R-bar ──
    # d2(k, n) — for k subgroups of size n
    _D2_TABLE: Dict[Tuple[int, int], float] = {
        # (subgroups, subgroup_size) — commonly used values
        (1, 2): 1.128, (1, 3): 1.693, (1, 4): 2.059, (1, 5): 2.326,
        (2, 2): 1.128, (2, 3): 1.693, (2, 4): 2.059, (2, 5): 2.326,
        (3, 2): 1.128, (3, 3): 1.693, (3, 4): 2.059, (3, 5): 2.326,
        (5, 2): 1.128, (5, 3): 1.693, (5, 4): 2.059, (5, 5): 2.326,
        (10, 2): 1.128, (10, 3): 1.693, (10, 4): 2.059, (10, 5): 2.326,
    }

    # ── d2 constants for range-based σ estimation ──
    # d2(n) — for subgroup of size n
    _D2: Dict[int, float] = {
        2: 1.128, 3: 1.693, 4: 2.059, 5: 2.326,
        6: 2.534, 7: 2.704, 8: 2.847, 9: 2.970, 10: 3.078,
    }

    def analyze(self, df: pd.DataFrame, method: str = "ANOVA",
                usl: Optional[float] = None, lsl: Optional[float] = None,
                tolerance: Optional[float] = None,
                part_col: str = "Part", operator_col: str = "Operator",
                trial_col: str = "Trial", value_col: str = "Value") -> GRRResult:
        """
        Run full GR&R analysis.

        Args:
            df: Long-format DataFrame with Part, Operator, Trial, Value columns.
            method: "ANOVA" or "XbarR"
            usl, lsl: Specification limits for %Tolerance calculation.
            tolerance: Direct tolerance width (usl - lsl). Overrides usl/lsl.
        """
        if method.upper() == "ANOVA":
            return self._analyze_anova(df, usl, lsl, tolerance,
                                       part_col, operator_col, trial_col, value_col)
        else:
            return self._analyze_xbar_r(df, usl, lsl, tolerance,
                                        part_col, operator_col, trial_col, value_col)

    # ═══════════════════════════════════════════════════════
    #  ANOVA Method (Gold Standard)
    # ═══════════════════════════════════════════════════════

    def _analyze_anova(self, df: pd.DataFrame, usl: Optional[float],
                       lsl: Optional[float], tolerance: Optional[float],
                       part_col: str, op_col: str, trial_col: str, val_col: str) -> GRRResult:
        """Two-way crossed ANOVA with interaction."""

        df = df.copy()
        df[part_col] = df[part_col].astype(str)
        df[op_col] = df[op_col].astype(str)

        p = df[part_col].nunique()    # number of parts
        o = df[op_col].nunique()      # number of operators
        r = df[trial_col].nunique()   # number of trials/replicates
        N = len(df)

        # ── Compute means ──
        grand_mean = df[val_col].mean()
        part_means = df.groupby(part_col)[val_col].mean()
        op_means = df.groupby(op_col)[val_col].mean()
        part_op_means = df.groupby([part_col, op_col])[val_col].mean()

        # ── ANOVA Sums of Squares ──
        # SS_Part
        ss_part = 0.0
        for pi in part_means.index:
            ss_part += o * r * (part_means[pi] - grand_mean) ** 2

        # SS_Operator
        ss_op = 0.0
        for oj in op_means.index:
            ss_op += p * r * (op_means[oj] - grand_mean) ** 2

        # SS_Part×Operator (interaction)
        ss_po = 0.0
        for (pi, oj), y_bar_ij in part_op_means.items():
            ss_po += r * (y_bar_ij - part_means[pi] - op_means[oj] + grand_mean) ** 2

        # SS_Error (Repeatability)
        ss_e = 0.0
        for _, row in df.iterrows():
            pi, oj = row[part_col], row[op_col]
            y_bar_ij = part_op_means.loc[(pi, oj)]
            ss_e += (row[val_col] - y_bar_ij) ** 2

        # SS_Total
        ss_total = ((df[val_col] - grand_mean) ** 2).sum()

        # ── Degrees of Freedom ──
        df_part = p - 1
        df_op = o - 1
        df_po = (p - 1) * (o - 1)
        df_e = p * o * (r - 1)
        df_total = N - 1

        # ── Mean Squares ──
        ms_part = ss_part / df_part if df_part > 0 else 0.0
        ms_op = ss_op / df_op if df_op > 0 else 0.0
        ms_po = ss_po / df_po if df_po > 0 else 0.0
        ms_e = ss_e / df_e if df_e > 0 else 0.0

        # ── F-values ──
        f_part = ms_part / ms_po if ms_po > 0 else float('inf')
        f_op = ms_op / ms_po if ms_po > 0 else float('inf')
        f_po = ms_po / ms_e if ms_e > 0 else float('inf')

        # ── P-values (approximate from F-distribution) ──
        from scipy.stats import f as f_dist
        p_part = 1 - f_dist.cdf(f_part, df_part, df_po) if ms_po > 0 else 0.0
        p_op = 1 - f_dist.cdf(f_op, df_op, df_po) if ms_po > 0 else 0.0
        p_po = 1 - f_dist.cdf(f_po, df_po, df_e) if ms_e > 0 else 0.0

        # ── Variance Components (EMS method) ──
        var_e = ms_e                                             # σ²_repeatability
        var_po = max(0.0, (ms_po - ms_e) / r)                   # σ²_interaction
        var_o = max(0.0, (ms_op - ms_po) / (p * r))             # σ²_operator
        var_p = max(0.0, (ms_part - ms_po) / (o * r))           # σ²_part

        var_repeatability = var_e
        var_interaction = var_po
        var_operator = var_o
        var_reproducibility = var_o + var_po
        var_grr = var_repeatability + var_reproducibility
        var_part = var_p
        var_total = var_grr + var_part

        # ── Standard Deviations ──
        sigma_repeatability = np.sqrt(var_repeatability)
        sigma_interaction = np.sqrt(var_interaction)
        sigma_operator = np.sqrt(var_operator)
        sigma_reproducibility = np.sqrt(var_reproducibility)
        sigma_grr = np.sqrt(var_grr)
        sigma_part = np.sqrt(var_part)
        sigma_total = np.sqrt(var_total)

        # ── % Study Variation (6σ method) ──
        tv = sigma_total    # Total Variation = σ_total
        if tv > 0:
            pct_repeatability = 100 * sigma_repeatability / tv
            pct_reproducibility = 100 * sigma_reproducibility / tv
            pct_operator = 100 * sigma_operator / tv
            pct_interaction = 100 * sigma_interaction / tv
            pct_grr = 100 * sigma_grr / tv
            pct_part = 100 * sigma_part / tv
        else:
            pct_repeatability = pct_reproducibility = pct_operator = 0.0
            pct_interaction = pct_grr = pct_part = 0.0

        # ── % Tolerance ──
        tol = self._resolve_tolerance(usl, lsl, tolerance)
        if tol is not None and tol > 0:
            pct_tol_repeatability = 100 * 6 * sigma_repeatability / tol
            pct_tol_reproducibility = 100 * 6 * sigma_reproducibility / tol
            pct_tol_grr = 100 * 6 * sigma_grr / tol
            pct_tol_part = 100 * 6 * sigma_part / tol
        else:
            pct_tol_repeatability = pct_tol_reproducibility = 0.0
            pct_tol_grr = pct_tol_part = 0.0

        # ── ndc ──
        ndc = np.sqrt(2) * (sigma_part / sigma_grr) if sigma_grr > 0 else float('inf')

        # ── Classification ──
        grade_grr = self._classify_grr(pct_grr)
        grade_ndc = "✅ Adequate (≥5)" if ndc >= 5 else "❌ Inadequate (<5)"

        # ── Build ANOVA table ──
        anova_rows = [
            {"Source": part_col, "SS": ss_part, "df": df_part, "MS": ms_part,
             "F": f_part, "p": p_part, "sig": self._sig_stars(p_part)},
            {"Source": op_col, "SS": ss_op, "df": df_op, "MS": ms_op,
             "F": f_op, "p": p_op, "sig": self._sig_stars(p_op)},
            {"Source": f"{part_col}×{op_col}", "SS": ss_po, "df": df_po, "MS": ms_po,
             "F": f_po, "p": p_po, "sig": self._sig_stars(p_po)},
            {"Source": "Repeatability", "SS": ss_e, "df": df_e, "MS": ms_e,
             "F": float('nan'), "p": float('nan'), "sig": ""},
            {"Source": "Total", "SS": ss_total, "df": df_total, "MS": float('nan'),
             "F": float('nan'), "p": float('nan'), "sig": ""},
        ]
        anova_df = pd.DataFrame(anova_rows)

        # ── Study-level statistics ──
        pm = part_means.reset_index()
        pm.columns = ["Part", "Mean"]
        pm["n"] = r * o

        om = op_means.reset_index()
        om.columns = ["Operator", "Mean"]
        om["n"] = p * r

        pom = part_op_means.reset_index()
        pom.columns = ["Part", "Operator", "Mean"]

        # ── Range statistics ──
        range_rows = []
        for (pi, oj), group in df.groupby([part_col, op_col]):
            vals = group[val_col].values
            range_rows.append({"Part": pi, "Operator": oj,
                               "Range": vals.max() - vals.min(),
                               "Mean": vals.mean()})
        range_df = pd.DataFrame(range_rows)

        return GRRResult(
            method="ANOVA",
            n_parts=p, n_operators=o, n_trials=r,
            var_repeatability=var_repeatability,
            var_reproducibility=var_reproducibility,
            var_operator=var_operator,
            var_interaction=var_interaction,
            var_grr=var_grr,
            var_part=var_part,
            var_total=var_total,
            sigma_repeatability=sigma_repeatability,
            sigma_reproducibility=sigma_reproducibility,
            sigma_operator=sigma_operator,
            sigma_interaction=sigma_interaction,
            sigma_grr=sigma_grr,
            sigma_part=sigma_part,
            sigma_total=sigma_total,
            pct_repeatability=pct_repeatability,
            pct_reproducibility=pct_reproducibility,
            pct_operator=pct_operator,
            pct_interaction=pct_interaction,
            pct_grr=pct_grr,
            pct_part=pct_part,
            pct_tol_repeatability=pct_tol_repeatability,
            pct_tol_reproducibility=pct_tol_reproducibility,
            pct_tol_grr=pct_tol_grr,
            pct_tol_part=pct_tol_part,
            ndc=ndc,
            grade_grr=grade_grr,
            grade_ndc=grade_ndc,
            anova_table=anova_df,
            part_means=pm,
            operator_means=om,
            part_op_means=pom,
            range_stats=range_df,
            data_long=df,
        )

    # ═══════════════════════════════════════════════════════
    #  Xbar-R Method (Simpler, no interaction)
    # ═══════════════════════════════════════════════════════

    def _analyze_xbar_r(self, df: pd.DataFrame, usl: Optional[float],
                        lsl: Optional[float], tolerance: Optional[float],
                        part_col: str, op_col: str, trial_col: str, val_col: str) -> GRRResult:
        """Average & Range method (classical GR&R)."""

        df = df.copy()
        df[part_col] = df[part_col].astype(str)
        df[op_col] = df[op_col].astype(str)

        p = df[part_col].nunique()
        o = df[op_col].nunique()
        r = df[trial_col].nunique()

        grand_mean = df[val_col].mean()

        # ── Ranges by Operator-Part ──
        range_data = []
        for (pi, oj), group in df.groupby([part_col, op_col]):
            vals = group[val_col].values
            range_data.append({
                "Part": pi, "Operator": oj,
                "R": vals.max() - vals.min(),
                "Xbar": vals.mean(),
            })
        range_df = pd.DataFrame(range_data)

        # R-bar (average of ranges)
        R_bar = range_df["R"].mean()

        # ── Operator averages ──
        op_means = range_df.groupby("Operator")["Xbar"].mean()
        X_bar_diff = op_means.max() - op_means.min()  # X_bar_diff

        # ── Part averages ──
        part_means = range_df.groupby("Part")["Xbar"].mean()
        R_p = part_means.max() - part_means.min()  # R_part

        # ── d2 constants ──
        d2_r = self._D2.get(r, r)          # d2 for trials
        d2_op = self._D2.get(o, o)         # d2 for operators
        n_r_for_d2 = 1  # subgroup size = 1 for single trial range

        # ── Variance Components (Xbar-R method, AIAG) ──
        # EV (Equipment Variation) = R_bar / d2
        sigma_e = R_bar / d2_r
        var_repeatability = sigma_e ** 2

        # AV (Appraiser Variation) = sqrt((X_bar_diff / d2_op)^2 - EV^2/(p*r))
        sigma_o = X_bar_diff / d2_op if d2_op > 0 else 0
        av_sq = sigma_o ** 2 - (var_repeatability / (p * r))
        var_reproducibility = max(0.0, av_sq)
        sigma_reproducibility = np.sqrt(var_reproducibility)

        # GR&R
        var_grr = var_repeatability + var_reproducibility
        sigma_grr = np.sqrt(var_grr)

        # PV (Part Variation) = R_p / d2*
        # d2* for p parts
        d2_p = self._D2.get(p, 3.078) if p <= 10 else p
        sigma_part = R_p / d2_p if d2_p > 0 else 0
        var_part = sigma_part ** 2

        # TV (Total Variation)
        var_total = var_grr + var_part
        sigma_total = np.sqrt(var_total)

        # ── % Study Variation ──
        tv = sigma_total
        if tv > 0:
            pct_repeatability = 100 * sigma_e / tv
            pct_reproducibility = 100 * sigma_reproducibility / tv
            pct_grr = 100 * sigma_grr / tv
            pct_part = 100 * sigma_part / tv
        else:
            pct_repeatability = pct_reproducibility = pct_grr = pct_part = 0.0

        # ── % Tolerance ──
        tol = self._resolve_tolerance(usl, lsl, tolerance)
        if tol is not None and tol > 0:
            pct_tol_repeatability = 100 * 6 * sigma_e / tol
            pct_tol_reproducibility = 100 * 6 * sigma_reproducibility / tol
            pct_tol_grr = 100 * 6 * sigma_grr / tol
            pct_tol_part = 100 * 6 * sigma_part / tol
        else:
            pct_tol_repeatability = pct_tol_reproducibility = 0.0
            pct_tol_grr = pct_tol_part = 0.0

        # ── ndc ──
        ndc = np.sqrt(2) * (sigma_part / sigma_grr) if sigma_grr > 0 else float('inf')

        # ── Classification ──
        grade_grr = self._classify_grr(pct_grr)
        grade_ndc = "✅ Adequate (≥5)" if ndc >= 5 else "❌ Inadequate (<5)"

        # ── Build summary stats ──
        pm = part_means.reset_index()
        pm.columns = ["Part", "Mean"]

        om = op_means.reset_index()
        om.columns = ["Operator", "Mean"]

        pom = range_df[["Part", "Operator", "Xbar"]].rename(columns={"Xbar": "Mean"})

        return GRRResult(
            method="Xbar-R",
            n_parts=p, n_operators=o, n_trials=r,
            var_repeatability=var_repeatability,
            var_reproducibility=var_reproducibility,
            var_operator=var_reproducibility,   # Xbar-R doesn't separate these
            var_interaction=0.0,
            var_grr=var_grr,
            var_part=var_part,
            var_total=var_total,
            sigma_repeatability=sigma_e,
            sigma_reproducibility=sigma_reproducibility,
            sigma_operator=sigma_reproducibility,
            sigma_interaction=0.0,
            sigma_grr=sigma_grr,
            sigma_part=sigma_part,
            sigma_total=sigma_total,
            pct_repeatability=pct_repeatability,
            pct_reproducibility=pct_reproducibility,
            pct_operator=pct_reproducibility,
            pct_interaction=0.0,
            pct_grr=pct_grr,
            pct_part=pct_part,
            pct_tol_repeatability=pct_tol_repeatability,
            pct_tol_reproducibility=pct_tol_reproducibility,
            pct_tol_grr=pct_tol_grr,
            pct_tol_part=pct_tol_part,
            ndc=ndc,
            grade_grr=grade_grr,
            grade_ndc=grade_ndc,
            part_means=pm,
            operator_means=om,
            part_op_means=pom,
            range_stats=range_df,
            data_long=df,
        )

    # ═══════════════════════════════════════════════════════
    #  Chart Data Builders
    # ═══════════════════════════════════════════════════════

    def build_components_fig(self, result: GRRResult, mode: str = "study_var",
                              title: str = "Components of Variation"):
        """Build Plotly figure for variance components bar chart.

        Args:
            result: GRR analysis result.
            mode: "study_var" (%Study Var), "contribution" (%Contribution = variance/total),
                  or "tolerance" (%Tolerance).
        """
        import plotly.graph_objects as go

        if mode == "contribution":
            t = result.var_total if result.var_total > 0 else 1.0
            repeat_val = 100 * result.var_repeatability / t
            repro_val = 100 * result.var_reproducibility / t
            grr_val = 100 * result.var_grr / t
            part_val = 100 * result.var_part / t
            ylabel = "% Contribution"
            threshold_line = None
        elif mode == "tolerance":
            repeat_val = result.pct_tol_repeatability
            repro_val = result.pct_tol_reproducibility
            grr_val = result.pct_tol_grr
            part_val = result.pct_tol_part
            ylabel = "% Tolerance (6σ / Tol)"
            threshold_line = 30
        else:  # study_var
            repeat_val = result.pct_repeatability
            repro_val = result.pct_reproducibility
            grr_val = result.pct_grr
            part_val = result.pct_part
            ylabel = "% Study Variation"
            threshold_line = 30

        categories = ["%GR&R", "Repeatability", "Reproducibility", "Part-to-Part"]
        values = [grr_val, repeat_val, repro_val, part_val]
        colors = ["#e74c3c" if grr_val > 30 else "#f39c12" if grr_val > 10 else "#27ae60",
                  "#e67e22", "#9b59b6", "#3498db"]

        fig = go.Figure(data=[
            go.Bar(x=categories, y=values, marker_color=colors,
                   text=[f"{v:.1f}%" for v in values], textposition="outside")
        ])
        fig.update_layout(
            title=title,
            yaxis_title=ylabel,
            yaxis=dict(range=[0, max(105, max(values) * 1.2)]),
            showlegend=False,
            height=400,
        )
        if threshold_line:
            fig.add_hline(y=threshold_line, line_dash="dash", line_color="red",
                          annotation_text=f"AIAG {threshold_line}%", annotation_position="right")

        return fig

    def build_xbar_chart(self, result: GRRResult,
                          title: str = "Xbar Chart by Operator"):
        """Xbar chart — part averages by operator with control limits."""
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots

        if result.part_op_means is None:
            return go.Figure()

        df = result.part_op_means
        operators = sorted(df["Operator"].unique())
        parts = sorted(df["Part"].unique())

        # Calculate control limits per operator using within-operator range
        # UCL/LCL = grand_mean ± A2 * R_bar
        # A2 for n=trials
        _A2 = {2: 1.880, 3: 1.023, 4: 0.729, 5: 0.577}
        A2 = _A2.get(result.n_trials, 0.577)
        grand_mean = df["Mean"].mean()
        R_bar = result.range_stats["Range"].mean() if result.range_stats is not None else 0
        ucl = grand_mean + A2 * R_bar
        lcl = grand_mean - A2 * R_bar

        n_ops = len(operators)
        fig = make_subplots(rows=n_ops, cols=1, shared_xaxes=True,
                            subplot_titles=[f"Operator: {op}" for op in operators],
                            vertical_spacing=0.08)

        for i, op in enumerate(operators):
            op_df = df[df["Operator"] == op].sort_values("Part")
            row = i + 1
            fig.add_trace(go.Scatter(
                x=op_df["Part"], y=op_df["Mean"], mode="markers+lines",
                name=op, marker=dict(size=8), showlegend=False
            ), row=row, col=1)
            # Control limits
            fig.add_hline(y=grand_mean, line_dash="solid", line_color="green",
                          row=row, col=1)
            fig.add_hline(y=ucl, line_dash="dash", line_color="red",
                          row=row, col=1)
            fig.add_hline(y=lcl, line_dash="dash", line_color="red",
                          row=row, col=1)
            fig.update_yaxes(title_text="Mean", row=row, col=1)

        fig.update_xaxes(title_text="Part", row=n_ops, col=1)
        fig.update_layout(title=title, height=200 * n_ops + 80)
        return fig

    def build_r_chart(self, result: GRRResult,
                       title: str = "R Chart by Operator"):
        """R chart — part ranges by operator with control limits."""
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots

        if result.range_stats is None:
            return go.Figure()

        df = result.range_stats
        operators = sorted(df["Operator"].unique())
        parts = sorted(df["Part"].unique())

        # R chart control limits
        # UCL_R = D4 * R_bar, LCL_R = D3 * R_bar
        _D3 = {2: 0.0, 3: 0.0, 4: 0.0, 5: 0.0}
        _D4 = {2: 3.267, 3: 2.574, 4: 2.282, 5: 2.114}
        D3 = _D3.get(result.n_trials, 0.0)
        D4 = _D4.get(result.n_trials, 2.114)
        R_bar = df["Range"].mean()
        ucl_r = D4 * R_bar
        lcl_r = D3 * R_bar

        n_ops = len(operators)
        fig = make_subplots(rows=n_ops, cols=1, shared_xaxes=True,
                            subplot_titles=[f"Operator: {op}" for op in operators],
                            vertical_spacing=0.08)

        for i, op in enumerate(operators):
            op_df = df[df["Operator"] == op].sort_values("Part")
            row = i + 1
            fig.add_trace(go.Scatter(
                x=op_df["Part"], y=op_df["Range"], mode="markers+lines",
                name=op, marker=dict(size=8), showlegend=False,
                line_color="#e67e22",
            ), row=row, col=1)
            fig.add_hline(y=R_bar, line_dash="solid", line_color="green",
                          row=row, col=1)
            fig.add_hline(y=ucl_r, line_dash="dash", line_color="red",
                          row=row, col=1)

        fig.update_xaxes(title_text="Part", row=n_ops, col=1)
        fig.update_layout(title=title, height=200 * n_ops + 80)
        return fig

    def build_part_operator_plot(self, result: GRRResult,
                                  title: str = "Measurements by Part & Operator"):
        """Box plot / scatter of measurements grouped by part and operator."""
        import plotly.express as px

        if result.data_long is None:
            return go.Figure()

        df = result.data_long
        fig = px.box(df, x="Part", y="Value", color="Operator",
                     title=title, points="all",
                     color_discrete_sequence=px.colors.qualitative.Set2)
        fig.update_layout(height=450, boxmode="group")
        return fig

    def build_run_chart(self, result: GRRResult,
                         title: str = "Run Chart by Part"):
        """Measurements by trial order per part, faceted by operator."""
        import plotly.express as px

        if result.data_long is None:
            return go.Figure()

        df = result.data_long.copy()
        df["Part_Op"] = df["Part"] + " / " + df["Operator"]

        fig = px.line(df, x="Trial", y="Value", color="Operator",
                      facet_col="Part", facet_col_wrap=min(4, result.n_parts),
                      markers=True, title=title,
                      color_discrete_sequence=px.colors.qualitative.Set2)
        fig.update_layout(height=200 * min(result.n_parts, 4) + 100)
        return fig

    def build_part_average_chart(self, result: GRRResult,
                                  title: str = "Part Averages with Operator Range"):
        """Part averages with min-max operator spread (whisker plot)."""
        import plotly.graph_objects as go

        if result.part_op_means is None:
            return go.Figure()

        df = result.part_op_means
        parts = sorted(df["Part"].unique())

        part_stats = []
        for part in parts:
            pdata = df[df["Part"] == part]["Mean"]
            part_stats.append({
                "Part": part, "Mean": pdata.mean(),
                "Min": pdata.min(), "Max": pdata.max(),
                "Spread": pdata.max() - pdata.min(),
            })
        ps_df = pd.DataFrame(part_stats)

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=ps_df["Part"], y=ps_df["Spread"],
            name="Operator Spread (Max-Min)",
            marker_color="#9b59b6", opacity=0.7,
            text=[f"{s:.3f}" for s in ps_df["Spread"]], textposition="outside",
        ))
        fig.add_trace(go.Scatter(
            x=ps_df["Part"], y=ps_df["Mean"], mode="markers",
            name="Part Average", marker=dict(size=10, color="#2c3e50"),
        ))
        fig.update_layout(title=title, height=400,
                          yaxis_title="Value", xaxis_title="Part",
                          barmode="overlay")
        return fig

    # ═══════════════════════════════════════════════════════
    #  Helpers
    # ═══════════════════════════════════════════════════════

    @staticmethod
    def _resolve_tolerance(usl, lsl, tolerance):
        if tolerance is not None:
            return tolerance
        if usl is not None and lsl is not None:
            return usl - lsl
        return None

    @staticmethod
    def _classify_grr(pct_grr: float) -> str:
        if pct_grr < 10:
            return "✅ Acceptable (<10%)"
        elif pct_grr <= 30:
            return "⚠️ Marginal (10%–30%)"
        else:
            return "❌ Unacceptable (>30%)"

    @staticmethod
    def _sig_stars(p: float) -> str:
        if p < 0.001:
            return "***"
        elif p < 0.01:
            return "**"
        elif p < 0.05:
            return "*"
        return ""
