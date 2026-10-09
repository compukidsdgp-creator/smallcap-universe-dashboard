"""
universe_dashboard.py — the always-on command center for your small-cap engine.

Read-only viewer: it displays a SNAPSHOT your local engine produces. It does NOT
fetch market data (NSE/BSE block cloud IPs). Deploy on Streamlit Cloud for 24x7
access; your local daily job pushes a fresh snapshot to the repo it reads.

Panels:
  • Conviction clusters — ⭐..⭐⭐⭐⭐⭐ sections from the conviction score
  • Conviction Terminal — the embedded candlestick terminal (fresh each run)
  • Catalyst board — recent news for the top-conviction names
  • Forward scoreboard — how each pick ACTUALLY did since it was picked

No predicted-growth column by design: the engine's edge is marginal and unproven
live, so we show the real track record, never a crystal-ball number.

    pip install streamlit pandas
    streamlit run universe_dashboard.py
"""
from __future__ import annotations
import json
import os
from datetime import datetime

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Small-Cap Engine · Universe", layout="wide",
                   initial_sidebar_state="collapsed", page_icon="📡")

# ---------- data location: a snapshot folder the local engine fills ----------
SNAP = os.environ.get("SNAPSHOT_DIR", "snapshot")   # or point at your outputs/ locally
def _p(name): return os.path.join(SNAP, name)


