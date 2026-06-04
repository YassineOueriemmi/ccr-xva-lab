"""CCR & XVA Lab home page."""
from utils.ui import inject_css, bbg_header, ORANGE, GOLD, TEAL
import streamlit as st
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


inject_css()
bbg_header("CCR & XVA LAB")

st.markdown("""
<div style="padding:40px 0 28px;">
    <div style="font-size:clamp(28px,5vw,52px);font-weight:700;color:#fff;
                font-family:'IBM Plex Mono',monospace;margin-bottom:6px;letter-spacing:.03em;">
        CCR & <span style="color:#FF6600;">XVA</span> Lab
    </div>
    <div style="font-size:11px;color:#555;letter-spacing:.15em;
                text-transform:uppercase;margin-bottom:18px;">
        Built by Yassine Oueriemmi
    </div>
    <div style="font-size:12px;color:#888;max-width:560px;line-height:1.9;">
        A small Streamlit project built to understand how OTC derivatives exposure
        translates into CVA, XVA and CVA risk metrics.
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<hr style="border-color:#1a1a1a;margin:0 0 28px">',
            unsafe_allow_html=True)


# Navigation cards
st.markdown('<div style="font-size:8px;color:#444;text-transform:uppercase;'
            'letter-spacing:.2em;margin-bottom:14px;">PAGES</div>',
            unsafe_allow_html=True)

_pages = [
    ("01  COUNTERPARTY PORTFOLIO", "Set trade inputs and simulate the exposure profile.",
     ORANGE, "pages/01_Counterparty_Portfolio.py"),
    ("02  XVA METRICS",            "Translate exposure into simplified fair-value adjustments.",
     ORANGE, "pages/02_XVA_Metrics.py"),
    ("03  CVA RISK & VAR",         "Stress CVA drivers and simulate a spread-only ΔCVA distribution.",
     GOLD, "pages/03_CVA_VaR_Stress.py"),
    ("04  METHODOLOGY",            "Explain the workflow, assumptions and limitations.",
     TEAL,  "pages/04_Methodology.py"),
]
c1, c2 = st.columns(2, gap="small")
for i, (title, desc, color, page) in enumerate(_pages):
    col = c1 if i % 2 == 0 else c2
    with col:
        st.markdown(
            f'<div style="background:#0a0a0a;border:1px solid #1a1a1a;border-left:3px solid {color};'
            f'padding:16px 18px 12px;margin-bottom:8px;">'
            f'<div style="font-size:9px;color:{color};font-weight:700;letter-spacing:.1em;'
            f'margin-bottom:6px;">{title}</div>'
            f'<div style="font-size:9px;color:#555;line-height:1.6;">{desc}</div>'
            f'</div>', unsafe_allow_html=True
        )
        if st.button(f"→ Open", key=f"nav_{i}", use_container_width=True):
            st.switch_page(page)

st.markdown("<div style='margin-top:28px'></div>", unsafe_allow_html=True)
