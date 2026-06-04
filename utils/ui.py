"""
utils/ui.py — CCR & XVA Lab
Design system: Bloomberg-style dark theme, identical to VOL LAB.
"""
import streamlit as st

# ── Color tokens ─────────────────────────────────────────────────────────────
BG      = "#000000"
SURFACE = "#0a0a0a"
BORDER  = "#1a1a1a"
ORANGE  = "#FF6600"
WHITE   = "#FFFFFF"
LGRAY   = "#CCCCCC"
MGRAY   = "#888888"
DGRAY   = "#444444"
GREEN   = "#00CC44"
RED     = "#FF3333"
BLUE    = "#0099FF"
GOLD    = "#FFB300"
PURPLE  = "#AA44FF"
TEAL    = "#00BBBB"

# ── Plotly layout ─────────────────────────────────────────────────────────────
LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="#0a0a0a",
    font=dict(family="IBM Plex Mono, Courier New, monospace", size=10, color="#888"),
    margin=dict(t=36, b=32, l=44, r=20),
    xaxis=dict(gridcolor="#1a1a1a", zerolinecolor="#222", color="#888"),
    yaxis=dict(gridcolor="#1a1a1a", zerolinecolor="#222", color="#888"),
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="#1a1a1a", borderwidth=1,
                font=dict(size=9, color="#888")),
    hoverlabel=dict(bgcolor="#111", bordercolor="#FF6600",
                    font=dict(family="IBM Plex Mono", size=11, color="#fff")),
)

def apply_layout(fig, height=340, **kw):
    fig.update_layout(**{**LAYOUT, "height": height, **kw})
    return fig


