# ui_desktop/tab3_sniper.py
# Titan SOP V100.0 — Tab 3: 單兵狙擊
# [靈魂注入 V82.0 → V100.0]
# 完整移植：
#   3.1 萬用個股狙擊雷達
#     t1 量子路徑預演 (G-Score + 波動率機率錐 + 五維劇本)
#     t2 亞當理論二次反射
#     t3 日K線 (黃金/死亡交叉標記)
#     t4 月K線 (43/87/284MA)
#     t5 ARK 戰情室 (三情境 DCF)
#     t6 智能估值引擎
#     t7 艾略特5波模擬

import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import yfinance as yf

# ── V82 引擎導入 ──────────────────────────────────────────────────────────────
from macro_risk import MacroRiskEngine

@st.cache_resource
def _load_macro():
    return MacroRiskEngine()

# ═══════════════════════════════════════════════════════════════
# 輔助函式 (全部從 V82 宏觀大盤之前的所有代碼.py 移植)
# ═══════════════════════════════════════════════════════════════
def safe_clamp(val, min_v, max_v):
    if val is None or pd.isna(val): return min_v
    return max(min_v, min(max_v, float(val)))

def get_advanced_granville(cp, op, ma87_curr, ma87_prev5):
    slope = ma87_curr - ma87_prev5
    bias  = ((cp - ma87_curr) / ma87_curr) * 100 if ma87_curr > 0 else 0
    is_rising  = slope > 0.3
    is_falling = slope < -0.3
    if bias > 25:  return "🔴 正乖離過大", "乖離 > 25%，過熱"
    if bias < -25: return "🟢 負乖離過大", "乖離 < -25%，超跌"
    if cp > ma87_curr and op < ma87_curr and not is_falling: return "🚀 G1 突破買點", "突破生命線且均線未下彎"
    if cp < ma87_curr and is_rising:                          return "🛡️ G2 假跌破(買)", "跌破上揚均線"
    if cp > ma87_curr and bias < 3 and is_rising:             return "🧱 G3 回測支撐", "回測生命線有守"
    if cp > ma87_curr and op < ma87_curr and not is_rising:   return "💀 G4 跌破賣點", "跌破生命線且均線未上揚"
    if cp > ma87_curr and is_falling:                         return "🎣 G5 假突破(賣)", "突破下彎均線"
    if cp < ma87_curr and bias > -3 and is_falling:           return "🚧 G6 反彈遇壓", "反彈生命線不過"
    return "盤整 (無訊號)", "均線走平，區間震盪"

def calculate_zigzag(df, deviation=0.03):
    df = df.reset_index()
    date_col = next((c for c in df.columns if str(c).lower() in ['date','index']), None)
    if date_col: df.rename(columns={date_col: 'Date'}, inplace=True)
    if 'Close' not in df.columns or 'Date' not in df.columns: return pd.DataFrame()
    closes = df['Close'].values; dates = df['Date'].values
    if len(closes) == 0: return pd.DataFrame()
    pivots = [{'idx':0,'Price':closes[0],'Type':'Start','Date':dates[0]}]
    trend = 0; last_p = closes[0]; last_i = 0
    for i in range(1, len(closes)):
        diff = (closes[i] - last_p) / last_p
        if trend == 0:
            if diff > deviation: trend=1; last_p=closes[i]; last_i=i
            elif diff < -deviation: trend=-1; last_p=closes[i]; last_i=i
        elif trend == 1:
            if closes[i] > last_p: last_p=closes[i]; last_i=i
            elif diff < -deviation:
                pivots.append({'idx':last_i,'Price':last_p,'Type':'High','Date':dates[last_i]})
                trend=-1; last_p=closes[i]; last_i=i
        elif trend == -1:
            if closes[i] < last_p: last_p=closes[i]; last_i=i
            elif diff > deviation:
                pivots.append({'idx':last_i,'Price':last_p,'Type':'Low','Date':dates[last_i]})
                trend=1; last_p=closes[i]; last_i=i
    pivots.append({'idx':len(closes)-1,'Price':closes[-1],'Type':'Current','Date':dates[-1]})
    return pd.DataFrame(pivots)

