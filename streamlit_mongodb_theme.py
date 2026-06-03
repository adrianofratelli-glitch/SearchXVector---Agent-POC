"""
MongoDB Atlas — Streamlit Theme
Paleta oficial: #001E2B · #00ED64 · Plus Jakarta Sans
config.toml define primaryColor=#00ED64 — handles slider/checkbox/toggle nativamente.
Compatível com Streamlit 1.36+.
"""

import streamlit as st


def inject_mongodb_theme():
    """CSS global MongoDB Atlas. Chamar logo após st.set_page_config()."""
    st.html("""
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
    <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
    <style>

    /* Material Icons — ligatures habilitadas para renderizar nomes como "expand_more" */
    .material-icons {
        font-family: 'Material Icons' !important;
        font-feature-settings: 'liga' 1 !important;
        -webkit-font-feature-settings: 'liga' 1 !important;
        font-weight: normal !important;
        font-style: normal !important;
        line-height: 1 !important;
        display: inline-block !important;
        text-transform: none !important;
        -webkit-font-smoothing: antialiased !important;
    }

    /* ── TOKENS ── */
    :root {
        --green:     #00ED64;
        --green-dim: #00C74E;
        --green-glow: rgba(0,237,100,0.18);

        --bg:        #001E2B;
        --bg-card:   #00283A;
        --bg-sidebar:#00141C;
        --bg-hover:  #003447;

        --border:    rgba(0,237,100,0.12);
        --border-md: rgba(0,237,100,0.22);

        --txt:       #FFFFFF;
        --txt-2:     #B8C4C2;
        --txt-3:     #6B8080;

        --font: 'Plus Jakarta Sans', system-ui, sans-serif;
        --mono: 'JetBrains Mono', monospace;
        --radius: 6px;
    }

    /* ── BASE ── */
    html, body, [class*="css"] { font-family: var(--font) !important; }
    .stApp { background-color: var(--bg) !important; }
    #MainMenu, footer, header { visibility: hidden !important; }
    .block-container { padding-top: 0 !important; max-width: 1380px !important; }

    /* ── SIDEBAR ── */
    section[data-testid="stSidebar"] {
        background-color: var(--bg-sidebar) !important;
        border-right: 1px solid var(--border) !important;
    }
    section[data-testid="stSidebar"] * { font-family: var(--font) !important; }

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
        border: 1px solid rgba(184,196,194,0.18) !important;
        border-radius: var(--radius) !important;
        color: var(--txt) !important;
        font-family: var(--font) !important;
        font-size: 14px !important;
    }
    .stTextInput > div > div > input::placeholder { color: var(--txt-3) !important; }
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--green) !important;
        box-shadow: 0 0 0 3px var(--green-glow) !important;
    }

    /* ── SELECT / MULTISELECT ── */
    .stSelectbox > div > div,
    .stMultiSelect > div > div {
        background: var(--bg-card) !important;
        border: 1px solid rgba(184,196,194,0.18) !important;
        border-radius: var(--radius) !important;
        color: var(--txt) !important;
        font-family: var(--font) !important;
    }
    [data-baseweb="popover"] ul {
        background: var(--bg-hover) !important;
        border: 1px solid var(--border-md) !important;
        border-radius: var(--radius) !important;
    }
    [data-baseweb="popover"] ul li {
        color: var(--txt-2) !important;
        font-family: var(--font) !important;
        font-size: 13px !important;
    }
    [data-baseweb="popover"] ul li:hover { background: var(--bg-card) !important; }
    .stMultiSelect span[data-baseweb="tag"] {
        background: rgba(0,237,100,0.1) !important;
        border: 1px solid rgba(0,237,100,0.25) !important;
        color: var(--green) !important;
        border-radius: 4px !important;
        font-size: 12px !important; font-weight: 600 !important;
    }

    /* ── BOTÃO PRIMÁRIO — verde MongoDB, texto escuro bem legível ── */
    .stButton > button[kind="primary"],
    .stFormSubmitButton > button,
    .stButton > button:not([kind="secondary"]) {
        background: var(--green) !important;
        color: #001E2B !important;
        border: none !important;
        border-radius: var(--radius) !important;
        font-family: var(--font) !important;
        font-size: 14px !important;
        font-weight: 700 !important;
        padding: 10px 28px !important;
        letter-spacing: 0.01em !important;
        transition: background 0.15s, box-shadow 0.15s, transform 0.1s !important;
        width: auto !important;
    }
    .stButton > button:not([kind="secondary"]):hover,
    .stFormSubmitButton > button:hover {
        background: var(--green-dim) !important;
        box-shadow: 0 4px 16px rgba(0,237,100,0.22) !important;
        transform: translateY(-1px) !important;
    }

    /* ── BOTÃO SECUNDÁRIO — ghost escuro, texto legível ── */
    .stButton > button[kind="secondary"] {
        background: rgba(0,237,100,0.06) !important;
        color: var(--txt-2) !important;
        border: 1px solid var(--border-md) !important;
        border-radius: var(--radius) !important;
        font-family: var(--font) !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        padding: 8px 16px !important;
        transition: background 0.15s, border-color 0.15s !important;
        width: auto !important;
    }
    .stButton > button[kind="secondary"]:hover {
        background: rgba(0,237,100,0.12) !important;
        border-color: var(--green) !important;
        color: var(--txt) !important;
    }

    /* ── TABS ── */
    .stTabs [data-baseweb="tab-list"] {
        background: transparent !important;
        border-bottom: 1px solid var(--border) !important;
        padding: 0 !important; gap: 0 !important;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        color: var(--txt-3) !important;
        font-family: var(--font) !important;
        font-size: 13px !important; font-weight: 500 !important;
        padding: 12px 18px !important;
        border-bottom: 2px solid transparent !important;
        transition: color 0.15s !important;
    }
    .stTabs [data-baseweb="tab"]:hover { color: var(--txt-2) !important; }
    .stTabs [aria-selected="true"] {
        color: var(--green) !important;
        border-bottom-color: var(--green) !important;
        font-weight: 600 !important;
    }
    .stTabs [data-baseweb="tab-panel"] { padding-top: 24px !important; }

    /* ── FORM CONTAINER ── */
    [data-testid="stForm"] {
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-radius: 10px !important;
        padding: 20px !important;
    }

    /* ── EXPANDER ── */
    [data-testid="stExpander"] {
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
        overflow: hidden !important;
    }
    [data-testid="stExpander"] summary {
        background: var(--bg-card) !important;
        color: var(--txt-2) !important;
        font-family: var(--font) !important;
        font-size: 13px !important; font-weight: 500 !important;
        padding: 10px 14px !important;
        list-style: none !important;
    }
    [data-testid="stExpander"] summary::-webkit-details-marker { display: none !important; }
    [data-testid="stExpander"] summary:hover {
        background: var(--bg-hover) !important;
        color: var(--green) !important;
    }
    [data-testid="stExpander"] > div {
        background: var(--bg-card) !important;
        border-top: 1px solid var(--border) !important;
        padding: 14px !important;
    }

    /* ── DATAFRAME ── */
    .stDataFrame { border: 1px solid var(--border) !important; border-radius: 8px !important; overflow: hidden !important; }
    .stDataFrame thead tr th {
        background: var(--bg-hover) !important;
        color: var(--txt-3) !important;
        font-family: var(--font) !important;
        font-size: 11px !important; font-weight: 700 !important;
        text-transform: uppercase !important; letter-spacing: 0.08em !important;
    }
    .stDataFrame tbody tr td {
        background: var(--bg-card) !important;
        color: var(--txt-2) !important;
        font-family: var(--mono) !important; font-size: 12px !important;
        border-color: var(--border) !important;
    }
    .stDataFrame tbody tr:hover td { background: var(--bg-hover) !important; }

    /* ── MÉTRICAS (st.metric nativo) ── */
    [data-testid="metric-container"] {
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-radius: 8px !important; padding: 16px !important;
    }
    [data-testid="metric-container"] label {
        font-size: 10px !important; font-weight: 700 !important;
        color: var(--txt-3) !important; text-transform: uppercase !important;
        letter-spacing: 0.1em !important; font-family: var(--font) !important;
    }
    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        font-family: var(--mono) !important;
        font-size: 20px !important; font-weight: 600 !important;
        color: var(--txt) !important;
    }

    /* ── CODE / JSON ── */
    .stJson, pre, code {
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius) !important;
        font-family: var(--mono) !important; font-size: 12px !important;
        color: var(--green) !important;
    }

    /* ── CHAT ── */
    .stChatMessage {
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
    }

    /* ── ALERTAS ── */
    [data-testid="stAlert"] { border-radius: var(--radius) !important; font-family: var(--font) !important; }

    /* ── DIVIDER ── */
    hr { border: none !important; border-top: 1px solid var(--border) !important; margin: 20px 0 !important; }

    /* ── SPINNER ── */
    .stSpinner > div { border-top-color: var(--green) !important; }

    /* ── SCROLLBAR ── */
    ::-webkit-scrollbar { width: 5px; height: 5px; }
    ::-webkit-scrollbar-thumb { background: rgba(0,237,100,0.2); border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(0,237,100,0.35); }

    /* ── SLIDER label text ── */
    [data-testid="stSlider"] p { color: var(--txt-3) !important; font-size: 11px !important; font-family: var(--mono) !important; }

    /* ── LABEL / CAPTION ── */
    [data-testid="stWidgetLabel"] p, .stCaption p { color: var(--txt-3) !important; font-family: var(--font) !important; }

    /* ── SIDEBAR: ocultar botão collapse (renderiza "keyboard_double_arrow...") ── */
    [data-testid="stSidebarCollapseButton"],
    [data-testid="collapsedControl"],
    button[data-testid="baseButton-headerNoPadding"],
    [data-testid="stSidebarHeader"] button { display: none !important; }

    /* ── EXPANDER: esconder ícone Material não renderizado ── */
    /* Remove o primeiro filho do container interno do summary (o ícone) */
    [data-testid="stExpander"] summary > div > *:first-child,
    [data-testid="stExpander"] summary > div > span:first-child,
    [data-testid="stExpander"] summary svg,
    [data-testid="stExpander"] summary > span:first-child {
        display: none !important;
    }
    /* Adiciona seta CSS própria antes do título */
    [data-testid="stExpander"] summary::before {
        content: '▸';
        color: var(--txt-3);
        font-size: 13px;
        margin-right: 6px;
        font-family: sans-serif !important;
        transition: content 0.15s;
    }
    details[open] > summary::before { content: '▾'; }

    /* ── CHAT avatars: garante arredondamento correto ── */
    [data-testid="stChatMessageAvatarUser"],
    [data-testid="stChatMessageAvatarAssistant"] {
        background: var(--bg-hover) !important;
        border: 1px solid var(--border) !important;
        border-radius: 50% !important;
        font-size: 18px !important;
    }

    /* ── FORM SUBMIT: garantir texto sempre escuro e legível ── */
    .stFormSubmitButton > button,
    .stFormSubmitButton > button * {
        color: #001E2B !important;
        font-weight: 700 !important;
    }

    </style>
    """)