# ---------- design system ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');
:root{
  --bg:#07090d; --panel:#0e131b; --panel2:#141b26; --line:#1e2733;
  --txt:#e9eef5; --dim:#7a8699; --faint:#4a5564;
  --grn:#2ee6a0; --red:#ff5c7a; --gold:#ffc24b; --blue:#4c8dff; --purple:#b57bff;
  --mono:'JetBrains Mono',ui-monospace,monospace;
}
.stApp{background:radial-gradient(1200px 600px at 20% -10%, #10213a22, transparent),
                 radial-gradient(1000px 500px at 100% 0%, #2a103a22, transparent), var(--bg);}
html,body,[class*="css"]{font-family:'Inter',sans-serif; color:var(--txt);}
#MainMenu,footer,header{visibility:hidden;}
.block-container{padding-top:1.5rem; max-width:1300px;}
h1,h2,h3{font-family:'Inter';font-weight:800;letter-spacing:-.02em;}
.hero{display:flex;align-items:center;gap:16px;margin-bottom:4px;}
.hero .logo{font-size:30px;}
.hero h1{font-size:28px;margin:0;background:linear-gradient(90deg,#fff,#8fb6ff);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}
.sub{color:var(--dim);font-size:13px;margin-bottom:22px;font-family:var(--mono);}
.kpibar{display:flex;gap:14px;flex-wrap:wrap;margin:8px 0 26px;}
.kpi{background:linear-gradient(180deg,var(--panel2),var(--panel));border:1px solid var(--line);
     border-radius:16px;padding:16px 22px;min-width:140px;position:relative;overflow:hidden;}
.kpi::after{content:'';position:absolute;top:0;left:0;right:0;height:2px;
     background:linear-gradient(90deg,var(--blue),var(--purple));opacity:.6;}
.kpi .n{font-size:30px;font-weight:800;font-family:var(--mono);line-height:1;}
.kpi .l{font-size:11px;color:var(--dim);text-transform:uppercase;letter-spacing:.8px;margin-top:8px;}
.cluster{margin:26px 0 10px;display:flex;align-items:center;gap:12px;}
.cluster .stars{font-size:22px;}
.cluster h2{font-size:17px;margin:0;}
.cluster .cnt{color:var(--dim);font-family:var(--mono);font-size:13px;}
.card{background:linear-gradient(180deg,var(--panel2),var(--panel));border:1px solid var(--line);
      border-radius:16px;padding:16px 18px;margin-bottom:12px;transition:.15s;}
.card:hover{border-color:#2d3a4d;transform:translateY(-1px);}
.row1{display:flex;justify-content:space-between;align-items:baseline;gap:10px;}
.tk{font-size:17px;font-weight:700;}
.co{color:var(--dim);font-size:12.5px;}
.convpill{font-family:var(--mono);font-weight:700;font-size:13px;padding:3px 11px;border-radius:20px;
          background:#141b26;border:1px solid var(--line);}
.chips{display:flex;gap:7px;flex-wrap:wrap;margin:10px 0 2px;}
.chip{font-size:11px;padding:2px 9px;border-radius:6px;background:#121a24;border:1px solid var(--line);color:var(--dim);}
.chip.ev{color:var(--blue);border-color:#243b63;}
.chip.g{color:var(--grn);border-color:#1e5c44;}
.chip.r{color:var(--red);border-color:#5c1e2e;}
.metricgrid{display:grid;grid-template-columns:repeat(4,1fr);gap:4px;margin-top:10px;}
.m{text-align:center;}.m .k{font-size:9.5px;color:var(--faint);text-transform:uppercase;letter-spacing:.5px;}
.m .v{font-family:var(--mono);font-size:14px;font-weight:600;margin-top:2px;}
.v.pos{color:var(--grn);}.v.neg{color:var(--red);}
.news{border-left:2px solid var(--blue);padding:6px 0 6px 12px;margin:7px 0;}
.news a{color:#b9ccff;text-decoration:none;font-size:13px;}.news a:hover{text-decoration:underline;}
.news .src{color:var(--faint);font-size:10.5px;font-family:var(--mono);}
.stale{background:#2a1418;border:1px solid #5c1e2e;color:#ff9db0;padding:8px 14px;border-radius:10px;
       font-size:12.5px;margin-bottom:16px;font-family:var(--mono);}
.fresh{background:#0d2a1e;border:1px solid #1e5c44;color:#7ff0c0;padding:8px 14px;border-radius:10px;
       font-size:12.5px;margin-bottom:16px;font-family:var(--mono);}
.disc{color:var(--faint);font-size:11px;border-top:1px solid var(--line);margin-top:30px;padding-top:14px;line-height:1.7;}
.stTabs [data-baseweb="tab-list"]{gap:4px;}
.stTabs [data-baseweb="tab"]{background:var(--panel);border:1px solid var(--line);border-radius:10px 10px 0 0;
        padding:8px 18px;font-size:13px;}
.stTabs [aria-selected="true"]{background:var(--panel2);border-bottom-color:var(--panel2);color:#fff;}
.termnote{color:var(--dim);font-size:12px;font-family:var(--mono);margin:2px 0 10px;}
</style>
""", unsafe_allow_html=True)


# ---------- loaders (resilient to missing files/columns) ----------
@st.cache_data(ttl=300)
def load_csv(name):
    p = _p(name)
    if os.path.exists(p):
        try:
            return pd.read_csv(p)
        except Exception:
            return pd.DataFrame()
    return pd.DataFrame()


@st.cache_data(ttl=300)
def load_news():
    p = _p("news.json")
    if os.path.exists(p):
        try:
            return json.load(open(p, encoding="utf-8"))
        except Exception:
            return {}
    return {}


@st.cache_data(ttl=300)
def load_terminal_html():
    """The embedded Conviction Terminal — generated locally, shipped in the snapshot."""
    p = _p("terminal.html")
    if os.path.exists(p):
        try:
            return open(p, encoding="utf-8").read()
        except Exception:
            return None
    return None


def stars(conv):
    """Map conviction score to 1-5 stars. (<=0→1 ... >6→5)"""
    if conv is None or pd.isna(conv):
        return 1
    c = float(conv)
    if c <= 1: return 1
    if c <= 2.5: return 2
    if c <= 4: return 3
    if c <= 6: return 4
    return 5


def snapshot_age():
    p = _p("conviction.csv")
    if not os.path.exists(p):
        return None
    return datetime.fromtimestamp(os.path.getmtime(p))


# ---------- header ----------
st.markdown('<div class="hero"><span class="logo">📡</span>'
            '<h1>Small-Cap Engine — Universe</h1></div>', unsafe_allow_html=True)
_age = snapshot_age()
st.markdown(f'<div class="sub">research command center · snapshot '
            f'{_age:%d %b %Y, %H:%M} · read-only viewer</div>' if _age else
            '<div class="sub">research command center · read-only viewer</div>',
            unsafe_allow_html=True)

cv = load_csv("conviction.csv")
fl = load_csv("forward_log.csv")
fin = load_csv("financials.csv")
news = load_news()

# freshness banner
if _age:
    days = (datetime.now() - _age).days
    if days <= 2:
        st.markdown(f'<div class="fresh">✓ snapshot current — {days}d old</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="stale">⚠ snapshot {days}d old — local engine may not have pushed. '
                    f'Data shown is as of {_age:%d %b}.</div>', unsafe_allow_html=True)

if cv.empty:
    st.warning("No snapshot found. Point SNAPSHOT_DIR at a folder containing "
               "conviction.csv / forward_log.csv (your engine's outputs).")
    st.stop()

# ---------- KPI bar ----------
total_picks = fl["symbol"].nunique() if not fl.empty and "symbol" in fl else cv["symbol"].nunique()
n5 = sum(stars(c) == 5 for c in cv["conviction"]) if "conviction" in cv else 0
n4 = sum(stars(c) == 4 for c in cv["conviction"]) if "conviction" in cv else 0
analysed = int(cv["analysed"].sum()) if "analysed" in cv else 0
st.markdown(f"""<div class="kpibar">
  <div class="kpi"><div class="n">{len(cv)}</div><div class="l">Current picks</div></div>
  <div class="kpi"><div class="n" style="color:var(--gold)">{n5}</div><div class="l">★★★★★</div></div>
  <div class="kpi"><div class="n" style="color:var(--blue)">{n4}</div><div class="l">★★★★</div></div>
  <div class="kpi"><div class="n">{total_picks}</div><div class="l">Universe (all-time)</div></div>
  <div class="kpi"><div class="n">{analysed}</div><div class="l">Filings analysed</div></div>
</div>""", unsafe_allow_html=True)

tab1, tab_term, tab2, tab3 = st.tabs(
    ["⭐ Conviction clusters", "⚡ Conviction Terminal", "📰 Catalyst board", "📈 Forward scoreboard"])

# ===== TAB 1: star clusters =====
with tab1:
    q = st.text_input("", placeholder="🔍 search ticker or company…", label_visibility="collapsed")
    d = cv.copy()
    d["stars"] = d["conviction"].apply(stars) if "conviction" in d else 1
    if q:
        ql = q.lower()
        d = d[d["symbol"].str.lower().str.contains(ql) |
              d.get("name", pd.Series([""]*len(d))).astype(str).str.lower().str.contains(ql)]

    def growth_for(sym):
        if fin.empty or "Symbol" not in fin:
            return None
        s = fin[(fin["Symbol"].astype(str).str.upper() == sym.upper()) &
                (fin["Metric"].isin(["Sales", "Revenue"]))]
        v = pd.to_numeric(s.get("Value"), errors="coerce").dropna().tolist()[-5:]
        if len(v) < 2 or v[-2] == 0:
            return None
        return (v[-1] / v[-2] - 1) * 100

    for sv in (5, 4, 3, 2, 1):
        grp = d[d["stars"] == sv].sort_values("conviction", ascending=False) if "conviction" in d else d[d["stars"] == sv]
        if grp.empty:
            continue
        st.markdown(f'<div class="cluster"><span class="stars">{"★"*sv}{"☆"*(5-sv)}</span>'
                    f'<h2>{["","Speculative","Watch","Moderate","High","Top"][sv]} conviction</h2>'
                    f'<span class="cnt">{len(grp)} names</span></div>', unsafe_allow_html=True)
        cols = st.columns(2)
        for i, (_, r) in enumerate(grp.iterrows()):
            g = growth_for(r["symbol"])
            gcls = "pos" if (g is not None and g > 0) else "neg" if g is not None else ""
            gtxt = f"{g:+.0f}%" if g is not None else "—"
            sue = f"{r['SUE']:.2f}" if "SUE" in r and pd.notna(r.get("SUE")) else "—"
            mcap = f"₹{r['mcap']:,.0f}" if "mcap" in r and pd.notna(r.get("mcap")) else "—"
            conv = f"{r['conviction']:g}" if "conviction" in r and pd.notna(r.get("conviction")) else "—"
            evs = "".join(f'<span class="chip ev">{e}</span>'
                          for e in str(r.get("event_types", "")).split("+") if e)
            with cols[i % 2]:
                st.markdown(f"""<div class="card">
                  <div class="row1"><div><span class="tk">{r['symbol']}</span>
                    <span class="co"> {r.get('name','')}</span></div>
                    <span class="convpill">★ {conv}</span></div>
                  <div class="chips">{evs}</div>
                  <div class="metricgrid">
                    <div class="m"><div class="k">M-Cap Cr</div><div class="v">{mcap}</div></div>
                    <div class="m"><div class="k">SUE</div><div class="v">{sue}</div></div>
                    <div class="m"><div class="k">Sales QoQ</div><div class="v {gcls}">{gtxt}</div></div>
                    <div class="m"><div class="k">Tier</div><div class="v">{r.get('tier','—')}</div></div>
                  </div></div>""", unsafe_allow_html=True)

# ===== TAB: Conviction Terminal (embedded, generated locally) =====
with tab_term:
    _term = load_terminal_html()
    if _term:
        st.markdown('<div class="termnote">Candles + volume + SMA from your local price history · '
                    'click a row to load its chart · sortable / searchable / ★-only</div>',
                    unsafe_allow_html=True)
        components.html(_term, height=860, scrolling=True)
    else:
        st.info("Conviction Terminal not in this snapshot yet. The local engine writes "
                "`terminal.html` (candlestick terminal) into the snapshot folder each run — "
                "add `run_dashboard.py` + the copy step to RUN_DAILY.bat (see setup notes).")

# ===== TAB 2: catalyst board =====
with tab2:
    st.markdown("#### Recent catalysts — top conviction names")
    top = cv.sort_values("conviction", ascending=False).head(12) if "conviction" in cv else cv.head(12)
    any_news = False
    for _, r in top.iterrows():
        items = news.get(r["symbol"], [])
        if not items:
            continue
        any_news = True
        st.markdown(f"**{r['symbol']}** · {r.get('name','')}  ·  ★ {r.get('conviction','')}")
        for n in items[:3]:
            st.markdown(f'<div class="news"><a href="{n.get("link","#")}" target="_blank">'
                        f'{n.get("title","")}</a><div class="src">{n.get("src","news")}</div></div>',
                        unsafe_allow_html=True)
    if not any_news:
        st.info("No news in this snapshot. The local engine writes news.json "
                "(per-symbol headlines) alongside the CSVs.")

# ===== TAB 3: forward scoreboard =====
with tab3:
    st.markdown("#### How picks have actually performed since flagged")
    st.caption("The honest track record — realized, out-of-sample, net of cost. "
               "Not a prediction. Populated by grade_forward.py.")
    if fl.empty:
        st.info("forward_log.csv not in snapshot yet.")
    else:
        graded = [c for c in fl.columns if "alpha" in c.lower() or "net" in c.lower() or "ret" in c.lower()]
        show_cols = [c for c in ["date", "symbol", "name", "event_types", "verdict"] if c in fl.columns] + graded
        view = fl[show_cols].sort_values("date", ascending=False) if "date" in fl else fl[show_cols]
        st.dataframe(view, use_container_width=True, height=500, hide_index=True)
        if not graded:
            st.caption("No graded columns yet — run grade_forward.py (matures at 1/3/6 months) "
                       "to populate realized alpha here.")

st.markdown("""<div class="disc">
<b>Read-only viewer.</b> Data is a snapshot pushed by the local engine; it is as fresh as the
last push (see banner). No market data is fetched here. <b>No predicted returns are shown</b> —
the engine's edge is marginal and unproven live, so this tracks the real forward record instead
of forecasting. Conviction ranks what to research first, not what to buy. The buy decision is
yours, with the filing open; the forward log is the judge. Not investment advice.
</div>""", unsafe_allow_html=True)
