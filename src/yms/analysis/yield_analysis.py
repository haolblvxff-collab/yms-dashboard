"""
YMS Yield Analysis Engine
==========================
Defect Pareto, Yield Loss Decomposition, Defect Density Trend, Kill Ratio.
"""
import numpy as np
import pandas as pd
from typing import Optional, List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class YieldReport:
    """Complete yield analysis report."""
    total_lots: int
    total_defects: int
    overall_yield: float
    # Pareto
    pareto_df: Optional[pd.DataFrame] = None
    # Defect density by lot
    density_trend: Optional[pd.DataFrame] = None
    # Yield loss decomposition
    loss_by_type: Optional[pd.DataFrame] = None
    loss_by_severity: Optional[pd.DataFrame] = None
    # Kill ratio
    kill_ratio: float = 0.0
    kill_by_type: Optional[pd.DataFrame] = None


class YieldAnalysis:
    """Yield loss and defect analysis for semiconductor manufacturing."""

    def __init__(self):
        pass

    def analyze(self, lots_df: pd.DataFrame, defects_df: pd.DataFrame,
                lot_col: str = "Lot_ID", total_dice_per_wafer: int = 1000,
                n_wafers_per_lot: int = 25) -> YieldReport:
        """Full yield analysis from lots and defects data.

        Args:
            lots_df: DataFrame with Lot_ID, Status columns (from Lots table).
            defects_df: DataFrame with Lot_ID, Defect_Type, Count, Severity columns.
            total_dice_per_wafer: Total dice per wafer for kill ratio estimation.
            n_wafers_per_lot: Number of wafers per lot.
        """
        n_lots = lots_df[lot_col].nunique() if not lots_df.empty else 0
        n_defects = defects_df["Count"].sum() if not defects_df.empty else 0

        # Overall yield (based on completed lots)
        completed = lots_df[lots_df["Status"] == "Completed"] if "Status" in lots_df.columns else lots_df
        overall_yield = len(completed) / max(len(lots_df), 1) * 100 if "Status" in lots_df.columns else 100.0

        # ── Pareto by defect type ──
        pareto_df = self._build_pareto(defects_df, group_col="Defect_Type", count_col="Count")

        # ── Yield loss by defect type ──
        loss_by_type = self._build_yield_loss(defects_df, total_dice_per_wafer, n_wafers_per_lot,
                                              group_col="Defect_Type")

        # ── Yield loss by severity ──
        if "Severity" in defects_df.columns:
            loss_by_severity = self._build_yield_loss(defects_df, total_dice_per_wafer, n_wafers_per_lot,
                                                       group_col="Severity")
        else:
            loss_by_severity = None

        # ── Defect density trend ──
        density_trend = self._build_density_trend(defects_df, lot_col=lot_col,
                                                   n_wafers=n_wafers_per_lot)

        # ── Kill ratio ──
        kill_ratio, kill_by_type = self._estimate_kill_ratio(defects_df, total_dice_per_wafer,
                                                              n_wafers_per_lot)

        return YieldReport(
            total_lots=n_lots,
            total_defects=int(n_defects),
            overall_yield=overall_yield,
            pareto_df=pareto_df,
            density_trend=density_trend,
            loss_by_type=loss_by_type,
            loss_by_severity=loss_by_severity,
            kill_ratio=kill_ratio,
            kill_by_type=kill_by_type,
        )

    def _build_pareto(self, df: pd.DataFrame, group_col: str = "Defect_Type",
                       count_col: str = "Count") -> pd.DataFrame:
        """Build Pareto analysis DataFrame."""
        if df.empty:
            return pd.DataFrame()

        grouped = df.groupby(group_col)[count_col].sum().sort_values(ascending=False).reset_index()
        total = grouped[count_col].sum()
        grouped["Percentage"] = (grouped[count_col] / total * 100).round(1)
        grouped["Cumulative"] = grouped["Percentage"].cumsum().round(1)
        grouped.columns = ["Category", "Count", "Pct", "Cum_Pct"]
        return grouped

    def _build_yield_loss(self, df: pd.DataFrame, dice_per_wafer: int, wafers_per_lot: int,
                           group_col: str = "Defect_Type") -> pd.DataFrame:
        """Decompose yield loss by category using Poisson model.

        Yield_loss_i = 1 - exp(-DD_i) where DD_i = defects_i / total_dice
        """
        if df.empty:
            return pd.DataFrame()

        total_dice = len(df["Lot_ID"].unique()) * wafers_per_lot * dice_per_wafer if df["Lot_ID"].nunique() > 0 else 1
        grouped = df.groupby(group_col)["Count"].sum().sort_values(ascending=False).reset_index()
        grouped["Defect_Density"] = grouped["Count"] / total_dice
        grouped["Limited_Yield"] = np.exp(-grouped["Defect_Density"]) * 100
        grouped["Yield_Loss_Pct"] = (100 - grouped["Limited_Yield"]).round(2)
        grouped.columns = ["Category", "Defect_Count", "DD", "DLY(%)", "Loss(%)"]
        return grouped

    def _build_density_trend(self, df: pd.DataFrame, lot_col: str = "Lot_ID",
                              n_wafers: int = 25) -> pd.DataFrame:
        """Defect density per lot trend."""
        if df.empty or lot_col not in df.columns:
            return pd.DataFrame()

        density = df.groupby(lot_col)["Count"].sum().reset_index()
        density["Defect_Density"] = (density["Count"] / n_wafers).round(2)
        density.columns = ["Lot", "Total_Defects", "Defects_per_Wafer"]
        return density

    def _estimate_kill_ratio(self, df: pd.DataFrame, dice_per_wafer: int = 1000,
                              wafers_per_lot: int = 25) -> Tuple[float, pd.DataFrame]:
        """Estimate kill ratio (probability a defect kills a die).

        Uses a simplified Poisson model: Yield = exp(-KR * DD)
        Assuming reasonable overall yield ~85-95%, KR ≈ 0.3-0.7 typically.
        """
        if df.empty:
            return 0.0, pd.DataFrame()

        total_defects = df["Count"].sum()
        unique_lots = df["Lot_ID"].nunique() if "Lot_ID" in df.columns else 1
        total_dice = unique_lots * wafers_per_lot * dice_per_wafer
        dd = total_defects / total_dice if total_dice > 0 else 0

        # Rough estimate: typical KR for random defects in semiconductor
        # Using Murphy model approximation
        kr = 0.5 if dd == 0 else min(1.0, max(0.05, -np.log(0.9) / dd if dd > 0 else 0.5))

        # By defect type
        if "Defect_Type" in df.columns:
            type_kr = []
            grouped = df.groupby("Defect_Type")
            for dtype, grp in grouped:
                cnt = grp["Count"].sum()
                dd_type = cnt / total_dice if total_dice > 0 else 0
                # Different defect types have different kill probabilities
                # Particles typically ~0.3-0.5, pattern defects ~0.7-1.0
                if "particle" in dtype.lower() or "颗粒" in dtype:
                    kr_type = 0.35
                elif "pattern" in dtype.lower() or "图形" in dtype or "bridge" in dtype.lower():
                    kr_type = 0.75
                elif "scratch" in dtype.lower() or "划伤" in dtype:
                    kr_type = 0.9
                else:
                    kr_type = 0.5
                type_kr.append({
                    "Defect_Type": dtype, "Count": int(cnt),
                    "DD": round(dd_type, 6), "Kill_Ratio": kr_type,
                    "Estimated_Kill": int(cnt * kr_type),
                })
            kr_df = pd.DataFrame(type_kr).sort_values("Count", ascending=False).reset_index(drop=True)
        else:
            kr_df = pd.DataFrame()

        return round(kr, 3), kr_df

    # ── Chart Builders ──

    def build_pareto_chart(self, pareto_df: pd.DataFrame,
                            title: str = "Defect Pareto Analysis"):
        """Dual-axis Pareto chart (bar + cumulative line)."""
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots

        if pareto_df.empty:
            return go.Figure()

        df = pareto_df.head(15)
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        fig.add_trace(go.Bar(
            x=df["Category"], y=df["Count"], name="Defect Count",
            marker_color="#3498db", text=df["Count"], textposition="outside",
        ), secondary_y=False)

        fig.add_trace(go.Scatter(
            x=df["Category"], y=df["Cum_Pct"], name="Cumulative %",
            mode="lines+markers", marker=dict(size=8, color="#e74c3c"),
            line=dict(width=2, color="#e74c3c"),
        ), secondary_y=True)

        fig.add_hline(y=80, line_dash="dash", line_color="gray",
                      annotation_text="80%", secondary_y=True)

        fig.update_layout(title=title, height=450)
        fig.update_yaxes(title_text="Defect Count", secondary_y=False)
        fig.update_yaxes(title_text="Cumulative %", range=[0, 105], secondary_y=True)
        fig.update_xaxes(tickangle=-30)
        return fig

    def build_loss_waterfall(self, loss_df: pd.DataFrame,
                              title: str = "Yield Loss Decomposition"):
        """Waterfall chart showing yield loss breakdown."""
        import plotly.graph_objects as go

        if loss_df.empty:
            return go.Figure()

        df = loss_df.head(10)
        fig = go.Figure(go.Waterfall(
            name="Yield Loss",
            orientation="v",
            measure=["relative"] * len(df) + ["total"],
            x=list(df["Category"]) + ["Total Loss"],
            y=list(df["Loss(%)"]) + [df["Loss(%)"].sum()],
            text=[f"{v:.1f}%" for v in df["Loss(%)"]] + [f"{df['Loss(%)'].sum():.1f}%"],
            connector={"line": {"color": "gray"}},
            decreasing={"marker": {"color": "#e74c3c"}},
            increasing={"marker": {"color": "#e67e22"}},
            totals={"marker": {"color": "#2c3e50"}},
        ))
        fig.update_layout(title=title, height=400, yaxis_title="Yield Loss (%)")
        return fig

    def build_density_trend_chart(self, density_df: pd.DataFrame,
                                   title: str = "Defect Density Trend by Lot"):
        """Defect density trend line chart."""
        import plotly.graph_objects as go

        if density_df.empty:
            return go.Figure()

        df = density_df.head(30)
        avg_dd = df["Defects_per_Wafer"].mean()
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df["Lot"], y=df["Defects_per_Wafer"],
            name="Defects/Wafer", marker_color="#3498db",
            text=df["Defects_per_Wafer"].round(1), textposition="outside",
        ))
        fig.add_hline(y=avg_dd, line_dash="dash", line_color="red",
                      annotation_text=f"Avg: {avg_dd:.1f}")
        fig.update_layout(title=title, height=400,
                          xaxis_title="Lot", yaxis_title="Defects per Wafer",
                          xaxis=dict(tickangle=-45))
        return fig

    def build_kill_ratio_chart(self, kr_df: pd.DataFrame,
                                title: str = "Kill Ratio by Defect Type"):
        """Kill ratio estimation bar chart."""
        import plotly.graph_objects as go

        if kr_df.empty:
            return go.Figure()

        df = kr_df.head(10)
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df["Defect_Type"], y=df["Kill_Ratio"],
            name="Kill Ratio", marker_color="#e74c3c",
            text=[f"{kr:.2f}" for kr in df["Kill_Ratio"]], textposition="outside",
        ))
        fig.add_trace(go.Scatter(
            x=df["Defect_Type"], y=df["Estimated_Kill"],
            name="Est. Killed Dice", mode="markers",
            marker=dict(size=12, color="#2c3e50", symbol="x"),
        ))
        fig.update_layout(title=title, height=400,
                          yaxis_title="Kill Ratio / Killed Dice",
                          xaxis=dict(tickangle=-30))
        return fig

    def build_yield_summary_gauge(self, overall_yield: float,
                                   title: str = "Overall Lot Yield"):
        """Gauge chart for overall yield."""
        import plotly.graph_objects as go
        color = "#27ae60" if overall_yield >= 90 else ("#f39c12" if overall_yield >= 80 else "#e74c3c")
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=overall_yield,
            title={"text": title},
            delta={"reference": 90},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": color},
                "steps": [
                    {"range": [0, 80], "color": "#fadbd8"},
                    {"range": [80, 90], "color": "#fdebd0"},
                    {"range": [90, 100], "color": "#d5f5e3"},
                ],
                "threshold": {
                    "line": {"color": "red", "width": 2},
                    "thickness": 0.8, "value": 90,
                },
            },
        ))
        fig.update_layout(height=300)
        return fig
