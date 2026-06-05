"""
MongoDB Atlas — Streamlit Theme
Paleta oficial: #001E2B · #00ED64 · Plus Jakarta Sans
config.toml define primaryColor=#00ED64 — handles slider/checkbox/toggle nativamente.
Compatível com Streamlit 1.36+  (st.html() para CSS e componentes).
"""

import streamlit as st


def inject_mongodb_theme():
    """CSS global MongoDB Atlas. Chamar logo após st.set_page_config()."""
    st.html("""
    <!-- Fontes proprietárias MongoDB: Euclid Circular A (sans) + Value Serif (display) -->
    <style>
    @font-face {
        font-family: "Euclid Circular A";
        src: url("https://d2va9gm4j17fy9.cloudfront.net/fonts/euclid-circular/EuclidCircularA-Regular-WebXL.woff2") format("woff2"),
             url("https://d2va9gm4j17fy9.cloudfront.net/fonts/euclid-circular/EuclidCircularA-Regular-WebXL.woff") format("woff");
        font-weight: 400; font-style: normal; font-display: swap;
    }
    @font-face {
        font-family: "Euclid Circular A";
        src: url("https://d2va9gm4j17fy9.cloudfront.net/fonts/euclid-circular/EuclidCircularA-Medium-WebXL.woff2") format("woff2"),
             url("https://d2va9gm4j17fy9.cloudfront.net/fonts/euclid-circular/EuclidCircularA-Medium-WebXL.woff") format("woff");
        font-weight: 500; font-style: normal; font-display: swap;
    }
    @font-face {
        font-family: "Euclid Circular A";
        src: url("https://d2va9gm4j17fy9.cloudfront.net/fonts/euclid-circular/EuclidCircularA-Semibold-WebXL.woff2") format("woff2"),
             url("https://d2va9gm4j17fy9.cloudfront.net/fonts/euclid-circular/EuclidCircularA-Semibold-WebXL.woff") format("woff");
        font-weight: 600; font-style: normal; font-display: swap;
    }
    @font-face {
        font-family: "Euclid Circular A";
        src: url("https://d2va9gm4j17fy9.cloudfront.net/fonts/euclid-circular/EuclidCircularA-Bold-WebXL.woff2") format("woff2"),
             url("https://d2va9gm4j17fy9.cloudfront.net/fonts/euclid-circular/EuclidCircularA-Bold-WebXL.woff") format("woff");
        font-weight: 700; font-style: normal; font-display: swap;
    }
    @font-face {
        font-family: "MongoDB Value Serif";
        src: url("https://d2va9gm4j17fy9.cloudfront.net/fonts/value-serif/MongoDBValueSerif-Bold.woff2") format("woff2"),
             url("https://d2va9gm4j17fy9.cloudfront.net/fonts/value-serif/MongoDBValueSerif-Bold.woff") format("woff");
        font-weight: 700; font-style: normal; font-display: swap;
    }
    </style>
    <link href="https://fonts.googleapis.com/css2?family=Source+Code+Pro:wght@400;500;600&display=swap" rel="stylesheet">
    <style>

    /* ── TOKENS — MongoDB LeafyGreen design system ── */
    :root {
        --green:       #00ED64;   /* LeafyGreen green/base    */
        --green-dim:   #00A35C;   /* LeafyGreen green/dark1   */
        --green-glow:  rgba(0,237,100,0.18);
        --green-lo:    rgba(0,237,100,0.08);
        --green-bd:    rgba(0,237,100,0.22);

        --bg:          #001E2B;   /* LeafyGreen black         */
        --bg-card:     #00263A;   /* elevated surface (navy)  */
        --bg-sidebar:  #00141C;
        --bg-hover:    #00344F;
        --bg-raised:   #002235;

        --border:      rgba(0,237,100,0.12);
        --border-md:   rgba(0,237,100,0.22);
        --border-sub:  rgba(255,255,255,0.06);

        --txt:         #E3FCF7;   /* LeafyGreen white (warm)  */
        --txt-2:       #889397;   /* LeafyGreen gray/base     */
        --txt-3:       #5C6C75;   /* LeafyGreen gray/dark1    */

        --yellow:      #FFC010;   /* LeafyGreen yellow/base   */
        --teal:        #00D2FF;
        --blue:        #0498EC;   /* LeafyGreen blue/light1   */
        --purple:      #B45AF2;   /* LeafyGreen purple/base   */
        --orange:      #E27E25;
        --red:         #FF6960;   /* LeafyGreen red (dark-mode) */

        --font:  "Euclid Circular A", "Helvetica Neue", Helvetica, Arial, sans-serif;
        --serif: "MongoDB Value Serif", Georgia, serif;
        --mono:  "Source Code Pro", Menlo, Consolas, monospace;
        --radius: 6px;
    }

    /* ── BASE ── */
    html, body, [class*="css"] { font-family: var(--font) !important; }
    .stApp { background-color: var(--bg) !important; }
    /* Esconde o header/toolbar do Streamlit (barra escura no topo) — Streamlit 1.36+ */
    #MainMenu, footer, header { visibility: hidden !important; }
    [data-testid="stHeader"],
    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    [data-testid="stStatusWidget"] { display: none !important; height: 0 !important; }
    .block-container { padding-top: 0 !important; max-width: 1440px !important; }

    /* ── SIDEBAR ── */
    section[data-testid="stSidebar"] {
        background-color: var(--bg-sidebar) !important;
        border-right: 1px solid var(--border) !important;
    }
    section[data-testid="stSidebar"] * { font-family: var(--font) !important; }
    [data-testid="stSidebarCollapseButton"],
    [data-testid="collapsedControl"],
    [data-testid="stSidebarHeader"] button { display: none !important; }

    /* ── TIPOGRAFIA ── */
    h1,h2,h3,h4,h5,h6 {
        font-family: var(--font) !important;
        color: var(--txt) !important;
        letter-spacing: -0.02em !important;
    }
    h1 { font-size: 22px !important; font-weight: 800 !important; }
    h2 { font-size: 18px !important; font-weight: 700 !important; }
    h3 { font-size: 15px !important; font-weight: 600 !important; }
    p, li, span, label { font-family: var(--font) !important; color: var(--txt-2) !important; }

    /* ── INPUTS ── */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: var(--bg-card) !important;
        border: 1px solid rgba(184,196,194,0.15) !important;
        border-radius: var(--radius) !important;
        color: var(--txt) !important;
        font-family: var(--font) !important; font-size: 14px !important;
    }
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--green) !important;
        box-shadow: 0 0 0 3px var(--green-glow) !important;
    }
    .stTextInput > div > div > input::placeholder { color: var(--txt-3) !important; }

    /* ── SELECT / MULTISELECT ── */
    .stSelectbox > div > div,
    .stMultiSelect > div > div {
        background: var(--bg-card) !important;
        border: 1px solid rgba(184,196,194,0.15) !important;
        border-radius: var(--radius) !important;
        color: var(--txt) !important;
    }
    .stSelectbox > div > div:focus-within,
    .stMultiSelect > div > div:focus-within {
        border-color: var(--green) !important;
        box-shadow: 0 0 0 3px var(--green-glow) !important;
    }
    [data-baseweb="popover"] ul {
        background: var(--bg-hover) !important;
        border: 1px solid var(--border-md) !important;
        border-radius: var(--radius) !important;
    }
    [data-baseweb="popover"] ul li { color: var(--txt-2) !important; font-size: 13px !important; }
    [data-baseweb="popover"] ul li:hover { background: var(--bg-card) !important; }
    .stMultiSelect span[data-baseweb="tag"] {
        background: var(--green-lo) !important;
        border: 1px solid var(--border-md) !important;
        color: var(--green) !important;
        border-radius: 4px !important; font-size: 12px !important; font-weight: 600 !important;
    }

    /* ── BOTÃO PRIMÁRIO ── */
    .stButton > button:not([kind="secondary"]),
    .stFormSubmitButton > button {
        background: var(--green) !important;
        color: #001E2B !important;
        border: none !important;
        border-radius: var(--radius) !important;
        font-family: var(--font) !important; font-size: 14px !important; font-weight: 700 !important;
        padding: 10px 24px !important;
        transition: background 0.15s, box-shadow 0.15s, transform 0.1s !important;
        width: auto !important;
    }
    .stButton > button:not([kind="secondary"]):hover,
    .stFormSubmitButton > button:hover {
        background: var(--green-dim) !important;
        box-shadow: 0 4px 16px rgba(0,237,100,0.25) !important;
        transform: translateY(-1px) !important;
    }
    .stFormSubmitButton > button, .stFormSubmitButton > button * { color: #001E2B !important; }

    /* ── BOTÃO SECUNDÁRIO ── */
    .stButton > button[kind="secondary"] {
        background: rgba(0,237,100,0.06) !important;
        color: var(--txt-2) !important;
        border: 1px solid var(--border-md) !important;
        border-radius: var(--radius) !important;
        font-family: var(--font) !important; font-size: 13px !important; font-weight: 500 !important;
        padding: 8px 16px !important; width: auto !important;
    }
    .stButton > button[kind="secondary"]:hover {
        background: rgba(0,237,100,0.12) !important;
        border-color: var(--green) !important; color: var(--txt) !important;
    }

    /* ── TABS ── */
    .stTabs [data-baseweb="tab-list"] {
        background: transparent !important;
        border-bottom: 1px solid var(--border) !important;
        padding: 0 !important; gap: 0 !important;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent !important; color: var(--txt-3) !important;
        font-family: var(--font) !important; font-size: 13px !important; font-weight: 500 !important;
        padding: 12px 18px !important; border-bottom: 2px solid transparent !important;
        transition: color 0.15s !important;
    }
    .stTabs [data-baseweb="tab"]:hover { color: var(--txt-2) !important; }
    .stTabs [aria-selected="true"] {
        color: var(--green) !important; border-bottom-color: var(--green) !important; font-weight: 600 !important;
    }
    .stTabs [data-baseweb="tab-panel"] { padding-top: 24px !important; }

    /* ── FORM CONTAINER ── */
    [data-testid="stForm"] {
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-radius: 10px !important; padding: 20px !important;
    }

    /* ── DATAFRAME ── */
    .stDataFrame { border: 1px solid var(--border) !important; border-radius: 8px !important; overflow: hidden !important; }
    .stDataFrame thead tr th {
        background: var(--bg-hover) !important; color: var(--txt-3) !important;
        font-family: var(--font) !important; font-size: 10px !important;
        font-weight: 700 !important; text-transform: uppercase !important; letter-spacing: 0.08em !important;
    }
    .stDataFrame tbody tr td {
        background: var(--bg-card) !important; color: var(--txt-2) !important;
        font-family: var(--mono) !important; font-size: 12px !important; border-color: var(--border) !important;
    }
    .stDataFrame tbody tr:hover td { background: var(--bg-hover) !important; }

    /* ── MÉTRICAS NATIVAS ── */
    [data-testid="metric-container"] {
        background: var(--bg-card) !important; border: 1px solid var(--border) !important;
        border-radius: 8px !important; padding: 16px !important;
    }
    [data-testid="metric-container"] label {
        font-size: 10px !important; font-weight: 700 !important; color: var(--txt-3) !important;
        text-transform: uppercase !important; letter-spacing: 0.1em !important; font-family: var(--font) !important;
    }
    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        font-family: var(--font) !important; font-size: 22px !important;
        font-weight: 700 !important; color: var(--txt) !important; letter-spacing: -0.02em !important;
    }

    /* ── EXPANDER ── */
    [data-testid="stExpander"] {
        background: var(--bg-card) !important; border: 1px solid var(--border) !important;
        border-radius: 8px !important; overflow: hidden !important;
    }
    [data-testid="stExpander"] summary {
        background: var(--bg-card) !important; color: var(--txt-2) !important;
        font-family: var(--font) !important; font-size: 13px !important; font-weight: 500 !important;
        padding: 10px 14px !important; list-style: none !important;
    }
    [data-testid="stExpander"] summary::-webkit-details-marker { display: none !important; }
    [data-testid="stExpander"] summary:hover { background: var(--bg-hover) !important; color: var(--green) !important; }
    /* Esconde o ícone nativo (renderiza como texto "arrow_drop_down" sem a Material font) */
    [data-testid="stExpander"] summary [data-testid="stExpanderToggleIcon"],
    [data-testid="stExpander"] summary [data-testid="stIconMaterial"],
    [data-testid="stExpander"] summary [data-testid="stIconMaterialOutlined"],
    [data-testid="stExpander"] summary [class*="material-symbols"],
    [data-testid="stExpander"] summary [class*="material-icons"],
    [data-testid="stExpander"] summary span[class*="icon"],
    [data-testid="stExpander"] summary svg {
        display: none !important; width: 0 !important; visibility: hidden !important;
    }
    /* Seta CSS própria */
    [data-testid="stExpander"] summary::before {
        content: '▸'; color: var(--txt-3); font-size: 13px;
        margin-right: 8px; font-family: sans-serif !important; display: inline-block; visibility: visible !important;
    }
    [data-testid="stExpander"] details[open] > summary::before,
    details[open] > summary::before { content: '▾'; }
    [data-testid="stExpander"] > div {
        background: var(--bg-card) !important; border-top: 1px solid var(--border) !important; padding: 14px !important;
    }

    /* ── CODE / JSON ── */
    .stJson, pre, code {
        background: var(--bg-card) !important; border: 1px solid var(--border) !important;
        border-radius: var(--radius) !important; font-family: var(--mono) !important;
        font-size: 12px !important; color: var(--green) !important;
    }

    /* ── CHAT ── */
    .stChatMessage {
        background: var(--bg-card) !important; border: 1px solid var(--border) !important; border-radius: 8px !important;
    }
    [data-testid="stChatMessageAvatarUser"],
    [data-testid="stChatMessageAvatarAssistant"] {
        background: var(--bg-hover) !important; border: 1px solid var(--border) !important; border-radius: 50% !important;
    }

    /* ── ALERTAS ── */
    [data-testid="stAlert"] { border-radius: var(--radius) !important; font-family: var(--font) !important; }

    /* ── DIVIDER ── */
    hr { border: none !important; border-top: 1px solid var(--border) !important; margin: 20px 0 !important; }

    /* ── SPINNER ── */
    .stSpinner > div { border-top-color: var(--green) !important; }

    /* ── SCROLLBAR ── */
    ::-webkit-scrollbar { width: 5px; height: 5px; }
    ::-webkit-scrollbar-thumb { background: rgba(0,237,100,0.18); border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(0,237,100,0.32); }

    /* ── SLIDER ── */
    [data-testid="stSlider"] p { color: var(--txt-3) !important; font-size: 11px !important; font-family: var(--mono) !important; }
    [data-testid="stWidgetLabel"] p, .stCaption p { color: var(--txt-3) !important; font-family: var(--font) !important; }

    </style>
    """)


