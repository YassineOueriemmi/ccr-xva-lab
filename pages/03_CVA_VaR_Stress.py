
from models.credit import run_stress_tests, simulate_cva_var
from utils.ui import (inject_css, page_header, section_title, formula_box,
                      apply_layout, bbg_header, disclaimer, fmt, ORANGE, RED, GOLD, MGRAY, BLUE, GREEN)
import plotly.graph_objects as go
import pandas as pd
import streamlit as st
import numpy as np
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


_cps = st.session_state.get("counterparties", [{"name": "Counterparty"}])
_cp = _cps[0] if _cps else {}
_cp_label = f"{_cp.get('name', 'Counterparty')} ({_cp.get('rating', '—')})"

inject_css()
bbg_header(f"03 · CVA RISK & VAR — {_cp_label}")
page_header("03", "CVA RISK & VAR",
            f"Deterministic stress scenarios · Monte Carlo CVA VaR · {_cp_label}")

if "sim_results" not in st.session_state:
    st.warning("Run the simulation in **01 Counterparty Portfolio** first.")
    st.stop()

results = st.session_state["sim_results"]
params = st.session_state["params"]
t = results["t"]
EE = results["EE"]
rf = float(params.get("risk_free", 0.03))

# Sidebar
_lbl = ('<div style="font-size:8px;color:#444;text-transform:uppercase;'
        'letter-spacing:.2em;padding:14px 0 8px;border-top:1px solid #1a1a1a;">{}</div>')

with st.sidebar:
    st.markdown('<div style="font-size:8px;color:#444;text-transform:uppercase;'
                'letter-spacing:.2em;padding:16px 0 8px;">BASE PARAMETERS</div>',
                unsafe_allow_html=True)
    # recup le CDS et la recovery from rating ou par défaut taux génériques
    _suggested_cds = _cp.get("suggested_cds", 120)
    _suggested_recovery = _cp.get("suggested_recovery", 0.40)
    st.caption(f"Indicative for {_cp.get('name', 'counterparty')} "
               f"({_cp.get('rating', '—')}): {_suggested_cds} bps CDS · "
               f"{_suggested_recovery:.0%} recovery")
    cds_bps = st.number_input("Base CDS spread (bps)", value=_suggested_cds,
                              min_value=1, max_value=5000, step=5)
    recovery = st.number_input("Recovery rate", value=_suggested_recovery,
                               min_value=0.0, max_value=0.99, step=0.01, format="%.2f")

    st.markdown(_lbl.format("MONTE CARLO CVA VAR"), unsafe_allow_html=True)
    n_scenarios = st.select_slider("Scenarios",
                                   options=[1000, 5000, 10000, 50000, 10_000], value=10000)
    horizon_days = st.number_input(
        # 10 jours par defaut
        "VaR horizon (days)", value=10, min_value=1, max_value=252, step=1)
    spread_vol = st.number_input(
        # vol annuel
        "Annual spread vol (bps)", value=60, min_value=1, max_value=500, step=5)
    mc_seed = st.number_input("Seed", value=42, min_value=0, step=1)

# Tabs
tab_stress, tab_var = st.tabs(["STRESS SCENARIOS", "MONTE CARLO CVA VAR"])


# STRESS SCENARIOS

with tab_stress:
    section_title("STRESS SCENARIOS")
    sb1, sb2 = st.columns([2, 1])
    with sb1:
        run_stress = st.button("▶  RUN STRESS TESTS", type="primary",
                               use_container_width=True)
    with sb2:
        if st.button("× CLEAR", key="stress_clr", use_container_width=True):
            st.session_state.pop("stress_results", None)
            st.rerun()

    if run_stress or "stress_results" in st.session_state:
        if run_stress:
            st.session_state["stress_results"] = run_stress_tests(
                EE_base=EE, t=t,
                base_cds_bps=cds_bps, base_recovery=recovery,
                risk_free_rate=rf)

        stress_rows = st.session_state["stress_results"]
        base_cva_cost = stress_rows[0]["Base CVA Cost"]  # CVA de base
        # pire CVA
        worst = max(stress_rows, key=lambda r: r["Stressed CVA Cost"])

        section_title("CVA COST SUMMARY")
        c1, c2, c3 = st.columns(3)
        c1.metric("Base CVA Cost",  fmt(base_cva_cost))
        c2.metric("Worst CVA Cost", fmt(worst["Stressed CVA Cost"]))
        c3.metric("Max Δ CVA Cost", fmt(worst["Δ CVA Cost"]))

        section_title("SCENARIO RESULTS")

        def color_pct(v):
            if v > 50:
                return "color: #FF3333"
            if v > 20:
                return "color: #FFB300"
            return "color: #33CC66"

        df_stress = pd.DataFrame(stress_rows)
        st.dataframe(
            df_stress[["Scenario", "Stressed CVA Cost",
                       "Base CVA Cost", "Δ CVA Cost", "% Change"]]
            .style
            .format({
                "Stressed CVA Cost": fmt,
                "Base CVA Cost":     fmt,
                "Δ CVA Cost":        fmt,
                "% Change":          "{:.1f}%",
            })
            .map(color_pct, subset=["% Change"]),
            use_container_width=True,
            hide_index=True,
        )

        section_title("CVA COST UNDER STRESS SCENARIOS")
        base_line = base_cva_cost / 1e6
        scenarios = [r["Scenario"] for r in stress_rows]
        cvas_m = [r["Stressed CVA Cost"] / 1e6 for r in stress_rows]
        colors = [
            RED if c > base_line * 1.50 else
            GOLD if c > base_line * 1.10 else
            ORANGE
            for c in cvas_m]
        fig_s = go.Figure()
        fig_s.add_trace(go.Bar(x=scenarios, y=cvas_m,
                        marker_color=colors, name="Stressed CVA Cost"))
        fig_s.add_hline(y=base_line, line=dict(color=ORANGE, dash="dash"),
                        annotation_text=f"Base: {fmt(base_cva_cost)}", annotation_font_color=ORANGE)
        apply_layout(fig_s, height=320, xaxis_title="Stress Scenario",
                     yaxis_title="CVA Cost ($M)", title="CVA Cost Under Stress Scenarios")
        st.plotly_chart(fig_s, use_container_width=True)


