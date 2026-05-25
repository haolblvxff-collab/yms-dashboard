"""
YMS Correlation Analysis Engine
================================
Wraps the existing correlation_analysis.py functions into a class
suitable for Streamlit UI and API consumption.
"""
import numpy as np
import pandas as pd
from scipy import stats
from typing import Optional, List, Dict, Tuple
import warnings


class CorrelationAnalysis:
    """Correlation analysis between process parameters and yield."""

    def __init__(self):
        pass

    def analyze(self, df: pd.DataFrame, param_cols: List[str],
                yield_col: str, method: str = "spearman") -> pd.DataFrame:
        """Rank parameters by correlation with yield.

        Returns DataFrame sorted by |correlation| descending.
        """
        results = []
        for param in param_cols:
            mask = df[[param, yield_col]].notna().all(axis=1)
            x = df.loc[mask, param].values
            y = df.loc[mask, yield_col].values
            if len(x) < 3:
                continue
            if method == "pearson":
                corr, p = stats.pearsonr(x, y)
            else:
                corr, p = stats.spearmanr(x, y)

            # Handle NaN from constant input or degenerate data
            if np.isnan(corr):
                corr = 0.0
            if np.isnan(p):
                p = 1.0

            sig = "***" if p < 0.001 else ("**" if p < 0.01 else ("*" if p < 0.05 else "ns"))
            results.append({
                "Parameter": param, "Correlation": round(corr, 4),
                "Abs_Correlation": round(abs(corr), 4),
                "P_value": round(p, 6), "Significance": sig,
            })
        return pd.DataFrame(results).sort_values("Abs_Correlation", ascending=False).reset_index(drop=True)

    def cross_correlation_matrix(self, df: pd.DataFrame,
                                  columns: Optional[List[str]] = None,
                                  method: str = "spearman") -> pd.DataFrame:
        """Full correlation matrix between all selected columns."""
        if columns is None:
            columns = df.select_dtypes(include=[np.number]).columns.tolist()
        numeric = df[columns].select_dtypes(include=[np.number])
        return numeric.corr(method=method)

    def find_key_params(self, ranking: pd.DataFrame,
                         min_corr: float = 0.3, max_p: float = 0.05) -> pd.DataFrame:
        """Filter to statistically significant key parameters."""
        return ranking[
            (ranking["Abs_Correlation"] >= min_corr) &
            (ranking["P_value"] < max_p)
        ]

    # ── Chart builders ──

    def build_heatmap(self, corr_matrix: pd.DataFrame,
                       title: str = "Correlation Heatmap"):
        """Plotly correlation heatmap (RdBu colormap)."""
        import plotly.graph_objects as go
        z = corr_matrix.values
        labels = corr_matrix.columns.tolist()
        fig = go.Figure(data=go.Heatmap(
            z=z, x=labels, y=labels,
            colorscale="RdBu", zmid=0,
            text=np.round(z, 2), texttemplate="%{text}",
            colorbar=dict(title="r"),
            hovertemplate="%{x} vs %{y}: r=%{z:.3f}<extra></extra>",
        ))
        fig.update_layout(
            title=title, height=max(500, 40 * len(labels)),
            xaxis=dict(tickangle=-45), margin=dict(l=120, r=40, t=60, b=100),
        )
        return fig

    def build_ranking_bar(self, ranking: pd.DataFrame,
                            title: str = "Parameter-Yield Correlation Ranking"):
        """Horizontal bar chart of correlations sorted by magnitude."""
        import plotly.graph_objects as go
        df = ranking.head(20).sort_values("Correlation")
        colors = ["#e74c3c" if r < 0 else "#27ae60" for r in df["Correlation"]]
        fig = go.Figure(data=[go.Bar(
            x=df["Correlation"], y=df["Parameter"],
            orientation="h", marker_color=colors,
            text=[f"{r:.3f} {s}" for r, s in zip(df["Correlation"], df["Significance"])],
            textposition="outside",
        )])
        fig.add_vline(x=0, line_color="gray", line_width=1)
        fig.update_layout(title=title, height=max(300, 25 * len(df)),
                          xaxis_title="Correlation", margin=dict(l=150))
        return fig

    def build_scatter_pair(self, df: pd.DataFrame, x_col: str, y_col: str,
                            method: str = "spearman"):
        """Scatter plot with regression line for a parameter pair."""
        import plotly.graph_objects as go
        mask = df[[x_col, y_col]].notna().all(axis=1)
        x = df.loc[mask, x_col].values
        y = df.loc[mask, y_col].values

        if method == "pearson":
            r, p = stats.pearsonr(x, y)
        else:
            r, p = stats.spearmanr(x, y)

        # Trend line via numpy polyfit
        if len(x) >= 2:
            slope, intercept = np.polyfit(x, y, 1)
            trend_x = np.linspace(x.min(), x.max(), 100)
            trend_y = slope * trend_x + intercept
        else:
            trend_x, trend_y = [], []

        sig = "***" if p < 0.001 else ("**" if p < 0.01 else ("*" if p < 0.05 else "ns"))

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x, y=y, mode="markers",
                                  marker=dict(size=6, opacity=0.5, color="#3498db"),
                                  name="Data"))
        if len(trend_x) > 0:
            fig.add_trace(go.Scatter(x=trend_x, y=trend_y, mode="lines",
                                      line=dict(color="#e74c3c", width=2),
                                      name=f"Trend (r={r:.3f} {sig})"))
        fig.update_layout(
            title=f"{x_col} vs {y_col} r={r:.3f} {sig} p={p:.4f}",
            xaxis_title=x_col, yaxis_title=y_col, height=350,
        )
        return fig
