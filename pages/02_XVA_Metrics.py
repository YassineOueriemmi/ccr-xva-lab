from models.xva import (calculate_cva, calculate_dva, calculate_fva, calculate_mva,
                        discount_factors)
from utils.ui import (inject_css, page_header, section_title, formula_box,
                      apply_layout, bbg_header, disclaimer, fmt,
                      ORANGE, BLUE, GREEN, RED, PURPLE, GOLD, MGRAY, TEAL)
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import streamlit as st
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


cps = st.session_state.get("counterparties", [{"name": "Counterparty 1"}])
_cp = cps[0] if cps else {}
_cp_label = f"{_cp.get('name', 'Counterparty 1')} ({_cp.get('rating', '—')})"

inject_css()
bbg_header(f"02 · XVA METRICS — {_cp_label}")
page_header("02", "XVA METRICS",
            f"Fair-value & funding adjustments · {_cp_label}")

if "sim_results" not in st.session_state:
    st.info("Run the simulation in **01 Counterparty Portfolio** first.")
    st.stop()

results = st.session_state["sim_results"]
params = st.session_state["params"]

t = results["t"]
EE = results["EE"]
ENE = results["ENE"]
rf = float(params.get("risk_free", 0.03))
notional = float(params.get("notional", 100e6))
vol = float(params.get("vol", 0.15))

# Sidebar
with st.sidebar:
    st.markdown('<div style="font-size:8px;color:#444;text-transform:uppercase;'
                'letter-spacing:.2em;padding:16px 0 10px;">COUNTERPARTY CREDIT</div>',
                unsafe_allow_html=True)
    _cp = cps[0] if cps else {}
    _suggested_cds = _cp.get("suggested_cds", 120)
    st.caption(f"Indicative CDS for {_cp.get('name', 'counterparty')} "
               f"({_cp.get('rating', '—')}): {_suggested_cds} bps")
    cds_bps = st.number_input("Counterparty CDS (bps)", value=_suggested_cds,
                              min_value=1, max_value=5000, step=5)
    recovery = st.number_input("Recovery rate", value=0.40,
                               min_value=0.0, max_value=0.99, step=0.01, format="%.2f")

    st.markdown('<div style="font-size:8px;color:#444;text-transform:uppercase;'
                'letter-spacing:.2em;padding:16px 0 10px;border-top:1px solid #1a1a1a;">'
                'BANK (OWN CREDIT)</div>', unsafe_allow_html=True)
    own_cds = st.number_input("Bank own CDS (bps)", value=80,
                              min_value=1, max_value=2000, step=5)
    own_rec = st.number_input("Bank own recovery", value=0.40,
                              min_value=0.0, max_value=0.99, step=0.01, format="%.2f")

    st.markdown('<div style="font-size:8px;color:#444;text-transform:uppercase;'
                'letter-spacing:.2em;padding:16px 0 10px;border-top:1px solid #1a1a1a;">'
                'FUNDING & MARGIN</div>', unsafe_allow_html=True)
    funding_spread = st.number_input("Funding spread (bps)", value=50,
                                     min_value=0, max_value=500, step=5)
    mpor_days = st.number_input("MPOR (days)", value=10,
                                min_value=1, max_value=30, step=1)
    init_margin = st.number_input("Initial margin ($M)", value=5.0,
                                  min_value=0.0, max_value=500.0, step=0.5,
                                  format="%.1f")

# Compute XVA
cva_result = calculate_cva(EE, t, cds_bps, recovery, rf)
dva_result = calculate_dva(ENE, t, own_cds, own_rec, rf)
fva_result = calculate_fva(EE, t, funding_spread, rf)
mva_result = calculate_mva(
    init_margin_dollars=init_margin * 1e6,
    t=t,
    funding_spread_bps=funding_spread,
    risk_free_rate=rf,
)


cva_cost = cva_result["CVA"]       # positive: cost to bank
dva_benefit = dva_result["DVA"]       # positive: benefit to bank
fva_cost = fva_result["FVA"]       # positive: cost to bank
mva_cost = mva_result["MVA"]       # positive: cost to bank

bva_impact = -cva_cost + dva_benefit           # negative when CVA > DVA
total_xva_cost = cva_cost - dva_benefit + fva_cost + mva_cost
risk_free_mtm = float(params.get("current_mtm", 2e6))
adjusted_value = risk_free_mtm - total_xva_cost

# XVA SUMMARY row 1
section_title("XVA SUMMARY")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Risk-Free MtM", fmt(risk_free_mtm))
c2.metric("CVA Cost",      fmt(cva_cost))
c3.metric("DVA Benefit",   fmt(dva_benefit))
c4.metric("BVA Impact (-CVA+DVA)", fmt(bva_impact))

# row 2
c5, c6, c7, c8 = st.columns(4)
c5.metric("FVA Cost",       fmt(fva_cost))
c6.metric("MVA Cost",       fmt(mva_cost))
c7.metric("Total XVA Cost", fmt(total_xva_cost))
c8.metric("XVA-Adj. Value", fmt(adjusted_value))

# Waterfall
section_title("WATERFALL — RISK-FREE VALUE → XVA-ADJUSTED VALUE")

wf_labels = ["MtM (Risk-Free)", "− CVA Cost", "+ DVA Benefit",
             "− FVA Cost", "− MVA Cost", "XVA-Adjusted"]
wf_y = [risk_free_mtm, -cva_cost, dva_benefit, -fva_cost, -mva_cost, 0]
wf_measure = ["absolute", "relative",
              "relative", "relative", "relative", "total"]
wf_text = [
    fmt(risk_free_mtm),
    f"−{fmt(cva_cost)}",
    f"+{fmt(dva_benefit)}",
    f"−{fmt(fva_cost)}",
    f"−{fmt(mva_cost)}",
    fmt(adjusted_value),
]

fig_wf = go.Figure(go.Waterfall(
    orientation="v",
    measure=wf_measure,
    x=wf_labels,
    y=wf_y,
    text=wf_text,
    textposition="outside",
    connector=dict(line=dict(color="#555", width=1.5, dash="dot")),
    decreasing=dict(marker_color=RED),
    increasing=dict(marker_color=GREEN),
    totals=dict(marker_color=ORANGE),
))
apply_layout(fig_wf, height=380,
             title="XVA Waterfall — Fair-Value Adjustments",
             showlegend=False)
st.plotly_chart(fig_wf, use_container_width=True)
