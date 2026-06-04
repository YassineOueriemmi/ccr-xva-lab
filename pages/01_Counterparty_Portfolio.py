"""
Portfolio setup and exposure simulation
"""
from models.simulation import simulate_exposure
from utils.ui import (inject_css, page_header, section_title, formula_box,
                      apply_layout, bbg_header, disclaimer,
                      ORANGE, BLUE, GREEN, RED, PURPLE, GOLD, MGRAY)
import plotly.graph_objects as go
import numpy as np
import streamlit as st
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


inject_css()
bbg_header("01 · COUNTERPARTY PORTFOLIO & EXPOSURE SIMULATION")
page_header("01", "COUNTERPARTY PORTFOLIO",
            "Counterparty setup · GBM exposure simulation")

# Sidebar
with st.sidebar:
    st.markdown('<div style="font-size:8px;color:#444;text-transform:uppercase;'
                'letter-spacing:.2em;padding:16px 0 10px;">TRADE PARAMETERS</div>',
                unsafe_allow_html=True)

    notional = st.number_input(
        "Notional ($)", value=100_000_000, step=10_000_000, format="%d")
    current_mtm = st.number_input(
        "Current MtM ($)", value=2_000_000, step=100_000, format="%d")
    maturity = st.number_input(
        "Maturity (years)", value=5.0, min_value=0.5, max_value=30.0, step=0.5)
    vol = st.number_input("Exposure volatility", value=0.15, min_value=0.01, max_value=1.0,
                          step=0.01, format="%.2f")
    n_steps = st.slider("Time steps", min_value=10,
                        max_value=60, value=20, step=5)
    n_scenarios = st.select_slider("Monte Carlo scenarios", options=[
                                   1000, 2000, 5000, 10000], value=5000)
    risk_free = st.number_input("Risk-free rate", value=0.03, min_value=0.0, max_value=0.20,
                                step=0.005, format="%.3f")


# Counterparty definition
section_title("COUNTERPARTY")

RATINGS = ["AAA", "AA", "A", "BBB", "BB", "B", "CCC"]

cols = st.columns([2, 1])
cols[0].markdown(
    '<div style="font-size:8px;color:#444;text-transform:uppercase;letter-spacing:.15em;">Name</div>', unsafe_allow_html=True)
cols[1].markdown(
    '<div style="font-size:8px;color:#444;text-transform:uppercase;letter-spacing:.15em;">Rating</div>', unsafe_allow_html=True)

row = st.columns([2, 1])
cp_name = row[0].text_input(
    "Name", value="Counterparty 1", label_visibility="collapsed", key="cp_name")
cp_rating = row[1].selectbox(
    "Rating", RATINGS, index=3, label_visibility="collapsed", key="cp_rating")

counterparty = {"name": cp_name, "rating": cp_rating}

# Run simulation
st.markdown("---")
_col_btn, _col_clr = st.columns([2, 1])
with _col_btn:
    run = st.button("▶  RUN SIMULATION", type="primary",
                    use_container_width=True)
with _col_clr:
    if st.button("× CLEAR", key="sim_clr", use_container_width=True):
        for k in ("sim_results", "params", "counterparties"):
            st.session_state.pop(k, None)
        st.rerun()

