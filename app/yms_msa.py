"""
YMS MSA / GR&R Module — Streamlit UI
=====================================
Measurement System Analysis: Gauge Repeatability & Reproducibility.
Methods: ANOVA (gold standard), Xbar-R (classic).
"""
import streamlit as st
import pandas as pd
import numpy as np
import os
import sys
import importlib.util
import io

# ── Import MSA engine ──
_msa_path = os.path.join(os.path.dirname(__file__), "..", "src", "yms", "analysis", "msa_gauge_rr.py")
_msa_spec = importlib.util.spec_from_file_location("msa_gauge_rr", os.path.abspath(_msa_path))
_msa_mod = importlib.util.module_from_spec(_msa_spec)
_msa_spec.loader.exec_module(_msa_mod)
MSAGaugeRR = _msa_mod.MSAGaugeRR
GRRResult = _msa_mod.GRRResult

msa = MSAGaugeRR()


def render_msa_page(db_run_query=None, db_insert_query=None):
    """Render the MSA/GR&R Streamlit page.

    Args:
        db_run_query: function(query, params=None) -> pd.DataFrame
        db_insert_query: function(query, params) -> lastrowid
    """
    st.title("🔬 MSA — Gauge R&R Analysis")
    st.caption("Measurement System Analysis · AIAG MSA 4th Edition")

    # ── Study Management ──
    tab1, tab2, tab3 = st.tabs(["📋 Study Setup", "📝 Data Entry", "📊 Analysis & Charts"])

    # ═══════════════════════════════════════════════════════
    #  Tab 1: Study Setup
    # ═══════════════════════════════════════════════════════
    with tab1:
        _render_setup_tab(db_run_query, db_insert_query)

    # ═══════════════════════════════════════════════════════
    #  Tab 2: Data Entry
    # ═══════════════════════════════════════════════════════
    with tab2:
        study_id = _render_data_entry_tab(db_run_query, db_insert_query)

    # ═══════════════════════════════════════════════════════
    #  Tab 3: Analysis & Charts
    # ═══════════════════════════════════════════════════════
    with tab3:
        _render_analysis_tab(db_run_query, study_id)


# ═══════════════════════════════════════════════════════════
#  Tab 1: Study Setup
# ═══════════════════════════════════════════════════════════

def _render_setup_tab(run_query, insert_query):
    """Study creation and loading."""
    st.subheader("Study Management")

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("#### ➕ Create New Study")
        with st.form("grr_study_form"):
            study_name = st.text_input("Study Name", placeholder="e.g. CD-SEM GR&R 2026-Q2")
            description = st.text_area("Description (optional)", placeholder="Measurement tool, location, purpose...")
            c1a, c1b = st.columns(2)
            with c1a:
                method = st.selectbox("Method", ["ANOVA", "Xbar-R"],
                                       help="ANOVA: gold standard, estimates interaction. Xbar-R: classic simpler method.")
            with c1b:
                gauge_name = st.text_input("Gauge/Tool Name", placeholder="e.g. CD-SEM #3")
            c1c, c1d, c1e = st.columns(3)
            with c1c:
                usl = st.number_input("USL (规格上限)", value=0.0, step=0.01,
                                      help="Upper spec limit for %Tolerance calculation. 0 = skip.")
            with c1d:
                lsl = st.number_input("LSL (规格下限)", value=0.0, step=0.01,
                                      help="Lower spec limit for %Tolerance calculation. 0 = skip.")
            with c1e:
                tolerance = st.number_input("Tolerance (直接)", value=0.0, step=0.01,
                                            help="Direct tolerance = USL - LSL. Overrides USL/LSL if set.")

            submitted = st.form_submit_button("💾 Create Study", use_container_width=True)

            if submitted and study_name:
                if insert_query:
                    tol_val = tolerance if tolerance > 0 else (
                        (usl - lsl) if (usl > 0 and lsl > 0 and usl > lsl) else None)
                    study_id = insert_query(
                        """INSERT INTO GRR_Studies (Study_Name, Description, Method, Gauge_Name, USL, LSL, Tolerance)
                           VALUES (?, ?, ?, ?, ?, ?, ?)""",
                        (study_name, description or "", method, gauge_name or "",
                         usl if usl > 0 else None,
                         lsl if lsl > 0 else None,
                         tol_val)
                    )
                    st.success(f"Study '{study_name}' created! ID: {study_id}")
                    st.rerun()
                else:
                    st.error("Database connection not available.")

    with c2:
        st.markdown("#### 📂 Load Existing Study")
        if run_query:
            studies = run_query("SELECT * FROM GRR_Studies ORDER BY Created_At DESC")
            if not studies.empty:
                study_names = studies["Study_Name"].tolist()
                selected_name = st.selectbox("Select Study", study_names,
                                              key="load_study_select")
                selected_row = studies[studies["Study_Name"] == selected_name].iloc[0]

                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.metric("Method", selected_row["Method"])
                with col_b:
                    st.metric("Gauge", selected_row.get("Gauge_Name", "-") or "-")
                with col_c:
                    st.metric("ID", int(selected_row["ID"]))

                if selected_row.get("USL"):
                    st.caption(f"USL={selected_row['USL']}, LSL={selected_row['LSL']} "
                               f"Tolerance={selected_row.get('Tolerance', '-')}")
                if selected_row.get("Description"):
                    st.caption(f"📝 {selected_row['Description']}")

                st.session_state["grr_active_study_id"] = int(selected_row["ID"])
                st.session_state["grr_active_study_name"] = selected_name
            else:
                st.info("No studies yet. Create one first.")
        else:
            st.warning("Database not connected.")