# ── COMPONENTES ────────────────────────────────────────────────────────────────

def mdb_leaf(w: int = 24, h: int = 28):
    """Logo folha MongoDB de duas tonalidades (light green + evergreen) + caule."""
    return (
        f'<svg width="{w}" height="{h}" viewBox="0 0 26 32" fill="none" '
        f'style="flex-shrink:0;filter:drop-shadow(0 0 6px rgba(0,237,100,0.35));">'
        # metade clara (esquerda)
        '<path d="M13 1C13 1 3 11 3 19C3 24.52 7.48 29 13 29L13 1Z" fill="#00ED64"/>'
        # metade escura (direita) — evergreen
        '<path d="M13 1C13 1 23 11 23 19C23 24.52 18.52 29 13 29L13 1Z" fill="#00A35C"/>'
        # caule
        '<rect x="12" y="28" width="2" height="4" rx="1" fill="#00684A"/>'
        '</svg>'
    )


def mdb_header(title: str, subtitle: str = "", pills: list = None):
    """Header MongoDB Atlas com logo folha, título (Value Serif) e pills."""
    pill_palette = {
        "green":  ("#00ED64", "rgba(0,237,100,0.10)",  "rgba(0,237,100,0.28)"),
        "blue":   ("#0498EC", "rgba(4,152,236,0.10)", "rgba(4,152,236,0.28)"),
        "purple": ("#B45AF2", "rgba(180,90,242,0.10)","rgba(180,90,242,0.28)"),
        "orange": ("#FFC010", "rgba(255,192,16,0.10)", "rgba(255,192,16,0.28)"),
    }
    pills_html = ""
    if pills:
        for p in pills:
            c, bg, bd = pill_palette.get(p.get("color","green"), pill_palette["green"])
            pills_html += (
                f'<span style="font-size:10px;font-weight:700;padding:3px 10px;border-radius:4px;'
                f'border:1px solid {bd};background:{bg};color:{c};'
                f'text-transform:uppercase;letter-spacing:0.07em;white-space:nowrap;'
                f'font-family:Euclid Circular A,sans-serif;">{p["label"]}</span>'
            )
    sub = (f'<p style="margin:6px 0 0;font-size:12px;color:#3D5A6C;'
           f'font-family:Source Code Pro,monospace;">{subtitle}</p>') if subtitle else ""
    st.html(f"""
    <div style="background:linear-gradient(180deg,#00141C 0%,#001E2B 100%);
                border-bottom:1px solid rgba(0,237,100,0.12);
                padding:16px 4px 14px;margin-bottom:6px;">
        <div style="display:flex;align-items:center;gap:13px;flex-wrap:wrap;">
            {mdb_leaf(24, 28)}
            <span style="font-family:'MongoDB Value Serif',Georgia,serif;font-size:23px;
                         font-weight:700;color:#E3FCF7;letter-spacing:-0.015em;line-height:1;">{title}</span>
            <div style="display:flex;gap:6px;flex-wrap:wrap;margin-left:2px;">{pills_html}</div>
        </div>
        {sub}
    </div>
    """)


