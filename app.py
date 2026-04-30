import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from datetime import datetime

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="London Intel Dashboard",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  /* ── Base ── */
  html, body, [data-testid="stAppViewContainer"] {
      background: #0d0d0d;
      color: #e0e0e0;
      font-family: 'Courier New', monospace;
  }
  [data-testid="stHeader"] { background: transparent; }

  /* ── Nav bar ── */
  .nav-bar {
      display: flex;
      gap: 12px;
      padding: 14px 0 18px 0;
      border-bottom: 1px solid #2a2a2a;
      margin-bottom: 28px;
  }
  .nav-btn {
      background: #1a1a1a;
      color: #aaa;
      border: 1px solid #333;
      border-radius: 6px;
      padding: 8px 22px;
      font-family: 'Courier New', monospace;
      font-size: 13px;
      letter-spacing: 0.04em;
      cursor: pointer;
      transition: all 0.2s;
  }
  .nav-btn:hover  { background: #252525; color: #fff; border-color: #555; }
  .nav-btn.active { background: #c0392b; color: #fff; border-color: #c0392b; }

  /* ── Cards ── */
  .card {
      background: #141414;
      border: 1px solid #222;
      border-radius: 8px;
      padding: 18px 22px;
      margin-bottom: 14px;
  }
  .card-title { color: #e74c3c; font-size: 14px; font-weight: bold; margin-bottom: 6px; }
  .card-meta  { color: #666; font-size: 11px; margin-bottom: 8px; }
  .card-body  { color: #ccc; font-size: 13px; line-height: 1.6; white-space: pre-wrap; }

  /* ── Log page ── */
  .log-header {
      font-size: 11px;
      color: #555;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      margin-bottom: 6px;
  }
  .log-date { color: #e74c3c; font-size: 12px; font-weight: bold; }

  .badge {
      display: inline-block;
      border-radius: 4px;
      padding: 2px 9px;
      font-size: 11px;
      font-weight: bold;
      letter-spacing: 0.06em;
      margin-right: 6px;
  }
  .badge-Progress    { background:#1a3a2a; color:#2ecc71; border:1px solid #2ecc71; }
  .badge-Next\ Steps { background:#1a2a3a; color:#3498db; border:1px solid #3498db; }
  .badge-Meeting     { background:#3a1a2a; color:#e91e8c; border:1px solid #e91e8c; }
  .badge-Network     { background:#2a2a1a; color:#f39c12; border:1px solid #f39c12; }
  .badge-Note        { background:#2a2a2a; color:#aaa;    border:1px solid #555;    }

  /* ── Password box ── */
  .pw-wrap {
      max-width: 380px;
      margin: 80px auto;
      background: #111;
      border: 1px solid #c0392b44;
      border-radius: 10px;
      padding: 40px 36px;
      text-align: center;
  }
  .pw-title { color:#e74c3c; font-size:16px; letter-spacing:0.1em; margin-bottom:24px; }

  /* ── Policy tag ── */
  .policy-tag {
      display:inline-block; background:#1a1a3a; color:#7878dd;
      border:1px solid #3a3a6a; border-radius:4px;
      padding:2px 8px; font-size:11px; margin:2px 3px;
  }
  /* ── Divider ── */
  hr.log-div { border:none; border-top:1px solid #1e1e1e; margin:6px 0 16px 0; }
</style>
""", unsafe_allow_html=True)

# ── Google Sheet URLs ─────────────────────────────────────────────────────────
SHEET_ID = 1uu3LhIMNhDRVDZw6ldpX5FAQ8wb2j-5-zTGoOX11dqE   # ← replace if needed

def sheet_url(tab: str) -> str:
    return (
        f"https://docs.google.com/spreadsheets/d/{SHEET_ID}"
        f"/gviz/tq?tqx=out:csv&sheet={tab}"
    )

@st.cache_data(ttl=300)
def load_sheet(tab: str) -> pd.DataFrame:
    try:
        return pd.read_csv(sheet_url(tab))
    except Exception as e:
        st.error(f"Could not load sheet '{tab}': {e}")
        return pd.DataFrame()

# ── Session state bootstrap ───────────────────────────────────────────────────
for key, default in {
    "page": "policy",
    "raw_clicks": 0,
    "last_raw_click": 0.0,
    "show_pw": False,
    "log_unlocked": False,
    "pw_error": False,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ── CEZ borough data ──────────────────────────────────────────────────────────
CEZ_BOROUGHS = {
    "Hammersmith & Fulham": {
        "coords": [51.4927, -0.2339],
        "cez": True,
        "intel": "H&F Creative Enterprise Zone — Affordable Workspace policy active. "
                 "Contact: Richard Miller (H&F Council). Retrofit Fund available.",
        "focus": True,
    },
    "Hackney": {
        "coords": [51.5450, -0.0553],
        "cez": True,
        "intel": "Hackney Wick & Fish Island CEZ. Strong artist studio ecosystem. "
                 "SPACE Studios, Stour Space active operators.",
        "focus": True,
    },
    "Lambeth": {
        "coords": [51.4607, -0.1163],
        "cez": True,
        "intel": "Brixton CEZ. Pop Brixton model. Council supportive of meanwhile-use.",
        "focus": True,
    },
    "Westminster": {
        "coords": [51.4973, -0.1372],
        "cez": False,
        "intel": "North Paddington — not a formal CEZ but affordable workspace clauses "
                 "in some planning permissions.",
        "focus": True,
    },
    "Tower Hamlets": {
        "coords": [51.5099, -0.0059],
        "cez": True,
        "intel": "Whitechapel & Poplar CEZ. Good transport links.",
        "focus": False,
    },
    "Southwark": {
        "coords": [51.4979, -0.0820],
        "cez": True,
        "intel": "Bermondsey / Old Kent Road CEZ. Significant regeneration underway.",
        "focus": False,
    },
}

# ── Helper: nav button ────────────────────────────────────────────────────────
def nav_button(label: str, key: str, page_target: str):
    active = "active" if st.session_state.page == page_target else ""
    if st.button(label, key=key):
        if page_target == "raw":
            import time
            now = time.time()
            if now - st.session_state.last_raw_click < 1.2:
                st.session_state.raw_clicks += 1
            else:
                st.session_state.raw_clicks = 1
            st.session_state.last_raw_click = now
            if st.session_state.raw_clicks >= 3 and not st.session_state.log_unlocked:
                st.session_state.show_pw = True
                st.session_state.raw_clicks = 0
        st.session_state.page = page_target
        st.rerun()

# ── Navigation bar ────────────────────────────────────────────────────────────
st.markdown('<div class="nav-bar">', unsafe_allow_html=True)
col1, col2, col3, col4, col5 = st.columns([1.4, 1.2, 1.2, 1, 3])
with col1:
    st.markdown("**🗺 London Intel**", help="London CEZ Intelligence Dashboard")
with col2:
    nav_button("📄 Policy Docs", "btn_policy", "policy")
with col3:
    nav_button("🗺️ Intel Map",   "btn_map",    "map")
with col4:
    nav_button("📡 Raw Feed",    "btn_raw",    "raw")
with col5:
    if st.session_state.log_unlocked:
        nav_button("🔐 Owner Log", "btn_log", "log")
st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: Policy Docs
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "policy":
    st.markdown("### 📄 Policy Documents")
    st.markdown('<p style="color:#666;font-size:12px;">CEZ policy library — funding, planning & workspace frameworks</p>', unsafe_allow_html=True)

    df = load_sheet("Policy_Documents")
    if df.empty:
        st.info("No policy documents found. Check your Google Sheet tab name.")
    else:
        # Expect columns: Title, Borough, Type, Summary, URL, Tags
        search = st.text_input("🔍 Search", placeholder="Search policies…", label_visibility="collapsed")
        if search:
            mask = df.apply(lambda r: search.lower() in str(r).lower(), axis=1)
            df = df[mask]

        for _, row in df.iterrows():
            title   = row.get("Title",   "Untitled")
            borough = row.get("Borough", "")
            ptype   = row.get("Type",    "")
            summary = row.get("Summary", "")
            url     = row.get("URL",     "")
            tags    = str(row.get("Tags", "")).split(",") if row.get("Tags") else []

            tag_html = "".join(f'<span class="policy-tag">{t.strip()}</span>' for t in tags if t.strip())
            link_html = f'<a href="{url}" target="_blank" style="color:#e74c3c;font-size:12px;">→ Open document</a>' if url else ""

            st.markdown(f"""
            <div class="card">
              <div class="card-title">{title}</div>
              <div class="card-meta">{borough} · {ptype}</div>
              <div class="card-body">{summary}</div>
              <div style="margin-top:10px">{tag_html}</div>
              <div style="margin-top:8px">{link_html}</div>
            </div>
            """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: Intel Map
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "map":
    st.markdown("### 🗺️ London CEZ Intelligence Map")
    st.markdown('<p style="color:#666;font-size:12px;">Red = active CEZ zone · Click a marker for borough intel</p>', unsafe_allow_html=True)

    m = folium.Map(
        location=[51.505, -0.09],
        zoom_start=11,
        tiles="CartoDB dark_matter",
    )

    for borough, data in CEZ_BOROUGHS.items():
        color  = "#e74c3c" if data["cez"] else "#3498db"
        radius = 14 if data.get("focus") else 9
        popup_html = f"""
        <div style="font-family:Courier New;background:#111;color:#eee;
                    padding:12px;border-radius:6px;min-width:220px;">
          <b style="color:{'#e74c3c' if data['cez'] else '#3498db'}">{borough}</b><br>
          <span style="color:#aaa;font-size:11px">
            {'🔴 CEZ Active' if data['cez'] else '🔵 Non-CEZ'}
            {'· ⭐ Priority' if data.get('focus') else ''}
          </span><br><br>
          <span style="font-size:12px">{data['intel']}</span>
        </div>
        """
        folium.CircleMarker(
            location=data["coords"],
            radius=radius,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.7,
            popup=folium.Popup(popup_html, max_width=280),
            tooltip=borough,
        ).add_to(m)

    st_folium(m, width=None, height=540)

    # Borough legend
    st.markdown("#### Priority Boroughs")
    cols = st.columns(4)
    priorities = [(b, d) for b, d in CEZ_BOROUGHS.items() if d.get("focus")]
    for i, (b, d) in enumerate(priorities):
        with cols[i % 4]:
            badge = "🔴 CEZ" if d["cez"] else "🔵 Non-CEZ"
            st.markdown(f"""
            <div class="card" style="padding:12px 16px">
              <div class="card-title" style="font-size:13px">{b}</div>
              <div class="card-meta">{badge}</div>
              <div class="card-body" style="font-size:12px">{d['intel'][:80]}…</div>
            </div>
            """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: Raw Feed
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "raw":
    st.markdown("### 📡 Raw Intelligence Feed")
    st.markdown('<p style="color:#666;font-size:12px;">Unfiltered field intelligence — boroughs, contacts, spaces</p>', unsafe_allow_html=True)

    df = load_sheet("Raw_Intelligence")
    if df.empty:
        st.info("No raw intelligence found. Check your Google Sheet tab name.")
    else:
        # Expect columns: Date, Borough, Source, Content, Tags
        boroughs = ["All"] + sorted(df["Borough"].dropna().unique().tolist()) if "Borough" in df.columns else ["All"]
        sel = st.selectbox("Filter by borough", boroughs, label_visibility="collapsed")
        if sel != "All":
            df = df[df["Borough"] == sel]

        for _, row in df.iterrows():
            date    = row.get("Date",    "")
            borough = row.get("Borough", "")
            source  = row.get("Source",  "")
            content = row.get("Content", "")
            tags    = str(row.get("Tags", "")).split(",") if row.get("Tags") else []
            tag_html = "".join(f'<span class="policy-tag">{t.strip()}</span>' for t in tags if t.strip())

            st.markdown(f"""
            <div class="card">
              <div class="card-title">{borough} · {source}</div>
              <div class="card-meta">{date}</div>
              <div class="card-body">{content}</div>
              <div style="margin-top:8px">{tag_html}</div>
            </div>
            """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PASSWORD GATE — shown as overlay when Raw Feed clicked 3×
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.show_pw and not st.session_state.log_unlocked:
    st.markdown("---")
    st.markdown("""
    <div class="pw-wrap">
      <div class="pw-title">🔐 RESTRICTED ACCESS</div>
      <p style="color:#666;font-size:12px;margin-bottom:20px">Owner log detected. Enter passphrase to continue.</p>
    </div>
    """, unsafe_allow_html=True)

    pw_input = st.text_input(
        "Passphrase",
        type="password",
        placeholder="enter passphrase…",
        key="pw_field",
        label_visibility="collapsed",
    )

    col_a, col_b = st.columns([1, 1])
    with col_a:
        if st.button("Unlock", use_container_width=True):
            if pw_input.strip().lower() == "secret diary":
                st.session_state.log_unlocked = True
                st.session_state.show_pw = False
                st.session_state.page = "log"
                st.rerun()
            else:
                st.session_state.pw_error = True
    with col_b:
        if st.button("Cancel", use_container_width=True):
            st.session_state.show_pw = False
            st.rerun()

    if st.session_state.pw_error:
        st.markdown('<p style="color:#e74c3c;text-align:center;font-size:12px">✗ Incorrect passphrase</p>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: Owner Log (secret diary)
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "log" and st.session_state.log_unlocked:

    # Header
    st.markdown("""
    <div style="border-bottom:1px solid #1e1e1e;padding-bottom:16px;margin-bottom:24px">
      <div style="color:#e74c3c;font-size:11px;letter-spacing:0.15em;text-transform:uppercase;margin-bottom:4px">
        🔐 Owner Log — Private
      </div>
      <div style="color:#eee;font-size:20px;font-weight:bold">Secret Diary</div>
      <div style="color:#555;font-size:11px;margin-top:4px">London CEZ Project · Field Journal</div>
    </div>
    """, unsafe_allow_html=True)

    df = load_sheet("Secretdiary")   # tab name from your screenshot
    if df.empty:
        st.warning("No entries found. Make sure your Google Sheet has a tab named 'Secretdiary' with columns: Date / Type / Content")
    else:
        # ── Filters ──
        col_f1, col_f2 = st.columns([2, 1])
        with col_f1:
            search = st.text_input("🔍 Search entries", placeholder="Search…", label_visibility="collapsed")
        with col_f2:
            type_opts = ["All"] + sorted(df["Type"].dropna().unique().tolist()) if "Type" in df.columns else ["All"]
            sel_type  = st.selectbox("Type", type_opts, label_visibility="collapsed")

        # Filter
        if "Type" in df.columns and sel_type != "All":
            df = df[df["Type"] == sel_type]
        if search and not df.empty:
            mask = df.apply(lambda r: search.lower() in str(r).lower(), axis=1)
            df   = df[mask]

        # Sort newest first
        if "Date" in df.columns:
            df = df.sort_values("Date", ascending=False, na_position="last")

        st.markdown(f'<div style="color:#555;font-size:11px;margin-bottom:16px">{len(df)} entries</div>', unsafe_allow_html=True)

        # ── Badge colour map ──
        BADGE_CLASS = {
            "Progress":   "badge-Progress",
            "Next Steps": "badge-Next Steps",
            "Meeting":    "badge-Meeting",
            "Network":    "badge-Network",
            "Note":       "badge-Note",
        }

        # ── Render entries ──
        for _, row in df.iterrows():
            date    = str(row.get("Date",    "")).strip()
            etype   = str(row.get("Type",    "Note")).strip()
            content = str(row.get("Content", "")).strip()

            badge_cls = BADGE_CLASS.get(etype, "badge-Note")
            badge_html = f'<span class="badge {badge_cls}">{etype.upper()}</span>'

            # Format date nicely if possible
            try:
                date_fmt = datetime.strptime(date, "%Y-%m-%d").strftime("%d %b %Y")
            except Exception:
                date_fmt = date

            st.markdown(f"""
            <div class="card" style="border-left:3px solid #c0392b">
              <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px">
                {badge_html}
                <span class="log-date">{date_fmt}</span>
              </div>
              <hr class="log-div">
              <div class="card-body" style="font-size:13px;line-height:1.75">{content}</div>
            </div>
            """, unsafe_allow_html=True)

    # Lock button
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔒 Lock & Exit", key="lock_btn"):
        st.session_state.log_unlocked = False
        st.session_state.page = "policy"
        st.rerun()
