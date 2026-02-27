import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import requests

st.set_page_config(page_title="MarketLens", page_icon="📈", layout="wide", initial_sidebar_state="collapsed")

# ── LIGHT THEME CSS ───────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1rem 2rem 2rem 2rem !important; max-width: 100% !important; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    border-bottom: 2px solid #e2e8f0; gap: 0; padding: 0; background: transparent;
}
.stTabs [data-baseweb="tab"] {
    color: #64748b !important; font-weight: 500; font-size: 0.85rem;
    letter-spacing: 0.04em; padding: 0.8rem 1.6rem;
    border-bottom: 2px solid transparent; background: transparent !important;
}
.stTabs [aria-selected="true"] {
    color: #2563eb !important; border-bottom: 2px solid #2563eb !important;
}

/* Metrics */
div[data-testid="metric-container"] {
    background: #f8fafc !important; border: 1px solid #e2e8f0 !important;
    border-radius: 8px; padding: 0.8rem 1rem !important;
}
div[data-testid="metric-container"] label {
    color: #64748b !important; font-size: 0.7rem !important;
    text-transform: uppercase; letter-spacing: 0.08em;
}
div[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #0f172a !important; font-size: 1.3rem !important; font-weight: 700;
}
div[data-testid="metric-container"] [data-testid="stMetricDelta"] { font-size: 0.8rem !important; }

/* Buttons - chip style */
.stButton > button {
    background: #ffffff !important; border: 1px solid #e2e8f0 !important;
    color: #374151 !important; border-radius: 6px !important;
    font-size: 0.78rem !important; font-weight: 600 !important;
    padding: 0.3rem 0.8rem !important; transition: all 0.15s ease !important;
}
.stButton > button:hover {
    border-color: #2563eb !important; color: #2563eb !important;
    background: #eff6ff !important;
}
.stButton > button[kind="primary"] {
    background: #2563eb !important; border-color: #2563eb !important;
    color: #ffffff !important;
}

/* Text input */
.stTextInput > div > div > input {
    border: 1px solid #e2e8f0 !important; border-radius: 8px !important;
    padding: 0.55rem 0.85rem !important; font-size: 0.9rem !important;
    color: #0f172a !important; background: #ffffff !important;
}
.stTextInput > div > div > input:focus {
    border-color: #2563eb !important; box-shadow: 0 0 0 3px rgba(37,99,235,0.1) !important;
}