# ═══════════════════════════════════════════════════════════
#  Tab 2: Data Entry
# ═══════════════════════════════════════════════════════════

def _render_data_entry_tab(run_query, insert_query):
    """Data entry for GR&R measurements. Returns active study_id or None."""
    study_id = st.session_state.get("grr_active_study_id", None)
    study_name = st.session_state.get("grr_active_study_name", "None")

    if study_id is None:
        st.info("👈 Please select or create a study in the **Study Setup** tab first.")
        return None

    st.subheader(f"Data Entry — {study_name} (ID: {study_id})")

    # Study config
    if run_query:
        study = run_query("SELECT * FROM GRR_Studies WHERE ID = ?", [study_id])
        if not study.empty:
            srow = study.iloc[0]
            method = srow["Method"]
            st.caption(f"Method: **{method}** | "
                       f"Gauge: {srow.get('Gauge_Name', '-')} | "
                       f"USL={srow.get('USL', '-')}, LSL={srow.get('LSL', '-')}")
        else:
            st.error("Study not found.")
            return None

    # Entry mode selection
    entry_mode = st.radio("Entry Mode", ["🧮 Manual Matrix", "📋 Bulk Paste (CSV/TSV)", "🎲 Generate Demo Data"],
                           horizontal=True)

    if entry_mode == "🧮 Manual Matrix":
        _render_manual_matrix(study_id, insert_query)
    elif entry_mode == "📋 Bulk Paste (CSV/TSV)":
        _render_bulk_paste(study_id, insert_query)
    else:
        _render_demo_generator(study_id, insert_query)

    return study_id


def _render_manual_matrix(study_id, insert_query):
    """Manual part × operator × trial matrix input."""
    st.markdown("#### Manual Data Entry")

    c1, c2, c3 = st.columns(3)
    with c1:
        n_parts = st.number_input("Number of Parts", min_value=2, max_value=30, value=10, key="mm_parts")
    with c2:
        n_ops = st.number_input("Number of Operators", min_value=2, max_value=10, value=3, key="mm_ops")
    with c3:
        n_trials = st.number_input("Trials per Measurement", min_value=2, max_value=10, value=3, key="mm_trials")

    # Build editable matrix
    parts = [f"Part-{i+1}" for i in range(n_parts)]
    ops = [f"Op-{i+1}" for i in range(n_ops)]

    st.markdown(f"**Matrix:** {n_parts} parts × {n_ops} operators × {n_trials} trials = **{n_parts * n_ops * n_trials}** measurements")

    # Build input grid: each operator gets a sub-table
    for op in ops:
        st.markdown(f"##### 👤 {op}")
        cols = st.columns(n_trials + 1)
        cols[0].markdown("**Part**")
        for t in range(n_trials):
            cols[t + 1].markdown(f"**Trial {t+1}**")

        for part in parts:
            row_cols = st.columns(n_trials + 1)
            row_cols[0].write(part)
            for t in range(n_trials):
                key = f"grr_input_{study_id}_{op}_{part}_{t}"
                row_cols[t + 1].text_input(
                    part, key=key, label_visibility="collapsed",
                    placeholder="0.00"
                )

    if st.button("💾 Save All Measurements", use_container_width=True, key="save_mm"):
        saved = 0
        for op in ops:
            for part in parts:
                for t in range(n_trials):
                    key = f"grr_input_{study_id}_{op}_{part}_{t}"
                    val_str = st.session_state.get(key, "").strip()
                    if val_str:
                        try:
                            val = float(val_str)
                            insert_query(
                                """INSERT INTO GRR_Measurements (Study_ID, Part_ID, Operator_ID, Trial, Value)
                                   VALUES (?, ?, ?, ?, ?)""",
                                (study_id, part, op, t + 1, val)
                            )
                            saved += 1
                        except ValueError:
                            st.warning(f"Invalid value for {op} / {part} / Trial {t+1}: '{val_str}'")

        if saved > 0:
            st.success(f"Saved {saved} measurements!")
            st.rerun()


