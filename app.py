import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

st.set_page_config(page_title="Earnings Analyzer", layout="wide")

st.title("Earnings Report Analyzer")
st.caption("Enter any stock ticker to get a plain-English breakdown of their latest earnings.")

# --- Input ---
col1, col2 = st.columns([2, 1])
with col1:
    ticker_input = st.text_input("Stock Ticker", placeholder="e.g. AAPL, MSFT, NVDA").upper().strip()
with col2:
    st.write("")
    st.write("")
    analyze_btn = st.button("Analyze", type="primary", use_container_width=True)


def fmt_large(n):
    """Format large numbers into readable billions/millions."""
    if n is None or pd.isna(n):
        return "N/A"
    if abs(n) >= 1e12:
        return f"${n/1e12:.2f}T"
    if abs(n) >= 1e9:
        return f"${n/1e9:.2f}B"
    if abs(n) >= 1e6:
        return f"${n/1e6:.2f}M"
    return f"${n:,.0f}"


def fmt_pct(n):
    if n is None or pd.isna(n):
        return "N/A"
    return f"{n:.1f}%"


def pct_change(new, old):
    if old is None or new is None or pd.isna(old) or pd.isna(new) or old == 0:
        return None
    return ((new - old) / abs(old)) * 100


def delta_color(val):
    if val is None or pd.isna(val):
        return "gray"
    return "green" if val >= 0 else "red"


def delta_arrow(val):
    if val is None or pd.isna(val):
        return ""
    return "▲" if val >= 0 else "▼"


def generate_summary(info, income_q, eps_trend):
    """Build a rule-based plain-English summary."""
    lines = []
    name = info.get("longName", ticker_input)

    # Revenue trend
    if income_q is not None and len(income_q.columns) >= 2:
        rev_key = next((k for k in income_q.index if "Total Revenue" in k or "Revenue" in k), None)
        if rev_key:
            rev_latest = income_q.loc[rev_key].iloc[0]
            rev_prior = income_q.loc[rev_key].iloc[1]
            rev_chg = pct_change(rev_latest, rev_prior)
            if rev_chg is not None:
                direction = "grew" if rev_chg >= 0 else "declined"
                lines.append(
                    f"**Revenue** {direction} {abs(rev_chg):.1f}% year-over-year to {fmt_large(rev_latest)}."
                )

    # EPS
    if eps_trend is not None and len(eps_trend) >= 2:
        eps_latest = eps_trend.iloc[0]["epsActual"] if "epsActual" in eps_trend.columns else None
        eps_est = eps_trend.iloc[0]["epsEstimate"] if "epsEstimate" in eps_trend.columns else None
        if eps_latest is not None and not pd.isna(eps_latest):
            lines.append(f"**Earnings per share (EPS)** came in at ${eps_latest:.2f}.")
            if eps_est is not None and not pd.isna(eps_est) and eps_est != 0:
                diff = eps_latest - eps_est
                beat_miss = "beat" if diff >= 0 else "missed"
                lines.append(
                    f"This **{beat_miss}** analyst estimates of ${eps_est:.2f} "
                    f"by ${abs(diff):.2f} ({abs(diff/eps_est)*100:.1f}%)."
                )

    # Profitability
    profit_margin = info.get("profitMargins")
    if profit_margin is not None:
        margin_pct = profit_margin * 100
        if margin_pct > 20:
            label = "strong"
        elif margin_pct > 10:
            label = "healthy"
        elif margin_pct > 0:
            label = "thin"
        else:
            label = "negative"
        lines.append(f"The company has a **{label} net profit margin** of {margin_pct:.1f}%.")

    # Guidance / forward PE
    fwd_pe = info.get("forwardPE")
    trail_pe = info.get("trailingPE")
    if fwd_pe and trail_pe and not pd.isna(fwd_pe) and not pd.isna(trail_pe):
        if fwd_pe < trail_pe:
            lines.append(
                f"The forward P/E of {fwd_pe:.1f}x is below the trailing P/E of {trail_pe:.1f}x, "
                "suggesting the market expects **earnings growth** ahead."
            )
        else:
            lines.append(
                f"The forward P/E of {fwd_pe:.1f}x is above the trailing P/E of {trail_pe:.1f}x, "
                "suggesting the market expects **earnings to soften** ahead."
            )

    if not lines:
        lines.append("Summary data is limited for this ticker. See the charts below for trends.")

    return lines


