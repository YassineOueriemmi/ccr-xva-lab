""" Model Methodology"""
from utils.ui import (inject_css, page_header, section_title, formula_box,
                      bbg_header, ORANGE, GOLD, TEAL, BLUE, MGRAY)
import pandas as pd
import streamlit as st
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


inject_css()
bbg_header("04 · METHODOLOGY")
page_header("04", "METHODOLOGY",
            "Model workflow")


# 1. PROJECT OBJECTIVE

section_title("PROJECT OBJECTIVE")
st.markdown("""
<div style="font-size:10px;color:#888;line-height:1.9;margin-bottom:12px;">
The objective of this lab is to illustrate how an OTC derivative exposure profile can be
translated into simplified XVA and CVA risk metrics. 
</div>
<div style="font-size:9px;color:#555;line-height:2.0;padding-left:12px;">
· Simulate future MtM and exposure profiles (EE, ENE, PFE)<br>
· Compute simplified CVA, DVA, FVA and MVA fair-value adjustments<br>
· Perform deterministic CVA stress tests and spread-only Monte Carlo CVA VaR
</div>
""", unsafe_allow_html=True)


# 2. WORKFLOW OVERVIEW

section_title("WORKFLOW OVERVIEW")

_steps = [
    ("01", "Trade Inputs",
     "Notional · MtM · maturity · volatility",             ORANGE),
    ("02", "Exposure Simulation",
     "MtM paths → EE · ENE · PFE",                         ORANGE),
    ("03", "XVA Metrics",
     "CVA · DVA · FVA · MVA · adjusted value",              GOLD),
    ("04", "CVA Risk & VaR",
     "Stress scenarios · Monte Carlo ΔCVA distribution",    GOLD),
    ("05", "Interpretation",
     "Understand risk drivers — not production numbers",     TEAL),
]
cols = st.columns(5)
for col, (num, title, desc, color) in zip(cols, _steps):
    col.markdown(
        f'<div style="background:#0a0a0a;border:1px solid #1a1a1a;border-top:2px solid {color};'
        f'padding:14px 12px;text-align:center;">'
        f'<div style="font-size:9px;color:{color};font-weight:700;margin-bottom:6px;">{num}</div>'
        f'<div style="font-size:10px;color:#ccc;font-weight:600;margin-bottom:6px;">{title}</div>'
        f'<div style="font-size:8px;color:#555;line-height:1.5;">{desc}</div>'
        f'</div>', unsafe_allow_html=True
    )

st.markdown("<div style='margin-top:20px'></div>", unsafe_allow_html=True)


# 3. EXPOSURE ENGINE

section_title("1 — EXPOSURE ENGINE")
st.markdown("""
<div style="font-size:9px;color:#555;line-height:1.9;margin-bottom:12px;">
The exposure module simulates future MtM paths for a simplified OTC trade using
Geometric Brownian Motion. Positive MtM generates counterparty exposure for the bank,
negative MtM is used to compute expected negative exposure for DVA.
</div>""", unsafe_allow_html=True)

with st.expander("Formulas", expanded=False):
    formula_box("Exposure(t) = max(MtM(t), 0)")
    formula_box("EE(t) = E[ max(MtM(t), 0) ] &nbsp;— Expected Exposure")
    formula_box(
        "ENE(t) = E[ max(−MtM(t), 0) ] &nbsp;— Expected Negative Exposure")
    formula_box("PFE₉₅(t) = 95th percentile of Exposure(t)")


# 4. XVA METRICS

section_title("2 — XVA METRICS")
st.markdown("""
<div style="font-size:9px;color:#555;line-height:1.9;margin-bottom:12px;">
The XVA page converts the exposure profile into simplified fair-value adjustments.
CVA and DVA are based on default probabilities implied from CDS spreads.
FVA and MVA use simplified funding cost approximations over the EE profile.
</div>""", unsafe_allow_html=True)

with st.expander("Formulas", expanded=False):
    formula_box("CVA = Σ DF(tᵢ) × ΔPD_cp(tᵢ) × LGD × EE(tᵢ)")
    formula_box("DVA = Σ DF(tᵢ) × ΔPD_bank(tᵢ) × LGD_bank × ENE(tᵢ)")
    formula_box("FVA = Σ DF(tᵢ) × s_f × EE(tᵢ) × Δt")
    formula_box("MVA = Σ DF(tᵢ) × s_f × IM × Δt")
    formula_box("Adjusted Value = Risk-Free MtM − CVA + DVA − FVA − MVA")
    formula_box(
        "λ = CDS spread / LGD &nbsp;|&nbsp; ΔPD(tᵢ) = exp(−λ·tᵢ₋₁) − exp(−λ·tᵢ)")


# 5. CVA RISK & VAR

section_title("3 — CVA RISK & VAR")

col_s, col_v = st.columns(2, gap="large")

with col_s:
    st.markdown("""
    <div style="font-size:9px;color:#FF6600;font-weight:700;text-transform:uppercase;
                letter-spacing:.1em;margin-bottom:8px;">Deterministic Stress Testing</div>
    <div style="font-size:9px;color:#555;line-height:1.9;margin-bottom:10px;">
    The stress module reuses the EE profile from the exposure engine and applies
    analytical shocks to credit spreads, recovery rates and exposure levels.
    </div>
    <div style="font-size:9px;color:#555;line-height:2.0;padding-left:12px;">
    · Spread shocks increase the implied hazard rate → higher CVA cost.<br>
    · Recovery shocks increase LGD (λ kept constant).<br>
    · Exposure vol shocks scale the EE profile.
    </div>""", unsafe_allow_html=True)
    with st.expander("Formula", expanded=False):
        formula_box("Δ CVA Cost = CVA(stressed) − CVA(base)")

with col_v:
    st.markdown("""
    <div style="font-size:9px;color:#FF6600;font-weight:700;text-transform:uppercase;
                letter-spacing:.1em;margin-bottom:8px;">Monte Carlo CVA VaR</div>
    <div style="font-size:9px;color:#555;line-height:1.9;margin-bottom:10px;">
    The MC module simulates random CDS spread shocks over a selected horizon.
    For each shocked spread the CVA is recalculated analytically and a ΔCVA
    distribution is obtained.
    </div>
    <div style="font-size:9px;color:#555;line-height:2.0;padding-left:12px;">
    · Spread-only VaR — the EE profile is kept fixed.<br>
    · CVA VaR 99% = Q₉₉(ΔCVA distribution).<br>
    · ES 99% = average ΔCVA in the tail beyond VaR 99%.
    </div>""", unsafe_allow_html=True)
    with st.expander("Formulas", expanded=False):
        formula_box("shock = σ_spread × √(h/252) × Z,  Z ~ N(0,1)")
        formula_box("CVA VaR 99% = Q₉₉(ΔCVA)")
        formula_box("ES 99% = E[ ΔCVA | ΔCVA ≥ VaR₉₉ ]")