def mdb_kpi_card(label: str, value: str, delta: str = "", delta_type: str = "",
                 color: str = "green"):
    """
    Card KPI estilo MongoDB Atlas dashboard — top border colorida + valor grande + delta.
    color: "green" | "teal" | "yellow" | "blue" | "orange" | "red"
    delta_type: "up" | "down" | "warn" | ""
    """
    palette = {
        "green":  "#00ED64",
        "teal":   "#00D2FF",
        "yellow": "#FFC010",
        "blue":   "#0498EC",
        "purple": "#B45AF2",
        "orange": "#E27E25",
        "red":    "#FF6960",
        "muted":  "#89979B",
    }
    delta_colors = {"up": "#00ED64", "down": "#FF6960", "warn": "#FFC010", "": "#3D5A6C"}
    accent     = palette.get(color, palette["green"])
    d_color    = delta_colors.get(delta_type, "#3D5A6C")
    delta_html = (f'<div style="font-size:11px;color:{d_color};font-family:Source Code Pro,monospace;'
                  f'margin-top:8px;letter-spacing:0.01em;">{delta}</div>') if delta else ""

    st.html(f"""
    <div style="
        background:linear-gradient(160deg,rgba(0,0,0,0.15) 0%,#002235 100%);
        border:1px solid rgba(255,255,255,0.06);
        border-top:3px solid {accent};
        border-radius:0 0 8px 8px;
        padding:16px 18px 14px;
        position:relative; overflow:hidden;
        transition:box-shadow 0.2s;
    ">
        <div style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:0.12em;
                    color:#3D5A6C;font-family:Euclid Circular A,sans-serif;margin-bottom:8px;">{label}</div>
        <div style="font-size:30px;font-weight:700;color:{accent};
                    font-family:'Euclid Circular A',sans-serif;line-height:1.05;letter-spacing:-0.03em;">{value}</div>
        {delta_html}
    </div>
    """)