# ── CSS ───────────────────────────────────────────────────────────────────────
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'IBM Plex Mono', 'Courier New', monospace !important;
    background: #000 !important;
}
.stApp { background: #000 !important; }
.block-container { padding: 1.5rem 2rem !important; max-width: 1400px !important; }

[data-testid="collapsedControl"] { display: none !important; }
[data-testid="stSidebarCollapseButton"] { display: none !important; }
button[aria-label="Close sidebar"] span[data-testid="stIconMaterial"] { display: none !important; }

/* ── Sidebar base ── */
section[data-testid="stSidebar"] {
    background: #080808 !important;
    border-right: 1px solid #1a1a1a !important;
}
section[data-testid="stSidebar"] * { font-family: 'IBM Plex Mono', monospace !important; }

/* ── Sidebar nav links ── */
section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a {
    border-radius: 0 !important;
    font-size: 10px !important;
    text-transform: uppercase;
    color: #444 !important;
    padding: 8px 14px !important;
    border-left: 2px solid transparent !important;
    letter-spacing: .1em;
}
section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a:hover,
section[data-testid="stSidebar"] [data-testid="stSidebarNav"] [aria-current] {
    background: #111 !important;
    color: #FF6600 !important;
    border-left-color: #FF6600 !important;
}

/* ── Sidebar nav title ── */
section[data-testid="stSidebar"] [data-testid="stSidebarNav"]::before {
    content: "CCR & XVA LAB";
    display: block;
    font-size: 14px;
    font-weight: 700;
    color: #FF6600;
    padding: 16px 14px 10px;
    letter-spacing: .15em;
    border-bottom: 1px solid #1a1a1a;
    margin-bottom: 8px;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: #000 !important; border-bottom: 1px solid #1a1a1a !important; gap: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important; color: #444 !important;
    font-size: 9px !important; text-transform: uppercase; letter-spacing: .15em;
    padding: 10px 20px !important; border-bottom: 2px solid transparent !important;
    font-family: 'IBM Plex Mono', monospace !important;
}
.stTabs [aria-selected="true"] { color: #FF6600 !important; border-bottom-color: #FF6600 !important; }

/* ── Metrics ── */
[data-testid="stMetric"] {
    background: #0a0a0a !important; border: 1px solid #1a1a1a !important;
    border-top: 2px solid #FF6600 !important; border-radius: 0 !important;
    padding: 12px 16px !important;
}
[data-testid="stMetricValue"] {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 20px !important; font-weight: 600 !important; color: #FF6600 !important;
}
[data-testid="stMetricLabel"] {
    font-family: 'IBM Plex Mono', monospace !important; font-size: 8px !important;
    text-transform: uppercase !important; letter-spacing: .2em !important; color: #444 !important;
}

/* ── Buttons ── */
.stButton button {
    background: #0a0a0a !important; border: 1px solid #222 !important;
    color: #666 !important; font-family: 'IBM Plex Mono', monospace !important;
    font-size: 9px !important; text-transform: uppercase;
    letter-spacing: .12em; border-radius: 0 !important; transition: all .1s;
}
.stButton button:hover { border-color: #FF6600 !important; color: #FF6600 !important; }
button[kind="primary"] {
    background: #FF6600 !important; color: #000 !important;
    border: none !important; font-weight: 700 !important;
}

/* ── Inputs ── */
.stSelectbox label, .stNumberInput label, .stSlider label {
    font-size: 8px !important; text-transform: uppercase !important;
    letter-spacing: .2em !important; color: #444 !important;
}

/* ── Dataframe ── */
.stDataFrame { border: 1px solid #1a1a1a !important; border-radius: 0 !important; }

hr { border-color: #1a1a1a !important; }
.stInfo, .stSuccess, .stWarning, .stError { border-radius: 0 !important; }

/* ── KPI band ── */
.kpi-band {
    display: grid; grid-template-columns: repeat(6, 1fr);
    gap: 1px; background: #1a1a1a; border: 1px solid #1a1a1a; margin-bottom: 20px;
}
.kpi-cell  { background: #0a0a0a; padding: 12px 16px; border-top: 2px solid; }
.kpi-lbl   { font-size: 7px; color: #444; text-transform: uppercase; letter-spacing: .2em; margin-bottom: 4px; }
.kpi-sym   { font-size: 10px; font-weight: 700; margin-bottom: 2px; }
.kpi-val   { font-size: 18px; font-weight: 600; line-height: 1.1; font-family: 'IBM Plex Mono', monospace; }
.kpi-sub   { font-size: 7px; color: #444; margin-top: 2px; }
.pos { color: #00CC44; }
.neg { color: #FF3333; }
.neu { color: #FF6600; }

/* ── Section title ── */
.sec-ttl {
    font-size: 8px; color: #FF6600; text-transform: uppercase;
    letter-spacing: .25em; border-bottom: 1px solid #1a1a1a;
    padding-bottom: 6px; margin: 20px 0 12px;
}

/* ── Formula ── */
.formula {
    background: #0a0a0a; border: 1px solid #1a1a1a;
    border-left: 2px solid #FF6600; padding: 10px 14px;
    font-size: 11px; color: #888; margin: 10px 0;
    font-family: 'IBM Plex Mono', monospace;
}
.formula strong { color: #FF6600; }

/* ── Page header ── */
.page-hdr {
    border-bottom: 1px solid #1a1a1a; padding-bottom: 14px;
    margin-bottom: 20px; display: flex; align-items: flex-end; gap: 16px;
}
.page-num   { font-size: 40px; font-weight: 700; color: #1a1a1a; line-height: 1; }
.page-title { font-size: 20px; font-weight: 600; color: #fff; }
.page-sub   { font-size: 8px; color: #444; text-transform: uppercase; letter-spacing: .2em; margin-top: 3px; }

/* ── Top bar ── */
.bbg-bar {
    background: #FF6600; color: #000;
    padding: 8px 24px; margin: -24px -32px 20px -32px;
    font-size: 10px; font-weight: 700; letter-spacing: .2em;
    text-transform: uppercase; display: flex;
    justify-content: space-between; align-items: center;
}

/* ── Disclaimer ── */
.disclaimer {
    background: #0a0a0a; border: 1px solid #333;
    border-left: 2px solid #FFB300; padding: 8px 14px;
    font-size: 9px; color: #555; margin: 12px 0; letter-spacing: .04em;
}
</style>
"""

def inject_css():
    st.markdown(CSS, unsafe_allow_html=True)

def bbg_header(right=""):
    st.markdown(
        f'<div class="bbg-bar">'
        f'<span>▌ CCR & XVA LAB — COUNTERPARTY CREDIT RISK · XVA · REGULATORY METRICS</span>'
        f'<span>{right}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

def page_header(num, title, subtitle):
    st.markdown(
        f'<div class="page-hdr">'
        f'<div class="page-num">{num}</div>'
        f'<div><div class="page-title">{title}</div>'
        f'<div class="page-sub">{subtitle}</div></div>'
        f'</div>',
        unsafe_allow_html=True,
    )

def section_title(text, color=ORANGE):
    st.markdown(f'<div class="sec-ttl" style="color:{color}">{text}</div>', unsafe_allow_html=True)

def formula_box(html):
    st.markdown(f'<div class="formula">{html}</div>', unsafe_allow_html=True)

def disclaimer(text):
    st.markdown(f'<div class="disclaimer">⚠ {text}</div>', unsafe_allow_html=True)

def kpi_band(items):
    """items: list of (label, sym, val_str, sub, color)"""
    html = '<div class="kpi-band">'
    for label, sym, val, sub, color in items:
        neg = str(val).startswith("-")
        pos = not neg and str(val) not in ("—", "0", "0.00")
        cls = "neg" if neg else ("pos" if pos else "neu")
        html += (
            f'<div class="kpi-cell" style="border-top-color:{color}">'
            f'<div class="kpi-lbl">{label}</div>'
            f'<div class="kpi-sym" style="color:{color}">{sym}</div>'
            f'<div class="kpi-val {cls}">{val}</div>'
            f'<div class="kpi-sub">{sub}</div>'
            f'</div>'
        )
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)

def apply_layout(fig, height=340, **kw):
    fig.update_layout(**{**LAYOUT, "height": height, **kw})
    return fig

def fmt(v):
    """Format a dollar value."""
    if abs(v) >= 1e9: return f"${v/1e9:.2f}B"
    if abs(v) >= 1e6: return f"${v/1e6:.2f}M"
    if abs(v) >= 1e3: return f"${v/1e3:.1f}K"
    return f"${v:.2f}"

def fmt_bps(v):
    return f"{v:.0f} bps"

def fmt_pct(v):
    return f"{v*100:.2f}%"
