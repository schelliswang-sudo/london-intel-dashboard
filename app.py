import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from datetime import datetime
import requests

st.set_page_config(
    page_title="London Intelligence Dashboard",
    page_icon="🗺",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.main { background: #fafafa; }
[data-testid="stAppViewContainer"] { background: #fafafa; }
[data-testid="stHeader"] { background: #fafafa; }
.dashboard-title { font-family: 'DM Serif Display', serif; font-size: 2rem; color: #111; letter-spacing: -0.02em; margin-bottom: 0; line-height: 1; }
.dashboard-sub { font-size: 0.78rem; color: #666; letter-spacing: 0.15em; text-transform: uppercase; margin-top: 4px; }
.section-label { font-size: 11px; color: #bbb; text-transform: uppercase; letter-spacing: 0.12em; margin-bottom: 12px; padding-bottom: 8px; border-bottom: 0.5px solid #eee; }
.stat-card { background: #f0f0f0; border: 0.5px solid #e0e0e0; border-radius: 10px; padding: 16px 20px; margin-bottom: 8px; }
.stat-label { font-size: 11px; color: #999; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 4px; }
.stat-value { font-size: 28px; font-weight: 300; color: #111; }
.doc-card { background: #fff; border: 0.5px solid #e8e8e8; border-radius: 10px; padding: 18px 20px; margin-bottom: 10px; }
.doc-card:hover { border-color: #bbb; }
.doc-title { font-size: 14px; font-weight: 500; color: #111; margin-bottom: 6px; line-height: 1.4; }
.doc-meta { font-size: 11px; color: #aaa; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 8px; }
.doc-summary { font-size: 13px; color: #555; line-height: 1.6; margin-bottom: 10px; }
.doc-link { font-size: 12px; color: #c84b4b; text-decoration: none; }
.venue-card { background: #fff; border: 0.5px solid #e8e8e8; border-left: 2px solid #c84b4b; border-radius: 0 8px 8px 0; padding: 14px 16px; margin-bottom: 10px; }
.venue-name { font-size: 15px; font-weight: 500; color: #111; margin-bottom: 4px; }
.venue-addr { font-size: 12px; color: #888; margin-bottom: 8px; }
.venue-notes { font-size: 13px; color: #444; line-height: 1.6; white-space: pre-wrap; }
div[data-testid="stButton"] button { background: #fff !important; color: #555 !important; border: 0.5px solid #ddd !important; border-radius: 6px !important; font-family: 'DM Sans', sans-serif !important; font-size: 12px !important; font-weight: 500 !important; letter-spacing: 0.05em !important; padding: 6px 16px !important; transition: all 0.15s !important; }
div[data-testid="stButton"] button:hover { border-color: #aaa !important; color: #111 !important; }
.stSelectbox > div { background: #fff !important; }
</style>
""", unsafe_allow_html=True)

SHEET_ID = "1uu3LhIMNhDRVDZw6ldpX5FAQ8wb2j-5-zTGoOX11dqE"

@st.cache_data(ttl=300)
def load_policy_data():
    try:
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip()
        return df
    except:
        return pd.DataFrame({"Borough":[],"Document_Title":[],"Category":[],"Summary":[],"Link":[],"Upload_Date":[]})

@st.cache_data(ttl=300)
def load_venues():
    try:
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=1199979058"
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip()
        return df
    except:
        return pd.DataFrame({"Name":[],"Address":[],"Notes":[]})

@st.cache_data(ttl=0)
def load_journal():
    try:
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=1803037877"
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"Journal load error: {e}")
        return pd.DataFrame({"Date":[],"Type":[],"Update":[],"Feedback":[],"Summary":[],"Goal":[]})

@st.cache_data(ttl=86400)
def geocode(address):
    try:
        r = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": address + ", London, UK", "format": "json", "limit": 1},
            headers={"User-Agent": "LondonIntelDashboard/1.0"},
            timeout=5
        )
        data = r.json()
        if data:
            return float(data[0]["lat"]), float(data[0]["lon"])
    except:
        pass
    return None, None

if "page" not in st.session_state:
    st.session_state.page = "policy"
if "selected_venue" not in st.session_state:
    st.session_state.selected_venue = None
if "journal_expanded" not in st.session_state:
    st.session_state.journal_expanded = set()
if "journal_month" not in st.session_state:
    st.session_state.journal_month = None

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
            st.rerun()
    with c2:
        if st.button("Venue Map", key="nav_map"):
            st.session_state.page = "map"
            st.rerun()
    with c3:
        if st.button("Journal", key="nav_journal"):
            st.session_state.page = "journal"
            st.rerun()

st.markdown("---")

# ═══════════════════════════════════════════
# PAGE 1: POLICY DOCS
# ═══════════════════════════════════════════
if st.session_state.page == "policy":
    df_policy = load_policy_data()
    col_stats, col_docs = st.columns([1, 3])
    with col_stats:
        st.markdown('<div class="section-label">Overview</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="stat-card"><div class="stat-label">Total Documents</div><div class="stat-value">{len(df_policy)}</div></div>', unsafe_allow_html=True)
        categories = df_policy["Category"].dropna().unique() if "Category" in df_policy.columns else []
        st.markdown(f'<div class="stat-card"><div class="stat-label">Categories</div><div class="stat-value">{len(categories)}</div></div>', unsafe_allow_html=True)
        if len(categories) > 0:
            st.markdown('<div class="section-label" style="margin-top:20px;">Filter</div>', unsafe_allow_html=True)
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
            link_html = f'<a href="{link}" target="_blank" class="doc-link">View document →</a>' if pd.notna(link) and str(link).startswith("http") else ""
            date_html = f" · {date}" if pd.notna(date) and date else ""
            st.markdown(f"""
            <div class="doc-card">
                <div class="doc-title">{title}</div>
                <div class="doc-meta">{category}{date_html} · {borough}</div>
                <div class="doc-summary">{summary}</div>
                {link_html}
            </div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════
# PAGE 2: VENUE MAP
# ═══════════════════════════════════════════
elif st.session_state.page == "map":
    df_venues = load_venues()
    col_map, col_info = st.columns([3, 1])
    with col_map:
        st.markdown('<div class="section-label">Venue Map — Click a pin to explore</div>', unsafe_allow_html=True)
        m = folium.Map(location=[51.505, -0.09], zoom_start=11, tiles="CartoDB positron", zoom_control=True, scrollWheelZoom=False)
        if len(df_venues) > 0:
            for _, row in df_venues.iterrows():
                name = str(row.get("Name", "")).strip()
                address = str(row.get("Address", "")).strip()
                notes = str(row.get("Notes", "")).strip()
                if not name or not address:
                    continue
                lat, lng = geocode(address)
                if lat is None:
                    continue
                popup_html = f'<div style="font-family:DM Sans,sans-serif;min-width:180px;padding:4px"><b style="color:#c84b4b;font-size:13px">{name}</b><br><span style="font-size:11px;color:#888">{address}</span></div>'
                folium.CircleMarker(
                    location=[lat, lng], radius=8,
                    color="#c84b4b", fill=True, fill_color="#c84b4b", fill_opacity=0.8,
                    popup=folium.Popup(popup_html, max_width=220),
                    tooltip=name
                ).add_to(m)
        map_data = st_folium(m, width=None, height=520, returned_objects=["last_object_clicked_tooltip"])
        if map_data and map_data.get("last_object_clicked_tooltip"):
            clicked = str(map_data["last_object_clicked_tooltip"]).strip()
            st.session_state.selected_venue = clicked
    with col_info:
        st.markdown('<div class="section-label">Venue Details</div>', unsafe_allow_html=True)
        if st.session_state.selected_venue and len(df_venues) > 0:
            v = st.session_state.selected_venue
            match = df_venues[df_venues["Name"].str.strip() == v]
            if len(match) > 0:
                row = match.iloc[0]
                name = str(row.get("Name", ""))
                address = str(row.get("Address", ""))
                notes = str(row.get("Notes", ""))
                st.markdown(f'<div class="venue-card"><div class="venue-name">{name}</div><div class="venue-addr">📍 {address}</div><div class="venue-notes">{notes}</div></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="color:#aaa;font-size:13px;margin-top:20px;">Click a pin on the map to view details.</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-label" style="margin-top:24px;">All Venues</div>', unsafe_allow_html=True)
        if len(df_venues) > 0:
            for _, row in df_venues.iterrows():
                name = str(row.get("Name","")).strip()
                if name:
                    if st.button(f"📍 {name}", key=f"vbtn_{name}"):
                        st.session_state.selected_venue = name
                        st.rerun()
        else:
            st.markdown('<div style="color:#aaa;font-size:12px;">No venues yet. Add rows to the Venues sheet.</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════
# PAGE 3: JOURNAL
# ═══════════════════════════════════════════
elif st.session_state.page == "journal":
    df_j = load_journal()

    st.markdown('<div style="font-family:DM Serif Display,serif;font-size:1.5rem;color:#111;margin-bottom:4px;">Journal</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:11px;color:#bbb;letter-spacing:0.12em;text-transform:uppercase;margin-bottom:20px;">Field Notes — Trivium Sch Ltd</div>', unsafe_allow_html=True)

    if len(df_j) == 0:
        st.markdown('<div style="color:#aaa;font-size:13px;">No entries yet. Add rows to the Journal sheet.</div>', unsafe_allow_html=True)
        st.write(f"DEBUG: df shape = {df_j.shape}, columns = {list(df_j.columns)}")
    else:
        df_j["_date"] = pd.to_datetime(df_j["Date"], errors="coerce")
        df_j = df_j.dropna(subset=["_date"])
        df_j["_month_key"] = df_j["_date"].dt.strftime("%Y-%m")
        df_j["_month_label"] = df_j["_date"].dt.strftime("%b %Y")

        months = sorted(df_j["_month_key"].unique().tolist(), reverse=False)
        month_labels = {k: df_j[df_j["_month_key"]==k]["_month_label"].iloc[0] for k in months}

        if st.session_state.journal_month is None or st.session_state.journal_month not in months:
            st.session_state.journal_month = months[-1]

        # Build goal lookup
        goal_lookup = {}
        if "Goal" in df_j.columns:
            for mk in months:
                mdf = df_j[df_j["_month_key"]==mk]
                goals = mdf["Goal"].dropna()
                goals = goals[goals.str.strip().str.lower() != "nan"]
                goals = goals[goals.str.strip() != ""]
                if len(goals) > 0:
                    goal_lookup[mk] = goals.iloc[0]

        # ── Build full HTML for journal (one block, JS handles interaction) ──
        # Collect all month data
        all_months_data = {}
        for mk in months:
            month_df = df_j[df_j["_month_key"]==mk].sort_values("_date", ascending=False)
            entries = []
            for idx, (_, row) in enumerate(month_df.iterrows()):
                date_raw = str(row.get("Date","")).strip()
                try:
                    date_fmt = datetime.strptime(date_raw, "%Y-%m-%d").strftime("%d %b")
                except:
                    date_fmt = date_raw
                update   = str(row.get("Update","")).strip()
                feedback = str(row.get("Feedback","")).strip()
                summary  = str(row.get("Summary","")).strip()
                if update and update.lower() != "nan":
                    entries.append({"date": date_fmt, "type": "update", "content": update.replace("'","&#39;")})
                if feedback and feedback.lower() != "nan":
                    entries.append({"date": date_fmt, "type": "feedback", "content": feedback.replace("'","&#39;")})
                if summary and summary.lower() != "nan":
                    entries.append({"date": date_fmt, "type": "summary", "content": summary.replace("'","&#39;")})
            all_months_data[mk] = entries

        active_mk = st.session_state.journal_month

        # Build month selector HTML
        month_sel_html = '<div style="display:flex;border-bottom:1.5px solid #e0e0e0;margin-bottom:0;flex-wrap:wrap;">'
        for mk in months:
            is_act = mk == active_mk
            label = month_labels[mk]
            goal = goal_lookup.get(mk, "")
            act_lbl = "color:#c84b4b;font-weight:500;border-bottom:2px solid #c84b4b;" if is_act else "color:#aaa;"
            act_goal_border = "border-color:#c84b4b;" if is_act else ""
            act_goal_color = "color:#111;" if is_act else "color:#bbb;font-style:italic;"
            goal_text = goal if goal else "No goal set yet"
            month_sel_html += f'''
            <div style="display:flex;flex-direction:column;align-items:center;min-width:130px;cursor:pointer" onclick="selectMonth(\'{mk}\')">
              <div id="mlbl-{mk}" style="font-size:14px;padding:6px 16px 10px;{act_lbl}">{label}</div>
              <div style="width:1px;height:8px;background:#e0e0e0;"></div>
              <div id="mgoal-{mk}" style="margin:8px 8px 12px;padding:8px 10px;border:0.5px solid #e8e8e8;{act_goal_border}border-radius:8px;background:#f8f8f8;font-size:11px;{act_goal_color}line-height:1.5;width:106px;min-height:40px;">{goal_text}</div>
            </div>'''
        month_sel_html += '</div>'

        # Build timeline HTML for each month
        timelines_html = ""
        for mk in months:
            entries = all_months_data[mk]
            display = "block" if mk == active_mk else "none"
            tl = f'<div id="tl-{mk}" style="display:{display};padding-top:20px;">'

            if not entries:
                tl += '<div style="color:#aaa;font-size:13px;padding-left:20px;">No entries for this month yet.</div>'
            else:
                tl += '<div style="position:relative;">'
                # Vertical line
                tl += '<div style="position:absolute;left:50%;top:0;bottom:0;width:1.5px;background:#e0e0e0;transform:translateX(-50%);z-index:0;"></div>'
                tl += '<div style="position:relative;z-index:1;">'

                for i, entry in enumerate(entries):
                    etype   = entry["type"]
                    content = entry["content"]
                    date_f  = entry["date"]
                    eid     = f"e-{mk}-{i}"

                    dot_col = {"update":"#c84b4b","feedback":"#2eaa5e","summary":"#3a7fd5"}[etype]
                    bbg     = {"update":"#fbeaea","feedback":"#e6f5ec","summary":"#e8f0fb"}[etype]
                    bfg     = dot_col
                    blabel  = etype.capitalize()
                    preview = content[:65] + ("…" if len(content)>65 else "")

                    if etype == "summary":
                        # dot on center, content LEFT
                        tl += f'''
                        <div style="display:flex;align-items:flex-start;margin-bottom:8px;">
                          <div style="flex:1;text-align:right;padding-right:14px;">
                            <div style="font-size:10px;color:#bbb;margin-bottom:3px;">{date_f}</div>
                            <div id="{eid}-prev" style="font-size:12px;color:#aaa;font-style:italic;">Summary</div>
                            <div id="{eid}-body" style="display:none;background:#f0f5ff;border:0.5px solid #d0dff5;border-radius:8px;padding:10px 12px;font-size:12px;color:#333;line-height:1.7;text-align:left;margin-top:4px;">
                              <span style="display:inline-block;font-size:9px;font-weight:600;text-transform:uppercase;letter-spacing:.08em;padding:1px 6px;border-radius:3px;background:{bbg};color:{bfg};margin-bottom:4px;">{blabel}</span><br>{content}
                            </div>
                          </div>
                          <div style="width:20px;flex-shrink:0;display:flex;justify-content:center;padding-top:2px;">
                            <div onclick="tog(\'{eid}\')" style="width:11px;height:11px;border-radius:50%;background:{dot_col};border:2.5px solid #fafafa;cursor:pointer;box-sizing:border-box;"></div>
                          </div>
                          <div style="flex:1;"></div>
                        </div>'''
                    else:
                        # dot on center, content RIGHT
                        tl += f'''
                        <div style="display:flex;align-items:flex-start;margin-bottom:8px;">
                          <div style="flex:1;"></div>
                          <div style="width:20px;flex-shrink:0;display:flex;justify-content:center;padding-top:2px;">
                            <div onclick="tog(\'{eid}\')" style="width:11px;height:11px;border-radius:50%;background:{dot_col};border:2.5px solid #fafafa;cursor:pointer;box-sizing:border-box;"></div>
                          </div>
                          <div style="flex:1;padding-left:14px;">
                            <div style="font-size:10px;color:#bbb;margin-bottom:2px;">{date_f}</div>
                            <div id="{eid}-prev" style="font-size:12px;color:#777;">{preview}</div>
                            <div id="{eid}-body" style="display:none;background:#fff;border:0.5px solid #e8e8e8;border-radius:8px;padding:10px 12px;font-size:12px;color:#333;line-height:1.7;margin-top:4px;">
                              <span style="display:inline-block;font-size:9px;font-weight:600;text-transform:uppercase;letter-spacing:.08em;padding:1px 6px;border-radius:3px;background:{bbg};color:{bfg};margin-bottom:4px;">{blabel}</span><br>{content}
                            </div>
                          </div>
                        </div>'''

                tl += '</div></div>'
            tl += '</div>'
            timelines_html += tl

        # JavaScript
        all_month_keys = str(months).replace("'","\"")
        js = f'''
        <script>
        function selectMonth(mk) {{
            var keys = {all_month_keys};
            keys.forEach(function(k) {{
                var tl = document.getElementById("tl-" + k);
                var lbl = document.getElementById("mlbl-" + k);
                var goal = document.getElementById("mgoal-" + k);
                if (tl) tl.style.display = "none";
                if (lbl) {{ lbl.style.color="#aaa"; lbl.style.fontWeight="400"; lbl.style.borderBottom="none"; }}
                if (goal) {{ goal.style.borderColor="#e8e8e8"; goal.style.color="#bbb"; goal.style.fontStyle="italic"; }}
            }});
            var activeTl = document.getElementById("tl-" + mk);
            var activeLbl = document.getElementById("mlbl-" + mk);
            var activeGoal = document.getElementById("mgoal-" + mk);
            if (activeTl) activeTl.style.display = "block";
            if (activeLbl) {{ activeLbl.style.color="#c84b4b"; activeLbl.style.fontWeight="500"; activeLbl.style.borderBottom="2px solid #c84b4b"; }}
            if (activeGoal) {{ activeGoal.style.borderColor="#c84b4b"; activeGoal.style.color="#111"; activeGoal.style.fontStyle="normal"; }}
        }}
        function tog(eid) {{
            var prev = document.getElementById(eid + "-prev");
            var body = document.getElementById(eid + "-body");
            if (!body) return;
            if (body.style.display === "none") {{
                body.style.display = "block";
                if (prev) prev.style.display = "none";
            }} else {{
                body.style.display = "none";
                if (prev) prev.style.display = "block";
            }}
        }}
        </script>'''

        full_html = month_sel_html + '<div style="margin-top:8px;">' + timelines_html + '</div>' + js
        st.markdown(full_html, unsafe_allow_html=True)