# ── COMPONENTES ────────────────────────────────────────────────────────────────

def mdb_header(title: str, subtitle: str = "", pills: list = None):
    """Header MongoDB Atlas com logo SVG, título e pills por capability."""
    pill_palette = {
        "green":  ("#00ED64", "rgba(0,237,100,0.10)", "rgba(0,237,100,0.28)"),
        "blue":   ("#4DB33D", "rgba(77,179,61,0.10)", "rgba(77,179,61,0.28)"),
        "purple": ("#7E8CF7", "rgba(126,140,247,0.10)","rgba(126,140,247,0.28)"),
        "orange": ("#FFC010", "rgba(255,192,16,0.10)", "rgba(255,192,16,0.28)"),
    }
    pills_html = ""
    if pills:
        for p in pills:
            c, bg, bd = pill_palette.get(p.get("color","green"), pill_palette["green"])
            pills_html += (
                f'<span style="font-size:10px;font-weight:700;padding:4px 10px;'
                f'border-radius:4px;border:1px solid {bd};background:{bg};color:{c};'
                f'text-transform:uppercase;letter-spacing:0.07em;white-space:nowrap;'
                f'font-family:Plus Jakarta Sans,sans-serif;">{p["label"]}</span>'
            )

    sub = (f'<p style="margin:5px 0 0;font-size:12px;color:#3D5A5A;'
           f'font-family:JetBrains Mono,monospace;">{subtitle}</p>') if subtitle else ""

    # Logo: folha MongoDB oficial (SVG simplificado)
    logo = ('<svg width="26" height="26" viewBox="0 0 28 34" fill="none">'
            '<path d="M14 0C14 0 4 11 4 19.5C4 24.747 8.477 29 14 29C19.523 29 24 24.747 24 19.5C24 11 14 0 14 0Z" fill="#00ED64"/>'
            '<rect x="13" y="28" width="2" height="6" rx="1" fill="#00ED64"/>'
            '</svg>')

    st.html(f"""
    <div style="background:#00141C;border-bottom:1px solid rgba(0,237,100,0.10);
                padding:16px 4px 14px;margin-bottom:4px;">
        <div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap;">
            {logo}
            <span style="font-family:Plus Jakarta Sans,sans-serif;font-size:20px;
                         font-weight:800;color:#FFFFFF;letter-spacing:-0.025em;
                         line-height:1.2;">{title}</span>
            <div style="display:flex;gap:6px;flex-wrap:wrap;">{pills_html}</div>
        </div>
        {sub}
    </div>
    """)