def _render_bulk_paste(study_id, insert_query):
    """Bulk paste CSV/TSV data."""
    st.markdown("#### Bulk Paste (CSV / TSV format)")
    st.caption("Expected columns: `Part`, `Operator`, `Trial`, `Value` — comma or tab separated.")

    paste_text = st.text_area("Paste data here", height=200,
                               placeholder="Part,Operator,Trial,Value\nPart-1,Op-1,1,5.23\nPart-1,Op-1,2,5.19\nPart-1,Op-2,1,5.28\n...")

    if st.button("📥 Import & Save", use_container_width=True, key="save_bulk"):
        if paste_text.strip():
            try:
                # Try CSV first, then TSV
                df = pd.read_csv(io.StringIO(paste_text))
                if len(df.columns) == 1:
                    df = pd.read_csv(io.StringIO(paste_text), sep="\t")

                required = {"Part", "Operator", "Trial", "Value"}
                if not required.issubset(set(df.columns)):
                    st.error(f"Missing columns. Required: {required}. Found: {list(df.columns)}")
                    return

                # Clear existing
                insert_query("DELETE FROM GRR_Measurements WHERE Study_ID = ?", [study_id])

                saved = 0
                for _, row in df.iterrows():
                    try:
                        insert_query(
                            """INSERT INTO GRR_Measurements (Study_ID, Part_ID, Operator_ID, Trial, Value)
                               VALUES (?, ?, ?, ?, ?)""",
                            (study_id, str(row["Part"]), str(row["Operator"]),
                             int(row["Trial"]), float(row["Value"]))
                        )
                        saved += 1
                    except Exception as e:
                        st.warning(f"Skipped row: {e}")

                st.success(f"Imported {saved} measurements!")
                st.rerun()
            except Exception as e:
                st.error(f"Parse error: {e}")