def mdb_metric_card(label: str, value: str, unit: str = "", color: str = "default", badge: str = ""):
    """Card de métrica alternativo (versão compacta sem top border)."""
    val_color = {"green": "#00ED64", "yellow": "#FFC010", "blue": "#0498EC", "default": "#E3FCF7"}.get(color, "#E3FCF7")
    border = "rgba(0,237,100,0.22)" if color == "green" else "rgba(0,237,100,0.08)"
    bg     = "linear-gradient(160deg,rgba(0,237,100,0.06),#00283A 70%)" if color == "green" else "#00283A"
    badge_html = (
        f'<span style="position:absolute;top:8px;right:8px;font-size:9px;font-weight:800;'
        f'padding:2px 7px;border-radius:3px;background:rgba(0,237,100,0.10);color:#00ED64;'
        f'border:1px solid rgba(0,237,100,0.22);text-transform:uppercase;letter-spacing:0.08em;'
        f'font-family:Euclid Circular A,sans-serif;">{badge}</span>'
    ) if badge else ""
    unit_html = (f'<div style="font-size:11px;color:#3D5A6C;margin-top:3px;'
                 f'font-family:Source Code Pro,monospace;">{unit}</div>') if unit else ""
    st.html(f"""
    <div style="background:{bg};border:1px solid {border};border-radius:8px;
                padding:14px 16px;position:relative;overflow:hidden;">
        {badge_html}
        <div style="font-size:10px;color:#3D5A6C;text-transform:uppercase;letter-spacing:0.1em;
                    font-weight:700;margin-bottom:5px;font-family:Euclid Circular A,sans-serif;">{label}</div>
        <div style="font-size:24px;font-weight:700;color:{val_color};
                    font-family:'Euclid Circular A',sans-serif;line-height:1.1;letter-spacing:-0.02em;">{value}</div>
        {unit_html}
    </div>
    """)