if run or ("sim_results" in st.session_state):
    if run:
        results = simulate_exposure(
            notional=notional,
            current_mtm=current_mtm,
            vol=vol,
            maturity=maturity,
            n_steps=n_steps,
            n_scenarios=n_scenarios,
            risk_free_rate=risk_free,
            collateralized=False,
        )
        st.session_state["sim_results"] = results
        st.session_state["params"] = {
            "notional": notional, "current_mtm": current_mtm,
            "maturity": maturity, "vol": vol, "n_steps": n_steps,
            "n_scenarios": n_scenarios, "risk_free": risk_free,
        }
        st.session_state["counterparties"] = [counterparty]

    results = st.session_state["sim_results"]
    params = st.session_state["params"]
    t = results["t"]
    EE = results["EE"]
    PFE95 = results["PFE95"]

    # KPI band
    section_title("EXPOSURE SUMMARY")

    def fmt(v):
        if abs(v) >= 1e6:
            return f"${v/1e6:.2f}M"
        if abs(v) >= 1e3:
            return f"${v/1e3:.1f}K"
        return f"${v:.2f}"

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Peak EE",   fmt(EE.max()))
    c2.metric("PFE 95%",   fmt(PFE95.max()))
    c3.metric("Notional",  fmt(notional))
    c4.metric("Maturity",  f"{params['maturity']:.1f}y")

    # Sample MtM paths
    section_title("SAMPLE MtM PATHS (50 scenarios)")
    mtm = results["mtm_paths"]
    n_show = min(50, mtm.shape[0])
    fig2 = go.Figure()
    for i in range(n_show):
        fig2.add_trace(go.Scatter(x=t, y=mtm[i]/1e6, mode="lines",
                                  line=dict(color=ORANGE, width=0.4),
                                  opacity=0.3, showlegend=False))
    fig2.add_trace(go.Scatter(x=t, y=EE/1e6, name="EE (mean)",
                              line=dict(color=ORANGE, width=2.5)))
    apply_layout(fig2, height=300,
                 xaxis_title="Time (years)", yaxis_title="MtM ($M)",
                 title="Monte Carlo MtM Paths")
    st.plotly_chart(fig2, use_container_width=True)

    # Exposure distribution at selected time step
    section_title("EXPOSURE DISTRIBUTION — PFE CROSS-SECTION")
    t_idx = st.slider(
        "Time step",
        min_value=1, max_value=len(t) - 1, value=len(t) // 2,
        key="dist_slider",
    )
    exp_slice = results["exposure_pos"][:, t_idx] / 1e6
    ee_val = EE[t_idx] / 1e6
    pfe_val = PFE95[t_idx] / 1e6
    pfe99_val = results["PFE99"][t_idx] / 1e6
    t_val = t[t_idx]

    fig_dist = go.Figure()
    fig_dist.add_trace(go.Histogram(
        x=exp_slice,
        nbinsx=60,
        marker_color=ORANGE,
        opacity=0.6,
        name="Exposure dist.",
    ))
    fig_dist.add_vline(x=ee_val,    line=dict(color=ORANGE, width=2, dash="dot"),
                       annotation_text=f"EE {ee_val:.2f}M",
                       annotation_font_color=ORANGE, annotation_position="top right")
    fig_dist.add_vline(x=pfe_val,   line=dict(color=GOLD,   width=2, dash="dash"),
                       annotation_text=f"PFE 95% {pfe_val:.2f}M",
                       annotation_font_color=GOLD, annotation_position="top right")
    fig_dist.add_vline(x=pfe99_val, line=dict(color=RED,    width=1.5, dash="dash"),
                       annotation_text=f"PFE 99% {pfe99_val:.2f}M",
                       annotation_font_color=RED, annotation_position="top right")
    apply_layout(fig_dist, height=300,
                 xaxis_title="Exposure ($M)",
                 yaxis_title="# scenarios",
                 title=f"Exposure Distribution at t = {t_val:.2f} yr  "
                 f"({results['exposure_pos'].shape[0]:,} scenarios)",
                 bargap=0.02)
    st.plotly_chart(fig_dist, use_container_width=True)

    # Exposure profile
    section_title("EXPOSURE PROFILES")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=t, y=PFE95/1e6, name="PFE 95%",
                             line=dict(color=GOLD, width=1.5, dash="dash")))
    fig.add_trace(go.Scatter(x=t, y=EE/1e6, name="EE",
                             line=dict(color=ORANGE, width=2.5)))
    fig.add_vline(x=t_val, line=dict(color="#333", width=1, dash="dot"))
    fig.add_hline(y=0, line=dict(color="#333", width=1))
    apply_layout(fig, height=300,
                 xaxis_title="Time (years)", yaxis_title="Exposure ($M)",
                 title="Exposure Profile — EE · PFE 95%")
    st.plotly_chart(fig, use_container_width=True)

else:
    st.info("Set trade parameters and click **▶ RUN SIMULATION**.")