def _render_demo_generator(study_id, insert_query):
    """Generate synthetic GR&R demo data with configurable characteristics."""
    st.markdown("#### Generate Demo Data")

    c1, c2, c3 = st.columns(3)
    with c1:
        n_parts = st.number_input("Parts", 3, 30, 10, key="demo_parts")
    with c2:
        n_ops = st.number_input("Operators", 2, 8, 3, key="demo_ops")
    with c3:
        n_trials = st.number_input("Trials", 2, 5, 3, key="demo_trials")

    c4, c5, c6 = st.columns(3)
    with c4:
        part_var = st.slider("Part Variation (σ_part)", 0.1, 5.0, 1.0, 0.1, key="demo_pvar",
                             help="Higher = parts more different from each other")
    with c5:
        repeat_var = st.slider("Repeatability (σ_ev)", 0.01, 1.0, 0.15, 0.01, key="demo_ev",
                               help="Equipment variation (noise within same part/op/trial)")
    with c6:
        repro_var = st.slider("Reproducibility (σ_av)", 0.01, 0.5, 0.10, 0.01, key="demo_av",
                              help="Operator bias variation")

    target_grr = st.slider("Target %GR&R", 5.0, 50.0, 15.0, 1.0,
                           help="Adjusts repeatability to hit approximate %GR&R target")
    st.caption(f"Expected: %GR&R ≈ {target_grr:.0f}% (precise value varies by random seed)")

    if st.button("🎲 Generate & Save", use_container_width=True, key="gen_demo"):
        np.random.seed(42)
        parts = [f"Part-{i+1}" for i in range(n_parts)]
        ops = [f"Op-{i+1}" for i in range(n_ops)]

        # Adjust repeatability to hit target %GR&R
        adj_repeat = (target_grr / 15.0) * repeat_var * 0.85

        rows = []
        for part_idx, part in enumerate(parts):
            part_effect = np.random.normal(0, part_var)
            for op_idx, op in enumerate(ops):
                op_effect = np.random.normal(0, repro_var)
                for trial in range(1, n_trials + 1):
                    value = 10.0 + part_effect + op_effect + np.random.normal(0, adj_repeat)
                    value = round(float(value), 4)
                    rows.append((study_id, part, op, trial, value))

        # Clear old and insert
        insert_query("DELETE FROM GRR_Measurements WHERE Study_ID = ?", [study_id])
        for row in rows:
            insert_query(
                """INSERT INTO GRR_Measurements (Study_ID, Part_ID, Operator_ID, Trial, Value)
                   VALUES (?, ?, ?, ?, ?)""", row
            )

        st.success(f"Generated {len(rows)} demo measurements ({n_parts} parts × {n_ops} operators × {n_trials} trials)")
        st.rerun()


# ═══════════════════════════════════════════════════════════
#  Tab 3: Analysis & Charts
# ═══════════════════════════════════════════════════════════