def calculate_5_waves(zigzag_df):
    if len(zigzag_df) < 2: return pd.DataFrame()
    last = zigzag_df.iloc[-1]; prev = zigzag_df.iloc[-2]
    direction = 1 if last['Price'] > prev['Price'] else -1
    wave_len = abs(last['Price'] - prev['Price'])
    sp = last['Price']; sd = last['Date']
    pts = []
    if direction == 1:
        p1 = sp - wave_len * 0.382; d1 = sd + pd.Timedelta(days=10); pts.append({'Date':d1,'Price':p1,'Label':'W2(回)'})
        p2 = p1 + wave_len * 1.618; d2 = d1 + pd.Timedelta(days=20); pts.append({'Date':d2,'Price':p2,'Label':'W3(推)'})
        p3 = p2 - (p2-p1)*0.382; d3 = d2 + pd.Timedelta(days=15); pts.append({'Date':d3,'Price':p3,'Label':'W4(回)'})
        p4 = p3 + wave_len; d4 = d3 + pd.Timedelta(days=15); pts.append({'Date':d4,'Price':p4,'Label':'W5(末)'})
    else:
        p1 = sp + wave_len*0.5; d1 = sd + pd.Timedelta(days=10); pts.append({'Date':d1,'Price':p1,'Label':'B波(彈)'})
        p2 = p1 - wave_len; d2 = d1 + pd.Timedelta(days=20); pts.append({'Date':d2,'Price':p2,'Label':'C波(殺)'})
    sim = pd.DataFrame(pts)
    origin = pd.DataFrame([{'Date':sd,'Price':sp,'Label':'Origin'}])
    return pd.concat([origin, sim], ignore_index=True)

def calculate_ark_scenarios(rev_ttm, shares, cp, g, m, pe, years=5):
    if not rev_ttm or not shares or shares == 0: return None
    cases = {'Bear':{'g_m':0.8,'pe_m':0.8,'m_adj':-0.05},'Base':{'g_m':1.0,'pe_m':1.0,'m_adj':0.0},'Bull':{'g_m':1.2,'pe_m':1.2,'m_adj':0.05}}
    scenarios = {}
    for c, mults in cases.items():
        tg = g*mults['g_m']; tpe = pe*mults['pe_m']; tm = max(0.01, m+mults['m_adj'])
        target = (rev_ttm * ((1+tg)**years) * tm * tpe) / shares
        cagr = (target/cp)**(1/years)-1 if cp > 0 else 0
        scenarios[c] = {'Target': target, 'CAGR': cagr}
    return scenarios

def calculate_smart_valuation(eps, rev, shares, g, m, pe, dr=0.1, y=10):
    if not rev or shares == 0: return 0
    fut_mc = rev * ((1+g)**y) * m * pe
    return (fut_mc / ((1+dr)**y)) / shares


