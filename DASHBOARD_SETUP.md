# 24×7 Universe Dashboard — setup

A read-only Streamlit dashboard, hosted free on Streamlit Cloud, that shows your
engine's universe, conviction star-clusters, catalyst news, realized growth and
the forward-log scoreboard. It reads a SNAPSHOT your local engine pushes — it
does NOT fetch market data (cloud IPs are blocked by NSE/BSE).

## Architecture (why it's built this way)
    LOCAL (home PC)                         CLOUD (Streamlit, 24×7)
    daily scan + weekly analysis   ──push──►  universe_dashboard.py
    make_snapshot.py -> snapshot/              reads snapshot/*.csv + news.json
The local machine stays the data engine (only it can reach NSE/BSE). The cloud
app is a pretty, always-on window onto the latest snapshot.

## One-time setup
1. Create a GitHub repo, e.g. `smallcap-universe` (can be PRIVATE).
2. Put `universe_dashboard.py` in it, plus an empty `snapshot/` folder.
3. On https://share.streamlit.io → New app → point at the repo →
   main file `universe_dashboard.py`. It deploys and gives you a URL.
   (Add `SNAPSHOT_DIR=snapshot` isn't needed — it's the default.)
4. requirements for the repo (a `requirements.txt`):
       streamlit
       pandas

## Daily/weekly: push a fresh snapshot (local PC)
After your scan/analysis, run:
    python make_snapshot.py
    push_snapshot.bat            (git add/commit/push of snapshot/)
Streamlit Cloud auto-redeploys on each push, so the dashboard updates within a
minute. Wire these two lines into the END of RUN_DAILY.bat / RUN_WEEKLY_ANALYSIS.bat
to make it hands-free.

## What it shows
- Conviction clusters: ⭐..⭐⭐⭐⭐⭐ sections (from the conviction score)
- Catalyst board: recent news per top name (from news.json)
- Realized growth: actual Sales QoQ per name (fact)
- Forward scoreboard: how picks ACTUALLY did since flagged (from forward_log +
  grade_forward). NO predicted-growth column — by design.

## Honest notes
- The freshness banner shows snapshot age; if your local push stops, it goes red.
- A PRIVATE repo keeps your picks private; Streamlit Cloud supports private repos.
- Never commit API keys. The snapshot is just CSVs + news headlines — no secrets.
- Not investment advice.
