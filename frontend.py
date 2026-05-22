"""
Groundwater Quality Risk Assessment — Streamlit Frontend (Redesigned)
=====================================================================
Sleek, minimal, startup-grade UI inspired by Vercel/Stripe/Notion.
Connects to the FastAPI backend at localhost:8000.
All API calls and data structures are preserved exactly.
"""

import streamlit as st
import requests
import json
import math

# ─── Page Config ────────────────────────────────────────────
st.set_page_config(
    page_title="Groundwater Risk Assessment",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded",
)

API_URL = "http://localhost:8000"

# ─── Design System ──────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Reset & Base ── */
html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
    background-color: #141820 !important;
    color: #d4d8e0 !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

[data-testid="stHeader"] {
    background-color: #141820 !important;
}

[data-testid="stSidebar"] {
    background-color: #111518 !important;
    border-right: 1px solid #1e2430 !important;
}

[data-testid="stSidebar"] * {
    color: #8b93a1 !important;
}

/* ── Headings ── */
h1 { color: #e8ecf1 !important; font-weight: 700 !important; letter-spacing: -0.03em !important; font-size: 1.6rem !important; }
h2 { color: #e0e4ea !important; font-weight: 600 !important; letter-spacing: -0.02em !important; font-size: 1.2rem !important; }
h3 { color: #c8cdd6 !important; font-weight: 600 !important; font-size: 1rem !important; }
h4 { color: #b0b8c4 !important; font-weight: 500 !important; font-size: 0.9rem !important; }

p, span, label, .stMarkdown { color: #a0a8b4 !important; }

/* ── Inputs ── */
[data-testid="stNumberInput"] input,
[data-testid="stTextInput"] input,
.stSelectbox > div > div,
.stTextInput > div > div > input {
    background-color: #1a1f28 !important;
    border: 1px solid #262d3a !important;
    border-radius: 10px !important;
    color: #d4d8e0 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.875rem !important;
    padding: 0.5rem 0.75rem !important;
    transition: border-color 0.2s ease !important;
}

[data-testid="stNumberInput"] input:focus,
[data-testid="stTextInput"] input:focus {
    border-color: #3b82f6 !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.1) !important;
    outline: none !important;
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #2563eb, #3b82f6) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.6rem 2rem !important;
    font-weight: 600 !important;
    font-size: 0.875rem !important;
    letter-spacing: 0.01em !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 2px 8px rgba(37,99,235,0.25) !important;
}

.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 14px rgba(37,99,235,0.35) !important;
}

/* ── Secondary buttons (used for sample data) ── */
[data-testid="stColumns"] .stButton > button[kind="secondary"],
.stButton > button[data-testid*="secondary"] {
    background: #1e2430 !important;
    color: #a0a8b4 !important;
    box-shadow: none !important;
    border: 1px solid #262d3a !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 0 !important;
    background: #1a1f28 !important;
    border-radius: 10px !important;
    padding: 4px !important;
    border: 1px solid #1e2430 !important;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 8px !important;
    padding: 8px 16px !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    color: #7a8290 !important;
    background: transparent !important;
    border: none !important;
    transition: all 0.15s ease !important;
}

.stTabs [aria-selected="true"] {
    background: #262d3a !important;
    color: #e0e4ea !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.2) !important;
}

.stTabs [data-baseweb="tab-highlight"] {
    display: none !important;
}

.stTabs [data-baseweb="tab-border"] {
    display: none !important;
}

/* ── Expander ── */
[data-testid="stExpander"] {
    background: #1a1f28 !important;
    border: 1px solid #1e2430 !important;
    border-radius: 10px !important;
    overflow: hidden;
}

[data-testid="stExpander"] summary {
    color: #a0a8b4 !important;
    font-size: 0.85rem !important;
}

/* ── Metrics ── */
[data-testid="stMetric"] {
    background: #1a1f28 !important;
    border: 1px solid #1e2430 !important;
    border-radius: 10px !important;
    padding: 16px !important;
}

[data-testid="stMetricValue"] {
    color: #e0e4ea !important;
    font-weight: 700 !important;
}

[data-testid="stMetricLabel"] {
    color: #6b7280 !important;
    font-size: 0.75rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
}

/* ── Info/Success/Warning/Error Boxes ── */
[data-testid="stAlert"] {
    border-radius: 10px !important;
    border: none !important;
    font-size: 0.85rem !important;
}

.stAlert [data-testid="stAlertContentInfo"] { background: #17202e !important; border-left: 3px solid #3b82f6 !important; }
.stAlert [data-testid="stAlertContentSuccess"] { background: #142118 !important; border-left: 3px solid #4ade80 !important; }
.stAlert [data-testid="stAlertContentWarning"] { background: #1e1c14 !important; border-left: 3px solid #f59e0b !important; }
.stAlert [data-testid="stAlertContentError"] { background: #1e1417 !important; border-left: 3px solid #ef4444 !important; }

/* ── Dividers ── */
hr { border-color: #1e2430 !important; opacity: 0.5 !important; }

/* ── Radio as Cards ── */
.stRadio > div {
    gap: 0 !important;
}

.stRadio > div > label {
    background: #1a1f28 !important;
    border: 1px solid #262d3a !important;
    border-radius: 10px !important;
    padding: 12px 16px !important;
    margin: 4px 0 !important;
    transition: all 0.15s ease !important;
    cursor: pointer !important;
}

.stRadio > div > label:hover {
    border-color: #3b82f6 !important;
    background: #1e2430 !important;
}

.stRadio > div > label[data-checked="true"] {
    border-color: #3b82f6 !important;
    background: rgba(59,130,246,0.08) !important;
}

/* ── Custom Classes ── */
.risk-safe {
    background: rgba(74,222,128,0.08);
    color: #4ade80;
    border-radius: 12px;
    padding: 16px 24px;
    font-size: 1.3rem;
    font-weight: 700;
    border-left: 4px solid #4ade80;
    letter-spacing: -0.02em;
}

.risk-moderate {
    background: rgba(245,158,11,0.08);
    color: #f59e0b;
    border-radius: 12px;
    padding: 16px 24px;
    font-size: 1.3rem;
    font-weight: 700;
    border-left: 4px solid #f59e0b;
    letter-spacing: -0.02em;
}

.risk-high {
    background: rgba(239,68,68,0.08);
    color: #ef4444;
    border-radius: 12px;
    padding: 16px 24px;
    font-size: 1.3rem;
    font-weight: 700;
    border-left: 4px solid #ef4444;
    letter-spacing: -0.02em;
}

.risk-unknown {
    background: rgba(107,114,128,0.08);
    color: #6b7280;
    border-radius: 12px;
    padding: 16px 24px;
    font-size: 1.3rem;
    font-weight: 700;
    border-left: 4px solid #6b7280;
    letter-spacing: -0.02em;
}

.glass-card {
    background: #1a1f28;
    border: 1px solid #262d3a;
    border-radius: 12px;
    padding: 20px;
    margin: 8px 0;
}

.param-exceeded {
    background: rgba(245,158,11,0.06);
    border-left: 3px solid #f59e0b;
    padding: 12px 16px;
    border-radius: 8px;
    margin: 6px 0;
    font-size: 0.875rem;
}

.param-ok {
    background: rgba(74,222,128,0.04);
    border-left: 3px solid rgba(74,222,128,0.4);
    padding: 12px 16px;
    border-radius: 8px;
    margin: 6px 0;
    font-size: 0.875rem;
}

.advice-box {
    background: rgba(59,130,246,0.06);
    border-radius: 12px;
    padding: 16px;
    border-left: 3px solid #3b82f6;
    margin-top: 12px;
}

.factor-bar {
    background: #262d3a;
    border-radius: 6px;
    height: 6px;
    margin: 4px 0;
}

.factor-fill {
    background: linear-gradient(90deg, #3b82f6, #60a5fa);
    border-radius: 6px;
    height: 6px;
    transition: width 0.5s ease;
}

.section-label {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #5b6370;
    font-weight: 600;
    margin-bottom: 8px;
}

.confidence-bar-bg {
    background: #262d3a;
    border-radius: 8px;
    height: 8px;
    width: 100%;
    overflow: hidden;
}

.brand-subtle {
    font-size: 0.7rem;
    color: #3b4555;
    letter-spacing: 0.05em;
}

/* ── Selectbox ── */
.stSelectbox [data-baseweb="select"] > div {
    background: #1a1f28 !important;
    border: 1px solid #262d3a !important;
    border-radius: 10px !important;
}

/* ── Caption ── */
.stCaption, [data-testid="stCaptionContainer"] {
    color: #5b6370 !important;
    font-size: 0.75rem !important;
}

/* ── Spinner ── */
.stSpinner > div {
    border-top-color: #3b82f6 !important;
}

/* ── JSON viewer ── */
[data-testid="stJson"] {
    background: #111518 !important;
    border-radius: 10px !important;
    border: 1px solid #1e2430 !important;
}
</style>
""", unsafe_allow_html=True)


# ─── Header ─────────────────────────────────────────────────
st.markdown("""
<div style="display:flex; align-items:center; gap:14px; margin-bottom:4px;">
    <div style="background:rgba(59,130,246,0.1); padding:10px; border-radius:10px;">
        <span style="font-size:1.5rem;">💧</span>
    </div>
    <div>
        <h1 style="margin:0; padding:0;">Groundwater Risk Assessment</h1>
        <p style="margin:0; font-size:0.8rem; color:#5b6370 !important;">
            Confidence-Aware Decision Support · BIS IS 10500:2012
        </p>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<p class="brand-subtle" style="text-align:right; margin-top:-20px;">✦ Powered by Eshwar AI</p>', unsafe_allow_html=True)
st.markdown("---")


# ─── Sidebar ────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### Assessment Mode")
    input_mode = st.radio(
        "Choose how to assess water quality:",
        ["🧪 Enter Water Parameters", "📍 Enter Location (Lat/Lon)",
         "🔀 Hybrid (Both)"],
        index=0,
        label_visibility="collapsed"
    )

    st.markdown("""
    <div style="margin:12px 0;">
        <div class="section-label">Mode descriptions</div>
    </div>
    """, unsafe_allow_html=True)

    if "Water Parameters" in input_mode:
        st.caption("Use lab measurements with the trained XGBoost model.")
    elif "Location" in input_mode:
        st.caption("Estimate from coordinates via spatial interpolation.")
    else:
        st.caption("Combine lab measurements + location context. ML when confidence ≥ 80%, else spatial.")

# Initialize location_name to prevent undefined reference errors
    location_name = ""

    st.markdown("---")

    st.markdown('<div class="section-label">System Info</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="glass-card" style="padding:14px; font-size:0.8rem;">
        <div style="margin-bottom:6px;"><span style="color:#5b6370;">Model</span> <span style="float:right;">XGBoost</span></div>
        <div style="margin-bottom:6px;"><span style="color:#5b6370;">Macro F1</span> <span style="float:right;">0.97</span></div>
        <div style="margin-bottom:6px;"><span style="color:#5b6370;">Training</span> <span style="float:right;">~14,500 samples</span></div>
        <div><span style="color:#5b6370;">Standard</span> <span style="float:right;">BIS IS 10500:2012</span></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="section-label">API Status</div>', unsafe_allow_html=True)
    try:
        r = requests.get(f"{API_URL}/health", timeout=3)
        if r.status_code == 200:
            st.success("Backend online")
        else:
            st.error("Backend error")
    except Exception:
        st.error("Backend offline — run: `uvicorn deploy.app:app`")


# ─── Helper: confidence badge ───────────────────────────────
def conf_color(c):
    if c >= 0.75: return "🟢"
    if c >= 0.50: return "🟡"
    return "🔴"

def render_confidence_bar(confidence: float):
    pct = int(confidence * 100)
    if confidence >= 0.75:
        color = "#4ade80"
    elif confidence >= 0.5:
        color = "#f59e0b"
    else:
        color = "#ef4444"
    st.markdown(f"""
    <div class="confidence-bar-bg">
      <div style="background:{color};border-radius:8px;height:8px;width:{pct}%;
                  transition:width 0.6s ease;"></div>
    </div>""", unsafe_allow_html=True)

def render_risk_badge(label: str):
    cls = {"SAFE": "risk-safe", "MODERATE": "risk-moderate",
           "HIGH": "risk-high"}.get(label, "risk-unknown")
    icon = {"SAFE": "✓", "MODERATE": "⚠", "HIGH": "✕"}.get(label, "?")
    st.markdown(f'<div class="{cls}">{icon}&nbsp;&nbsp;{label}</div>',
                unsafe_allow_html=True)


# ─── Helper: render full result ──────────────────────────────
def render_result(result: dict):
    expl   = result.get("explanation", {})
    params = result.get("parameter_summary", [])
    meta   = result.get("metadata", {})

    # Top row: risk + confidence + method
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        render_risk_badge(result.get("risk_label", "UNKNOWN"))
    with col2:
        conf = result.get("confidence", 0.0)
        st.markdown(f'<div class="section-label">Confidence</div>', unsafe_allow_html=True)
        st.markdown(f"<span style='font-size:1.5rem;font-weight:700;color:#e0e4ea;'>{conf*100:.0f}%</span>", unsafe_allow_html=True)
        render_confidence_bar(conf)
    with col3:
        st.markdown(f'<div class="section-label">Method</div>', unsafe_allow_html=True)
        method = result.get("method", "—")
        src    = result.get("decision_source", "")
        st.markdown(f"<span style='font-size:1.1rem;font-weight:600;color:#e0e4ea;'>{method}</span>", unsafe_allow_html=True)
        if src:
            st.caption(src)

    st.markdown("---")

    # Tabs for detail sections
    tab1, tab2, tab3, tab4 = st.tabs([
        "Explanation", "Parameters",
        "ML Insights", "Metadata"
    ])

    # ── Tab 1: Explanation ──────────────────────────────────
    with tab1:
        summary = expl.get("summary", "")
        if summary:
            st.markdown(f"""
            <div class="glass-card" style="display:flex;gap:12px;align-items:flex-start;">
                <span style="color:#3b82f6;font-size:1.1rem;margin-top:2px;">ℹ</span>
                <div>
                    <p style="font-size:0.9rem;line-height:1.6;color:#c8cdd6 !important;margin:0;">{summary}</p>
                    <p style="font-size:0.75rem;color:#5b6370 !important;margin-top:8px;font-style:italic;">
                        These contaminants may pose health risks if consumed over time.
                    </p>
                </div>
            </div>
            """, unsafe_allow_html=True)

        exceeded = expl.get("exceeded_params", [])
        if exceeded:
            st.markdown(f'<div class="section-label" style="margin-top:20px;">Exceeded Parameters ({len(exceeded)})</div>', unsafe_allow_html=True)
            for item in exceeded:
                with st.expander(
                    f"● {item['name']}  —  {item['value']} {item['unit']}  (limit: {item['bis_limit']})"
                ):
                    st.markdown(f"""
                    <div style="font-size:0.85rem;line-height:1.7;">
                        <div style="display:flex;gap:8px;margin:6px 0;">
                            <span style="color:#5b6370;">🔍 Cause:</span>
                            <span style="color:#a0a8b4;">{item['cause']}</span>
                        </div>
                        <div style="display:flex;gap:8px;margin:6px 0;">
                            <span style="color:#ef4444;">♥ Health Risk:</span>
                            <span style="color:#a0a8b4;">{item['health_risk']}</span>
                        </div>
                        <div style="display:flex;gap:8px;margin:6px 0;">
                            <span style="color:#3b82f6;">✦ Action:</span>
                            <span style="color:#a0a8b4;">{item['action']}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="glass-card" style="display:flex;align-items:center;gap:10px;">
                <span style="width:8px;height:8px;border-radius:50%;background:#4ade80;display:inline-block;"></span>
                <span style="font-size:0.875rem;color:#a0a8b4;">All parameters within BIS IS 10500:2012 safe limits.</span>
            </div>
            """, unsafe_allow_html=True)

        prob_note = expl.get("probability_note")
        if prob_note:
            st.caption(f"🤖 {prob_note}")

        advice = expl.get("overall_advice", "")
        if advice:
            label = result.get("risk_label", "")
            border_col = "#4ade80" if label == "SAFE" else "#f59e0b" if label == "MODERATE" else "#ef4444"
            st.markdown(f"""
            <div class="glass-card" style="border-left:3px solid {border_col};">
                <div class="section-label">Recommendation</div>
                <p style="font-size:0.875rem;color:#c8cdd6 !important;margin:0;">{advice}</p>
            </div>
            """, unsafe_allow_html=True)

    # ── Tab 2: Parameter Summary ────────────────────────────
    with tab2:
        if params:
            exceeded_count = expl.get("exceeded_count", 0)
            safe_count     = expl.get("safe_count", 0)

            mc1, mc2, mc3 = st.columns(3)
            mc1.metric("Total Parameters", len(params))
            mc2.metric("Within Limits", safe_count)
            mc3.metric("Exceeded", exceeded_count)

            st.markdown('<div style="height:12px;"></div>', unsafe_allow_html=True)

            for row in params:
                status = row["status"]
                val_str = f"{row['value']} {row['unit']}".strip()
                if status == "EXCEEDED":
                    st.markdown(
                        f'<div class="param-exceeded">'
                        f'<span style="display:inline-block;width:6px;height:6px;border-radius:50%;background:#ef4444;margin-right:8px;"></span>'
                        f'<b>{row["name"]}</b> &nbsp;—&nbsp; '
                        f'<span style="font-family:JetBrains Mono,monospace;font-size:0.8rem;">{val_str}</span> '
                        f'<span style="color:#5b6370;font-size:0.8rem;">(limit: {row["bis_limit"]})</span>'
                        f'</div>', unsafe_allow_html=True
                    )
                elif status == "OK":
                    st.markdown(
                        f'<div class="param-ok">'
                        f'<span style="display:inline-block;width:6px;height:6px;border-radius:50%;background:#4ade80;margin-right:8px;"></span>'
                        f'<b>{row["name"]}</b> &nbsp;—&nbsp; '
                        f'<span style="font-family:JetBrains Mono,monospace;font-size:0.8rem;">{val_str}</span> '
                        f'<span style="color:#5b6370;font-size:0.8rem;">(limit: {row["bis_limit"]})</span>'
                        f'</div>', unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        f'<div style="padding:8px 16px;margin:4px 0;'
                        f'border-left:3px solid #3b4555;border-radius:6px;">'
                        f'<b>{row["name"]}</b> &nbsp;—&nbsp; '
                        f'<span style="font-family:JetBrains Mono,monospace;font-size:0.8rem;">{val_str}</span>'
                        f'</div>', unsafe_allow_html=True
                    )
        else:
            st.info("No parameter data available for this prediction.")

    # ── Tab 3: ML Insights ──────────────────────────────────
    with tab3:
        factors = expl.get("top_ml_factors", [])
        probs   = meta.get("probabilities", {})

        if factors:
            st.markdown('<div class="section-label">Feature Importance (XGBoost)</div>', unsafe_allow_html=True)
            st.caption("Parameters with highest weight in the model's decision.")
            for f in factors:
                exceeded_flag = f.get("exceeded", False)
                dot_color = "#ef4444" if exceeded_flag else "#4ade80"
                imp    = f["importance"]
                bar_w  = int(imp * 3.5)
                st.markdown(
                    f'<div style="margin:10px 0;">'
                    f'<div style="display:flex;justify-content:space-between;align-items:center;">'
                    f'<span>'
                    f'<span style="display:inline-block;width:6px;height:6px;border-radius:50%;background:{dot_color};margin-right:8px;"></span>'
                    f'<span style="font-weight:600;font-size:0.875rem;">{f["name"]}</span></span>'
                    f'<span style="color:#5b6370;font-size:0.8rem;font-family:JetBrains Mono,monospace;">'
                    f'{f["value"]} · {imp:.1f}%</span></div>'
                    f'<div class="factor-bar">'
                    f'<div class="factor-fill" style="width:{min(bar_w,100)}%;"></div>'
                    f'</div></div>',
                    unsafe_allow_html=True
                )

        if probs:
            st.markdown('<div class="section-label" style="margin-top:24px;">Class Probability</div>', unsafe_allow_html=True)
            colors = {"SAFE": "#4ade80", "MODERATE": "#f59e0b", "HIGH": "#ef4444"}
            for label, prob in probs.items():
                pct = int(prob * 100)
                col = colors.get(label, "#6b7280")
                st.markdown(
                    f'<div style="display:flex;align-items:center;margin:8px 0;gap:10px;">'
                    f'<span style="width:70px;font-weight:600;color:{col};font-size:0.8rem;">{label}</span>'
                    f'<div style="flex:1;background:#262d3a;border-radius:6px;height:8px;overflow:hidden;">'
                    f'<div style="background:{col};width:{pct}%;border-radius:6px;height:8px;'
                    f'transition:width 0.5s ease;"></div></div>'
                    f'<span style="font-family:JetBrains Mono,monospace;font-size:0.75rem;color:#5b6370;width:40px;text-align:right;">{pct}%</span></div>',
                    unsafe_allow_html=True
                )

        if not factors and not probs:
            st.info("ML insights available only in ML or Hybrid mode with chemistry input.")

    # ── Tab 4: Metadata ─────────────────────────────────────
    with tab4:
        st.markdown('<div class="section-label">Technical Metadata</div>', unsafe_allow_html=True)
        if meta:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            for k, v in meta.items():
                if v is not None and k != "probabilities":
                    st.markdown(
                        f'<div style="display:flex;justify-content:space-between;padding:4px 0;font-size:0.85rem;">'
                        f'<span style="color:#5b6370;">{k.replace("_"," ").title()}</span>'
                        f'<span style="font-family:JetBrains Mono,monospace;font-size:0.8rem;">{v}</span>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div style="height:16px;"></div>', unsafe_allow_html=True)
        st.markdown('<div class="section-label">Raw Response</div>', unsafe_allow_html=True)
        st.json(result)


# ════════════════════════════════════════════════════════════
# INPUT PANELS
# ════════════════════════════════════════════════════════════

# ─── Default example values (typical Indian groundwater) ───
DEFAULTS = {
    "pH": 7.5, "NO3": 28.0, "F_mgL": 0.8, "Cl_mgL": 180.0,
    "SO4": 95.0, "Ca_mgL": 52.0, "Mg_mgL": 22.0,
    "Na_mgL": 120.0, "K_mgL": 4.0
}

HIGH_EXAMPLE = {
    "pH": 7.2, "NO3": 65.0, "F_mgL": 2.1, "Cl_mgL": 310.0,
    "SO4": 230.0, "Ca_mgL": 85.0, "Mg_mgL": 42.0,
    "Na_mgL": 220.0, "K_mgL": 14.0
}


def chemistry_form(prefix="ml", defaults=None):
    """Render chemistry input form. Returns dict of values."""
    if defaults is None:
        defaults = DEFAULTS

    st.markdown('<div class="section-label">Water Chemistry Parameters</div>', unsafe_allow_html=True)
    st.caption("Enter measured values — BIS IS 10500:2012 limits shown below each field")

    col1, col2, col3 = st.columns(3)

    with col1:
        pH     = st.number_input("pH (6.5–8.5)", min_value=0.0, max_value=14.0,
                                  value=defaults["pH"], step=0.1, key=f"{prefix}_pH")
        NO3    = st.number_input("Nitrate NO₃ (≤45 mg/L)", min_value=0.0,
                                  value=defaults["NO3"], step=1.0, key=f"{prefix}_NO3")
        F_mgL  = st.number_input("Fluoride F⁻ (≤1.5 mg/L)", min_value=0.0,
                                  value=defaults["F_mgL"], step=0.1, key=f"{prefix}_F")
    with col2:
        Cl_mgL = st.number_input("Chloride Cl⁻ (≤250 mg/L)", min_value=0.0,
                                  value=defaults["Cl_mgL"], step=5.0, key=f"{prefix}_Cl")
        SO4    = st.number_input("Sulphate SO₄ (≤200 mg/L)", min_value=0.0,
                                  value=defaults["SO4"], step=5.0, key=f"{prefix}_SO4")
        Ca_mgL = st.number_input("Calcium Ca²⁺ (≤75 mg/L)", min_value=0.0,
                                  value=defaults["Ca_mgL"], step=1.0, key=f"{prefix}_Ca")
    with col3:
        Mg_mgL = st.number_input("Magnesium Mg²⁺ (≤30 mg/L)", min_value=0.0,
                                  value=defaults["Mg_mgL"], step=1.0, key=f"{prefix}_Mg")
        Na_mgL = st.number_input("Sodium Na⁺ (≤200 mg/L)", min_value=0.0,
                                  value=defaults["Na_mgL"], step=5.0, key=f"{prefix}_Na")
        K_mgL  = st.number_input("Potassium K⁺ (≤12 mg/L)", min_value=0.0,
                                  value=defaults["K_mgL"], step=0.5, key=f"{prefix}_K")

    return {
        "pH": pH, "NO3": NO3, "F_mgL": F_mgL, "Cl_mgL": Cl_mgL,
        "SO4": SO4, "Ca_mgL": Ca_mgL, "Mg_mgL": Mg_mgL,
        "Na_mgL": Na_mgL, "K_mgL": K_mgL,
    }


# ════════════════════════════════════════════════════════════
# MODE 1: ML ONLY
# ════════════════════════════════════════════════════════════
if input_mode == "🧪 Enter Water Parameters":
    st.markdown("## ML-Based Prediction")
    st.caption("Predict water risk directly from lab measurements using the trained XGBoost model.")

    with st.expander("Load sample data", expanded=False):
        ecol1, ecol2 = st.columns(2)
        load_safe = ecol1.button("Safe Example", key="load_safe")
        load_high = ecol2.button("High-Risk Example", key="load_high")

    use_defaults = HIGH_EXAMPLE if (
        "load_high" in st.session_state and st.session_state.get("load_high")
    ) else DEFAULTS

    chemistry = chemistry_form(prefix="ml", defaults=use_defaults)

    st.markdown('<div style="height:8px;"></div>', unsafe_allow_html=True)

    if st.button("Assess Water Quality", type="primary", key="ml_submit"):
        with st.spinner("Running ML prediction..."):
            try:
                resp = requests.post(
                    f"{API_URL}/predict",
                    json={"chemistry": chemistry},
                    timeout=10
                )
                if resp.status_code == 200:
                    result = resp.json()
                    if location_name.strip():
                        st.markdown(f"""
                        <p style="font-size:0.85rem;color:#5b6370;">
                            Results for <span style="font-weight:600;color:#e0e4ea;">{location_name.strip()}</span>
                        </p>
                        """, unsafe_allow_html=True)
                    render_result(result)
                else:
                    st.error(f"API Error {resp.status_code}: {resp.text}")
            except Exception as e:
                st.markdown(f"""
                <div class="glass-card" style="border-left:3px solid #ef4444;">
                    <p style="font-weight:600;font-size:0.9rem;color:#e0e4ea;margin:0;">Something went wrong</p>
                    <p style="font-size:0.8rem;color:#5b6370;margin:6px 0 0;">{e}</p>
                    <p style="font-size:0.75rem;color:#3b4555;margin:6px 0 0;">
                        Ensure the backend is running: <code style="color:#60a5fa;">uvicorn deploy.app:app --reload</code>
                    </p>
                </div>
                """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# MODE 2: SPATIAL ONLY
# ════════════════════════════════════════════════════════════
elif input_mode == "📍 Enter Location (Lat/Lon)":
    st.markdown("## Spatial Prediction")
    st.caption("Estimate groundwater quality from location using spatial interpolation across 14,500+ CGWB stations.")

    EXAMPLE_LOCATIONS = {
        "— Select a preset —":                 None,
        "Ettimadai (10.8981°N, 76.9003°E)":    (10.8981, 76.9003),
        "Madukkarai (10.9083°N, 76.9667°E)":   (10.9083, 76.9667),
        "Coimbatore city (11.0017°N, 76.9711°E)": (11.0017, 76.9711),
        "Singanallur (10.9964°N, 77.0208°E)":  (10.9964, 77.0208),
        "Pollachi (10.6611°N, 77.0000°E)":     (10.6611, 77.0000),
        "Delhi (28.6139°N, 77.2090°E)":        (28.6139, 77.2090),
        "Hyderabad (17.3850°N, 78.4867°E)":    (17.3850, 78.4867),
        "Chennai (13.0827°N, 80.2707°E)":      (13.0827, 80.2707),
        "Custom location":                     None,
    }

    loc_choice = st.selectbox(
        "Select a preset or choose Custom:",
        list(EXAMPLE_LOCATIONS.keys())
    )

    is_preset = (EXAMPLE_LOCATIONS.get(loc_choice) is not None)
    if is_preset:
        default_lat, default_lon = EXAMPLE_LOCATIONS[loc_choice]
        default_name = loc_choice.split(" (")[0]
    else:
        default_lat, default_lon = 10.8981, 76.9003
        default_name = ""

    location_name = st.text_input(
        "Location name (optional)",
        value=default_name,
        placeholder="e.g. Ettimadai, Coimbatore"
    )

    col1, col2 = st.columns(2)
    latitude  = col1.number_input("Latitude",  value=default_lat,
                                   min_value=-90.0, max_value=90.0,
                                   format="%.4f", step=0.01)
    longitude = col2.number_input("Longitude", value=default_lon,
                                   min_value=-180.0, max_value=180.0,
                                   format="%.4f", step=0.01)

    display_name = location_name.strip() if location_name.strip() else f"{latitude:.4f}°N, {longitude:.4f}°E"
    st.caption(f"📍 Assessing: **{display_name}**")

    st.markdown('<div style="height:8px;"></div>', unsafe_allow_html=True)

    if st.button("Assess Location Risk", type="primary", key="spatial_submit"):
        spinner_msg = f"Querying spatial model for {display_name}..."
        with st.spinner(spinner_msg):
            try:
                resp = requests.post(
                    f"{API_URL}/predict",
                    json={"latitude": latitude, "longitude": longitude},
                    timeout=15
                )
                if resp.status_code == 200:
                    render_result(resp.json())
                else:
                    st.error(f"API Error {resp.status_code}: {resp.text}")
            except Exception as e:
                st.markdown(f"""
                <div class="glass-card" style="border-left:3px solid #ef4444;">
                    <p style="font-weight:600;font-size:0.9rem;color:#e0e4ea;margin:0;">Something went wrong</p>
                    <p style="font-size:0.8rem;color:#5b6370;margin:6px 0 0;">{e}</p>
                </div>
                """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# MODE 3: HYBRID
# ════════════════════════════════════════════════════════════
else:
    st.markdown("## Hybrid Prediction")
    st.caption("Combine lab measurements + location context. ML when confidence ≥ 80%, otherwise spatial estimation.")

    hcol1, hcol2 = st.columns([1, 1])
    with hcol1:
        st.markdown('<div class="section-label">Location</div>', unsafe_allow_html=True)
        h_lat = st.number_input("Latitude",  value=28.6139, format="%.4f",
                                  min_value=-90.0, max_value=90.0, key="h_lat")
        h_lon = st.number_input("Longitude", value=77.2090, format="%.4f",
                                  min_value=-180.0, max_value=180.0, key="h_lon")

    with hcol2:
        st.markdown('<div class="section-label">Decision Logic</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="glass-card" style="font-size:0.8rem;line-height:1.8;">
            <div>• ML confidence ≥ 80% → use ML prediction</div>
            <div>• Otherwise → spatial interpolation</div>
            <div>• Explanation reflects the dominant source</div>
        </div>
        """, unsafe_allow_html=True)

    chemistry = chemistry_form(prefix="hybrid")

    st.markdown('<div style="height:8px;"></div>', unsafe_allow_html=True)

    if st.button("Run Hybrid Assessment", type="primary", key="hybrid_submit"):
        with st.spinner("Running hybrid assessment..."):
            try:
                resp = requests.post(
                    f"{API_URL}/predict",
                    json={"latitude": h_lat, "longitude": h_lon, "chemistry": chemistry},
                    timeout=15
                )
                if resp.status_code == 200:
                    render_result(resp.json())
                else:
                    st.error(f"API Error {resp.status_code}: {resp.text}")
            except Exception as e:
                st.markdown(f"""
                <div class="glass-card" style="border-left:3px solid #ef4444;">
                    <p style="font-weight:600;font-size:0.9rem;color:#e0e4ea;margin:0;">Something went wrong</p>
                    <p style="font-size:0.8rem;color:#5b6370;margin:6px 0 0;">{e}</p>
                </div>
                """, unsafe_allow_html=True)


# ─── Footer ─────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style="text-align:center;padding:8px 0;">
    <p class="brand-subtle">
        Confidence-Aware Groundwater Quality Risk Assessment System · CGWB · BIS IS 10500:2012 · XGBoost (F1=0.97)
    </p>
</div>
""", unsafe_allow_html=True)