def mdb_metric_card(label: str, value: str, unit: str = "", color: str = "default", badge: str = ""):
    """Card de métrica MongoDB Atlas. color: green | yellow | default"""
    val_color = {"green": "#00ED64", "yellow": "#FFC010", "default": "#FFFFFF"}.get(color, "#FFFFFF")
    border = "rgba(0,237,100,0.22)" if color == "green" else "rgba(0,237,100,0.1)"
    bg     = "linear-gradient(160deg,rgba(0,237,100,0.06),#00283A 70%)" if color == "green" else "#00283A"

    badge_html = (
        f'<span style="position:absolute;top:8px;right:8px;font-size:9px;font-weight:800;'
        f'padding:2px 7px;border-radius:3px;background:rgba(0,237,100,0.12);color:#00ED64;'
        f'border:1px solid rgba(0,237,100,0.22);text-transform:uppercase;letter-spacing:0.08em;'
        f'font-family:Plus Jakarta Sans,sans-serif;">{badge}</span>'
    ) if badge else ""
    unit_html = (f'<div style="font-size:11px;color:#3D5A5A;margin-top:3px;'
                 f'font-family:JetBrains Mono,monospace;">{unit}</div>') if unit else ""

    st.html(f"""
    <div style="background:{bg};border:1px solid {border};border-radius:8px;
                padding:14px 16px;position:relative;overflow:hidden;">
        {badge_html}
        <div style="font-size:10px;color:#3D5A5A;text-transform:uppercase;letter-spacing:0.1em;
                    font-weight:700;margin-bottom:5px;font-family:Plus Jakarta Sans,sans-serif;">{label}</div>
        <div style="font-size:22px;font-weight:700;color:{val_color};
                    font-family:JetBrains Mono,monospace;line-height:1.15;">{value}</div>
        {unit_html}
    </div>
    """)