def _render_analysis_tab(run_query, study_id):
    """Run GR&R analysis and display results."""
    if study_id is None:
        st.info("👈 Please select a study and enter data first (Study Setup → Data Entry).")
        return

    if run_query is None:
        st.error("Database not available.")
        return

    # Load study config
    study = run_query("SELECT * FROM GRR_Studies WHERE ID = ?", [study_id])
    if study.empty:
        st.error("Study not found.")
        return
    srow = study.iloc[0]
    method = srow["Method"]

    # Load measurements
    df = run_query(
        """SELECT Part_ID AS Part, Operator_ID AS Operator, Trial, Value
           FROM GRR_Measurements WHERE Study_ID = ? ORDER BY Part_ID, Operator_ID, Trial""",
        [study_id]
    )

    if df.empty:
        st.warning("No measurement data. Add data in the **Data Entry** tab first.")
        return

    st.subheader(f"Analysis: {srow['Study_Name']}")
    st.caption(f"Method: **{method}** | {n_parts(df)} parts × {n_ops(df)} operators × {n_trials(df)} trials "
               f"= {len(df)} measurements")

    # ── Run Analysis Button ──
    if not st.button("▶️ Run GR&R Analysis", use_container_width=True):
        # Show raw data preview
        with st.expander("📋 Raw Data Preview", expanded=False):
            st.dataframe(df, use_container_width=True, height=200)
        return

    usl = srow.get("USL")
    lsl = srow.get("LSL")
    tol = srow.get("Tolerance")

    if usl is None or usl == 0:
        usl = None
    if lsl is None or lsl == 0:
        lsl = None
    if tol is None or tol == 0:
        tol = None

    try:
        result = msa.analyze(df, method=method, usl=usl, lsl=lsl, tolerance=tol)
    except Exception as e:
        st.error(f"Analysis error: {e}")
        st.exception(e)
        return

    # ═══════════════════════════════════════════════════════
    #  Results Display
    # ═══════════════════════════════════════════════════════

    st.markdown("---")
    st.markdown("### 📊 GR&R Results Summary")

    # ── KPI Row ──
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        grr_color = "normal" if result.pct_grr < 10 else ("off" if result.pct_grr <= 30 else "inverse")
        st.metric("%GR&R", f"{result.pct_grr:.1f}%", delta=result.grade_grr, delta_color=grr_color)
    with c2:
        st.metric("ndc", f"{result.ndc:.1f}", delta=result.grade_ndc,
                  delta_color="normal" if result.ndc >= 5 else "inverse")
    with c3:
        st.metric("%Repeatability (EV)", f"{result.pct_repeatability:.1f}%")
    with c4:
        st.metric("%Reproducibility (AV)", f"{result.pct_reproducibility:.1f}%")

    # ── Variance Components Table ──
    st.markdown("#### Variance Components")
    vc_data = {
        "Component": ["Repeatability (EV)", "Reproducibility (AV)", "  └ Operator", "  └ Part×Operator",
                       "GR&R (EV+AV)", "Part-to-Part (PV)", "Total Variation (TV)"],
        "Variance (σ²)": [
            f"{result.var_repeatability:.6f}",
            f"{result.var_reproducibility:.6f}",
            f"{result.var_operator:.6f}" if result.method == "ANOVA" else "N/A",
            f"{result.var_interaction:.6f}" if result.method == "ANOVA" else "N/A",
            f"{result.var_grr:.6f}",
            f"{result.var_part:.6f}",
            f"{result.var_total:.6f}",
        ],
        "StdDev (σ)": [
            f"{result.sigma_repeatability:.4f}",
            f"{result.sigma_reproducibility:.4f}",
            f"{result.sigma_operator:.4f}" if result.method == "ANOVA" else "-",
            f"{result.sigma_interaction:.4f}" if result.method == "ANOVA" else "-",
            f"{result.sigma_grr:.4f}",
            f"{result.sigma_part:.4f}",
            f"{result.sigma_total:.4f}",
        ],
        "% Study Var": [
            f"{result.pct_repeatability:.1f}%",
            f"{result.pct_reproducibility:.1f}%",
            f"{result.pct_operator:.1f}%" if result.method == "ANOVA" else "-",
            f"{result.pct_interaction:.1f}%" if result.method == "ANOVA" else "-",
            f"{result.pct_grr:.1f}%",
            f"{result.pct_part:.1f}%",
            f"100.0%",
        ],
    }
    if tol is not None or (usl is not None and lsl is not None):
        vc_data["% Tolerance"] = [
            f"{result.pct_tol_repeatability:.1f}%",
            f"{result.pct_tol_reproducibility:.1f}%",
            "-",
            "-",
            f"{result.pct_tol_grr:.1f}%",
            f"{result.pct_tol_part:.1f}%",
            "-",
        ]

    vc_df = pd.DataFrame(vc_data)
    st.dataframe(vc_df, use_container_width=True, hide_index=True,
                 column_config={
                     "Variance (σ²)": st.column_config.TextColumn(width="small"),
                     "StdDev (σ)": st.column_config.TextColumn(width="small"),
                     "% Study Var": st.column_config.TextColumn(width="small"),
                     "% Tolerance": st.column_config.TextColumn(width="small"),
                 })

    # ── ANOVA Table (ANOVA method only) ──
    if result.method == "ANOVA" and result.anova_table is not None:
        with st.expander("📐 ANOVA Table", expanded=False):
            st.dataframe(result.anova_table, use_container_width=True, hide_index=True)

    # ── Charts ──
    st.markdown("---")
    st.markdown("### 📈 Visualizations")

    chart_mode = st.radio("Y-axis scale", ["% Study Variation", "% Contribution", "% Tolerance"],
                           horizontal=True, key="chart_mode")
    mode_map = {"% Study Variation": "study_var", "% Contribution": "contribution", "% Tolerance": "tolerance"}
    cm = mode_map[chart_mode]

    # Components bar chart
    st.plotly_chart(msa.build_components_fig(result, mode=cm), use_container_width=True)

    # Xbar & R Charts
    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        st.plotly_chart(msa.build_xbar_chart(result), use_container_width=True)
    with chart_col2:
        st.plotly_chart(msa.build_r_chart(result), use_container_width=True)

    # Measurements by Part & Operator
    st.plotly_chart(msa.build_part_operator_plot(result), use_container_width=True)

    # Run chart & Part averages
    chart_col3, chart_col4 = st.columns(2)
    with chart_col3:
        if result.n_parts <= 16:
            st.plotly_chart(msa.build_run_chart(result), use_container_width=True)
    with chart_col4:
        st.plotly_chart(msa.build_part_average_chart(result), use_container_width=True)


# ── Helpers ──

def n_parts(df):
    if df.empty:
        return 0
    return df["Part"].nunique()

def n_ops(df):
    if df.empty:
        return 0
    return df["Operator"].nunique()

def n_trials(df):
    if df.empty:
        return 0
    return df["Trial"].nunique()