def mdb_sidebar(db_name: str = "POC", online: bool = True,
                collections: dict = None, indices: list = None):
    """
    Sidebar estilo MongoDB Atlas dashboard com:
    - Logo + brand
    - Seções de nav (BUSCA / ANALYTICS / AI)
    - Collections + índices
    - Cluster status pill
    """
    dot   = "#00ED64" if online else "#FF6960"
    label = "Online"  if online else "Offline"

    # ── Logo + Brand ──────────────────────────────────────────────────
    st.html(f"""
    <style>@keyframes mdb-dot{{0%,100%{{opacity:1;transform:scale(1)}}50%{{opacity:0.5;transform:scale(0.8)}}}}</style>
    <div style="padding:16px 4px 14px;border-bottom:1px solid rgba(0,237,100,0.10);margin-bottom:12px;">
        <div style="display:flex;align-items:center;gap:10px;">
            {mdb_leaf(26, 30)}
            <div>
                <div style="font-size:16px;font-weight:700;color:#E3FCF7;
                            font-family:'MongoDB Value Serif',Georgia,serif;letter-spacing:-0.01em;line-height:1.15;">
                    Search × Vector
                </div>
                <div style="font-size:9px;color:#3D5A6C;text-transform:uppercase;
                            letter-spacing:0.15em;font-family:'Source Code Pro',monospace;margin-top:2px;">
                    MongoDB Atlas POC
                </div>
            </div>
        </div>
    </div>
    """)

    # ── Nav Sections ──────────────────────────────────────────────────
    nav_items = {
        "BUSCA": [
            ("🔍", "Atlas Search",    True),
            ("⚡", "Search vs Vector", False),
        ],
        "HYBRID & AI": [
            ("🔀", "Hybrid RRF",  False),
            ("🤖", "AI Agent",    False),
        ],
    }

    nav_html = ""
    for section, items in nav_items.items():
        nav_html += f"""
        <div style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:0.16em;
                    color:#3D5A6C;font-family:'Euclid Circular A',sans-serif;
                    padding:14px 4px 6px;">{section}</div>"""
        for icon, name, active in items:
            active_style = (
                "background:rgba(0,237,100,0.08);border-left:2px solid #00ED64;color:#00ED64;"
                if active else
                "background:transparent;border-left:2px solid transparent;color:#6B8080;"
            )
            nav_html += f"""
            <div style="display:flex;align-items:center;gap:10px;padding:8px 12px;
                        border-radius:0 6px 6px 0;cursor:default;transition:background 0.15s;
                        {active_style}font-family:'Euclid Circular A',sans-serif;font-size:13px;
                        font-weight:{'600' if active else '400'};margin-bottom:2px;">
                <span style="font-size:14px;opacity:{'1' if active else '0.5'};">{icon}</span>
                <span>{name}</span>
            </div>"""

    st.html(f'<div style="margin-bottom:16px;">{nav_html}</div>')

    # ── Divider ───────────────────────────────────────────────────────
    st.html('<div style="height:1px;background:rgba(0,237,100,0.08);margin:8px 0 16px;"></div>')

    # ── Collections ───────────────────────────────────────────────────
    if collections:
        palette = ["#00ED64", "#0498EC", "#B45AF2", "#FFC010"]
        rows = "".join(
            f'<div style="display:flex;justify-content:space-between;align-items:center;'
            f'padding:8px 10px;border-radius:5px;background:#00283A;'
            f'border:1px solid rgba(0,237,100,0.07);margin-bottom:4px;">'
            f'<span style="font-family:Source Code Pro,monospace;font-size:11px;'
            f'color:{palette[i%len(palette)]};font-weight:500;">{n}</span>'
            f'<span style="font-family:Source Code Pro,monospace;font-size:10px;color:#3D5A6C;">{c:,}</span></div>'
            for i,(n,c) in enumerate(collections.items())
        )
        st.html(f"""
        <div style="margin-bottom:16px;">
            <div style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:0.16em;
                        color:#3D5A6C;font-family:'Euclid Circular A',sans-serif;margin-bottom:8px;">
                Collections</div>
            {rows}
        </div>""")

    # ── Índices ───────────────────────────────────────────────────────
    if indices:
        idx_rows = "".join(
            f'<div style="background:#00283A;border:1px solid rgba(0,237,100,0.07);'
            f'border-radius:5px;padding:8px 10px;margin-bottom:4px;">'
            f'<div style="font-family:Source Code Pro,monospace;font-size:11px;color:#00ED64;'
            f'font-weight:500;margin-bottom:2px;">{n}</div>'
            f'<div style="display:flex;align-items:center;gap:5px;font-size:10px;color:#3D5A6C;'
            f'font-family:Euclid Circular A,sans-serif;">'
            f'<span style="width:5px;height:5px;border-radius:50%;background:#00ED64;'
            f'box-shadow:0 0 4px #00ED64;display:inline-block;"></span>{k} · READY</div></div>'
            for n,k in indices
        )
        st.html(f"""
        <div style="margin-bottom:16px;">
            <div style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:0.16em;
                        color:#3D5A6C;font-family:'Euclid Circular A',sans-serif;margin-bottom:8px;">
                Índices Ativos</div>
            {idx_rows}
        </div>""")

    # ── Cluster Status (bottom pill) ──────────────────────────────────
    st.html(f"""
    <div style="background:rgba(0,237,100,0.06);border:1px solid rgba(0,237,100,0.18);
                border-radius:6px;padding:10px 12px;margin-top:8px;">
        <div style="font-size:9px;color:#3D5A6C;text-transform:uppercase;letter-spacing:0.14em;
                    font-family:'Euclid Circular A',sans-serif;margin-bottom:5px;">Cluster</div>
        <div style="display:flex;align-items:center;justify-content:space-between;">
            <span style="font-family:'Source Code Pro',monospace;font-size:13px;font-weight:700;
                         color:#00ED64;letter-spacing:0.02em;">{db_name}</span>
            <span style="display:flex;align-items:center;gap:5px;font-size:11px;color:{dot};
                         font-weight:600;font-family:'Euclid Circular A',sans-serif;">
                <span style="width:6px;height:6px;border-radius:50%;background:{dot};
                             box-shadow:0 0 6px {dot};display:inline-block;
                             animation:mdb-dot 2s ease-in-out infinite;"></span>
                {label}
            </span>
        </div>
    </div>
    """)


# ── Manter compatibilidade com código existente ──────────────────────────────
def mdb_cluster_status(db_name: str = "POC", online: bool = True,
                       collections: dict = None, indices: list = None):
    """Alias para mdb_sidebar — mantém compatibilidade com chamadas existentes."""
    mdb_sidebar(db_name=db_name, online=online, collections=collections, indices=indices)


def mdb_section_title(title: str, subtitle: str = ""):
    """Título de seção com identidade MongoDB Atlas."""
    sub = (f'<p style="font-size:12px;color:#3D5A6C;margin:4px 0 0;'
           f'font-family:Source Code Pro,monospace;">{subtitle}</p>') if subtitle else ""
    st.html(f"""
    <div style="margin-bottom:16px;">
        <div style="font-size:15px;font-weight:700;color:#E3FCF7;letter-spacing:-0.015em;
                    font-family:'Euclid Circular A',sans-serif;">{title}</div>{sub}
    </div>
    """)
