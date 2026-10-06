"""
universe_dashboard.py — bright, vibrant command center for the small-cap engine.
Read-only viewer of a snapshot the local engine pushes. No market fetch here.
No predicted-growth numbers — shows the real forward record instead.
"""
from __future__ import annotations
import json
import os
from datetime import datetime

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Small-Cap Engine · Universe", layout="wide",
                   initial_sidebar_state="collapsed", page_icon="🚀")

SNAP = os.environ.get("SNAPSHOT_DIR", "snapshot")
def _p(n): return os.path.join(SNAP, n)

# ---------------- bright design system ----------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap');
:root{
  --bg:#f4f7fb; --card:#ffffff; --ink:#15223b; --dim:#5b6b85; --faint:#9aa8c0;
  --line:#e6edf6;
  --violet:#7c5cff; --blue:#2e7bff; --cyan:#00bcd4; --green:#12b886; --lime:#74c62a;
  --amber:#ff9f1c; --orange:#ff6b35; --pink:#ff4d8d; --red:#ff3b5c; --gold:#ffb703;
  --mono:'JetBrains Mono',monospace;
}
.stApp{background:
  radial-gradient(1100px 500px at 8% -5%, #7c5cff18, transparent),
  radial-gradient(900px 500px at 95% 0%, #00bcd418, transparent),
  radial-gradient(700px 400px at 50% 110%, #ff4d8d12, transparent), var(--bg);}
html,body,[class*="css"]{font-family:'Plus Jakarta Sans',sans-serif;color:var(--ink);}
#MainMenu,footer,header{visibility:hidden;}
.block-container{padding-top:1.4rem;max-width:1320px;}
h1,h2,h3{font-weight:800;letter-spacing:-.02em;}

/* hero */
.hero{display:flex;align-items:center;gap:14px;margin-bottom:2px;}
.hero .logo{font-size:32px;}
.hero h1{font-size:30px;margin:0;
  background:linear-gradient(100deg,#7c5cff,#2e7bff 40%,#ff4d8d);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}
.sub{color:var(--dim);font-size:13px;margin-bottom:18px;font-family:var(--mono);}

/* KPI tiles — each a different vivid gradient */
.kpibar{display:flex;gap:14px;flex-wrap:wrap;margin:6px 0 24px;}
.kpi{flex:1;min-width:150px;border-radius:20px;padding:18px 20px;color:#fff;position:relative;overflow:hidden;
  box-shadow:0 10px 24px -12px rgba(30,40,80,.4);}
.kpi .n{font-size:32px;font-weight:800;font-family:var(--mono);line-height:1;}
.kpi .l{font-size:11.5px;text-transform:uppercase;letter-spacing:.9px;margin-top:8px;opacity:.95;font-weight:600;}
.k1{background:linear-gradient(135deg,#7c5cff,#2e7bff);}
.k2{background:linear-gradient(135deg,#ff9f1c,#ff3b5c);}
.k3{background:linear-gradient(135deg,#2e7bff,#00bcd4);}
.k4{background:linear-gradient(135deg,#12b886,#74c62a);}
.k5{background:linear-gradient(135deg,#ff4d8d,#7c5cff);}

/* banners */
.fresh{background:linear-gradient(90deg,#12b88618,#74c62a18);border:1px solid #12b88655;color:#0b7a5a;
  padding:10px 16px;border-radius:14px;font-size:13px;margin-bottom:16px;font-weight:600;font-family:var(--mono);}
.stale{background:#ff3b5c14;border:1px solid #ff3b5c66;color:#c81e3c;
  padding:10px 16px;border-radius:14px;font-size:13px;margin-bottom:16px;font-weight:600;font-family:var(--mono);}

/* cluster header */
.cluster{display:flex;align-items:center;gap:12px;margin:28px 0 12px;}
.cluster .stars{font-size:24px;}
.cluster h2{font-size:18px;margin:0;}
.cluster .cnt{font-family:var(--mono);font-size:13px;color:#fff;padding:3px 12px;border-radius:20px;font-weight:700;}

/* stock card — colored left accent by tier */
.card{background:var(--card);border:1px solid var(--line);border-radius:18px;padding:16px 18px;margin-bottom:12px;
  box-shadow:0 6px 18px -14px rgba(30,40,80,.5);transition:.16s;position:relative;overflow:hidden;}
.card:hover{transform:translateY(-3px);box-shadow:0 14px 30px -16px rgba(30,40,80,.55);}
.card::before{content:'';position:absolute;left:0;top:0;bottom:0;width:5px;}
.c5::before{background:linear-gradient(#ffb703,#ff6b35);}
.c4::before{background:linear-gradient(#2e7bff,#00bcd4);}
.c3::before{background:linear-gradient(#7c5cff,#ff4d8d);}
.c2::before{background:linear-gradient(#9aa8c0,#5b6b85);}
.c1::before{background:#cdd6e4;}
.row1{display:flex;justify-content:space-between;align-items:flex-start;gap:10px;}
.tk{font-size:18px;font-weight:800;}
.co{color:var(--dim);font-size:12.5px;font-weight:500;}
.starline{font-size:15px;letter-spacing:1px;margin-top:3px;}
.convpill{font-family:var(--mono);font-weight:800;font-size:15px;padding:5px 13px;border-radius:14px;color:#fff;white-space:nowrap;}
.p5{background:linear-gradient(135deg,#ffb703,#ff6b35);}
.p4{background:linear-gradient(135deg,#2e7bff,#00bcd4);}
.p3{background:linear-gradient(135deg,#7c5cff,#ff4d8d);}
.p2{background:#8b99b3;}.p1{background:#aeb9cc;}
.chips{display:flex;gap:7px;flex-wrap:wrap;margin:11px 0 3px;}
.chip{font-size:11px;font-weight:700;padding:3px 11px;border-radius:9px;}
.chip.ev{background:#2e7bff18;color:#1a5fd6;}
.chip.cr{background:#7c5cff18;color:#5a3fd6;}
.metricgrid{display:grid;grid-template-columns:repeat(4,1fr);gap:6px;margin-top:12px;}
.m{background:#f6f9fd;border-radius:11px;padding:8px 6px;text-align:center;}
.m .k{font-size:9px;color:var(--faint);text-transform:uppercase;letter-spacing:.5px;font-weight:700;}
.m .v{font-family:var(--mono);font-size:15px;font-weight:700;margin-top:3px;color:var(--ink);}
.v.pos{color:var(--green);}.v.neg{color:var(--red);}

/* news cards — bright, visible, indicative */
.newscard{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:14px 16px;margin-bottom:12px;
  box-shadow:0 6px 18px -14px rgba(30,40,80,.5);border-left:5px solid var(--blue);}
.newscard .nhead{display:flex;align-items:center;gap:10px;margin-bottom:8px;}
.newscard .ntk{font-weight:800;font-size:15px;}
.newscard .nconv{font-family:var(--mono);font-size:12px;font-weight:700;color:#fff;background:linear-gradient(135deg,#7c5cff,#2e7bff);padding:2px 9px;border-radius:10px;}
.nitem{display:block;padding:8px 0;border-top:1px solid var(--line);text-decoration:none;}
.nitem:first-of-type{border-top:none;}
.nitem .t{color:#1a2e52;font-weight:600;font-size:13.5px;line-height:1.4;}
.nitem:hover .t{color:var(--blue);}
.nitem .s{color:var(--faint);font-size:10.5px;font-family:var(--mono);margin-top:2px;}

.disc{color:var(--faint);font-size:11px;border-top:1px solid var(--line);margin-top:34px;padding-top:14px;line-height:1.7;}
.stTabs [data-baseweb="tab-list"]{gap:8px;}
.stTabs [data-baseweb="tab"]{background:#fff;border:1px solid var(--line);border-radius:14px;padding:9px 20px;font-weight:700;font-size:13.5px;color:var(--dim);box-shadow:0 4px 12px -10px rgba(30,40,80,.5);}
.stTabs [aria-selected="true"]{background:linear-gradient(135deg,#7c5cff,#2e7bff);color:#fff;border-color:transparent;}
.stTextInput input{background:#fff;border:2px solid var(--line);border-radius:14px;padding:12px 16px;font-size:14px;}
.stTextInput input:focus{border-color:var(--violet);}
.stSlider,.stMultiSelect{font-weight:600;}
div[data-testid="stExpander"]{border:1px solid var(--line);border-radius:14px;background:#fff;}
</style>
""", unsafe_allow_html=True)

# ---------------- loaders ----------------
@st.cache_data(ttl=300)
def load_csv(n):
    p=_p(n)
    try: return pd.read_csv(p) if os.path.exists(p) else pd.DataFrame()
    except Exception: return pd.DataFrame()

@st.cache_data(ttl=300)
def load_news():
    p=_p("news.json")
    try: return json.load(open(p,encoding="utf-8")) if os.path.exists(p) else {}
    except Exception: return {}

def stars(c):
    if c is None or pd.isna(c): return 1
    c=float(c)
    return 1 if c<=1 else 2 if c<=2.5 else 3 if c<=4 else 4 if c<=6 else 5

def snap_age():
    p=_p("conviction.csv")
    return datetime.fromtimestamp(os.path.getmtime(p)) if os.path.exists(p) else None

STAR_COL={5:"#ffb703",4:"#2e7bff",3:"#7c5cff",2:"#8b99b3",1:"#aeb9cc"}
def star_html(sv):
    full=f'<span style="color:{STAR_COL[sv]}">{"★"*sv}</span>'
    empty=f'<span style="color:#d7deea">{"☆"*(5-sv)}</span>'
    return full+empty

# ---------------- header ----------------
st.markdown('<div class="hero"><span class="logo">🚀</span><h1>Small-Cap Engine — Universe</h1></div>',unsafe_allow_html=True)
_age=snap_age()
st.markdown(f'<div class="sub">research command center · snapshot {_age:%d %b %Y, %H:%M} · read-only</div>'
            if _age else '<div class="sub">research command center · read-only</div>',unsafe_allow_html=True)

cv=load_csv("conviction.csv"); fl=load_csv("forward_log.csv"); fin=load_csv("financials.csv"); news=load_news()

if _age:
    days=(datetime.now()-_age).days
    st.markdown(f'<div class="fresh">✓ snapshot current — {days}d old</div>' if days<=2
                else f'<div class="stale">⚠ snapshot {days}d old — data as of {_age:%d %b}</div>',unsafe_allow_html=True)

if cv.empty:
    st.warning("No snapshot data. Point SNAPSHOT_DIR at a folder with conviction.csv / forward_log.csv.")
    st.stop()

cv["stars"]=cv["conviction"].apply(stars) if "conviction" in cv else 1

# KPI tiles
n5=int((cv["stars"]==5).sum()); n4=int((cv["stars"]==4).sum())
universe=fl["symbol"].nunique() if not fl.empty and "symbol" in fl else cv["symbol"].nunique()
analysed=int(cv["analysed"].sum()) if "analysed" in cv else 0
st.markdown(f"""<div class="kpibar">
  <div class="kpi k1"><div class="n">{len(cv)}</div><div class="l">Current picks</div></div>
  <div class="kpi k2"><div class="n">{n5}</div><div class="l">★★★★★ Top</div></div>
  <div class="kpi k3"><div class="n">{n4}</div><div class="l">★★★★ High</div></div>
  <div class="kpi k4"><div class="n">{universe}</div><div class="l">Universe all-time</div></div>
  <div class="kpi k5"><div class="n">{analysed}</div><div class="l">Filings analysed</div></div>
</div>""",unsafe_allow_html=True)

def growth(sym):
    if fin.empty or "Symbol" not in fin: return None
    s=fin[(fin["Symbol"].astype(str).str.upper()==sym.upper())&(fin["Metric"].isin(["Sales","Revenue"]))]
    v=pd.to_numeric(s.get("Value"),errors="coerce").dropna().tolist()[-5:]
    return (v[-1]/v[-2]-1)*100 if len(v)>=2 and v[-2] else None

tab1,tab2,tab3=st.tabs(["⭐ Conviction clusters","📰 Catalyst board","📈 Forward scoreboard"])

# ===== TAB 1 =====
with tab1:
    c1,c2=st.columns([2,1])
    q=c1.text_input("",placeholder="🔍 search ticker or company…",label_visibility="collapsed")
    show_tiers=c2.multiselect("tiers",[5,4,3,2,1],default=[5,4,3],
                              format_func=lambda x:"★"*x,label_visibility="collapsed",
                              placeholder="filter stars")
    if not show_tiers: show_tiers=[5,4,3,2,1]

    d=cv.copy()
    if q:
        ql=q.lower()
        d=d[d["symbol"].str.lower().str.contains(ql)|d.get("name",pd.Series([""]*len(d))).astype(str).str.lower().str.contains(ql)]

    def card(r):
        sv=int(r["stars"]); g=growth(r["symbol"])
        gcls="pos" if (g is not None and g>0) else "neg" if g is not None else ""
        gtxt=f"{g:+.0f}%" if g is not None else "—"
        sue=f'{r["SUE"]:.2f}' if "SUE" in r and pd.notna(r.get("SUE")) else "—"
        mcap=f'₹{r["mcap"]:,.0f}' if "mcap" in r and pd.notna(r.get("mcap")) else "—"
        conv=f'{r["conviction"]:g}' if "conviction" in r and pd.notna(r.get("conviction")) else "—"
        evs="".join(f'<span class="chip {"cr" if "CAPITAL" in e else "ev"}">{e}</span>' for e in str(r.get("event_types","")).split("+") if e)
        return f"""<div class="card c{sv}">
          <div class="row1"><div><span class="tk">{r['symbol']}</span>
            <div class="co">{r.get('name','')}</div><div class="starline">{star_html(sv)}</div></div>
            <span class="convpill p{sv}">{conv}</span></div>
          <div class="chips">{evs}</div>
          <div class="metricgrid">
            <div class="m"><div class="k">M-Cap Cr</div><div class="v">{mcap}</div></div>
            <div class="m"><div class="k">SUE</div><div class="v">{sue}</div></div>
            <div class="m"><div class="k">Sales QoQ</div><div class="v {gcls}">{gtxt}</div></div>
            <div class="m"><div class="k">Tier</div><div class="v">{r.get('tier','—')}</div></div>
          </div></div>"""

    LBL={5:"Top",4:"High",3:"Moderate",2:"Watch",1:"Speculative"}
    for sv in (5,4,3,2,1):
        if sv not in show_tiers: continue
        grp=d[d["stars"]==sv].sort_values("conviction",ascending=False) if "conviction" in d else d[d["stars"]==sv]
        if grp.empty: continue
        st.markdown(f'<div class="cluster"><span class="stars">{star_html(sv)}</span>'
                    f'<h2>{LBL[sv]} conviction</h2>'
                    f'<span class="cnt" style="background:{STAR_COL[sv]}">{len(grp)}</span></div>',unsafe_allow_html=True)
        # top tiers: rich cards; long tail (<=2 stars or big groups): inside an expander
        if sv>=3 and len(grp)<=30:
            cols=st.columns(2)
            for i,(_,r) in enumerate(grp.iterrows()):
                cols[i%2].markdown(card(r),unsafe_allow_html=True)
        else:
            with st.expander(f"Show {len(grp)} {LBL[sv].lower()} names"):
                cols=st.columns(2)
                for i,(_,r) in enumerate(grp.iterrows()):
                    cols[i%2].markdown(card(r),unsafe_allow_html=True)

# ===== TAB 2: catalyst =====
with tab2:
    st.markdown("### 📰 Catalyst board — what's in the news for your top names")
    top=cv.sort_values("conviction",ascending=False).head(15) if "conviction" in cv else cv.head(15)
    any_n=False; cols=st.columns(2); i=0
    for _,r in top.iterrows():
        items=news.get(r["symbol"],[])
        if not items: continue
        any_n=True
        conv=f'{r["conviction"]:g}' if pd.notna(r.get("conviction")) else ""
        body="".join(f'<a class="nitem" href="{n.get("link","#")}" target="_blank">'
                     f'<div class="t">{n.get("title","")}</div><div class="s">↗ {n.get("src","news")}</div></a>'
                     for n in items[:3])
        cols[i%2].markdown(f'<div class="newscard"><div class="nhead"><span class="ntk">{r["symbol"]}</span>'
                           f'<span class="co">{r.get("name","")}</span><span class="nconv">★ {conv}</span></div>{body}</div>',
                           unsafe_allow_html=True); i+=1
    if not any_n:
        st.info("No news in this snapshot. make_snapshot.py writes news.json for the top names.")

# ===== TAB 3: forward =====
with tab3:
    st.markdown("### 📈 Forward scoreboard — how picks actually performed")
    st.caption("Realized, out-of-sample, net of cost. The honest track record — not a prediction.")
    if fl.empty:
        st.info("forward_log.csv not in snapshot yet.")
    else:
        graded=[c for c in fl.columns if any(k in c.lower() for k in ("alpha","net","ret"))]
        cols=[c for c in ["date","symbol","name","event_types","verdict"] if c in fl.columns]+graded
        view=fl[cols].sort_values("date",ascending=False) if "date" in fl else fl[cols]
        st.dataframe(view,use_container_width=True,height=520,hide_index=True)
        if not graded:
            st.caption("No graded columns yet — run grade_forward.py (matures 1/3/6 months) for realized alpha.")

st.markdown("""<div class="disc"><b>Read-only viewer.</b> Data is a snapshot pushed by the local engine,
as fresh as the last push. No market data fetched here. <b>No predicted returns</b> — this tracks the real
forward record, not forecasts. Conviction ranks what to research first, not what to buy. Not investment advice.</div>""",
unsafe_allow_html=True)