# MONTE CARLO CVA VAR

with tab_var:
    section_title("MONTE CARLO CVA VAR")
    vb1, vb2 = st.columns([2, 1])
    with vb1:
        run_var = st.button("▶  RUN MONTE CARLO CVA VAR", type="primary",
                            use_container_width=True)
    with vb2:
        if st.button("× CLEAR", key="var_clr", use_container_width=True):
            st.session_state.pop("var_results", None)
            st.rerun()

    if run_var or "var_results" in st.session_state:
        if run_var:
            st.session_state["var_results"] = simulate_cva_var(
                EE=EE, t=t,
                base_cds_bps=cds_bps,
                recovery=recovery,
                risk_free_rate=rf,
                spread_vol_bps=float(spread_vol),
                horizon_days=int(horizon_days),
                n_scenarios=int(n_scenarios),
                seed=int(mc_seed))

        vr = st.session_state["var_results"]

        section_title("CVA VAR SUMMARY")
        v1, v2, v3 = st.columns(3)
        v1.metric("Base CVA Cost",   fmt(vr["base_cva"]))
        v2.metric("CVA VaR 95%",     fmt(vr["var_95"]))
        v3.metric("CVA VaR 99%",     fmt(vr["var_99"]))

        v4, v5 = st.columns(2)
        v4.metric("Exp. Shortfall 99%", fmt(vr["es_99"]))
        v5.metric("Worst ΔCVA",         fmt(vr["worst_delta"]))

        # Chart 1: CVA distribution
        section_title("CHART 1 — DISTRIBUTION OF ΔCVA")
        delta_m = vr["delta_cva"] / 1e6
        fig_h = go.Figure()
        fig_h.add_trace(go.Histogram(
            x=delta_m, nbinsx=80,
            marker_color=ORANGE, opacity=0.7, name="ΔCVA"))
        fig_h.add_vline(x=vr["var_95"] / 1e6,
                        line=dict(color=GOLD, width=2, dash="dash"),
                        annotation_text="VaR 95%", annotation_font_color=GOLD,
                        annotation_position="top right")
        fig_h.add_vline(x=vr["var_99"] / 1e6,
                        line=dict(color=RED, width=2, dash="dash"),
                        annotation_text="VaR 99%", annotation_font_color=RED,
                        annotation_position="top right")
        fig_h.add_vline(x=vr["es_99"] / 1e6,
                        line=dict(color="#AA44FF", width=1.5, dash="dot"),
                        annotation_text="ES 99%", annotation_font_color="#AA44FF",
                        annotation_position="top left")
        apply_layout(fig_h, height=320,
                     xaxis_title="ΔCVA Cost ($M)", yaxis_title="Frequency",
                     title=f"ΔCVA Distribution — {n_scenarios:,} Scenarios",
                     bargap=0.02)
        st.plotly_chart(fig_h, use_container_width=True)

        # Chart 2: Stressed CDS spread distribution
        section_title("CHART 2 — SIMULATED CDS SPREAD DISTRIBUTION")
        fig_sp = go.Figure()
        fig_sp.add_trace(go.Histogram(
            x=vr["stressed_spreads"], nbinsx=80,
            marker_color=BLUE, opacity=0.7, name="Stressed CDS"))
        fig_sp.add_vline(x=cds_bps,
                         line=dict(color=ORANGE, width=2, dash="dash"),
                         annotation_text=f"Base {cds_bps} bps",
                         annotation_font_color=ORANGE)
        apply_layout(fig_sp, height=280,
                     xaxis_title="Stressed CDS Spread (bps)", yaxis_title="Frequency",
                     title="Simulated CDS Spread Distribution",
                     bargap=0.02)
        st.plotly_chart(fig_sp, use_container_width=True)

        # Chart 3: CVA cost vs stressed spread
        section_title("CHART 3 — CVA COST vs STRESSED CDS SPREAD")
        _max_pts = 3_000
        _idx = np.random.default_rng(0).choice(
            len(vr["stressed_spreads"]), size=min(_max_pts, len(vr["stressed_spreads"])),
            replace=False)
        fig_sc = go.Figure()
        fig_sc.add_trace(go.Scatter(
            x=vr["stressed_spreads"][_idx],
            y=vr["stressed_cvas"][_idx] / 1e6,
            mode="markers",
            marker=dict(color=ORANGE, size=3, opacity=0.4),
            name="Scenarios"))
        fig_sc.add_vline(x=cds_bps, line=dict(color=ORANGE, width=1.5, dash="dash"),
                         annotation_text="Base spread", annotation_font_color=ORANGE)
        apply_layout(fig_sc, height=280,
                     xaxis_title="Stressed CDS Spread (bps)",
                     yaxis_title="Stressed CVA Cost ($M)",
                     title="CVA Cost vs Stressed CDS Spread")
        st.plotly_chart(fig_sc, use_container_width=True)
