import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import requests
import json

st.set_page_config(
    page_title="London Intelligence Dashboard",
    page_icon="🗺",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.main { background: #fafafa; }
[data-testid="stAppViewContainer"] { background: #fafafa; }
[data-testid="stHeader"] { background: #fafafa; }

.dashboard-title {
    font-family: 'DM Serif Display', serif;
    font-size: 2rem;
    color: #111;
    letter-spacing: -0.02em;
    margin-bottom: 0;
    line-height: 1;
    cursor: default;
}
.dashboard-sub {
    font-size: 0.78rem;
    color: #666;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-top: 4px;
}

.stat-card {
    background: #f0f0f0;
    border: 0.5px solid #e0e0e0;
    border-radius: 10px;
    padding: 16px 20px;
    margin-bottom: 8px;
}
.stat-label { font-size: 11px; color: #999; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 4px; }
.stat-value { font-size: 28px; font-weight: 300; color: #111; }

.doc-card {
    background: #fff;
    border: 0.5px solid #e8e8e8;
    border-radius: 10px;
    padding: 18px 20px;
    margin-bottom: 10px;
    transition: border-color 0.2s;
}
.doc-card:hover { border-color: #bbb; }
.doc-title { font-size: 14px; font-weight: 500; color: #111; margin-bottom: 6px; line-height: 1.4; }
.doc-meta { font-size: 11px; color: #aaa; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 8px; }
.doc-summary { font-size: 13px; color: #555; line-height: 1.6; margin-bottom: 10px; }
.doc-link { font-size: 12px; color: #c84b4b; text-decoration: none; }

.intel-card {
    background: #fff;
    border: 0.5px solid #e8e8e8;
    border-left: 2px solid #c84b4b;
    border-radius: 0 8px 8px 0;
    padding: 14px 16px;
    margin-bottom: 8px;
}
.intel-card.non-cez { border-left-color: #ccc; }
.intel-text { font-size: 13px; color: #444; line-height: 1.6; }
.intel-date { font-size: 11px; color: #bbb; margin-top: 6px; }

.badge-cez {
    display: inline-block;
    background: #3d1a1a;
    color: #e07070;
    font-size: 10px;
    font-weight: 500;
    padding: 2px 8px;
    border-radius: 3px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-left: 8px;
}
.badge-non {
    display: inline-block;
    background: #1e1e1e;
    color: #555;
    font-size: 10px;
    font-weight: 500;
    padding: 2px 8px;
    border-radius: 3px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-left: 8px;
}

.raw-card {
    background: #fff;
    border: 0.5px solid #e8e8e8;
    border-radius: 8px;
    padding: 14px 16px;
    margin-bottom: 8px;
}
.raw-title { font-size: 13px; font-weight: 500; color: #222; margin-bottom: 4px; }
.raw-snippet { font-size: 12px; color: #777; line-height: 1.5; }
.raw-meta { font-size: 11px; color: #bbb; margin-top: 6px; }
.status-pending {
    display: inline-block;
    background: #1e2a1e;
    color: #5a8a5a;
    font-size: 10px;
    padding: 2px 7px;
    border-radius: 3px;
    letter-spacing: 0.08em;
}

.section-label {
    font-size: 11px;
    color: #bbb;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-bottom: 12px;
    padding-bottom: 8px;
    border-bottom: 0.5px solid #eee;
}

/* Log page styles */
.log-entry {
    background: #fff;
    border: 0.5px solid #e8e8e8;
    border-radius: 10px;
    padding: 18px 20px;
    margin-bottom: 12px;
    position: relative;
}
.log-date {
    font-size: 11px;
    color: #aaa;
    letter-spacing: 0.1em;
    margin-bottom: 6px;
}
.log-content {
    font-size: 14px;
    color: #333;
    line-height: 1.7;
}
.log-type {
    display: inline-block;
    font-size: 10px;
    font-weight: 500;
    padding: 2px 8px;
    border-radius: 3px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 8px;
}
.type-progress { background: #1a2a1a; color: #6aaa6a; }
.type-next { background: #1a1a2a; color: #6a8aaa; }
.type-meeting { background: #2a1a1a; color: #aa6a6a; }
.type-network { background: #2a1a2a; color: #aa6aaa; }
.type-note { background: #2a2a1a; color: #aaaa6a; }

div[data-testid="stButton"] button {
    background: #fff !important;
    color: #555 !important;
    border: 0.5px solid #ddd !important;
    border-radius: 6px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 12px !important;
    font-weight: 500 !important;
    letter-spacing: 0.05em !important;
    padding: 6px 16px !important;
    transition: all 0.15s !important;
}
div[data-testid="stButton"] button:hover {
    border-color: #aaa !important;
    color: #111 !important;
}

.stSelectbox > div { background: #fff !important; }
</style>
""", unsafe_allow_html=True)

SHEET_ID = "1uu3LhIMNhDRVDZw6ldpX5FAQ8wb2j-5-zTGoOX11dqE"
SECRET_PASSWORD = "secret diary"

CEZ_BOROUGHS = [
    "Brent", "Croydon", "Ealing", "Hackney", "Tower Hamlets",
    "Hammersmith and Fulham", "Hammersmith & Fulham",
    "Haringey", "Hounslow", "Islington", "Lambeth",
    "Lewisham", "Waltham Forest", "Westminster"
]

@st.cache_data(ttl=300)
def load_borough_data():
    try:
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Borough_Intelligence"
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip()
        return df
    except:
        return pd.DataFrame({
            "Borough": ["Brent","Croydon","Ealing","Hackney & Tower Hamlets",
                        "Hammersmith & Fulham","Haringey","Hounslow","Islington",
                        "Lambeth","Lewisham","Waltham Forest","Westminster"],
            "Policy_Status": ["CEZ"]*12,
            "Intelligence": [""]*12,
            "Link": [""]*12,
            "Update_Date": [""]*12
        })

@st.cache_data(ttl=300)
def load_policy_data():
    try:
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Policy_Documents"
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip()
        return df
    except:
        return pd.DataFrame({
            "Borough": ["The Great London"],
            "Document_Title": ["CREATIVE ENTERPRISE ZONES | London (2017)"],
            "Category": ["CEZ Policy"],
            "Summary": ["Foundational CEZ policy document."],
            "Link": ["https://www.london.gov.uk"],
            "Upload_Date": ["2024-01-15"]
        })

@st.cache_data(ttl=300)
def load_raw_data():
    try:
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Raw_Intelligence"
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip()
        return df
    except:
        return pd.DataFrame({
            "Borough": ["Camden"],
            "Source_URL": ["https://..."],
            "Title": ["New parking consultation"],
            "Snippet": ["Summary..."],
            "Scraped_Date": ["2024-03-10"],
            "Status": ["Pending"]
        })

@st.cache_data(ttl=300)
def load_log_data():
    try:
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Secretdiary"
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip()
        return df
    except:
        return pd.DataFrame({
            "Date": ["2026-04-30"],
            "Type": ["Progress"],
            "Content": ["Dashboard launched successfully."]
        })

@st.cache_data(ttl=3600)
def load_geojson():
    import os, json as _json
    geojson_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "london_boroughs.geojson")
    if os.path.exists(geojson_path):
        with open(geojson_path) as f:
            return _json.load(f)
    return {"type":"FeatureCollection","features":[]}

def is_cez(name):
    name_lower = name.lower()
    for b in CEZ_BOROUGHS:
        if b.lower() in name_lower or name_lower in b.lower():
            return True
    return False

# Session state init
if "page" not in st.session_state:
    st.session_state.page = "policy"
if "selected_borough" not in st.session_state:
    st.session_state.selected_borough = None
if "raw_click_count" not in st.session_state:
    st.session_state.raw_click_count = 0
if "show_secret_input" not in st.session_state:
    st.session_state.show_secret_input = False
if "secret_unlocked" not in st.session_state:
    st.session_state.secret_unlocked = False

# ── HEADER ──
col_title, col_nav = st.columns([1, 2])

with col_title:
    st.markdown('<div class="dashboard-title">London Intel</div>', unsafe_allow_html=True)
    st.markdown('<div class="dashboard-sub">Commercial Intelligence Dashboard</div>', unsafe_allow_html=True)

with col_nav:
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3, _ = st.columns([1, 1, 1, 2])
    with c1:
        if st.button("Policy Docs", key="nav_policy"):
            st.session_state.page = "policy"
            st.session_state.raw_click_count = 0
    with c2:
        if st.button("Intel Map", key="nav_map"):
            st.session_state.page = "map"
            st.session_state.raw_click_count = 0
    with c3:
        if st.button("Raw Feed", key="nav_raw"):
            if st.session_state.secret_unlocked:
                st.session_state.page = "raw"
                st.rerun()
            else:
                st.session_state.raw_click_count += 1
                if st.session_state.raw_click_count >= 3:
                    st.session_state.show_secret_input = True
                    st.session_state.raw_click_count = 0
                    st.rerun()
                else:
                    st.session_state.page = "raw"
                    st.rerun()

# Secret password input
if st.session_state.show_secret_input and not st.session_state.secret_unlocked:
    st.markdown("---")
    col_pw, _ = st.columns([1, 3])
    with col_pw:
        pwd = st.text_input("", type="password", placeholder="Enter passphrase...", label_visibility="collapsed")
        if pwd == SECRET_PASSWORD:
            st.session_state.secret_unlocked = True
            st.session_state.show_secret_input = False
            st.session_state.page = "log"
            st.rerun()
        elif pwd and pwd != SECRET_PASSWORD:
            st.markdown('<div style="color:#666;font-size:12px;margin-top:4px;">Incorrect</div>', unsafe_allow_html=True)

st.markdown("---")

# ─────────────────────────────────────────────
# PAGE 1: POLICY DOCUMENTS
# ─────────────────────────────────────────────
if st.session_state.page == "policy":
    df_policy = load_policy_data()
    col_stats, col_docs = st.columns([1, 3])

    with col_stats:
        st.markdown('<div class="section-label">Overview</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="stat-card"><div class="stat-label">Total Documents</div><div class="stat-value">{len(df_policy)}</div></div>', unsafe_allow_html=True)
        categories = df_policy["Category"].dropna().unique() if "Category" in df_policy.columns else []
        st.markdown(f'<div class="stat-card"><div class="stat-label">Categories</div><div class="stat-value">{len(categories)}</div></div>', unsafe_allow_html=True)
        if len(categories) > 0:
            st.markdown('<div class="section-label" style="margin-top:20px;">Filter by category</div>', unsafe_allow_html=True)
            selected_cat = st.selectbox("", ["All"] + list(categories), label_visibility="collapsed")
        else:
            selected_cat = "All"

    with col_docs:
        st.markdown('<div class="section-label">Documents</div>', unsafe_allow_html=True)
        filtered = df_policy if selected_cat == "All" else df_policy[df_policy["Category"] == selected_cat]
        for _, row in filtered.iterrows():
            title = row.get("Document_Title", "Untitled")
            category = row.get("Category", "")
            summary = row.get("Summary", "")
            link = row.get("Link", "")
            date = row.get("Upload_Date", "")
            borough = row.get("Borough", "")
            link_html = f'<a href="{link}" target="_blank" class="doc-link">View document →</a>' if pd.notna(link) and link and link != "https://..." else ""
            date_html = f" · {date}" if pd.notna(date) and date else ""
            st.markdown(f"""
            <div class="doc-card">
                <div class="doc-title">{title}</div>
                <div class="doc-meta">{category}{date_html} · {borough}</div>
                <div class="doc-summary">{summary}</div>
                {link_html}
            </div>
            """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# PAGE 2: INTEL MAP
# ─────────────────────────────────────────────
elif st.session_state.page == "map":
    df_borough = load_borough_data()
    geojson_data = load_geojson()
    col_map, col_info = st.columns([3, 1])

    with col_map:
        st.markdown('<div class="section-label">London Boroughs — Click to explore</div>', unsafe_allow_html=True)
        m = folium.Map(location=[51.505, -0.09], zoom_start=10, tiles="CartoDB dark_matter", zoom_control=True, scrollWheelZoom=False)
        geojson_features = geojson_data.get("features", []) if geojson_data else []
        if geojson_features:
            def style_fn(feature):
                name = feature["properties"].get("name", feature["properties"].get("NAME", ""))
                cez = is_cez(name)
                return {"fillColor": "#c84b4b" if cez else "#2a2a2a", "fillOpacity": 0.65 if cez else 0.4, "color": "#e07070" if cez else "#444", "weight": 1}
            def highlight_fn(feature):
                return {"fillOpacity": 0.9, "weight": 2, "color": "#f0ede6"}
            first_props = geojson_features[0].get("properties", {})
            tooltip_field = "name" if "name" in first_props else "NAME"
            folium.GeoJson(geojson_data, style_function=style_fn, highlight_function=highlight_fn,
                tooltip=folium.GeoJsonTooltip(fields=[tooltip_field], aliases=["Borough:"],
                style="background-color:#1a1a1a;color:#f0ede6;border:1px solid #333;font-family:DM Sans,sans-serif;font-size:13px;")
            ).add_to(m)
        map_data = st_folium(m, width=None, height=500, returned_objects=["last_object_clicked_tooltip"])
        if map_data and map_data.get("last_object_clicked_tooltip"):
            clicked_name = map_data["last_object_clicked_tooltip"]
            if isinstance(clicked_name, dict):
                clicked_name = list(clicked_name.values())[0]
            st.session_state.selected_borough = str(clicked_name).replace("Borough:", "").strip()

    with col_info:
        st.markdown('<div class="section-label">Borough Intelligence</div>', unsafe_allow_html=True)
        if st.session_state.selected_borough:
            b = st.session_state.selected_borough
            cez = is_cez(b)
            badge = '<span class="badge-cez">CEZ</span>' if cez else '<span class="badge-non">Non-CEZ</span>'
            st.markdown(f'<div style="font-size:18px;font-weight:500;color:#111;margin-bottom:12px;">{b}{badge}</div>', unsafe_allow_html=True)
            # Safely find Borough column regardless of case/spaces
            borough_col = next((c for c in df_borough.columns if c.strip().lower() == "borough"), None)
            if borough_col is None:
                st.warning(f"Column 'Borough' not found. Available: {list(df_borough.columns)}")
                matches = pd.DataFrame()
            else:
                matches = df_borough[df_borough[borough_col].str.lower().str.contains(b.lower(), na=False)]
            if len(matches) > 0:
                for _, row in matches.iterrows():
                    intel = row.get("Intelligence", "")
                    link = row.get("Link", "")
                    date = row.get("Update_Date", "")
                    if not intel: intel = ""
                    if pd.notna(intel) and intel:
                        link_html = f'<br><a href="{link}" target="_blank" class="doc-link">Source →</a>' if pd.notna(link) and link else ""
                        date_html = f'<div class="intel-date">{date}</div>' if pd.notna(date) and date else ""
                        card_class = "intel-card" if cez else "intel-card non-cez"
                        st.markdown(f'<div class="{card_class}"><div class="intel-text">{intel}</div>{date_html}{link_html}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="intel-card non-cez"><div class="intel-text" style="color:#555;">No intelligence recorded yet for this borough.</div></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="color:#444;font-size:13px;margin-top:20px;">Click a borough on the map to view intelligence.</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-label" style="margin-top:24px;">Legend</div>', unsafe_allow_html=True)
        st.markdown("""
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
            <div style="width:12px;height:12px;background:#c84b4b;border-radius:2px;"></div>
            <span style="font-size:12px;color:#888;">CEZ designated area</span>
        </div>
        <div style="display:flex;align-items:center;gap:8px;">
            <div style="width:12px;height:12px;background:#2a2a2a;border:1px solid #444;border-radius:2px;"></div>
            <span style="font-size:12px;color:#888;">Non-CEZ borough</span>
        </div>
        """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# PAGE 3: RAW FEED
# ─────────────────────────────────────────────
elif st.session_state.page == "raw":
    df_raw = load_raw_data()
    col_filter, col_feed = st.columns([1, 3])
    with col_filter:
        st.markdown('<div class="section-label">Filter</div>', unsafe_allow_html=True)
        boroughs_raw = ["All"] + sorted(df_raw["Borough"].dropna().unique().tolist()) if "Borough" in df_raw.columns else ["All"]
        selected_borough_raw = st.selectbox("Borough", boroughs_raw, label_visibility="visible")
        statuses = ["All"] + sorted(df_raw["Status"].dropna().unique().tolist()) if "Status" in df_raw.columns else ["All"]
        selected_status = st.selectbox("Status", statuses, label_visibility="visible")
        st.markdown('<div class="stat-card" style="margin-top:20px;"><div class="stat-label">Total items</div><div class="stat-value">{}</div></div>'.format(len(df_raw)), unsafe_allow_html=True)
    with col_feed:
        st.markdown('<div class="section-label">Unfiltered Raw Feed — Awaiting Review</div>', unsafe_allow_html=True)
        filtered_raw = df_raw.copy()
        if selected_borough_raw != "All":
            filtered_raw = filtered_raw[filtered_raw["Borough"] == selected_borough_raw]
        if selected_status != "All":
            filtered_raw = filtered_raw[filtered_raw["Status"] == selected_status]
        if len(filtered_raw) == 0:
            st.markdown('<div style="color:#444;font-size:13px;">No items match the current filter.</div>', unsafe_allow_html=True)
        for _, row in filtered_raw.iterrows():
            borough = row.get("Borough", "")
            title = row.get("Title", "Untitled")
            snippet = row.get("Snippet", "")
            source = row.get("Source_URL", "")
            date = row.get("Scraped_Date", "")
            status = row.get("Status", "")
            status_html = f'<span class="status-pending">{status}</span>' if status else ""
            source_html = f'<a href="{source}" target="_blank" class="doc-link">Source →</a>' if pd.notna(source) and source and source != "https://..." else ""
            st.markdown(f"""
            <div class="raw-card">
                <div class="raw-title">{title} {status_html}</div>
                <div class="raw-snippet">{snippet}</div>
                <div class="raw-meta">{borough} · {date} &nbsp; {source_html}</div>
            </div>
            """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# PAGE 4: SECRET OWNER LOG
# ─────────────────────────────────────────────
elif st.session_state.page == "log" and st.session_state.secret_unlocked:
    df_log = load_log_data()

    col_head, col_lock = st.columns([4, 1])
    with col_head:
        st.markdown('<div style="font-family:DM Serif Display,serif;font-size:1.5rem;color:#111;margin-bottom:4px;">Owner\'s Log</div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size:11px;color:#bbb;letter-spacing:0.12em;text-transform:uppercase;margin-bottom:24px;">Private · Not visible to investors</div>', unsafe_allow_html=True)
    with col_lock:
        if st.button("🔒 Lock", key="lock_btn"):
            st.session_state.secret_unlocked = False
            st.session_state.page = "policy"
            st.rerun()

    type_colors = {
        "Progress": "type-progress",
        "Next Steps": "type-next",
        "Meeting": "type-meeting",
        "Network": "type-network",
        "Note": "type-note"
    }

    # Sort by date descending (newest first)
    if "Date" in df_log.columns:
        df_log = df_log.sort_values("Date", ascending=False)

    if len(df_log) == 0:
        st.markdown('<div style="color:#444;font-size:13px;">No log entries yet. Add rows to the Owner_Log sheet.</div>', unsafe_allow_html=True)

    for _, row in df_log.iterrows():
        date = row.get("Date", "")
        log_type = row.get("Type", "Note")
        content = row.get("Content", "")
        type_class = type_colors.get(log_type, "type-note")
        st.markdown(f"""
        <div class="log-entry">
            <div class="log-date">{date}</div>
            <span class="log-type {type_class}">{log_type}</span>
            <div class="log-content">{content}</div>
        </div>
        """, unsafe_allow_html=True)