def mdb_cluster_status(db_name: str = "POC", online: bool = True,
                       collections: dict = None, indices: list = None):
    """Sidebar MongoDB Atlas: cluster status + collections + índices."""
    dot   = "#00ED64" if online else "#DB3030"
    label = "Online"  if online else "Offline"

    st.html(f"""
    <style>@keyframes mdb-dot{{0%,100%{{opacity:1}}50%{{opacity:0.4}}}}</style>
    <div style="padding:16px 0 0;">
        <div style="font-size:10px;color:#3D5A5A;text-transform:uppercase;letter-spacing:0.12em;
                    font-weight:700;margin-bottom:8px;font-family:Plus Jakarta Sans,sans-serif;">Cluster Status</div>
        <div style="background:#00283A;border:1px solid rgba(0,237,100,0.10);border-radius:6px;padding:12px 14px;margin-bottom:16px;">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
                <span style="font-size:12px;color:#6B8080;font-family:Plus Jakarta Sans,sans-serif;">Database</span>
                <span style="font-size:11px;font-weight:700;padding:2px 8px;border-radius:3px;
                             background:rgba(126,140,247,0.12);color:#7E8CF7;
                             border:1px solid rgba(126,140,247,0.22);font-family:JetBrains Mono,monospace;">{db_name}</span>
            </div>
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <span style="font-size:12px;color:#6B8080;font-family:Plus Jakarta Sans,sans-serif;">Conexão</span>
                <span style="display:flex;align-items:center;gap:6px;font-size:12px;
                             color:{dot};font-weight:600;font-family:Plus Jakarta Sans,sans-serif;">
                    <span style="width:7px;height:7px;border-radius:50%;background:{dot};
                                 box-shadow:0 0 6px {dot};display:inline-block;
                                 animation:mdb-dot 2s ease-in-out infinite;"></span>{label}
                </span>
            </div>
        </div>
    </div>
    """)

    if collections:
        palette = ["#00ED64", "#4DB33D", "#7E8CF7", "#FFC010"]
        rows = "".join(
            f'<div style="display:flex;justify-content:space-between;align-items:center;'
            f'background:#00283A;border:1px solid rgba(0,237,100,0.08);border-radius:5px;padding:8px 12px;">'
            f'<span style="font-family:JetBrains Mono,monospace;font-size:12px;'
            f'color:{palette[i % len(palette)]};font-weight:500;">{n}</span>'
            f'<span style="font-family:JetBrains Mono,monospace;font-size:11px;color:#3D5A5A;">{c:,}</span></div>'
            for i, (n, c) in enumerate(collections.items())
        )
        st.html(f"""
        <div style="margin-bottom:16px;">
            <div style="font-size:10px;color:#3D5A5A;text-transform:uppercase;letter-spacing:0.12em;
                        font-weight:700;margin-bottom:8px;font-family:Plus Jakarta Sans,sans-serif;">Collections</div>
            <div style="display:flex;flex-direction:column;gap:4px;">{rows}</div>
        </div>
        """)

    if indices:
        rows = "".join(
            f'<div style="background:#00283A;border:1px solid rgba(0,237,100,0.08);border-radius:5px;padding:9px 12px;">'
            f'<div style="font-family:JetBrains Mono,monospace;font-size:12px;color:#00ED64;font-weight:500;margin-bottom:3px;">{n}</div>'
            f'<div style="display:flex;align-items:center;gap:5px;font-size:11px;color:#3D5A5A;font-family:Plus Jakarta Sans,sans-serif;">'
            f'<span style="width:5px;height:5px;border-radius:50%;background:#00ED64;'
            f'box-shadow:0 0 4px #00ED64;display:inline-block;"></span>{k} · READY</div></div>'
            for n, k in indices
        )
        st.html(f"""
        <div>
            <div style="font-size:10px;color:#3D5A5A;text-transform:uppercase;letter-spacing:0.12em;
                        font-weight:700;margin-bottom:8px;font-family:Plus Jakarta Sans,sans-serif;">Índices Ativos</div>
            <div style="display:flex;flex-direction:column;gap:4px;">{rows}</div>
        </div>
        """)


def mdb_section_title(title: str, subtitle: str = ""):
    """Título de seção com identidade MongoDB Atlas."""
    sub = (f'<p style="font-size:12px;color:#3D5A5A;margin:4px 0 0;'
           f'font-family:JetBrains Mono,monospace;">{subtitle}</p>') if subtitle else ""
    st.html(f"""
    <div style="margin-bottom:16px;">
        <div style="font-size:15px;font-weight:700;color:#FFFFFF;letter-spacing:-0.015em;
                    font-family:Plus Jakarta Sans,sans-serif;">{title}</div>{sub}
    </div>
    """)