/* Divider */
hr { border-color: #e2e8f0 !important; margin: 1.2rem 0 !important; }

/* Expander */
.streamlit-expanderHeader {
    background: #f8fafc !important; border: 1px solid #e2e8f0 !important;
    border-radius: 8px !important; color: #374151 !important; font-weight: 500 !important;
}

/* Section label */
.section-label {
    color: #64748b; font-size: 0.7rem; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.1em;
    padding-bottom: 0.5rem; border-bottom: 1px solid #e2e8f0; margin-bottom: 1rem;
}

/* App header */
.app-header {
    display: flex; align-items: center; justify-content: space-between;
    padding: 0.6rem 0 1rem 0; border-bottom: 2px solid #e2e8f0; margin-bottom: 1.2rem;
}
.app-logo { color: #2563eb; font-size: 1.25rem; font-weight: 800; letter-spacing: -0.02em; }
.app-tagline { color: #94a3b8; font-size: 0.78rem; margin-left: 0.6rem; }
.app-time { color: #94a3b8; font-size: 0.75rem; }

/* Volume table */
.vol-table { width: 100%; border-collapse: collapse; font-size: 0.83rem; }
.vol-table th {
    color: #64748b; font-size: 0.68rem; text-transform: uppercase;
    letter-spacing: 0.08em; padding: 0.4rem 0.6rem;
    border-bottom: 1px solid #e2e8f0; text-align: right; font-weight: 600;
}
.vol-table th:first-child { text-align: left; }
.vol-table td {
    padding: 0.55rem 0.6rem; border-bottom: 1px solid #f1f5f9;
    color: #0f172a; text-align: right;
}
.vol-table td:first-child { text-align: left; font-weight: 700; color: #2563eb; }
.vol-table tr:hover td { background: #f8fafc; }
.pos { color: #16a34a !important; font-weight: 600; }
.neg { color: #dc2626 !important; font-weight: 600; }

/* News */
.news-card {
    background: #ffffff; border: 1px solid #e2e8f0;
    border-left: 3px solid #2563eb; border-radius: 0 8px 8px 0;
    padding: 0.75rem 1rem; margin-bottom: 0.5rem;
    transition: box-shadow 0.15s;
}
.news-card:hover { box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
.news-headline { color: #0f172a; font-size: 0.85rem; font-weight: 500; line-height: 1.45; }
.news-meta { color: #94a3b8; font-size: 0.72rem; margin-top: 5px; }
.news-tag {
    display: inline-block; background: #eff6ff; color: #2563eb;
    border-radius: 4px; padding: 1px 6px; font-size: 0.68rem;
    font-weight: 700; margin-right: 6px;
}

/* Summary and flag cards */
.summary-item {
    background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px;
    padding: 0.65rem 1rem; margin-bottom: 0.4rem;
    color: #1e293b; font-size: 0.87rem; line-height: 1.5;
}
.flag-item {
    background: #fef2f2; border: 1px solid #fecaca;
    border-left: 3px solid #dc2626; border-radius: 0 6px 6px 0;
    padding: 0.5rem 0.9rem; margin-bottom: 0.4rem;
    color: #1e293b; font-size: 0.84rem;
}

/* Kalshi market cards */
.kalshi-card {
    background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px;
    padding: 1rem 1.1rem; margin-bottom: 0.6rem;
    transition: box-shadow 0.15s, border-color 0.15s;
}
.kalshi-card:hover { box-shadow: 0 2px 12px rgba(0,0,0,0.07); border-color: #94a3b8; }
.kalshi-title { color: #0f172a; font-size: 0.88rem; font-weight: 600; line-height: 1.4; margin-bottom: 0.6rem; }
.kalshi-prob-bar {
    width: 100%; height: 6px; background: #fee2e2; border-radius: 99px; margin-bottom: 0.5rem; overflow: hidden;
}
.kalshi-prob-fill { height: 100%; border-radius: 99px; background: #16a34a; }
.kalshi-pcts { display: flex; justify-content: space-between; margin-bottom: 0.4rem; }
.kalshi-yes { color: #16a34a; font-size: 0.82rem; font-weight: 700; }
.kalshi-no  { color: #dc2626; font-size: 0.82rem; font-weight: 700; }
.kalshi-meta { color: #94a3b8; font-size: 0.72rem; display: flex; justify-content: space-between; }
.kalshi-event {
    display: inline-block; background: #f1f5f9; color: #475569;
    border-radius: 4px; padding: 1px 7px; font-size: 0.68rem;
    font-weight: 600; margin-bottom: 0.4rem; text-transform: uppercase; letter-spacing: 0.04em;
}
.kalshi-filter-bar { display: flex; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 1rem; }
</style>
""", unsafe_allow_html=True)

# ── SESSION STATE ─────────────────────────────────────────────────────────────
if "selected_ticker" not in st.session_state:
    st.session_state.selected_ticker = ""

# ── CONSTANTS ─────────────────────────────────────────────────────────────────
SUGGESTED = ["AAPL", "MSFT", "NVDA", "TSLA", "AMZN", "META", "GOOGL", "AMD", "NFLX",
             "JPM", "BAC", "XOM", "PLTR", "DIS", "UBER"]

VOLUME_WATCH = ["AAPL", "MSFT", "NVDA", "TSLA", "AMZN", "META", "GOOGL", "AMD", "NFLX",
                "JPM", "BAC", "XOM", "PLTR", "SPY", "QQQ", "INTC", "F", "DIS", "SOFI", "UBER"]

# ── HELPERS ───────────────────────────────────────────────────────────────────
def fmt_large(n):
    if n is None: return "N/A"
    try:
        if pd.isna(n): return "N/A"
    except: pass
    if abs(n) >= 1e12: return f"${n/1e12:.2f}T"
    if abs(n) >= 1e9:  return f"${n/1e9:.2f}B"
    if abs(n) >= 1e6:  return f"${n/1e6:.2f}M"
    return f"${n:,.0f}"

def fmt_vol(n):
    if n is None: return "N/A"
    try:
        if pd.isna(n): return "N/A"
    except: pass
    if n >= 1e9: return f"{n/1e9:.1f}B"
    if n >= 1e6: return f"{n/1e6:.1f}M"
    if n >= 1e3: return f"{n/1e3:.1f}K"
    return f"{n:.0f}"

def fmt_pct(n):
    if n is None: return "N/A"
    try:
        if pd.isna(n): return "N/A"
    except: pass
    return f"{n:.1f}%"

def pct_change(new, old):
    try:
        if None in (new, old) or pd.isna(new) or pd.isna(old) or old == 0:
            return None
        return ((new - old) / abs(old)) * 100
    except:
        return None

def safe_fmt(df):
    try:
        return df.iloc[:, :4].apply(lambda col: col.map(lambda x: fmt_large(x) if pd.notna(x) else "—"))
    except:
        return df.iloc[:, :4]

def apply_chart_style(fig, height=280):
    """Apply consistent light-theme style to any chart."""
    fig.update_layout(
        height=height,
        paper_bgcolor="white",
        plot_bgcolor="#f8fafc",
        margin=dict(l=0, r=0, t=10, b=0),
        hovermode="x unified",
        legend=dict(orientation="h", y=1.12, font=dict(size=11, color="#64748b")),
        font=dict(family="Inter, sans-serif"),
    )
    fig.update_xaxes(showgrid=False, color="#94a3b8", tickfont=dict(size=10))
    fig.update_yaxes(gridcolor="#e2e8f0", color="#94a3b8", tickfont=dict(size=10))

# ── DATA FUNCTIONS ────────────────────────────────────────────────────────────
@st.cache_data(ttl=120)
def get_indices():
    symbols = {"S&P 500": "^GSPC", "NASDAQ": "^IXIC", "DOW": "^DJI", "VIX": "^VIX"}
    out = {}
    for name, sym in symbols.items():
        try:
            fi = yf.Ticker(sym).fast_info
            out[name] = {"price": fi.last_price, "change": pct_change(fi.last_price, fi.previous_close)}
        except:
            out[name] = {"price": None, "change": None}
    return out

@st.cache_data(ttl=300)
def get_sp500_history():
    return yf.Ticker("^GSPC").history(period="3mo")

@st.cache_data(ttl=300)
def get_top_volume():
    try:
        raw = yf.download(VOLUME_WATCH, period="2d", auto_adjust=True, progress=False)
        rows = []
        for t in VOLUME_WATCH:
            try:
                closes = raw["Close"][t].dropna()
                vols   = raw["Volume"][t].dropna()
                if len(closes) >= 2 and len(vols) >= 1:
                    rows.append({
                        "ticker": t,
                        "price":  closes.iloc[-1],
                        "change": pct_change(closes.iloc[-1], closes.iloc[-2]),
                        "volume": vols.iloc[-1],
                    })
            except:
                continue
        df = pd.DataFrame(rows)
        if df.empty:
            return df
        return df.sort_values("volume", ascending=False).head(10).reset_index(drop=True)
    except:
        return pd.DataFrame()

@st.cache_data(ttl=600)
def get_market_news():
    import xml.etree.ElementTree as ET
    from datetime import datetime, timezone

    def _ts_to_date(ts):
        """Convert a Unix timestamp int or ISO string to YYYY-MM-DD."""
        if isinstance(ts, (int, float)):
            return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d")
        return str(ts)[:10]

    def _rss_fallback(sym):
        """Fetch up to 3 items from Yahoo Finance RSS for a symbol."""
        try:
            resp = requests.get(
                f"https://feeds.finance.yahoo.com/rss/2.0/headline"
                f"?s={sym}&region=US&lang=en-US",
                timeout=5,
                headers={"User-Agent": "Mozilla/5.0"},
            )
            if not resp.ok:
                return []
            root = ET.fromstring(resp.content)
            out = []
            for item in root.findall("./channel/item")[:3]:
                title = item.findtext("title", "").strip()
                link  = item.findtext("link", "").strip()
                pd    = item.findtext("pubDate", "")
                try:
                    pub_time = datetime.strptime(pd[:16].strip(), "%a, %d %b %Y").strftime("%Y-%m-%d")
                except Exception:
                    pub_time = pd[:10]
                if title:
                    out.append({"title": title, "publisher": "Yahoo Finance",
                                "link": link, "time": pub_time})
            return out
        except Exception:
            return []

    items, seen = [], set()
    for sym in ["AAPL", "MSFT", "NVDA", "TSLA", "AMZN", "META", "GOOGL"]:
        sym_items = []
        try:
            ticker_news = yf.Ticker(sym).news or []
            for a in ticker_news[:3]:
                content = a.get("content", {})
                if isinstance(content, dict) and content:
                    title     = content.get("title", "").strip()
                    provider  = content.get("provider") or {}
                    publisher = provider.get("displayName", "") if isinstance(provider, dict) else ""
                    # canonicalUrl → clickThroughUrl → url (covers older & newer yfinance)
                    url_obj   = (content.get("canonicalUrl") or
                                 content.get("clickThroughUrl") or
                                 content.get("url") or {})
                    link      = url_obj.get("url", "") if isinstance(url_obj, dict) else str(url_obj)
                    pub_time  = _ts_to_date(content.get("pubDate", ""))
                else:
                    title     = a.get("title", "").strip()
                    publisher = a.get("publisher", "")
                    link      = a.get("link", "")
                    pub_time  = _ts_to_date(a.get("providerPublishTime", ""))
                if title:
                    sym_items.append({"title": title, "publisher": publisher,
                                      "link": link, "time": pub_time})
        except Exception:
            pass

        if not sym_items:
            sym_items = _rss_fallback(sym)

        for item in sym_items:
            if item["title"] not in seen:
                seen.add(item["title"])
                items.append({**item, "ticker": sym})

    return items[:14]

KALSHI_SERIES = [
    "KXBTC", "KXETH", "KXFED", "KXINX", "KXGOLD", "KXOIL",
    "KXNFL", "KXNBA", "KXNHL", "KXMLB", "KXMMA",
    "KXCPI", "KXJOB", "KXGDP", "KXWEA", "KXPOL",
    "KXAI", "KXTECH", "KXELEC",
]

@st.cache_data(ttl=180)
def get_kalshi_markets():
    all_markets = []
    last_err = ""
    for series in KALSHI_SERIES:
        try:
            resp = requests.get(
                "https://api.elections.kalshi.com/trade-api/v2/markets",
                params={"status": "open", "limit": 50, "series_ticker": series},
                timeout=10
            )
            if resp.status_code == 200:
                all_markets.extend(resp.json().get("markets", []))
            else:
                last_err = f"HTTP {resp.status_code} for {series}"
        except Exception as e:
            last_err = str(e)
    return all_markets, last_err

@st.cache_data(ttl=60)
def search_tickers(query):
    try:
        results = yf.Search(query, max_results=6).quotes
        return [
            (r["symbol"], r.get("shortname") or r.get("longname") or "")
            for r in results
            if r.get("symbol") and r.get("quoteType") in ("EQUITY", "ETF")
        ]
    except:
        return []

@st.cache_data(ttl=300)
def load_ticker(symbol):
    t = yf.Ticker(symbol)
    return t.info, t.quarterly_financials, t.quarterly_balance_sheet, t.quarterly_cashflow, t.earnings_history

# ── ANALYSIS HELPERS ──────────────────────────────────────────────────────────
def build_summary(info, income_q, earnings_hist, ticker):
    lines = []
    if income_q is not None and len(income_q.columns) >= 2:
        rev_key = next((k for k in income_q.index if "Total Revenue" in k or "Revenue" in k), None)
        if rev_key:
            rv_new = income_q.loc[rev_key].iloc[0]
            rv_old = income_q.loc[rev_key].iloc[1]
            chg = pct_change(rv_new, rv_old)
            if chg is not None:
                direction = "grew" if chg >= 0 else "declined"
                lines.append(f"Revenue {direction} <b>{abs(chg):.1f}%</b> year-over-year to <b>{fmt_large(rv_new)}</b>.")

    if earnings_hist is not None and not earnings_hist.empty:
        eps_actual = earnings_hist.iloc[0].get("epsActual") if "epsActual" in earnings_hist.columns else None
        eps_est    = earnings_hist.iloc[0].get("epsEstimate") if "epsEstimate" in earnings_hist.columns else None
        if eps_actual is not None and not pd.isna(eps_actual):
            lines.append(f"EPS came in at <b>${eps_actual:.2f}</b>.")
            if eps_est is not None and not pd.isna(eps_est) and eps_est != 0:
                diff = eps_actual - eps_est
                bm = "beat" if diff >= 0 else "missed"
                lines.append(f"This <b>{bm}</b> analyst estimates of ${eps_est:.2f} "
                              f"by ${abs(diff):.2f} ({abs(diff/eps_est)*100:.1f}%).")

    pm = info.get("profitMargins")
    if pm is not None:
        pct = pm * 100
        label = "strong" if pct > 20 else "healthy" if pct > 10 else "thin" if pct > 0 else "negative"
        lines.append(f"Net profit margin is <b>{pct:.1f}%</b> — considered <b>{label}</b>.")

    fpe = info.get("forwardPE")
    tpe = info.get("trailingPE")
    if fpe and tpe:
        try:
            if not pd.isna(fpe) and not pd.isna(tpe):
                if fpe < tpe:
                    lines.append(f"Forward P/E ({fpe:.1f}x) is below trailing P/E ({tpe:.1f}x) — "
                                  "market expects <b>earnings growth</b> ahead.")
                else:
                    lines.append(f"Forward P/E ({fpe:.1f}x) is above trailing P/E ({tpe:.1f}x) — "
                                  "market expects <b>earnings to moderate</b>.")
        except: pass

    if not lines:
        lines.append("Summary data is limited for this ticker. See the charts below for trends.")
    return lines

def build_flags(info, income_q):
    flags = []
    de = info.get("debtToEquity")
    if de:
        try:
            if not pd.isna(de) and de > 200:
                flags.append(f"High debt-to-equity ratio ({de:.0f}%) — elevated financial leverage.")
        except: pass
    pm = info.get("profitMargins")
    if pm is not None:
        try:
            if not pd.isna(pm) and pm < 0:
                flags.append("Negative profit margin — company is currently unprofitable.")
        except: pass
    if income_q is not None and len(income_q.columns) >= 4:
        rev_key = next((k for k in income_q.index if "Total Revenue" in k or "Revenue" in k), None)
        if rev_key:
            revs = income_q.loc[rev_key].iloc[:4].values
            chgs = [pct_change(revs[i], revs[i+1]) for i in range(3)]
            chgs = [c for c in chgs if c is not None]
            if len(chgs) >= 2 and chgs[0] < chgs[-1]:
                flags.append("Revenue growth is decelerating over recent quarters.")
    ocf = info.get("operatingCashflow")
    if ocf is not None:
        try:
            if not pd.isna(ocf) and ocf < 0:
                flags.append("Negative operating cash flow — the business is burning cash.")
        except: pass
    return flags

# ── APP HEADER ────────────────────────────────────────────────────────────────
now = datetime.now().strftime("%b %d, %Y  %H:%M")
st.markdown(f"""
<div class="app-header">
  <div style="display:flex; align-items:baseline; gap:0.5rem;">
    <span class="app-logo">◆ MarketLens</span>
    <span class="app-tagline">Earnings &amp; Market Intelligence</span>
  </div>
  <span class="app-time">{now}</span>
</div>
""", unsafe_allow_html=True)

# ── TABS ──────────────────────────────────────────────────────────────────────
tab_dash, tab_earn, tab_kalshi = st.tabs(["  Market Dashboard  ", "  Earnings Analyzer  ", "  Kalshi Markets  "])

# ══════════════════════════════════════════════════════════════════════════════
# MARKET DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
with tab_dash:

    # ── Index bar ─────────────────────────────────────────────────────────────
    indices = get_indices()
    idx_cols = st.columns(4)
    for col, (name, d) in zip(idx_cols, indices.items()):
        price_str = f"{d['price']:,.2f}" if d["price"] else "—"
        delta_str = f"{d['change']:+.2f}%" if d["change"] is not None else None
        col.metric(name, price_str, delta_str)

    st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)

    # ── S&P Chart + Volume ────────────────────────────────────────────────────
    left, right = st.columns([6, 4], gap="large")

    with left:
        st.markdown('<div class="section-label">S&P 500 — 3 Month Performance</div>', unsafe_allow_html=True)
        hist = get_sp500_history()
        if not hist.empty:
            start = hist["Close"].iloc[0]
            end   = hist["Close"].iloc[-1]
            is_up = end >= start
            line_color = "#16a34a" if is_up else "#dc2626"
            fill_rgb   = "22,163,74" if is_up else "220,38,38"
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=hist.index, y=hist["Close"],
                fill="tozeroy", fillcolor=f"rgba({fill_rgb},0.07)",
                line=dict(color=line_color, width=2),
                hovertemplate="%{x|%b %d}<br><b>%{y:,.0f}</b><extra></extra>",
            ))
            apply_chart_style(fig, height=280)
            y_min = hist["Close"].min() * 0.995
            y_max = hist["Close"].max() * 1.005
            fig.update_yaxes(range=[y_min, y_max])
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with right:
        st.markdown('<div class="section-label">Top Volume Today</div>', unsafe_allow_html=True)
        vol_df = get_top_volume()
        if not vol_df.empty:
            rows_html = ""
            for _, row in vol_df.iterrows():
                chg = row["change"]
                chg_str = f"{chg:+.1f}%" if chg is not None and not pd.isna(chg) else "—"
                cls = "pos" if (chg is not None and not pd.isna(chg) and chg >= 0) else "neg"
                rows_html += f"""
                <tr>
                  <td>{row['ticker']}</td>
                  <td>${row['price']:.2f}</td>
                  <td class="{cls}">{chg_str}</td>
                  <td>{fmt_vol(row['volume'])}</td>
                </tr>"""
            st.markdown(f"""
            <table class="vol-table">
              <thead><tr><th>Ticker</th><th>Price</th><th>Chg %</th><th>Volume</th></tr></thead>
              <tbody>{rows_html}</tbody>
            </table>""", unsafe_allow_html=True)
        else:
            st.info("Volume data unavailable.")

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    # ── News Feed ─────────────────────────────────────────────────────────────
    st.markdown('<div class="section-label">Market News</div>', unsafe_allow_html=True)
    news = get_market_news()
    if news:
        nc = st.columns(2)
        for i, item in enumerate(news):
            open_a  = f'<a href="{item["link"]}" target="_blank" style="text-decoration:none">' if item["link"] else ""
            close_a = "</a>" if item["link"] else ""
            nc[i % 2].markdown(f"""
            <div class="news-card">
              {open_a}<div class="news-headline">{item['title']}</div>{close_a}
              <div class="news-meta">
                <span class="news-tag">{item['ticker']}</span>
                {item['publisher']}{"  ·  " + item['time'] if item['time'] else ""}
              </div>
            </div>""", unsafe_allow_html=True)
    else:
        st.info("News unavailable at this time.")

# ══════════════════════════════════════════════════════════════════════════════
# EARNINGS ANALYZER
# ══════════════════════════════════════════════════════════════════════════════
with tab_earn:

    # ── Suggested tickers ─────────────────────────────────────────────────────
    st.markdown('<div class="section-label">Popular Tickers — Click to Load</div>', unsafe_allow_html=True)
    chip_cols = st.columns(len(SUGGESTED))
    for i, sym in enumerate(SUGGESTED):
        if chip_cols[i].button(sym, key=f"chip_{sym}"):
            st.session_state.selected_ticker = sym

    # ── Search bar ────────────────────────────────────────────────────────────
    st.markdown("<div style='height:0.3rem'></div>", unsafe_allow_html=True)
    s1, s2 = st.columns([5, 1])
    with s1:
        query = st.text_input(
            "search",
            value=st.session_state.selected_ticker,
            placeholder='Search by company name or ticker  (e.g. "Apple" or "AAPL")',
            label_visibility="collapsed",
        )
    with s2:
        go_btn = st.button("Analyze →", type="primary", use_container_width=True)

    # ── Live search suggestions ────────────────────────────────────────────────
    if query and len(query) > 2 and not go_btn:
        looks_like_ticker = query == query.upper() and len(query) <= 5
        if not looks_like_ticker:
            matches = search_tickers(query)
            if matches:
                st.markdown('<div style="color:#94a3b8;font-size:0.7rem;margin:6px 0;">SELECT A RESULT BELOW</div>', unsafe_allow_html=True)
                for sym, name in matches[:4]:
                    if st.button(f"  {sym}   ·   {name}", key=f"sr_{sym}"):
                        st.session_state.selected_ticker = sym
                        st.rerun()

    # ── Resolve ticker ────────────────────────────────────────────────────────
    active = st.session_state.selected_ticker
    if go_btn and query:
        active = query.strip().upper()
        st.session_state.selected_ticker = active

    # ── Analysis ──────────────────────────────────────────────────────────────
    if active:
        with st.spinner(f"Loading {active}..."):
            try:
                info, income_q, balance_q, cashflow_q, earnings_hist = load_ticker(active)
            except Exception as e:
                st.error(f"Could not load data for **{active}**: {e}")
                st.stop()

        if not info or (not info.get("currentPrice") and not info.get("regularMarketPrice")):
            st.error(f"No data found for **{active}**. Check the ticker and try again.")
            st.stop()

        name     = info.get("longName", active)
        sector   = info.get("sector", "")
        industry = info.get("industry", "")
        price    = info.get("currentPrice") or info.get("regularMarketPrice")

        st.markdown(f"<div style='margin-top:1.5rem'></div>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='color:#0f172a;margin:0;font-size:1.5rem;font-weight:800;'>{name}</h2>", unsafe_allow_html=True)
        st.markdown(f"<div style='color:#64748b;font-size:0.8rem;margin-bottom:1.2rem;'>{active} &nbsp;·&nbsp; {sector} &nbsp;·&nbsp; {industry}</div>", unsafe_allow_html=True)

        # Summary
        st.markdown('<div class="section-label">Quarter in Plain English</div>', unsafe_allow_html=True)
        for line in build_summary(info, income_q, earnings_hist, active):
            st.markdown(f'<div class="summary-item">{line}</div>', unsafe_allow_html=True)

        flags = build_flags(info, income_q)
        if flags:
            with st.expander(f"⚠  {len(flags)} Risk Signal{'s' if len(flags)>1 else ''} Detected", expanded=True):
                for f in flags:
                    st.markdown(f'<div class="flag-item">{f}</div>', unsafe_allow_html=True)

        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

        # Key Metrics
        st.markdown('<div class="section-label">Key Metrics</div>', unsafe_allow_html=True)
        mkt_cap     = info.get("marketCap")
        rev_ttm     = info.get("totalRevenue")
        eps_ttm     = info.get("trailingEps")
        pe          = info.get("trailingPE")
        fwd_pe      = info.get("forwardPE")
        gross_margin = (info.get("grossMargins") or 0) * 100 or None
        net_margin   = (info.get("profitMargins") or 0) * 100 or None
        rev_growth   = (info.get("revenueGrowth") or 0) * 100 or None
        earn_growth  = (info.get("earningsGrowth") or 0) * 100 or None

        m = st.columns(6)
        m[0].metric("Market Cap",    fmt_large(mkt_cap))
        m[1].metric("Revenue (TTM)", fmt_large(rev_ttm))
        m[2].metric("Price",         f"${price:,.2f}" if price else "N/A")
        m[3].metric("EPS (TTM)",     f"${eps_ttm:.2f}" if eps_ttm else "N/A")
        m[4].metric("P/E (Trail.)",  f"{pe:.1f}x" if pe and not pd.isna(pe) else "N/A")
        m[5].metric("P/E (Fwd.)",    f"{fwd_pe:.1f}x" if fwd_pe and not pd.isna(fwd_pe) else "N/A")

        m2 = st.columns(6)
        m2[0].metric("Gross Margin", fmt_pct(gross_margin))
        m2[1].metric("Net Margin",   fmt_pct(net_margin))
        m2[2].metric("Rev. Growth",  fmt_pct(rev_growth),  delta=f"{rev_growth:.1f}%" if rev_growth else None)
        m2[3].metric("EPS Growth",   fmt_pct(earn_growth), delta=f"{earn_growth:.1f}%" if earn_growth else None)

        st.divider()

        # EPS Beat/Miss
        if earnings_hist is not None and not earnings_hist.empty and "epsActual" in earnings_hist.columns:
            st.markdown('<div class="section-label">EPS: Actual vs Estimate</div>', unsafe_allow_html=True)
            df_e = earnings_hist.head(4).sort_index()
            qtrs = df_e.index.strftime("Q%q '%y") if hasattr(df_e.index, "strftime") else df_e.index.astype(str)
            fig_eps = go.Figure()
            fig_eps.add_trace(go.Bar(x=list(qtrs), y=df_e.get("epsEstimate", pd.Series(dtype=float)),
                                     name="Estimate", marker_color="#bfdbfe"))
            fig_eps.add_trace(go.Bar(x=list(qtrs), y=df_e.get("epsActual", pd.Series(dtype=float)),
                                     name="Actual", marker_color="#2563eb"))
            fig_eps.update_layout(barmode="group")
            apply_chart_style(fig_eps, height=240)
            st.plotly_chart(fig_eps, use_container_width=True, config={"displayModeBar": False})

        # Revenue & Net Income
        if income_q is not None and not income_q.empty:
            rev_key = next((k for k in income_q.index if "Total Revenue" in k or "Revenue" in k), None)
            ni_key  = next((k for k in income_q.index if "Net Income" in k), None)
            if rev_key or ni_key:
                st.markdown('<div class="section-label">Quarterly Revenue &amp; Net Income</div>', unsafe_allow_html=True)
                qtrs = income_q.columns[:8]
                fig_inc = make_subplots(specs=[[{"secondary_y": True}]])
                if rev_key:
                    fig_inc.add_trace(go.Bar(
                        x=qtrs.strftime("%b '%y"), y=income_q.loc[rev_key, qtrs].values,
                        name="Revenue", marker_color="#bfdbfe",
                    ), secondary_y=False)
                if ni_key:
                    fig_inc.add_trace(go.Scatter(
                        x=qtrs.strftime("%b '%y"), y=income_q.loc[ni_key, qtrs].values,
                        name="Net Income", mode="lines+markers",
                        line=dict(color="#2563eb", width=2), marker=dict(size=5),
                    ), secondary_y=True)
                apply_chart_style(fig_inc, height=280)
                st.plotly_chart(fig_inc, use_container_width=True, config={"displayModeBar": False})

        # Margin Trend
        if income_q is not None and not income_q.empty:
            rev_key = next((k for k in income_q.index if "Total Revenue" in k or "Revenue" in k), None)
            gp_key  = next((k for k in income_q.index if "Gross Profit" in k), None)
            ni_key  = next((k for k in income_q.index if "Net Income" in k), None)
            if rev_key and (gp_key or ni_key):
                st.markdown('<div class="section-label">Margin Trends</div>', unsafe_allow_html=True)
                qtrs = income_q.columns[:8]
                rev_vals = income_q.loc[rev_key, qtrs]
                fig_m = go.Figure()
                if gp_key:
                    gm = (income_q.loc[gp_key, qtrs] / rev_vals * 100).round(1)
                    fig_m.add_trace(go.Scatter(x=qtrs.strftime("%b '%y"), y=gm.values,
                        name="Gross Margin %", mode="lines+markers",
                        line=dict(color="#7c3aed", width=2), marker=dict(size=5)))
                if ni_key:
                    nm = (income_q.loc[ni_key, qtrs] / rev_vals * 100).round(1)
                    fig_m.add_trace(go.Scatter(x=qtrs.strftime("%b '%y"), y=nm.values,
                        name="Net Margin %", mode="lines+markers",
                        line=dict(color="#16a34a", width=2), marker=dict(size=5)))
                apply_chart_style(fig_m, height=240)
                fig_m.update_yaxes(ticksuffix="%")
                st.plotly_chart(fig_m, use_container_width=True, config={"displayModeBar": False})

        # Balance Sheet
        if balance_q is not None and not balance_q.empty:
            cash_key   = next((k for k in balance_q.index if "Cash" in k and "Equivalent" in k), None)
            debt_key   = next((k for k in balance_q.index if "Total Debt" in k), None)
            equity_key = next((k for k in balance_q.index if "Stockholders" in k or "Total Equity" in k), None)
            snap = {}
            if cash_key:   snap["Cash & Equivalents"] = balance_q.loc[cash_key].iloc[0]
            if debt_key:   snap["Total Debt"]          = balance_q.loc[debt_key].iloc[0]
            if equity_key: snap["Shareholders' Equity"] = balance_q.loc[equity_key].iloc[0]
            if snap:
                st.markdown('<div class="section-label">Balance Sheet Snapshot</div>', unsafe_allow_html=True)
                bs = st.columns(len(snap))
                for col, (label, val) in zip(bs, snap.items()):
                    col.metric(label, fmt_large(val))

        # Raw data
        with st.expander("Raw Quarterly Financials"):
            t1, t2, t3 = st.tabs(["Income Statement", "Balance Sheet", "Cash Flow"])
            with t1:
                if income_q is not None and not income_q.empty:
                    st.dataframe(safe_fmt(income_q), use_container_width=True)
            with t2:
                if balance_q is not None and not balance_q.empty:
                    st.dataframe(safe_fmt(balance_q), use_container_width=True)
            with t3:
                if cashflow_q is not None and not cashflow_q.empty:
                    st.dataframe(safe_fmt(cashflow_q), use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# KALSHI MARKETS
# ══════════════════════════════════════════════════════════════════════════════
with tab_kalshi:
    st.markdown('<div class="section-label">Live Prediction Markets</div>', unsafe_allow_html=True)

    # ── Search + category filter ───────────────────────────────────────────────
    kcol1, kcol2 = st.columns([4, 2])
    with kcol1:
        k_search = st.text_input("kalshi_search", placeholder="Search markets  (e.g. Fed, Bitcoin, NBA...)",
                                  label_visibility="collapsed")
    with kcol2:
        k_sort = st.selectbox("sort", ["Volume (High → Low)", "Probability (High → Low)",
                                        "Closing Soon", "Recently Added"],
                               label_visibility="collapsed")

    with st.spinner("Loading Kalshi markets..."):
        markets, k_err = get_kalshi_markets()

    if not markets:
        st.error(f"Could not load Kalshi markets. {k_err or 'No markets found for the selected series.'}")
    else:
        # ── Build category list from event tickers ────────────────────────────
        def get_series(m):
            et = m.get("event_ticker", "") or m.get("ticker", "")
            return et.split("-")[0] if "-" in et else et[:6]

        all_series = sorted(set(get_series(m) for m in markets))

        # Friendly category labels for common series
        SERIES_LABELS = {
            "KXFED": "Fed / Rates", "KXBTC": "Bitcoin", "KXETH": "Ethereum",
            "KXINX": "S&P 500", "KXGOLD": "Gold", "KXOIL": "Oil",
            "KXNFL": "NFL", "KXNBA": "NBA", "KXMLB": "MLB", "KXNHL": "NHL",
            "KXMMA": "MMA / UFC", "KXSOC": "Soccer",
            "KXPOP": "Pop Culture", "KXPOL": "Politics", "KXWEA": "Weather",
            "KXCPI": "Inflation / CPI", "KXJOB": "Jobs / Unemployment",
            "KXTECH": "Tech", "KXAI": "AI",
        }

        kcategory_options = ["All"] + [SERIES_LABELS.get(s, s) for s in all_series]
        series_lookup = {SERIES_LABELS.get(s, s): s for s in all_series}

        selected_cat_label = st.selectbox(
            "Category", kcategory_options, label_visibility="visible"
        )
        selected_series = series_lookup.get(selected_cat_label) if selected_cat_label != "All" else None

        # ── Filter markets ────────────────────────────────────────────────────
        filtered = markets
        if selected_series:
            filtered = [m for m in filtered if get_series(m) == selected_series]
        if k_search:
            q = k_search.lower()
            filtered = [m for m in filtered if q in m.get("title", "").lower()
                        or q in m.get("subtitle", "").lower()
                        or q in m.get("event_ticker", "").lower()]

        # ── Sort ──────────────────────────────────────────────────────────────
        def sort_key(m):
            lp = m.get("last_price") or 0
            vol = m.get("volume_24h") or m.get("volume") or 0
            ct = m.get("close_time") or "9999"
            if k_sort == "Volume (High → Low)":
                return -vol
            elif k_sort == "Probability (High → Low)":
                return -lp
            elif k_sort == "Closing Soon":
                return ct
            else:
                return m.get("created_time") or ""

        filtered.sort(key=sort_key)

        # ── Stats row ────────────────────────────────────────────────────────
        s1, s2, s3 = st.columns(3)
        s1.metric("Open Markets", f"{len(markets):,}")
        s2.metric("Showing", f"{len(filtered):,}")
        total_vol = sum(m.get("volume_24h") or 0 for m in filtered)
        s3.metric("24h Volume (shown)", f"{total_vol:,} contracts")

        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

        # ── Market cards ──────────────────────────────────────────────────────
        if not filtered:
            st.info("No markets match your filter.")
        else:
            # Render in 2-column grid
            cols = st.columns(2, gap="medium")
            for i, m in enumerate(filtered[:100]):   # cap at 100 displayed
                title       = m.get("title", "Untitled")
                subtitle    = m.get("subtitle", "")
                last_price  = m.get("last_price") or 0       # cents, 0-100
                yes_bid     = m.get("yes_bid") or 0
                no_bid      = m.get("no_bid") or 0
                vol_24h     = m.get("volume_24h") or m.get("volume") or 0
                close_time  = m.get("close_time", "")
                event_ticker = m.get("event_ticker", "")

                # Probability: use last_price (in cents → %)
                yes_pct = last_price   # already 0-100
                no_pct  = 100 - yes_pct

                # Format close date
                close_str = ""
                if close_time:
                    try:
                        dt = datetime.fromisoformat(close_time.replace("Z", "+00:00"))
                        close_str = dt.strftime("%b %d, %Y")
                    except:
                        close_str = close_time[:10]

                vol_str = f"{vol_24h:,}" if vol_24h else "—"

                # Color the bar based on probability
                bar_color = "#16a34a" if yes_pct >= 50 else "#dc2626"
                bar_bg    = "#dcfce7" if yes_pct >= 50 else "#fee2e2"

                cols[i % 2].markdown(f"""
                <div class="kalshi-card">
                  <div class="kalshi-event">{event_ticker}</div>
                  <div class="kalshi-title">{title}{(' — ' + subtitle) if subtitle else ''}</div>
                  <div class="kalshi-prob-bar" style="background:{bar_bg}">
                    <div class="kalshi-prob-fill" style="width:{yes_pct}%; background:{bar_color}"></div>
                  </div>
                  <div class="kalshi-pcts">
                    <span class="kalshi-yes">YES &nbsp;{yes_pct}¢</span>
                    <span class="kalshi-no">NO &nbsp;{no_pct}¢</span>
                  </div>
                  <div class="kalshi-meta">
                    <span>Vol 24h: {vol_str}</span>
                    <span>Closes {close_str}</span>
                  </div>
                </div>""", unsafe_allow_html=True)

            if len(filtered) > 100:
                st.caption(f"Showing top 100 of {len(filtered)} matching markets. Use the search or category filter to narrow down.")
