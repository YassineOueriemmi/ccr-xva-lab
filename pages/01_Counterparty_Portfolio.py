from models.simulation import simulate_exposure
from utils.ui import (inject_css, page_header, section_title, formula_box, apply_layout,
                      bbg_header, disclaimer, ORANGE, BLUE, GREEN, RED, PURPLE, GOLD, MGRAY)
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

with st.expander("Trade structure & funding logic", expanded=False):
    st.markdown("""
The transaction consists of two offsetting legs:

**Leg A — Uncollateralized trade with the corporate counterparty**

The bank enters into a derivative transaction with a corporate client. As the trade evolves,
the bank may have a positive mark-to-market (MtM), meaning the counterparty owes money to
the bank. However, because the transaction is uncollateralized, no cash is exchanged before
maturity.

Economically, the bank holds a receivable on its balance sheet but cannot monetize it
immediately. The exposure creates economic value, yet no corresponding cash inflow is
received.

**Leg B — Cleared hedge with a CCP**

To hedge the market risk of Leg A, the bank enters into an offsetting transaction through a
Central Counterparty (CCP).

Unlike the corporate trade, the cleared hedge is fully collateralized. The CCP requires the
posting of Initial Margin (IM) upfront, which remains locked throughout the life of the
trade. Although the margin remains the bank's property, it cannot be freely used elsewhere
and therefore generates a funding requirement.

In addition, the CCP performs daily mark-to-market and exchanges Variation Margin (VM).
Whenever the hedge moves against the bank, cash must be posted immediately to the CCP.

As a result:
- The cost of financing the Initial Margin is captured by the **Margin Valuation Adjustment (MVA)**.
- The cost of financing the Variation Margin cash outflows, combined with the absence of
  offsetting cash inflows from the uncollateralized client trade, is captured by the
  **Funding Valuation Adjustment (FVA)**.

The core economic issue is that the bank can generate gains on the client trade without
receiving cash, while simultaneously being required to post cash to the CCP on the hedge.
This liquidity mismatch creates a funding need that persists throughout the life of the
transaction and gives rise to FVA.
""")

# Sidebar
with st.sidebar:
    st.markdown('<div style="font-size:8px;color:#444;text-transform:uppercase;'
                'letter-spacing:.2em;padding:16px 0 10px;">TRADE PARAMETERS</div>',
                unsafe_allow_html=True)

    notional = st.number_input(
        "Notional ($)", value=100000000, step=10000000, format="%d")
    current_mtm = st.number_input(
        "Current MtM ($)", value=2000000, min_value=1, step=100000, format="%d",
        help="Must be positive: a GBM applied to the MtM can never change sign, "
             "so a negative starting MtM would make EE structurally zero. This lab "
             "only covers CVA (positive exposure to the counterparty), not DVA.")
    maturity = st.number_input(
        "Maturity (years)", value=5.0, min_value=0.5, max_value=30.0, step=0.5)
    vol = st.number_input("Exposure volatility", value=0.15,
                          min_value=0.01, max_value=1.0, step=0.01, format="%.2f")
    n_steps = st.slider("Time steps", min_value=10,
                        max_value=60, value=20, step=5)
    n_scenarios = st.select_slider("Monte Carlo scenarios", options=[
                                   1000, 2000, 5000, 10000], value=5000)
    risk_free = st.number_input("Risk-free rate", value=0.03,
                                min_value=0.0, max_value=0.20, step=0.005, format="%.3f")


# Counterparty definition
section_title("COUNTERPARTY")

RATINGS = ["AAA", "AA", "A", "BBB", "BB", "B", "CCC"]

# Indicative CDS spread and recovery rate by rating bucket
RATING_CDS_BPS = {"AAA": 25, "AA": 40, "A": 60,
                  "BBB": 120, "BB": 250, "B": 450, "CCC": 800}
RATING_RECOVERY = {"AAA": 0.45, "AA": 0.45, "A": 0.42, "BBB": 0.40,
                   "BB": 0.35, "B": 0.32, "CCC": 0.28}

cols = st.columns([2, 1, 1, 1])
cols[0].markdown(
    '<div style="font-size:8px;color:#444;text-transform:uppercase;letter-spacing:.15em;">Name</div>', unsafe_allow_html=True)