# ═══════════════════════════════════════════════════════════════
#  主渲染入口
# ═══════════════════════════════════════════════════════════════
def render():
    """Tab 3: 單兵狙擊 — 全功能復原版 (V82 靈魂 + V100 外殼)"""
    macro = _load_macro()

    with st.expander("3.1 🎯 萬用個股狙擊雷達 (Universal Sniper)", expanded=True):
        st.info("🌍 全球戰情模式：支援台股 (2330)、美股 (TSLA, PLTR)、加密貨幣 BTC-USD。已啟動雙軌扣抵預演系統。")

        w17_in = st.text_input("輸入代號或股名", value="2330", key="w17_v100").strip()

        if not w17_in:
            st.info("請輸入標的代號")
            return

        # 名稱 → 代號 轉換
        try:
            from macro_risk import STOCK_METADATA
            N2T = {v['name'].strip(): k for k, v in STOCK_METADATA.items()}
            if w17_in in N2T: w17_in = N2T[w17_in]
        except Exception:
            pass

        # 雙軌候選
        cands = [w17_in]
        if w17_in.isdigit(): cands = [f"{w17_in}.TW", f"{w17_in}.TWO"]
        elif not w17_in.endswith((".TW", ".TWO")): cands = [w17_in.upper(), f"{w17_in.upper()}.TW"]

        sdf = pd.DataFrame(); v_ticker = None
        with st.spinner("掃描全球資料庫…"):
            for c in cands:
                temp = macro.get_single_stock_data(c, period="max")
                if not temp.empty and len(temp) >= 300:
                    sdf = temp; v_ticker = c; break

        if sdf.empty:
            st.error("❌ 查無數據，或歷史數據不足 300 天無法計算年線扣抵。")
            return

        # ── 資料清洗 ─────────────────────────────────────────────
        try:
            if isinstance(sdf.columns, pd.MultiIndex):
                sdf.columns = sdf.columns.get_level_values(0)
            sdf.columns = [str(c).strip().capitalize() for c in sdf.columns]
            sdf = sdf.reset_index()
            date_col = next((c for c in sdf.columns if str(c).lower() in ['date','datetime','index']), None)
            if date_col:
                sdf.rename(columns={date_col: 'Date'}, inplace=True)
                sdf['Date'] = pd.to_datetime(sdf['Date'])
                sdf.set_index('Date', inplace=True)
                sdf.sort_index(inplace=True)
            col_map = {}
            for c in sdf.columns:
                if c.lower() in ['close','price']: col_map[c] = 'Close'
                elif c.lower() in ['volume','vol']: col_map[c] = 'Volume'
            sdf.rename(columns=col_map, inplace=True)
            for req in ['Open','High','Low']:
                if req not in sdf.columns: sdf[req] = sdf['Close']
            if 'Volume' not in sdf.columns: sdf['Volume'] = 0
            for c in ['Close','Open','High','Low','Volume']:
                sdf[c] = pd.to_numeric(sdf[c], errors='coerce')
            sdf = sdf.dropna()
        except Exception as e:
            st.error(f"資料格式錯誤: {e}"); return

        # ── 指標計算 ──────────────────────────────────────────────
        sdf['MA87']  = sdf['Close'].rolling(87).mean()
        sdf['MA284'] = sdf['Close'].rolling(284).mean()
        sdf['Prev_MA87']  = sdf['MA87'].shift(1)
        sdf['Prev_MA284'] = sdf['MA284'].shift(1)
        sdf['Cross_Signal'] = 0
        sdf.loc[(sdf['Prev_MA87'] <= sdf['Prev_MA284']) & (sdf['MA87'] > sdf['MA284']), 'Cross_Signal'] =  1
        sdf.loc[(sdf['Prev_MA87'] >= sdf['Prev_MA284']) & (sdf['MA87'] < sdf['MA284']), 'Cross_Signal'] = -1

        cp    = float(sdf['Close'].iloc[-1])
        op    = float(sdf['Open'].iloc[-1])
        m87   = float(sdf['MA87'].iloc[-1])  if not pd.isna(sdf['MA87'].iloc[-1])  else 0
        m87p5 = float(sdf['MA87'].iloc[-6])  if len(sdf) > 6 and not pd.isna(sdf['MA87'].iloc[-6]) else m87
        m284  = float(sdf['MA284'].iloc[-1]) if not pd.isna(sdf['MA284'].iloc[-1]) else 0

        # 趨勢天數
        trend_days = 0; trend_str = "整理中"
        if m87 > 0 and m284 > 0:
            is_bull = m87 > m284
            trend_str = "🔥 中期多頭 (87>284)" if is_bull else "❄️ 中期空頭 (87<284)"
            bull_s = sdf['MA87'] > sdf['MA284']
            cs = bull_s.iloc[-1]
            for i in range(len(bull_s)-1, -1, -1):
                if bull_s.iloc[i] == cs: trend_days += 1
                else: break

        g_title, g_desc = get_advanced_granville(cp, op, m87, m87p5)
        bias = ((cp - m87) / m87) * 100 if m87 > 0 else 0

        # ── 頭部指標 ─────────────────────────────────────────────
        st.subheader(f"🎯 {v_ticker} 戰情報告")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("目前股價",    f"{cp:.2f}")
        c2.metric("87MA (季線)", f"{m87:.2f}",  f"{cp-m87:.2f}")
        c3.metric("284MA (年線)",f"{m284:.2f}", f"{cp-m284:.2f}")
        c4.metric("乖離率 (Bias)",f"{bias:.1f}%")
        st.markdown(f"**趨勢狀態**: {trend_str} | 持續 **{trend_days}** 天 | 格蘭碧: **{g_title}** — {g_desc}")
        st.markdown("---")

        # ── 7 子分頁 ─────────────────────────────────────────────
        t1, t2, t3, t4, t5, t6, t7 = st.tabs([
            "🔮 量子路徑預演", "📐 亞當理論",
            "🕯️ 日K (含交叉)", "🗓️ 月K線",
            "🧠 ARK 戰情室", "💎 智能估值", "🌊 5波模擬"
        ])

        # ─── T1: 量子路徑預演 ────────────────────────────────────
        with t1:
            st.markdown("#### 🔮 殿堂級全息戰略預演 (Holographic Strategy)")
            hist_vol = sdf['Close'].pct_change().std() * 100
            cur_vol  = max(1.5, hist_vol)
            with st.expander("⚙️ 戰略參數設定", expanded=False):
                sc1, sc2 = st.columns(2)
                sim_days = sc1.slider("預演天數", 10, 60, 20)
                momentum = sc2.number_input("假設動能 (%)", -10.0, 10.0, 0.0, step=0.5)
                sc2.caption(f"目前波動率: {cur_vol:.1f}%")

            last_date  = sdf.index[-1]
            fut_dates  = [last_date + pd.Timedelta(days=i+1) for i in range(sim_days)]
            slope_10   = (sdf['Close'].iloc[-1] - sdf['Close'].iloc[-10]) / 10
            path_iner  = [cp + slope_10*(i+1) for i in range(sim_days)]
            path_bull  = [cp * (1 + (cur_vol/100) * np.sqrt(i+1)) for i in range(sim_days)]
            path_bear  = [cp * (1 - (cur_vol/100) * np.sqrt(i+1)) for i in range(sim_days)]

            sim_prices = []; curr_s = cp
            for _ in range(sim_days):
                curr_s *= (1 + momentum/100); sim_prices.append(curr_s)

            fut_series  = pd.Series(sim_prices, index=fut_dates)
            combined    = pd.concat([sdf['Close'], fut_series])
            comb_ma87   = combined.rolling(87).mean()
            comb_ma284  = combined.rolling(284).mean()
            si = len(sdf); ac = combined.values
            d87  = [float(ac[si+i-87])  if (si+i-87)  >= 0 else np.nan for i in range(sim_days)]
            d284 = [float(ac[si+i-284]) if (si+i-284) >= 0 else np.nan for i in range(sim_days)]

            f_df = pd.DataFrame({
                'Date':      fut_dates,
                'Sim_Price': sim_prices,
                'Bull_Bound':path_bull,
                'Bear_Bound':path_bear,
                'MA87':      comb_ma87.loc[fut_dates].values,
                'MA284':     comb_ma284.loc[fut_dates].values,
                'Deduct_87': d87,
                'Deduct_284':d284
            })

            # G-Score
            score = 0
            ma87c = comb_ma87.iloc[-sim_days-1]; ma284c = comb_ma284.iloc[-sim_days-1]
            if cp > ma87c:  score += 15
            if cp > ma284c: score += 15
            if cp > sdf['Close'].iloc[-20:].mean(): score += 20
            bd = abs(ma87c - ma284c) / ma284c if ma284c > 0 else 0
            is_sq = bd < 0.015
            if ma87c > ma284c: score += 30
            if np.nanmean(d87[:20]) < cp: score += 20

            if score >= 80: g_stat = "🔥 多頭坦途 (Clear Sky)"
            elif score >= 50: g_stat = "⚠️ 區間震盪 (Range Bound)"
            else: g_stat = "🐻 空頭承壓 (Bearish Pressure)"

            if is_sq:
                sq_msg = f"🌪️ **螺旋絞殺 (Squeeze)**：87/284MA 乖離僅 **{bd*100:.2f}%**。兩線打結，預計 **3-5天** 出現大變盤。"
            elif ma87c > ma284c:
                sq_msg = "🚀 **發散攻擊**：均線呈多頭排列，開口擴大，趨勢明確。"
            else:
                sq_msg = "📉 **空頭壓制**：均線呈空頭排列，上方層層賣壓。"

            fib_high  = max(path_bull); fib_low = min(path_bear)
            fib_0618  = fib_low + (fib_high - fib_low) * 0.618
            var_date  = (last_date + pd.Timedelta(days=13)).strftime('%m/%d')
            d87_first = d87[0] if d87 and not np.isnan(d87[0]) else 0

            st.markdown(f"""
<div style="background:#1E1E1E;padding:16px;border-radius:10px;border:1px solid #444;">
<h3 style="color:#FFA500;margin:0;">📊 G-Score 量化總評：{score} 分</h3>
<p style="color:#ddd;margin-top:5px;">狀態：<b>{g_stat}</b> | 指令：<b>{'積極操作' if score>70 else '觀望/區間' if score>40 else '保守防禦'}</b></p>
<hr style="border-top:1px solid #555;">
<h4 style="color:#4db8ff;margin:0;">⚔️ 雙線糾纏場 (Interaction)</h4>
<p style="color:#ccc;font-size:14px;margin-top:5px;">{sq_msg}</p>
<p style="color:#ccc;font-size:14px;">
  • <b>87MA (季)</b>：{ma87c:.1f} | 扣抵：{d87_first:.1f} ({'扣低助漲' if d87_first < cp else '扣高壓力'})<br>
  • <b>284MA (年)</b>：{ma284c:.1f} | 扣抵：{d284[0]:.1f if d284 and not np.isnan(d284[0]) else 'N/A'}
</p>
<hr style="border-top:1px solid #555;">
<h4 style="color:#98FB98;margin:0;">🔮 五維全息劇本 (Scenarios)</h4>
<p style="color:#ccc;font-size:14px;margin-top:5px;">關鍵變盤窗：<b>{var_date} (費氏轉折)</b></p>
<ul style="color:#ccc;font-size:14px;padding-left:20px;">
  <li><b>劇本 A (慣性 50%)</b>：在 <b>{fib_low:.1f} ~ {fib_high:.1f}</b> 區間震盪，以盤代跌。</li>
  <li><b>劇本 B (破底翻 30%)</b>：回測 <b>{fib_0618:.1f}</b> (Fib 0.618) 不破，V型反轉。</li>
  <li><b>劇本 C (風險 20%)</b>：若跌破 <b>{min(d87[:5]):.1f if d87 else 0}</b>，確認均線蓋頭向下。</li>
</ul>
</div>""", unsafe_allow_html=True)
            st.write("")

            base_f  = alt.Chart(f_df).encode(x='Date:T')
            cone    = base_f.mark_area(opacity=0.15, color='gray').encode(y='Bear_Bound:Q', y2='Bull_Bound:Q')
            l_sim   = base_f.mark_line(color='white', strokeDash=[4,2]).encode(y='Sim_Price')
            l_87    = base_f.mark_line(color='orange', strokeWidth=2).encode(y='MA87')
            l_284   = base_f.mark_line(color='#00bfff', strokeWidth=2).encode(y='MA284')
            g_87    = base_f.mark_line(color='red',    strokeDash=[1,1], opacity=0.5).encode(y='Deduct_87')
            g_284   = base_f.mark_line(color='blue',   strokeDash=[1,1], opacity=0.3).encode(y='Deduct_284')
            hist_d  = sdf.iloc[-60:].reset_index()
            bh      = alt.Chart(hist_d).encode(x='Date:T')
            candles = (bh.mark_rule().encode(y='Low', y2='High') +
                       bh.mark_bar().encode(y='Open', y2='Close',
                           color=alt.condition("datum.Open<=datum.Close", alt.value("#FF4B4B"), alt.value("#26A69A"))))
            final_c = (cone + candles + l_sim + l_87 + l_284 + g_87 + g_284).properties(
                height=500, title="量子路徑預演 (含波動率機率錐)")
            st.altair_chart(final_c.interactive(), use_container_width=True)

        # ─── T2: 亞當理論 ────────────────────────────────────────
        with t2:
            st.markdown("#### 📐 亞當理論二次反射路徑")
            try:
                adf = macro.calculate_adam_projection(sdf, 20)
                if not adf.empty:
                    h = sdf.iloc[-60:].reset_index(); h['T'] = 'History'
                    p = adf.reset_index(); p['T'] = 'Project'
                    p.rename(columns={'Projected_Price':'Close'}, inplace=True)
                    combined_df = pd.concat([h[['Date','Close','T']], p[['Date','Close','T']]])
                    chart = (alt.Chart(combined_df).mark_line()
                             .encode(x='Date:T',
                                     y=alt.Y('Close', scale=alt.Scale(zero=False)),
                                     color='T:N', strokeDash='T:N')
                             .properties(title="亞當理論二次反射路徑圖")
                             .interactive())
                    st.altair_chart(chart, use_container_width=True)
                else:
                    st.warning("資料不足，無法進行亞當理論投影。")
            except Exception as e:
                st.warning(f"亞當理論計算失敗: {e}")

        # ─── T3: 日K線 ───────────────────────────────────────────
        with t3:
            st.markdown("#### 🕯️ 日K線 (含黃金/死亡交叉)")
            kd = sdf.tail(252).reset_index()
            x_sc = alt.X('Date:T', axis=alt.Axis(format='%m/%d', title='Date'))
            bk   = alt.Chart(kd).encode(x=x_sc)
            col_c = alt.condition("datum.Open<=datum.Close", alt.value("#FF4B4B"), alt.value("#26A69A"))
            candle = (bk.mark_rule().encode(y=alt.Y('Low', scale=alt.Scale(zero=False)), y2='High', color=col_c) +
                      bk.mark_bar().encode(y='Open', y2='Close', color=col_c))
            l87_d  = bk.mark_line(color='blue',   strokeWidth=2).encode(y='MA87',  tooltip=['MA87'])
            l284_d = bk.mark_line(color='purple',  strokeWidth=2).encode(y='MA284', tooltip=['MA284'])
            chart_p = candle + l87_d + l284_d
            cross_d = kd[kd['Cross_Signal'] != 0]
            if not cross_d.empty:
                cross_pts = (alt.Chart(cross_d).mark_point(size=150, filled=True, opacity=1)
                             .encode(x='Date:T', y='Close',
                                     shape=alt.condition("datum.Cross_Signal > 0", alt.value("triangle-up"), alt.value("triangle-down")),
                                     color=alt.condition("datum.Cross_Signal > 0", alt.value("gold"), alt.value("black")),
                                     tooltip=['Date','Close','Cross_Signal']))
                chart_p += cross_pts
            chart_p = chart_p.properties(height=350, title=f"{v_ticker} 日K線圖")
            chart_vol = bk.mark_bar().encode(y='Volume', color=col_c).properties(height=100)
            st.altair_chart(alt.vconcat(chart_p, chart_vol).resolve_scale(x='shared').interactive(), use_container_width=True)
            st.caption("指標：🔵 87MA | 🟣 284MA | ▲ 黃金交叉(金) | ▼ 死亡交叉(黑)")

        # ─── T4: 月K線 ───────────────────────────────────────────
        with t4:
            st.markdown("#### 🗓️ 月K線 (43/87/284MA)")
            try:
                freq = 'ME'
                try: sdf.resample('ME').last()
                except Exception: freq = 'M'
                md = sdf.resample(freq).agg({'Open':'first','High':'max','Low':'min','Close':'last'}).dropna()
                if len(md) >= 43:
                    md['MA43']  = md['Close'].rolling(43).mean()
                    md['MA87']  = md['Close'].rolling(87).mean()
                    md['MA284'] = md['Close'].rolling(284).mean()
                    pm = md.tail(120).reset_index()
                    bm = alt.Chart(pm).encode(x=alt.X('Date:T', axis=alt.Axis(format='%Y-%m')))
                    col_m = alt.condition("datum.Open<=datum.Close", alt.value("#FF4B4B"), alt.value("#26A69A"))
                    mc   = (bm.mark_rule().encode(y='Low', y2='High', color=col_m) +
                            bm.mark_bar().encode(y='Open', y2='Close', color=col_m))
                    ln43  = bm.mark_line(color='orange').encode(y='MA43')
                    ln87  = bm.mark_line(color='blue').encode(y='MA87')
                    ln284 = bm.mark_line(color='purple').encode(y='MA284')
                    st.altair_chart((mc + ln43 + ln87 + ln284).interactive(), use_container_width=True)
                    st.caption("月線指標：🟠 43MA | 🔵 87MA | 🟣 284MA")
                else:
                    st.warning("月線資料不足 (需要至少 43 個月)。")
            except Exception as e:
                st.error(f"月線失敗: {e}")

        # ── 財務數據 (供 t5/t6 使用) ─────────────────────────────
        try:
            info         = yf.Ticker(v_ticker).info
            rev_ttm      = info.get('totalRevenue', 0)
            shares_out   = info.get('sharesOutstanding', 0)
            eps_ttm      = info.get('trailingEps', 0)
            ag           = info.get('revenueGrowth', info.get('earningsGrowth', 0.15)) or 0.15
            is_us        = not v_ticker.endswith(('.TW','.TWO'))
            region_tag   = "🇺🇸 美股" if is_us else "🇹🇼 台股"
            region_hint  = "美股通常享有較高估值溢價" if is_us else "台股估值相對保守"
        except Exception:
            rev_ttm=0; shares_out=0; eps_ttm=0; ag=0.15; is_us=False; region_tag="未知"; region_hint=""

        # ─── T5: ARK 戰情室 ──────────────────────────────────────
        with t5:
            st.markdown(f"### 🧠 ARK 戰情室 ({region_tag})")
            st.info(f"💡 基於期望值的三情境推演。{region_hint}")
            if rev_ttm > 0 and shares_out > 0:
                a1, a2, a3 = st.columns(3)
                safe_g  = safe_clamp(ag, -10.0, 50.0)
                base_g  = a1.number_input("基本成長率",  -10.0, 50.0,  safe_g, 0.01)
                base_m  = a2.number_input("基本淨利率",   -5.0,  5.0,    0.20, 0.01)
                base_pe = a3.number_input("基本 PE",       0.0, 9999.0, 30.0 if is_us else 20.0, 1.0)
                sc = calculate_ark_scenarios(rev_ttm, shares_out, cp, base_g, base_m, base_pe)
                if sc:
                    st.divider()
                    k1, k2, k3 = st.columns(3)
                    k1.error(f"🐻 **熊市**\n\n${sc['Bear']['Target']:.1f}\n\nCAGR: {sc['Bear']['CAGR']:.1%}")
                    k2.info(f"⚖️ **基本**\n\n${sc['Base']['Target']:.1f}\n\nCAGR: {sc['Base']['CAGR']:.1%}")
                    k3.success(f"🐮 **牛市**\n\n${sc['Bull']['Target']:.1f}\n\nCAGR: {sc['Bull']['CAGR']:.1%}")
            else:
                st.warning("財務數據不足，無法進行 ARK 推演。")

        # ─── T6: 智能估值 ────────────────────────────────────────
        with t6:
            st.markdown(f"### 💎 智能估值引擎 ({region_tag})")
            if rev_ttm > 0:
                ind_sel = st.selectbox("產業模板", ["🚀 軟體/SaaS","💊 生技","⚙️ 硬體","🏭 傳統"])
                if "軟體" in ind_sel:  def_m=0.25; def_pe=50.0
                elif "生技" in ind_sel: def_m=0.30; def_pe=40.0
                elif "硬體" in ind_sel: def_m=0.15; def_pe=25.0
                else:                   def_m=0.08; def_pe=15.0
                if is_us: def_pe *= 1.2
                s1, s2, s3 = st.columns(3)
                safe_gs = safe_clamp(ag, -10.0, 50.0)
                u_g  = s1.number_input("成長率",  -10.0, None, safe_gs, 0.01)
                u_m  = s2.number_input("淨利率",   -5.0, None, float(def_m), 0.01)
                u_pe = s3.number_input("終端 PE",   0.0, None, float(def_pe), 1.0)
                fair = calculate_smart_valuation(eps_ttm, rev_ttm, shares_out, u_g, u_m, u_pe)
                st.divider()
                v1, v2 = st.columns(2)
                v1.metric("目前股價",  f"{cp:.2f}")
                v2.metric("合理估值", f"{fair:.2f}", f"{cp-fair:.2f}", delta_color="inverse")
            else:
                st.warning("財務數據不足，無法進行估值。")

        # ─── T7: 艾略特 5 波 ─────────────────────────────────────
        with t7:
            st.markdown("### 🌊 艾略特 5 波模擬 (Elliott Wave Sim)")
            st.info("💡 虛線為 AI 模擬路徑。")
            zz = calculate_zigzag(sdf.tail(300), 0.03)
            if not zz.empty:
                bz = alt.Chart(zz).encode(x='Date:T')
                real_l = bz.mark_line(point=True, color='black').encode(
                    y=alt.Y('Price', scale=alt.Scale(zero=False)), tooltip=['Date','Price','Type'])
                text_p = bz.mark_text(dy=-15, color='blue', fontSize=14, fontWeight='bold').encode(
                    y='Price', text=alt.Text('Price', format='.1f'))
                chart_w = real_l + text_p
                sim = calculate_5_waves(zz)
                if not sim.empty:
                    sl = alt.Chart(sim).mark_line(strokeDash=[5,5], color='red').encode(
                        x='Date:T', y='Price', tooltip=['Date','Price','Label'])
                    sp_pts = alt.Chart(sim[sim['Label']!='Origin']).mark_circle(color='red', size=60).encode(x='Date:T', y='Price')
                    sl_lbl = alt.Chart(sim[sim['Label']!='Origin']).mark_text(dy=-30, color='blue', fontSize=14, fontWeight='bold').encode(
                        x='Date:T', y='Price', text='Label')
                    sl_val = alt.Chart(sim[sim['Label']!='Origin']).mark_text(dy=30, color='blue', fontSize=14, fontWeight='bold').encode(
                        x='Date:T', y='Price', text=alt.Text('Price', format='.1f'))
                    chart_w = chart_w + sl + sp_pts + sl_lbl + sl_val
                st.altair_chart(chart_w.interactive(), use_container_width=True)
            else:
                st.warning("波動過小，無法計算 ZigZag。")