def flag_risks(info, income_q):
    """Identify potential red flags."""
    flags = []

    # Debt to equity
    de = info.get("debtToEquity")
    if de and not pd.isna(de) and de > 200:
        flags.append(f"High debt-to-equity ratio ({de:.0f}%) — elevated financial leverage.")

    # Negative profit margin
    pm = info.get("profitMargins")
    if pm is not None and not pd.isna(pm) and pm < 0:
        flags.append("Negative profit margin — company is currently unprofitable.")

    # Revenue deceleration (last 3 quarters)
    if income_q is not None and len(income_q.columns) >= 4:
        rev_key = next((k for k in income_q.index if "Total Revenue" in k or "Revenue" in k), None)
        if rev_key:
            revs = income_q.loc[rev_key].iloc[:4].values
            changes = [pct_change(revs[i], revs[i + 1]) for i in range(3)]
            changes = [c for c in changes if c is not None]
            if len(changes) >= 2 and changes[0] < changes[-1]:
                flags.append("Revenue growth is decelerating over recent quarters.")

    # Operating cash flow
    ocf = info.get("operatingCashflow")
    if ocf is not None and not pd.isna(ocf) and ocf < 0:
        flags.append("Negative operating cash flow — the business is burning cash.")

    return flags


if analyze_btn and ticker_input:
    with st.spinner(f"Fetching data for {ticker_input}..."):
        try:
            stock = yf.Ticker(ticker_input)
            info = stock.info

            if not info or info.get("regularMarketPrice") is None and info.get("currentPrice") is None:
                st.error(f"Could not find data for ticker **{ticker_input}**. Check the symbol and try again.")
                st.stop()

            # Pull financial statements (quarterly)
            income_q = stock.quarterly_financials
            balance_q = stock.quarterly_balance_sheet
            cashflow_q = stock.quarterly_cashflow
            earnings_hist = stock.earnings_history

        except Exception as e:
            st.error(f"Error fetching data: {e}")
            st.stop()

    company_name = info.get("longName", ticker_input)
    sector = info.get("sector", "N/A")
    industry = info.get("industry", "N/A")
    current_price = info.get("currentPrice") or info.get("regularMarketPrice")

    st.markdown(f"## {company_name} ({ticker_input})")
    st.caption(f"{sector} · {industry}")

    # ── Plain English Summary ──────────────────────────────────────────────────
    st.markdown("### What Happened This Quarter")
    summary_lines = generate_summary(info, income_q, earnings_hist)
    for line in summary_lines:
        st.markdown(f"- {line}")

    risks = flag_risks(info, income_q)
    if risks:
        with st.expander("⚠️ Potential Red Flags", expanded=True):
            for r in risks:
                st.markdown(f"- {r}")

    st.divider()

    # ── Key Metrics ────────────────────────────────────────────────────────────
    st.markdown("### Key Metrics at a Glance")

    market_cap = info.get("marketCap")
    revenue_ttm = info.get("totalRevenue")
    gross_margin = info.get("grossMargins", 0) * 100 if info.get("grossMargins") else None
    profit_margin = info.get("profitMargins", 0) * 100 if info.get("profitMargins") else None
    eps_ttm = info.get("trailingEps")
    pe = info.get("trailingPE")
    fwd_pe = info.get("forwardPE")
    rev_growth = info.get("revenueGrowth", 0) * 100 if info.get("revenueGrowth") else None
    earnings_growth = info.get("earningsGrowth", 0) * 100 if info.get("earningsGrowth") else None

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Market Cap", fmt_large(market_cap))
    m2.metric("Revenue (TTM)", fmt_large(revenue_ttm))
    m3.metric("Current Price", f"${current_price:,.2f}" if current_price else "N/A")
    m4.metric("Trailing EPS", f"${eps_ttm:.2f}" if eps_ttm else "N/A")

    m5, m6, m7, m8 = st.columns(4)
    m5.metric(
        "Gross Margin",
        fmt_pct(gross_margin),
        delta=f"{gross_margin:.1f}%" if gross_margin else None,
        delta_color="normal" if gross_margin and gross_margin > 30 else "inverse",
    )
    m6.metric("Net Margin", fmt_pct(profit_margin))
    m7.metric("Trailing P/E", f"{pe:.1f}x" if pe and not pd.isna(pe) else "N/A")
    m8.metric("Forward P/E", f"{fwd_pe:.1f}x" if fwd_pe and not pd.isna(fwd_pe) else "N/A")

    if rev_growth is not None or earnings_growth is not None:
        m9, m10, _, _ = st.columns(4)
        m9.metric(
            "Revenue Growth (YoY)",
            fmt_pct(rev_growth),
            delta=f"{rev_growth:.1f}%" if rev_growth is not None else None,
        )
        m10.metric(
            "Earnings Growth (YoY)",
            fmt_pct(earnings_growth),
            delta=f"{earnings_growth:.1f}%" if earnings_growth is not None else None,
        )

    st.divider()

    # ── EPS Beat/Miss Chart ────────────────────────────────────────────────────
    if earnings_hist is not None and not earnings_hist.empty and "epsActual" in earnings_hist.columns:
        st.markdown("### EPS: Actual vs. Estimate (Last 4 Quarters)")
        df_eps = earnings_hist.head(4).copy()
        df_eps = df_eps.sort_index()

        # Label quarters
        df_eps["quarter"] = df_eps.index.strftime("Q%q %Y") if hasattr(df_eps.index, "strftime") else df_eps.index.astype(str)

        fig_eps = go.Figure()
        fig_eps.add_trace(go.Bar(
            x=df_eps["quarter"],
            y=df_eps.get("epsEstimate", []),
            name="Estimate",
            marker_color="#93c5fd",
        ))
        fig_eps.add_trace(go.Bar(
            x=df_eps["quarter"],
            y=df_eps.get("epsActual", []),
            name="Actual",
            marker_color="#22c55e",
        ))
        fig_eps.update_layout(
            barmode="group",
            height=300,
            margin=dict(t=20, b=20),
            legend=dict(orientation="h", y=1.1),
        )
        st.plotly_chart(fig_eps, use_container_width=True)

    # ── Revenue & Income Trend ─────────────────────────────────────────────────
    if income_q is not None and not income_q.empty:
        st.markdown("### Quarterly Revenue & Net Income Trend")

        rev_key = next((k for k in income_q.index if "Total Revenue" in k or "Revenue" in k), None)
        ni_key = next((k for k in income_q.index if "Net Income" in k), None)

        if rev_key or ni_key:
            quarters = income_q.columns[:8]  # last 8 quarters
            fig_inc = make_subplots(specs=[[{"secondary_y": True}]])

            if rev_key:
                rev_vals = income_q.loc[rev_key, quarters]
                fig_inc.add_trace(
                    go.Bar(x=quarters.strftime("%b %Y"), y=rev_vals.values, name="Revenue", marker_color="#6366f1"),
                    secondary_y=False,
                )

            if ni_key:
                ni_vals = income_q.loc[ni_key, quarters]
                fig_inc.add_trace(
                    go.Scatter(x=quarters.strftime("%b %Y"), y=ni_vals.values, name="Net Income",
                               mode="lines+markers", line=dict(color="#f59e0b", width=2)),
                    secondary_y=True,
                )

            fig_inc.update_yaxes(title_text="Revenue", secondary_y=False)
            fig_inc.update_yaxes(title_text="Net Income", secondary_y=True)
            fig_inc.update_layout(height=350, margin=dict(t=20, b=20), legend=dict(orientation="h", y=1.1))
            st.plotly_chart(fig_inc, use_container_width=True)

    # ── Margin Trend ──────────────────────────────────────────────────────────
    if income_q is not None and not income_q.empty:
        rev_key = next((k for k in income_q.index if "Total Revenue" in k or "Revenue" in k), None)
        gp_key = next((k for k in income_q.index if "Gross Profit" in k), None)
        ni_key = next((k for k in income_q.index if "Net Income" in k), None)

        if rev_key and (gp_key or ni_key):
            st.markdown("### Margin Trends")
            quarters = income_q.columns[:8]
            rev_vals = income_q.loc[rev_key, quarters]

            fig_marg = go.Figure()
            if gp_key:
                gp_vals = income_q.loc[gp_key, quarters]
                gross_margins = (gp_vals / rev_vals * 100).round(1)
                fig_marg.add_trace(go.Scatter(
                    x=quarters.strftime("%b %Y"), y=gross_margins.values,
                    name="Gross Margin %", mode="lines+markers", line=dict(color="#6366f1"),
                ))
            if ni_key:
                ni_vals = income_q.loc[ni_key, quarters]
                net_margins = (ni_vals / rev_vals * 100).round(1)
                fig_marg.add_trace(go.Scatter(
                    x=quarters.strftime("%b %Y"), y=net_margins.values,
                    name="Net Margin %", mode="lines+markers", line=dict(color="#22c55e"),
                ))

            fig_marg.update_layout(
                yaxis_title="Margin %",
                height=300,
                margin=dict(t=20, b=20),
                legend=dict(orientation="h", y=1.1),
            )
            st.plotly_chart(fig_marg, use_container_width=True)

    # ── Balance Sheet Snapshot ─────────────────────────────────────────────────
    if balance_q is not None and not balance_q.empty:
        st.divider()
        st.markdown("### Balance Sheet Snapshot (Latest Quarter)")

        cash_key = next((k for k in balance_q.index if "Cash" in k and "Equivalent" in k), None)
        debt_key = next((k for k in balance_q.index if "Total Debt" in k or "Long Term Debt" in k), None)
        equity_key = next((k for k in balance_q.index if "Stockholders" in k or "Total Equity" in k), None)

        snap = {}
        if cash_key:
            snap["Cash & Equivalents"] = balance_q.loc[cash_key].iloc[0]
        if debt_key:
            snap["Total Debt"] = balance_q.loc[debt_key].iloc[0]
        if equity_key:
            snap["Shareholders' Equity"] = balance_q.loc[equity_key].iloc[0]

        if snap:
            bs_cols = st.columns(len(snap))
            for i, (label, val) in enumerate(snap.items()):
                bs_cols[i].metric(label, fmt_large(val))

    # ── Raw Data (Collapsible) ─────────────────────────────────────────────────
    with st.expander("Raw Quarterly Financials"):
        tab1, tab2, tab3 = st.tabs(["Income Statement", "Balance Sheet", "Cash Flow"])
        with tab1:
            if income_q is not None and not income_q.empty:
                st.dataframe(income_q.iloc[:, :4].applymap(
                    lambda x: fmt_large(x) if pd.notna(x) else "N/A"
                ))
        with tab2:
            if balance_q is not None and not balance_q.empty:
                st.dataframe(balance_q.iloc[:, :4].applymap(
                    lambda x: fmt_large(x) if pd.notna(x) else "N/A"
                ))
        with tab3:
            if cashflow_q is not None and not cashflow_q.empty:
                st.dataframe(cashflow_q.iloc[:, :4].applymap(
                    lambda x: fmt_large(x) if pd.notna(x) else "N/A"
                ))

elif analyze_btn and not ticker_input:
    st.warning("Please enter a ticker symbol.")