cols[1].markdown(
    '<div style="font-size:8px;color:#444;text-transform:uppercase;letter-spacing:.15em;">Rating</div>', unsafe_allow_html=True)
cols[2].markdown(
    '<div style="font-size:8px;color:#444;text-transform:uppercase;letter-spacing:.15em;">Indicative CDS</div>', unsafe_allow_html=True)
cols[3].markdown(
    '<div style="font-size:8px;color:#444;text-transform:uppercase;letter-spacing:.15em;">Indicative Recovery</div>', unsafe_allow_html=True)

row = st.columns([2, 1, 1, 1])
cp_name = row[0].text_input(
    "Name", value="Counterparty 1", label_visibility="collapsed", key="cp_name")
cp_rating = row[1].selectbox(
    "Rating", RATINGS, index=3, label_visibility="collapsed", key="cp_rating")
suggested_cds = RATING_CDS_BPS[cp_rating]
suggested_recovery = RATING_RECOVERY[cp_rating]
row[2].markdown(
    f'<div style="padding-top:8px;color:{ORANGE};font-size:14px;">'f'{suggested_cds} bps</div>', unsafe_allow_html=True)
row[3].markdown(
    f'<div style="padding-top:8px;color:{ORANGE};font-size:14px;">'f'{suggested_recovery:.0%}</div>', unsafe_allow_html=True)

counterparty = {"name": cp_name, "rating": cp_rating,
                "suggested_cds": suggested_cds, "suggested_recovery": suggested_recovery}

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
            risk_free_rate=risk_free)
        st.session_state["sim_results"] = results
        st.session_state["params"] = {
            "notional": notional, "current_mtm": current_mtm,
            "maturity": maturity, "vol": vol, "n_steps": n_steps,
            "n_scenarios": n_scenarios, "risk_free": risk_free}
        st.session_state["counterparties"] = [counterparty]

    results = st.session_state["sim_results"]
    params = st.session_state["params"]
    t = results["t"]
    EE = results["EE"]
    PFE95 = results["PFE95"]

    section_title("EXPOSURE SUMMARY")

    def fmt(v):
        if abs(v) >= 1e6:
            return f"${v/1e6:.2f}M"
        if abs(v) >= 1e3:
            return f"${v/1e3:.1f}K"
        return f"${v:.2f}"

    c1, c2, c3, c4 = st.columns(4)
    # max = pic de risque, sous GBM pur la dispersion croît avec t donc EE culmine près de la maturité (pas de bosse comme un swap, c'est une limite du model mais on reste sur une simulation)
    c1.metric("Peak EE",   fmt(EE.max()))
    # même logique que pour le peak EE
    c2.metric("PFE 95%",   fmt(PFE95.max()))
    c3.metric("Notional",  fmt(notional))
    c4.metric("Maturity",  f"{params['maturity']:.1f}y")

    # Sample MtM paths
    section_title("SAMPLE MtM PATHS (50 scenarios)")
    mtm = results["mtm_paths"]
    n_show = min(50, mtm.shape[0])
    fig2 = go.Figure()
    for i in range(n_show):
        fig2.add_trace(go.Scatter(x=t, y=mtm[i]/1e6, mode="lines", line=dict(
            color=ORANGE, width=0.4), opacity=0.3, showlegend=False))
    fig2.add_trace(go.Scatter(x=t, y=EE/1e6, name="EE (mean)",
                   line=dict(color=ORANGE, width=2.5)))
    apply_layout(fig2, height=300, xaxis_title="Time (years)",
                 yaxis_title="MtM ($M)", title="Monte Carlo MtM Paths")
    st.plotly_chart(fig2, use_container_width=True)

    # Exposure profile
    section_title("EXPOSURE PROFILES")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=t, y=PFE95/1e6, name="PFE 95%",
                  line=dict(color=GOLD, width=1.5, dash="dash")))
    fig.add_trace(go.Scatter(x=t, y=EE/1e6, name="EE",
                  line=dict(color=ORANGE, width=2.5)))
    fig.add_hline(y=0, line=dict(color="#333", width=1))
    apply_layout(fig, height=300, xaxis_title="Time (years)",
                 yaxis_title="Exposure ($M)", title="Exposure Profile — EE · PFE 95%")
    st.plotly_chart(fig, use_container_width=True)
