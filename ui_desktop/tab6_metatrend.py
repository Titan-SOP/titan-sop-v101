# ui_desktop/tab6_metatrend.py
# Titan SOP V300 — Tab 6: 元趨勢戰法 (GLOBAL MARKET HOLOGRAM)
# ╔═══════════════════════════════════════════════════════════════════╗
# ║  V300 DEFINITIVE — Full Audit Against Original V90.3 Source      ║
# ║  RESTORED (11 critical fixes from V200 audit):                   ║
# ║    ✅ #1  TitanIntelAgency class (PEG/OpMargin/52W/FCF/News)    ║
# ║    ✅ #2  TitanAgentCouncil class (800-word Ragnarök prompt)     ║
# ║    ✅ #3  run_debate() AI execution with Gemini                  ║
# ║    ✅ #4  God Orbit (上帝軌道) log-linear regression chart       ║
# ║    ✅ #5  9 Smart Links (TradingView/Finviz/鉅亨網/Goodinfo)    ║
# ║    ✅ #6  20 First Principles (not 10)                           ║
# ║    ✅ #7  File upload capability                                  ║
# ║    ✅ #8  Kill List st.form + drop_duplicates                    ║
# ║    ✅ #9  Anti-Laziness Protocol (800+ word minimum)             ║
# ║    ✅ #10 Output format template (structured 5-gladiator)        ║
# ║    ✅ #11 Valkyrie report with PEG/OpMargin/52W fields           ║
# ║  ENHANCED (beyond original):                                      ║
# ║    ✅ Cinematic Hero Billboard + Poster Rail                      ║
# ║    ✅ 120px Rank Badge + Spectrum Analyzer                        ║
# ║    ✅ Section 6.5 Macro Hedge (FULL — was placeholder)            ║
# ║    ✅ Section 6.6 Geo Backtest Sandbox (FULL — was placeholder)   ║
# ╚═══════════════════════════════════════════════════════════════════╝

import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
import altair as alt
from datetime import datetime, timedelta
from scipy.stats import linregress
import io
import time

# ══════════════════════════════════════════════════════════════
# 🎯 FEATURE 3: VALKYRIE AI TYPEWRITER (st.write_stream)
# ══════════════════════════════════════════════════════════════
def stream_generator(text):
    """
    Valkyrie AI Typewriter: Stream text word-by-word
    Creates the sensation of live AI transmission.
    """
    for word in text.split():
        yield word + " "
        time.sleep(0.02)

# ══════════════════════════════════════════════════════════════
# 🎯 FEATURE 1: TACTICAL GUIDE MODAL (st.dialog)
# ══════════════════════════════════════════════════════════════
@st.dialog("🔰 戰術指導 Mode")
def show_guide_modal():
    st.markdown("""
    ### 指揮官，歡迎進入本戰區
    
    **核心功能**：
    - **7 維度幾何掃描**：從 35 年到 3 個月，全時間尺度角度分析，識別長期趨勢與短期動能。
    - **22 階泰坦信評系統**：SSS/AAA/Phoenix 等智能評級，精準定位標的當前位置與潛力。
    - **AI 議會戰略工廠**：整合瓦爾基里情報 + 20 條第一性原則，生成 800+ 字深度分析提示詞。
    
    **操作方式**：點擊上方選單切換模式 (6.1 掃描 → 6.2 深鑽 → 6.3 獵殺清單 → 6.4 智能工具)。
    
    **狀態監控**：隨時留意畫面中的警示訊號 (乖離過大、Phoenix 信號、加速度異常)。
    
    ---
    **🧬 6.3 百倍股 10D DNA 升級版（Chris Mayer × Baillie Gifford 標準）**：
    - **D8 🩸 創辦人綁定**：內部人持股 `heldPercentInsiders` > 10% 大加分（Owner-Operator 效應）
    - **D9 📈 估值擴張**：P/E < 30 或 PEG < 1.5 加分（低估值 × 高成長 = 百倍股催化劑）
    - **D10 🛡️ SaaS Rule of 40**：營收成長率 + 營業利益率 > 40% 加分（排除「燒錢黑洞」）
    
    *建議：先執行 6.1 全局掃描，再針對目標標的進入 6.2 深度分析，且6.3有百倍股專區*
    """)
    
    if st.button("✅ Roger that, 收到", type="primary", use_container_width=True):
        st.session_state["guide_shown_" + __name__] = True
        st.rerun()

# ── 可選依賴 ──
try:
    import google.generativeai as genai
    _HAS_GENAI = True
except ImportError:
    _HAS_GENAI = False

try:
    from config import WAR_THEATERS
except ImportError:
    WAR_THEATERS = {
        "🇺🇸 美股科技": ["NVDA","TSLA","PLTR","META","GOOG","MSFT","AMZN","AAPL"],
        "🇹🇼 台股半導體": ["2330.TW","2303.TW","2454.TW","3711.TW","6531.TW"],
        "🌏 全球 ETF":    ["SPY","QQQ","SOXX","FXI","EWZ"],
    }


# ═══════════════════════════════════════════════════════════════
# [SLOT-6.1] 數據引擎 — VERBATIM from original
# ═══════════════════════════════════════════════════════════════
def get_time_slice(df, months):
    """精準切割最後 N 個月的數據片段"""
    if df is None or df.empty:
        return df
    if len(df) >= months:
        return df.iloc[-months:]
    return df


@st.cache_data(ttl=3600)
def download_full_history(ticker, start="1990-01-01"):
    """下載完整歷史月K線 [V86.2]: 支援台股上櫃 (.TWO)"""
    try:
        original_ticker = ticker
        if ticker.isdigit() and len(ticker) >= 4:
            ticker = f"{ticker}.TW"
        df = yf.download(ticker, start=start, progress=False, auto_adjust=True)
        # 上市沒數據 → 嘗試上櫃
        if df.empty and original_ticker.isdigit() and len(original_ticker) >= 4:
            ticker = f"{original_ticker}.TWO"
            df = yf.download(ticker, start=start, progress=False, auto_adjust=True)
        # yfinance 多層索引整平
        if isinstance(df.columns, pd.MultiIndex):
            try:
                df.columns = df.columns.get_level_values(0)
            except:
                pass
        if df.empty:
            return None
        if not isinstance(df.index, pd.DatetimeIndex):
            df.index = pd.to_datetime(df.index)
        # 儲存日K到 session_state
        if 'daily_price_data' not in st.session_state:
            st.session_state.daily_price_data = {}
        st.session_state.daily_price_data[original_ticker] = df
        # 轉月K
        df_monthly = df.resample('M').agg({
            'Open': 'first', 'High': 'max', 'Low': 'min',
            'Close': 'last', 'Volume': 'sum'
        }).dropna()
        return df_monthly
    except Exception:
        return None


# ═══════════════════════════════════════════════════════════════
# [SLOT-6.2] 數學引擎 — linregress (VERBATIM)
# ═══════════════════════════════════════════════════════════════
def calculate_geometry_metrics(df, months):
    """計算單一時間窗口的幾何指標"""
    if df is None or df.empty:
        return {'angle': 0, 'r2': 0, 'slope': 0}
    slice_df = get_time_slice(df, months)
    if len(slice_df) < 3:
        return {'angle': 0, 'r2': 0, 'slope': 0}
    log_prices = np.log(slice_df['Close'].values)
    x = np.arange(len(log_prices))
    slope, intercept, r_value, p_value, std_err = linregress(x, log_prices)
    angle = np.arctan(slope * 100) * (180 / np.pi)
    angle = np.clip(angle, -90, 90)
    r2 = r_value ** 2
    return {
        'angle': round(float(angle), 2),
        'r2': round(float(r2), 4),
        'slope': round(float(slope), 6)
    }


def compute_7d_geometry(ticker):
    """7 維度完整幾何掃描"""
    df = download_full_history(ticker)
    if df is None:
        return None
    periods = {'35Y': 420, '10Y': 120, '5Y': 60, '3Y': 36, '1Y': 12, '6M': 6, '3M': 3}
    results = {}
    for label, months in periods.items():
        results[label] = calculate_geometry_metrics(df, months)
    results['acceleration'] = round(results['3M']['angle'] - results['1Y']['angle'], 2)
    results['phoenix_signal'] = (results['10Y']['angle'] < 0) and (results['6M']['angle'] > 25)
    return results


# ═══════════════════════════════════════════════════════════════
# [SLOT-6.3] 22 階泰坦信評 (VERBATIM)
# ═══════════════════════════════════════════════════════════════
def titan_rating_system(geo):
    """22 階信評邏輯樹"""
    if geo is None:
        return ("N/A", "無數據", "數據不足", "#808080")
    a35 = geo['35Y']['angle']; a10 = geo['10Y']['angle']; a5 = geo['5Y']['angle']
    a1 = geo['1Y']['angle'];  a6 = geo['6M']['angle'];  a3 = geo['3M']['angle']
    r2_1 = geo['1Y']['r2'];   r2_3 = geo['3M']['r2']
    acc = geo['acceleration']; phx = geo['phoenix_signal']

    if all([a35 > 45, a10 > 45, a1 > 45, a3 > 45]):    return ("SSS", "Titan (泰坦)", "全週期超過45度，神級標的", "#FFD700")
    if a1 > 40 and a6 > 45 and a3 > 50 and acc > 20:    return ("AAA", "Dominator (統治者)", "短期加速向上，完美趨勢", "#FF4500")
    if phx and a3 > 30:                                  return ("Phoenix", "Phoenix (浴火重生)", "長空短多，逆轉信號", "#FF6347")
    if r2_1 > 0.95 and 20 < a1 < 40 and acc > 0:        return ("Launchpad", "Launchpad (發射台)", "線性度極高，蓄勢待發", "#32CD32")
    if a1 > 35 and a3 > 40 and r2_3 > 0.85:             return ("AA+", "Elite (精英)", "一年期強勢上攻", "#FFA500")
    if a1 > 30 and a6 > 35:                              return ("AA", "Strong Bull (強多)", "中短期穩定上升", "#FFD700")
    if a1 > 25 and a3 > 30:                              return ("AA-", "Steady Bull (穩健多)", "趨勢健康向上", "#ADFF2F")
    if a6 > 20 and a3 > 25:                              return ("A+", "Moderate Bull (溫和多)", "短期表現良好", "#7FFF00")
    if a3 > 15:                                          return ("A", "Weak Bull (弱多)", "短期微幅上揚", "#98FB98")
    if -5 < a3 < 15 and a1 > 0:                          return ("BBB+", "Neutral+ (中性偏多)", "盤整偏多", "#F0E68C")
    if -10 < a3 < 10 and -10 < a1 < 10:                  return ("BBB", "Neutral (中性)", "橫盤震蕩", "#D3D3D3")
    if -15 < a3 < 5 and a1 < 0:                          return ("BBB-", "Neutral- (中性偏空)", "盤整偏弱", "#DDA0DD")
    if a1 > 20 and a3 < -10:                              return ("Divergence", "Divergence (背離)", "價格創高但動能衰竭", "#FF1493")
    if -25 < a3 < -15 and a1 > -10:                       return ("BB+", "Weak Bear (弱空)", "短期下跌", "#FFA07A")
    if -35 < a3 < -25:                                    return ("BB", "Moderate Bear (中等空)", "下跌趨勢明確", "#FF6347")
    if -45 < a3 < -35:                                    return ("BB-", "Strong Bear (強空)", "跌勢凌厲", "#DC143C")
    if a3 < -45 and a1 < -30:                             return ("B+", "Severe Bear (重度空)", "崩跌模式", "#8B0000")
    if a10 < -30 and a3 < -40:                            return ("B", "Depression (蕭條)", "長期熊市", "#800000")
    if a35 < -20 and a10 < -35:                           return ("C", "Structural Decline (結構衰退)", "世代熊市", "#4B0082")
    if a3 < -60:                                          return ("D", "Collapse (崩盤)", "極度危險", "#000000")
    if a10 < -20 and a3 > 15 and acc > 30:                return ("Reversal", "Reversal (觸底反彈)", "熊市中的V型反轉", "#00CED1")
    return ("N/A", "Unknown (未分類)", "無法歸類", "#808080")


# ═══════════════════════════════════════════════════════════════
# [FIX #1 #11] TitanIntelAgency — 完整類別 (RESTORED)
# ═══════════════════════════════════════════════════════════════
class TitanIntelAgency:
    """[V90.2 PROJECT VALKYRIE] 自動情報抓取引擎"""
    def __init__(self):
        self.ticker_obj = None

    def fetch_full_report(self, ticker):
        try:
            original_ticker = ticker
            if ticker.isdigit() and len(ticker) >= 4:
                ticker = f"{ticker}.TW"
            self.ticker_obj = yf.Ticker(ticker)
            try:
                test_info = self.ticker_obj.info
                if not test_info or 'symbol' not in test_info:
                    if original_ticker.isdigit() and len(original_ticker) >= 4:
                        ticker = f"{original_ticker}.TWO"
                        self.ticker_obj = yf.Ticker(ticker)
            except:
                if original_ticker.isdigit() and len(original_ticker) >= 4:
                    ticker = f"{original_ticker}.TWO"
                    self.ticker_obj = yf.Ticker(ticker)
            fundamentals = self._fetch_fundamentals()
            news = self._fetch_news()
            return self._generate_report(ticker, fundamentals, news)
        except Exception as e:
            return f"❌ **情報抓取失敗**\n\n錯誤訊息: {str(e)}\n\n請確認股票代號是否正確，或手動貼上情報。"

    def _fetch_fundamentals(self):
        try:
            info = self.ticker_obj.info
            return {
                '市值': info.get('marketCap', 'N/A'),
                '現價': info.get('currentPrice', 'N/A'),
                'Forward PE': info.get('forwardPE', 'N/A'),
                'PEG Ratio': info.get('pegRatio', 'N/A'),
                '營收成長 (YoY)': info.get('revenueGrowth', 'N/A'),
                '毛利率': info.get('grossMargins', 'N/A'),
                '營業利益率': info.get('operatingMargins', 'N/A'),
                'ROE': info.get('returnOnEquity', 'N/A'),
                '負債比': info.get('debtToEquity', 'N/A'),
                '自由現金流': info.get('freeCashflow', 'N/A'),
                '機構目標價': info.get('targetMeanPrice', 'N/A'),
                '52週高點': info.get('fiftyTwoWeekHigh', 'N/A'),
                '52週低點': info.get('fiftyTwoWeekLow', 'N/A'),
                '產業': info.get('industry', 'N/A'),
                '公司簡介': info.get('longBusinessSummary', 'N/A'),
            }
        except Exception as e:
            return {'錯誤': str(e)}

    def _fetch_news(self):
        try:
            news_list = self.ticker_obj.news
            if not news_list:
                return []
            formatted = []
            for item in news_list[:5]:
                ts = item.get('providerPublishTime', 0)
                pt = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M') if ts else 'N/A'
                formatted.append({
                    'title': item.get('title', 'N/A'),
                    'publisher': item.get('publisher', 'N/A'),
                    'time': pt,
                    'link': item.get('link', '#'),
                })
            return formatted
        except:
            return []

    def _generate_report(self, ticker, fundamentals, news):
        def _fmt_pct(v):
            return f"{v * 100:.2f}%" if isinstance(v, (int, float)) else str(v)
        def _fmt_bn(v):
            if isinstance(v, (int, float)):
                return f"${v / 1e9:.2f}B" if v > 1e9 else f"${v / 1e6:.2f}M"
            return str(v)

        report = f"""# 🤖 瓦爾基里情報報告 (Valkyrie Intel Report)
**標的代號**: {ticker}
**抓取時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 📊 基本面數據 (Fundamentals)

"""
        if '錯誤' in fundamentals:
            report += f"❌ 基本面數據抓取失敗: {fundamentals['錯誤']}\n\n"
        else:
            report += f"**市值**: {_fmt_bn(fundamentals.get('市值', 'N/A'))}\n"
            report += f"**現價**: ${fundamentals.get('現價', 'N/A')}\n"
            report += f"**Forward PE**: {fundamentals.get('Forward PE', 'N/A')}\n"
            report += f"**PEG Ratio**: {fundamentals.get('PEG Ratio', 'N/A')}\n"
            report += f"**機構目標價**: ${fundamentals.get('機構目標價', 'N/A')}\n\n"
            report += f"**營收成長 (YoY)**: {_fmt_pct(fundamentals.get('營收成長 (YoY)', 'N/A'))}\n"
            report += f"**毛利率**: {_fmt_pct(fundamentals.get('毛利率', 'N/A'))}\n"
            report += f"**營業利益率**: {_fmt_pct(fundamentals.get('營業利益率', 'N/A'))}\n"
            report += f"**ROE**: {_fmt_pct(fundamentals.get('ROE', 'N/A'))}\n\n"
            report += f"**負債比**: {fundamentals.get('負債比', 'N/A')}\n"
            report += f"**自由現金流**: {_fmt_bn(fundamentals.get('自由現金流', 'N/A'))}\n\n"
            report += f"**52週高點**: ${fundamentals.get('52週高點', 'N/A')}\n"
            report += f"**52週低點**: ${fundamentals.get('52週低點', 'N/A')}\n\n"
            report += f"**產業**: {fundamentals.get('產業', 'N/A')}\n\n"
            bs = str(fundamentals.get('公司簡介', 'N/A'))
            if bs != 'N/A' and len(bs) > 200:
                bs = bs[:200] + "..."
            report += f"**公司簡介**: {bs}\n\n"
        report += "---\n\n## 📰 最新新聞 (Latest News)\n\n"
        if not news:
            report += "⚠️ 未抓取到新聞，或該標的新聞較少。\n\n"
        else:
            for i, n in enumerate(news, 1):
                report += f"**{i}. {n['title']}**\n"
                report += f"   - 來源: {n['publisher']}\n"
                report += f"   - 時間: {n['time']}\n"
                report += f"   - [閱讀全文]({n['link']})\n\n"
        report += "---\n\n💡 **使用提示**: 以上數據由 Yahoo Finance 自動抓取，請搭配人工判斷使用。\n"
        return report


# ═══════════════════════════════════════════════════════════════
# [FIX #2 #3 #9 #10] TitanAgentCouncil — 完整類別 (RESTORED)
# 800-word Anti-Laziness + run_debate + structured output
# ═══════════════════════════════════════════════════════════════
class TitanAgentCouncil:
    """V90.2: 五權分立角鬥士 + 20 條第一性原則"""
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.model = None
        if api_key and _HAS_GENAI:
            try:
                genai.configure(api_key=api_key)
                try:
                    self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
                except:
                    self.model = genai.GenerativeModel('gemini-1.5-flash')
            except Exception as e:
                st.toast(f"⚠️ AI 模型初始化失敗: {e}", icon="⚡")

    def generate_battle_prompt(self, ticker, price, geo_data, rating_info,
                               intel_text="", commander_note="", selected_principles=None,
                               mode="full_tribunal"):
        """
        TRIBUNAL PROTOCOL V400 — 重構版提示詞引擎
        mode: "full_tribunal" | "bull_thesis" | "bear_thesis" | "stress_test" | "quick_verdict"
        """
        level, name, desc, color = rating_info
        acc   = geo_data.get('acceleration', 0)
        phx   = geo_data.get('phoenix_signal', False)
        a35   = geo_data.get('35Y', {}).get('angle', 0)
        a10   = geo_data.get('10Y', {}).get('angle', 0)
        a5    = geo_data.get('5Y',  {}).get('angle', 0)
        a3y   = geo_data.get('3Y',  {}).get('angle', 0)
        a1    = geo_data.get('1Y',  {}).get('angle', 0)
        a6    = geo_data.get('6M',  {}).get('angle', 0)
        a3    = geo_data.get('3M',  {}).get('angle', 0)
        r2_1  = geo_data.get('1Y',  {}).get('r2', 0)
        r2_3  = geo_data.get('3M',  {}).get('r2', 0)
        r2_10 = geo_data.get('10Y', {}).get('r2', 0)
        sl_1  = geo_data.get('1Y',  {}).get('slope', 0)
        sl_3  = geo_data.get('3M',  {}).get('slope', 0)

        # ── 預計算關鍵衍生指標（AI 必須以這些具體數字為錨）──
        consistency_score = sum([
            1 if a35 > 0 else 0, 1 if a10 > 0 else 0,
            1 if a5  > 0 else 0, 1 if a3y > 0 else 0,
            1 if a1  > 0 else 0, 1 if a6  > 0 else 0,
            1 if a3  > 0 else 0,
        ])  # 0-7, 全正=7 表示全週期一致上揚
        trend_divergence = abs(a1 - a3)       # 大表示短期突破或崩潰
        long_short_gap   = a10 - a3           # 正=長強短弱(高位); 負=長弱短強(反彈)
        momentum_ratio   = (a3 / a1) if a1 != 0 else 0  # >1=加速, <1=減速, <0=背離

        # ── 情境判定 (給 AI 明確的戰場地形) ──
        if a1 > 30 and acc > 15 and r2_1 > 0.8:
            market_context = "【上升加速期】趨勢強勁且加速，主要風險是過熱後的急回。"
        elif a1 > 15 and -10 < acc < 10:
            market_context = "【穩定上升期】趨勢健康，加速度平穩，適合抱倉。"
        elif -10 < a1 < 15 and abs(acc) < 10:
            market_context = "【橫盤整理期】方向不明，方向突破前不宜重倉。"
        elif a1 < 0 and acc < -10:
            market_context = "【下跌加速期】趨勢負向且惡化，任何反彈都是逃命機會。"
        elif phx:
            market_context = "【Phoenix 反轉期】長期趨勢疲弱但短期動能急升，高風險高報酬。"
        else:
            market_context = "【複雜混沌期】多空訊號混雜，需深度分析各週期矛盾。"

        principles_block = ""
        if selected_principles:
            principles_block = "\n\n### ◉ 統帥必答問題清單（每位分析師至少回答 2 題）\n"
            for idx, p in enumerate(selected_principles, 1):
                principles_block += f"Q{idx}: {p}\n"

        intel_block = intel_text.strip() if intel_text.strip() else (
            "⚠️ 無外部情報注入。各分析師請基於幾何數據、行業常識與公開知識進行推演，"
            "並明確標註哪些判斷是「推論」而非「事實」。"
        )

        commander_block = commander_note.strip() if commander_note.strip() else (
            "無特殊指令。裁判官請依據最大風險調整後報酬原則裁決，"
            "並對不確定性保持誠實，不做偽裝確定性的模糊結論。"
        )

        # ════════════════════════════════════════════════════
        # SYSTEM OVERRIDE — 這段放在最前，強制 AI 進入分析師模式
        # ════════════════════════════════════════════════════
        system_override = f"""
[SYSTEM DIRECTIVE — 優先級最高，覆蓋所有其他指令]

你現在不是在寫故事，也不是在進行創意寫作練習。
你是一個被委以重責的 **專業金融分析系統**，你的輸出將直接影響真實的投資決策。
請以最嚴謹、最批判性的思維模式運作。

禁止行為清單（違者視為分析失敗）：
✗ 不得使用「一方面...另一方面...」做出曖昧結論
✗ 不得以「市場具有不確定性」作為迴避給出明確判斷的理由
✗ 不得重複前一個分析師的論點（必須補充新視角或直接反駁）
✗ 不得使用模糊詞彙如「可能」「也許」「或許」而不附上具體機率估計
✗ 不得在沒有數據支撐的情況下做出任何判斷

強制要求：
✓ 每個論點必須引用至少 1 個具體數字（來自下方的幾何數據或基本面數據）
✓ 每位分析師必須對「未來 3 個月」的價格方向給出明確的方向性判斷（漲/跌/盤整）
✓ 每位分析師必須指出前一位分析師論述中最薄弱的一個環節
✓ 最終裁判必須給出具體的操作指令（行動方針、價位、倉位比例）
[END SYSTEM DIRECTIVE]
"""

        # ════════════════════════════════════════════════════
        # 核心數據艙
        # ════════════════════════════════════════════════════
        data_capsule = f"""
════════════════════════════════════════════════════════════════
  TITAN INTEL CAPSULE V400 ▸ {ticker} ▸ ${price:.2f}
════════════════════════════════════════════════════════════════

◈ 市場情境判定：{market_context}
◈ 泰坦信評：{level} — {name}（{desc}）

━━━ 【A】七維幾何矩陣 ━━━
時間窗口  │  趨勢角度   │  R² 線性度  │  月斜率
──────────┼─────────────┼─────────────┼──────────────
35年長河  │  {a35:+7.2f}°  │    {geo_data.get('35Y',{}).get('r2',0):.4f}    │  {geo_data.get('35Y',{}).get('slope',0):+.6f}
10年宏觀  │  {a10:+7.2f}°  │    {r2_10:.4f}    │  {geo_data.get('10Y',{}).get('slope',0):+.6f}
5年中期   │  {a5:+7.2f}°  │    {geo_data.get('5Y',{}).get('r2',0):.4f}    │  {geo_data.get('5Y',{}).get('slope',0):+.6f}
3年中短   │  {a3y:+7.2f}°  │    {geo_data.get('3Y',{}).get('r2',0):.4f}    │  {geo_data.get('3Y',{}).get('slope',0):+.6f}
1年近期   │  {a1:+7.2f}°  │    {r2_1:.4f}    │  {sl_1:+.6f}
6月短期   │  {a6:+7.2f}°  │    {geo_data.get('6M',{}).get('r2',0):.4f}    │  {geo_data.get('6M',{}).get('slope',0):+.6f}
3月極短   │  {a3:+7.2f}°  │    {r2_3:.4f}    │  {sl_3:+.6f}

━━━ 【B】衍生動能指標 ━━━
▸ 加速度 (3M°−1Y°)  ：{acc:+.2f}°  {'← 動能加速 🚀' if acc > 10 else ('← 動能衰退 ⚠️' if acc < -10 else '← 動能平穩')}
▸ 趨勢一致性評分    ：{consistency_score}/7（{consistency_score} 個時間窗口角度為正）
▸ 長短期背離指數    ：{trend_divergence:.2f}°（10Y−3M = {long_short_gap:.2f}°，{'長強短弱→高位風險' if long_short_gap > 15 else ('長弱短強→反彈訊號' if long_short_gap < -15 else '長短一致')}）
▸ 動能比率 (3M/1Y) ：{momentum_ratio:.2f}x（{'加速上攻' if momentum_ratio > 1.2 else ('加速下行' if momentum_ratio < -1 else ('動能減退' if 0 < momentum_ratio < 0.8 else '正常'))})
▸ Phoenix 逆轉訊號 ：{'🔥 已觸發（長期角度負、短期角度＞25°）' if phx else '❄️ 未觸發'}

━━━ 【C】實彈情報（Valkyrie Intel）━━━
{intel_block}

━━━ 【D】統帥最高指令 ━━━
{commander_block}
{principles_block}
════════════════════════════════════════════════════════════════
"""

        # ════════════════════════════════════════════════════
        # 模式分支 — 依用戶選擇生成不同格式的 prompt
        # ════════════════════════════════════════════════════

        if mode == "quick_verdict":
            analyst_block = f"""
## 任務：快速裁決（Quick Verdict Mode）

你是「地球頂點·全知者」——查理·蒙格與索羅斯的思維融合體。
你剛剛獨自審閱了以上所有數據。現在以 500-800 字，給出一份**乾淨俐落的專業裁決**。

必須包含：
1. **核心論點**（3 條，每條不超過 2 句話，必須引用具體數字）
2. **最大風險**（1 條，必須指出上方數據中最令你不安的訊號）
3. **操作指令**（格式如下，所有項目必填）

### 【Apex 裁決】
- **行動方針**：[Strong Buy / Buy / 觀望 / Sell / Strong Sell]
- **進場視窗**：[價格區間 + 觸發條件]
- **停損邏輯**：[$XXX，對應 X% 回撤，基於哪個支撐]
- **停利目標**：[$XXX / $XXX（分批），基於哪個壓力]
- **持倉比例**：[X%，理由]
- **持有週期**：[預計持有 X 個月]
- **一句定論**：[不得超過 20 字的最終判斷]
"""

        elif mode == "bull_thesis":
            analyst_block = f"""
## 任務：多頭論文建構（Bull Thesis Mode）

你的任務是為 {ticker} 建構最強大的多頭投資論文。
不是「平衡分析」，是**盡一切可能論證為什麼這是值得買入的標的**。

分三個角色進行，每個角色 **600 字以上**，觀點必須不同：

### 📐 角色一：量化師（Quant Bull）
從幾何數據出發，**只挑選對多頭有利的訊號**來論證趨勢健康。
- 必引數據：趨勢一致性評分 {consistency_score}/7、加速度 {acc:+.1f}°、1Y R² {r2_1:.4f}
- 必回答：角度數值說明趨勢有多堅實？R² 說明趨勢有多穩定？

### 💼 角色二：成長投資人（Growth Bull）
從基本面和行業趨勢出發，論證為什麼當前估值是合理甚至低估的。
- 必引用實彈情報中的財務數據
- 必回答：未來 3 年的 EPS 成長路徑是什麼？

### 🚀 角色三：破壞式創新先知（Visionary Bull）
從 10 年視角論證這是百倍股。
- 必引用：行業 TAM、技術護城河、網路效應
- 必回答：2033 年這家公司的市值天花板是多少？為什麼？

### ⚖️ 多頭論文總結（Thesis Summary）
整合三個角色，給出：
- **3 個最強買入理由**（每條必須有具體數字支撐）
- **3 個最需監控的風險**（論文成立的前提條件）
- **價格目標**：保守 $X / 基準 $X / 樂觀 $X（12 個月）
"""

        elif mode == "bear_thesis":
            analyst_block = f"""
## 任務：空頭論文建構（Bear Thesis Mode）

你的任務是為 {ticker} 建構最嚴密的空頭/做空論文。
不是「平衡分析」，是**盡一切可能找出這個標的的致命缺陷**。

分三個角色進行，每個角色 **600 字以上**：

### 📐 角色一：數學空手（Quant Bear）
從幾何數據出發，**只挑選對空頭有利的訊號**。
- 必引數據：加速度 {acc:+.1f}°、動能比率 {momentum_ratio:.2f}x、長短期背離 {long_short_gap:.2f}°
- 必回答：角度和 R² 說明了什麼風險？歷史上類似幾何形態的後續走勢？

### 🐻 角色二：Michael Burry（Value Short）
從估值和財務數據出發，找出帳面上看不見的泡沫。
- 必引用實彈情報中的財務數據（PE、負債比、FCF）
- 必回答：均值回歸後，股價應該在哪裡？

### ⚰️ 角色三：宏觀毀滅者（Macro Bear）
從宏觀環境出發，找出會壓垮這個標的的外部因素。
- 必回答：利率、匯率、地緣政治、競爭對手中，哪個威脅最大？概率多高？

### ⚖️ 空頭論文總結
- **3 個最嚴重的做空理由**（每條必須有具體數字）
- **空頭成立的催化劑**（什麼事件會觸發下跌？）
- **下跌目標**：保守 -X% / 基準 -X% / 極端 -X%（12 個月）
- **做空的致命風險**（什麼情況下空頭論文會破功？）
"""

        elif mode == "stress_test":
            analyst_block = f"""
## 任務：極限壓力測試（Stress Test Mode）

不是分析正常情況。你的任務是系統性地測試 {ticker} 在各種極端情境下的生存能力。

### 情境一：股市崩盤 20%（Black Swan）
- 假設 SPY 下跌 20%，{ticker} 會跌多少？
- 基於幾何數據（β 係數、加速度 {acc:+.1f}°），估算最壞情況的跌幅
- {ticker} 在崩盤後，趨勢線的支撐位在哪裡？

### 情境二：利率再升 200bps
- 高利率對該公司估值（PE 壓縮）的精確影響
- DCF 模型在利率 +2% 下，公允價值會變為？
- 幾何角度是否能抵抗利率衝擊？

### 情境三：核心業務遭受顛覆
- 如果最大競爭對手以 50% 折扣搶市場，影響多深？
- 公司的護城河（引用基本面數據）能撐多久？
- 幾何數據中是否已經出現顛覆前兆（動能比率 {momentum_ratio:.2f}x）？

### 情境四：內部人大量出逃
- 如果高管在 6 個月內出售 30% 持股，這說明什麼？
- 結合當前幾何位置（信評 {level}），如何解讀？

### 壓力測試總結
- **生存概率**：[在上述四種情境下，各給出 0-100% 的生存評分]
- **最脆弱的環節**：[一句話總結最容易斷裂的地方]
- **對沖建議**：[如何用 20% 的倉位對沖 80% 的核心風險？]
"""

        else:  # full_tribunal — 完整五人法庭（大幅強化版）
            analyst_block = f"""
## ⚖️ TRIBUNAL PROTOCOL V400 — 五人金融法庭

**庭審對象**：{ticker} @ ${price:.2f}
**法庭性質**：這是一個投資決策法庭，每位分析師是「專家證人」，不是演員。
**判決後果**：裁決將直接決定是否動用基金的真實資本。

---

### 【出庭順序與強制輸出規格】

---

## 🧮 證人一：量化分析師（The Quant）
**身份**：15 年期貨市場量化策略師，只信數學，蔑視敘事。

**出庭必須完成以下 6 項量化分析**（跳過任何一項視為作證不完整）：

**[Q1] 趨勢一致性鑑定**
- 7 個時間窗口的角度逐一解讀，明確哪些窗口一致、哪些出現矛盾
- 趨勢一致性評分 {consistency_score}/7 代表什麼含義？歷史案例比較。

**[Q2] R² 線性度審計**
- 1Y R²={r2_1:.4f}，3M R²={r2_3:.4f}，10Y R²={r2_10:.4f}
- R² 高說明趨勢可預測性強，低說明震盪無方向。當前數值屬於哪種狀態？

**[Q3] 加速度動能判定**
- 加速度 {acc:+.2f}°（3M角度−1Y角度）
- 正值=近期加速上攻，負值=動能衰退。當前加速度意味著什麼交易機會？

**[Q4] 動能比率分析**
- 動能比率 {momentum_ratio:.2f}x（3M角度 / 1Y角度）
- 比率 >1.2 表示加速突破，<0 表示趨勢背離。如何解讀？

**[Q5] Phoenix 訊號驗證**
- Phoenix 訊號 = 長期角度（10Y）< 0 且 短期角度（6M）> 25°
- 當前狀態：{'已觸發。歷史上此訊號的成功率與失敗案例各是什麼？' if phx else '未觸發。距離觸發條件還差多遠？'}

**[Q6] 量化交易結論**
- 基於以上五項分析，給出：
  * 3 個月方向預判：[漲/跌/盤整] + 信心度 [X%]
  * 關鍵支撐位（基於趨勢線計算）
  * 關鍵壓力位（基於歷史角度推算）

**字數要求**：800 字以上。每個子項目獨立展開，不得合併簡化。

---

## 💼 證人二：公司內部人（The Insider）
**身份**：你是該公司的 CFO，剛剛結束法說會，正在捍衛股價的合理性。

**你知道一個秘密**：你比任何外部分析師都更了解公司的真實狀況。
但你也必須對抗以下已知的攻擊點（Quant 剛才的數據不能被忽視）：

**必須完成以下 5 項陳述**：

**[I1] 引用 Quant 數據為多頭背書**
- 從 Quant 的 6 項分析中，選出 2-3 個對你最有利的數據，說明為什麼幾何趨勢支持公司基本面。

**[I2] 基本面護城河宣示**
- 引用瓦爾基里情報中的財務數據（毛利率、ROE、FCF、市值等）
- 說明這些指標為什麼證明公司有可持續的競爭優勢

**[I3] 成長路徑具體化**
- 未來 4 個季度，你預期哪些財務指標會改善？具體幅度是？
- 如果沒有具體財務數據可引用，請基於行業標準進行估算並明確說明是估算

**[I4] 機構目標價解讀**
- 當前機構平均目標價與現價的關係，代表多少上行空間？
- 最樂觀和最悲觀的分析師各在哪裡，為什麼？

**[I5] CFO 反質詢**
- 預測 Burry（下一位）最可能攻擊你哪個弱點，主動提出防禦論點

**字數要求**：800 字以上。

---

## 🐻 證人三：做空獵人（The Big Short — Michael Burry）
**身份**：你是 CDS 交易的先驅，你發現了 2008 年次貸危機。你有妄想症，但妄想症患者有時候是對的。

**你剛剛聽了 Quant 和 Insider 的陳述，現在逐一拆解他們的謊言。**

**必須完成以下 5 項質詢**：

**[B1] 拆解 Quant 的數學盲點**
- Quant 的量化分析遺漏了什麼？哪個數字其實是危險信號而非利多？
- 特別針對：動能比率 {momentum_ratio:.2f}x 和長短期背離 {long_short_gap:.2f}° 代表的真實含義

**[B2] 撕開 Insider 的財務面具**
- 從瓦爾基里數據中找出 Insider 沒有提到的危險指標（負債比？FCF 品質？SBC 稀釋？）
- 用具體計算揭露：若均值回歸發生，股價應該在哪裡？

**[B3] 泰坦信評的合理性質疑**
- 信評 {level}（{name}）真的成立嗎？
- 找出至少 2 個讓你對信評存疑的具體數據矛盾

**[B4] 宏觀死亡威脅**
- 外部環境中，哪個因素最可能在未來 6 個月內摧毀這個「成長故事」？
- 給出具體的觸發條件和下跌目標

**[B5] 做空論文**
- 如果你要做空這支股票，你的論文是什麼？
- 進場價位、催化劑、目標價、停損點

**字數要求**：800 字以上。Burry 的風格是尖酸刻薄但有憑有據，不是謾罵。

---

## 🚀 證人四：創世紀先知（The Visionary — Cathie Wood × Peter Thiel）
**身份**：你看到了別人看不見的未來。你的基金持有這支股票 3 年了，你對抗 Burry 的方式不是辯論估值，而是讓他的估值框架變得無關緊要。

**你剛剛聽了 Burry 的做空論文，現在逐一反駁。**

**必須完成以下 5 項陳述**：

**[V1] Burry 的框架錯誤**
- 指出 Burry 使用了哪個過時的分析框架
- 解釋為什麼傳統 PE/DCF 在這個行業是「用直尺量曲線」

**[V2] 萊特定律 × 技術曲線**
- 引用萊特定律（Wright's Law）：產量翻倍→成本下降 X%
- 計算：若此規律成立，未來 3-5 年公司的成本結構會如何演化？

**[V3] TAM 爆炸性計算**
- 目前公司的市場占有率是多少？
- 若市場規模在 2030 年達到 $X Trillion，公司若能保持 Y% 市占，市值應該是？
- 必須給出具體數字，哪怕是範圍估算

**[V4] 引用幾何數據為長期多頭背書**
- 從 Quant 的幾何數據中，引用 35Y 和 10Y 的長期角度
- 說明長期趨勢線的斜率意味著什麼複利回報率

**[V5] 信仰與風險**
- 承認 Burry 的哪一個擔憂是真實存在的
- 說明為什麼即便這個風險成立，長期投資邏輯仍然不變

**字數要求**：800 字以上。

---

## ⚖️ 裁判官：地球頂點·全知者（The Apex Arbiter）
**身份**：查理·蒙格的反向思考 × 橋水達里歐的風險平衡哲學 × 索羅斯的反身性理論。

**你剛剛聆聽了四位專家證人的完整陳述。現在做出最終裁決。**
**這個裁決是真實資金的操作依據，你不能模糊，不能騎牆。**

**必須完成以下結構（總字數 1200 字以上）**：

### 【A. 法庭辯論總結】（300 字）
- 四位證人中，誰的論點最有說服力？為什麼？（必須具體說明哪個數據或邏輯最有力）
- 哪位證人的論述存在最明顯的邏輯漏洞？具體指出。
- 多空雙方的核心分歧點是什麼？（一句話定義戰場）

### 【B. 第一性原則裁決】（400 字）
- 回到最基本的問題：這家公司的商業模式，在物理和數學上，能持續創造超額回報嗎？
- 引用具體的幾何數據（至少 3 個數字）支持你的裁決
{principles_block if principles_block else "- 基於你的判斷，回答最關鍵的一個問題：此時買入，風險調整後的期望值是正還是負？"}

### 【C. 最終操作指令】（格式嚴格，所有項目必填，不得留空）
- **行動方針**：[Strong Buy / Buy / 分批佈局 / 觀望 / 減持 / Sell / Strong Sell]
- **觸發條件**：[什麼條件觸發執行？價格、技術、基本面各選一個]
- **進場價位**：[$XXX（基於趨勢線乖離率計算）]
- **停損邏輯**：[$XXX，對應 -X% 跌幅，基於哪個支撐水平]
- **停利目標 1**：[$XXX，+X%，對應哪個壓力位/技術目標]
- **停利目標 2**：[$XXX，+X%，長期目標]
- **持倉建議**：[X% of Portfolio，理由]
- **預期持有**：[X 個月，理由]
- **核心風險三條**：
  * 風險 1：[具體事件，觸發概率 X%，若觸發跌幅 -X%]
  * 風險 2：[具體事件，觸發概率 X%，若觸發跌幅 -X%]
  * 風險 3：[具體事件，觸發概率 X%，若觸發跌幅 -X%]

### 【D. 一句定論】
[不超過 25 個字，最終判決，不得模糊，不得對沖]
"""

        # 最終完整 prompt 組合
        prompt = f"""{system_override}

{'='*64}
  TITAN TRIBUNAL PROTOCOL V400
  分析標的：{ticker} | 現價：${price:.2f} | 模式：{mode.upper()}
  生成時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*64}

{data_capsule}

{'='*64}
  分析任務
{'='*64}
{analyst_block}

{'='*64}
  輸出規範
{'='*64}

**語言**：繁體中文（技術術語可保留英文）
**格式**：嚴格遵守上方每個角色的 [代碼] 子項目結構，逐一回答
**深度**：這不是摘要，是完整分析。每個子項目獨立展開，不得簡化合併
**禁止**：不得在結論中使用「需要進一步觀察」「視情況而定」等迴避性語言
**收尾**：全文最後一句必須是裁判官的【一句定論】，作為整份報告的錨點

請開始輸出。
"""
        return prompt

    def run_debate(self, ticker, price, geo_data, rating_info,
                   intel_text="", commander_note="", selected_principles=None):
        """[FIX #3] 執行 AI 辯論"""
        if not self.model:
            return "❌ **AI 功能未啟用**\n\n請在側邊欄輸入 Gemini API Key 以啟用此功能。"
        try:
            prompt = self.generate_battle_prompt(
                ticker, price, geo_data, rating_info, intel_text, commander_note, selected_principles
            )
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            if "429" in str(e):
                return f"⚠️ **API 配額已耗盡**\n\n{str(e)}\n\n建議稍後再試或切換模型。"
            return f"❌ **AI 辯論失敗**\n\n{str(e)}"


# ═══════════════════════════════════════════════════════════════
# [FIX #6] 20 條第一性原則 (RESTORED — 完整 20 條)
# ═══════════════════════════════════════════════════════════════
FIRST_PRINCIPLES_20 = [
    "[成長] 萊特定律檢視：產量翻倍，成本是否下降 15%？",
    "[成長] 非線性爆發點：用戶/算力是否呈指數級成長？",
    "[成長] TAM 邊界測試：若已達潛在市場 80%，為何還要買？",
    "[成長] 邊際成本歸零：多服務一人的成本是否趨近零？",
    "[成長] 網路效應：是否越多人用越好用？",
    "[生存] 燒錢率生存測試：若 18 個月融不到資，會死嗎？",
    "[生存] 研發含金量：R&D 是資產還是費用？",
    "[生存] 客戶集中度風險：最大客戶砍單 50% 會如何？",
    "[生存] 庫存周轉物理學：存貨週轉天數是否異常暴增？",
    "[生存] 自由現金流真偽：扣除 SBC 後真的有賺錢嗎？",
    "[泡沫] 均值回歸引力：利潤率若回歸平均，股價會腰斬嗎？",
    "[泡沫] 敘事與現實乖離：CEO 提 AI 次數 vs 實際營收佔比。",
    "[泡沫] 內部人逃生：高管是在買進還是賣出？",
    "[泡沫] 債務槓桿壓力：利息覆蓋率是否低於 3？",
    "[泡沫] 競爭紅海化：是否有低成本中國對手殺入？",
    "[終極] 不可替代性：若公司明天消失，世界有差嗎？",
    "[終極] 物理極限：成長是否受缺電/缺地/缺水限制？",
    "[終極] 人才密度：能否吸引全球最聰明工程師？",
    "[終極] 反脆弱性：遇黑天鵝(戰爭/疫情)是受傷還是獲利？",
    "[終極] 百倍股基因：2033 年之後若活著，它會變成什麼樣子？",
]

# ═══════════════════════════════════════════════════════════════
# [V2] 精準狙擊問題庫 — 投資委員會級別的外科手術提問
# 設計原則：每個問題都必須可用現有量化數據回答
#           問題本身即告訴 AI「我要的是數字，不是敘述」
# ═══════════════════════════════════════════════════════════════
SURGICAL_QUESTIONS = {
    "📐 趨勢結構診斷": [
        "7個時間維度中，哪幾個方向一致？哪裡出現背離？背離的操作意義是什麼？",
        "R²值最低的時間窗口是哪個？這個R²水平讓當前信評的可信度打幾折？",
        "當前加速度訊號的含義：在歷史上，類似加速度水平後的90天股價表現有什麼規律？",
        "Phoenix訊號（長期空頭+短期強多逆轉）：觸發/未觸發各意味著什麼？成功反轉的歷史確認條件是什麼？",
        "上帝軌道乖離率的均值回歸速度：類似乖離水平通常需要幾個月回歸，應對策略是什麼？",
    ],
    "💰 估值與基本面診斷": [
        "Forward PE / PEG 搭配當前營收成長率，給出合理估值區間，以及現在是貴還是便宜。",
        "毛利率和營業利益率的趨勢方向：若繼續此趨勢3年，對合理股價的影響是多少？",
        "自由現金流殖利率（FCF ÷ 市值）是多少？和10年期美債比，這筆投資的風險溢酬是否充足？",
        "用逆向工程推算：要讓現在的股價合理，公司需要在未來3年實現多少年化成長率？這個成長率現實嗎？",
        "機構平均目標價的可信度分析：過去一年機構的預測準確率和偏差方向，應打幾折使用？",
    ],
    "⚠️ 空頭論述與風險識別": [
        "給我3個讓這筆投資在6個月內虧損20%的具體情境，每個附上觸發條件和發生概率估計。",
        "技術性停損三法：趨勢線支撐位、波動率（ATR法）、52週低點——三個方法各給出具體停損價格。",
        "這家公司當前市場敘事中最大的謊言是什麼？市場在相信哪個未必會成真的故事？",
        "若主要競爭對手削減20%售價，這家公司的毛利率和競爭護城河能撐幾個季度？",
        "財務壓力測試：若利率維持高位2年，公司的現金流和負債比例能否支撐正常運營？",
    ],
    "🎯 進出場操作策略": [
        "給一個可直接執行的進場Checklist（非建議，是二元條件：每項滿足=✅/不滿足=❌，全✅才進場）。",
        "若總帳戶100萬，最大單筆損失控制在2%，這支股票的合理倉位是多少股？計算過程請展示。",
        "分批建倉策略：第一批最優進場點？加碼條件？減倉條件？完全退出條件？各是什麼？",
        "設計一個機械式出場規則，讓我在不做主觀判斷的情況下，自動知道何時離場。",
        "基於當前3個月和1年角度差，動能最可能持續幾個月？對應的最佳持有期和出場時機預估。",
    ],
    "🔭 宏觀與產業脈絡": [
        "當前利率、通膨、景氣循環對這家公司是順風還是逆風？請量化：每升息1碼對其估值影響多少？",
        "這家公司在AI/半導體/所在產業未來18個月最可能發生的結構性變化中，處於什麼位置？",
        "地緣政治風險（台海/美中關稅/供應鏈重組）對這家公司的直接衝擊：最壞情景下影響多大？",
        "若整體市場修正20%，基於這支股票的歷史Beta，它預計下跌多少？相對表現如何？",
    ],
}

# Tab 4 精選 10 條 (原始 V90.2 設計)
ESSENTIAL_PRINCIPLES_10 = [
    "[成長] 萊特定律檢視：產量翻倍，成本是否下降 15%？",
    "[成長] 非線性爆發點：用戶/算力是否呈指數級成長？",
    "[成長] TAM 邊界測試：若已達潛在市場 80%，為何還要買？",
    "[生存] 燒錢率生存測試：若 18 個月融不到資，會死嗎？",
    "[生存] 自由現金流真偽：扣除 SBC 後真的有賺錢嗎？",
    "[泡沫] 均值回歸引力：利潤率若回歸平均，股價會腰斬嗎？",
    "[泡沫] 敘事與現實乖離：CEO 提 AI 次數 vs 實際營收佔比。",
    "[泡沫] 內部人逃生：高管是在買進還是賣出？",
    "[終極] 不可替代性：若公司明天消失，世界有差嗎？",
    "[終極] 百倍股基因：2033 年若活著，它會變成什麼樣子？",
]


# ═══════════════════════════════════════════════════════════════
# 視覺化輔助 — 雷達圖 / 月K / 上帝軌道
# ═══════════════════════════════════════════════════════════════
def _render_radar(geo, ticker):
    cats = ['35Y', '10Y', '5Y', '3Y', '1Y', '6M', '3M']
    angles = [geo[c]['angle'] for c in cats]
    fig = go.Figure(go.Scatterpolar(
        r=angles, theta=cats, fill='toself',
        fillcolor='rgba(255,165,0,0.25)', line=dict(color='orange', width=2), name='角度 (°)'
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[-90, 90])),
        title=f"{ticker} — 7D 幾何雷達圖", template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)', height=400
    )
    st.plotly_chart(fig, use_container_width=True)


def _render_monthly_chart(ticker, months=120):
    df = st.session_state.get('daily_price_data', {}).get(ticker)
    if df is None:
        st.toast("⚠️ 無日K數據", icon="⚡")
        return
    dfc = df.copy()
    if isinstance(dfc.columns, pd.MultiIndex):
        dfc.columns = dfc.columns.get_level_values(0)
    dfc = dfc.reset_index()
    cols = dfc.columns.tolist()
    date_c = next((c for c in cols if str(c).lower() in ['date', 'index']), cols[0])
    dfc.rename(columns={date_c: 'Date'}, inplace=True)
    for c in ['Open', 'High', 'Low', 'Close', 'Volume']:
        if c not in dfc.columns:
            dfc[c] = dfc.get('Close', 0)
    dfc = dfc.tail(months * 22)
    dfc['MA87'] = dfc['Close'].rolling(87).mean()
    dfc['MA284'] = dfc['Close'].rolling(284).mean()
    bk = alt.Chart(dfc).encode(x=alt.X('Date:T'))
    col_cond = alt.condition("datum.Open<=datum.Close", alt.value("#FF4B4B"), alt.value("#26A69A"))
    candles = (
        bk.mark_rule().encode(y=alt.Y('Low', scale=alt.Scale(zero=False)), y2='High', color=col_cond)
        + bk.mark_bar().encode(y='Open', y2='Close', color=col_cond)
    )
    l87 = bk.mark_line(color='orange', strokeWidth=2).encode(y='MA87')
    l284 = bk.mark_line(color='#00bfff', strokeWidth=2).encode(y='MA284')
    st.altair_chart((candles + l87 + l284).interactive().properties(height=400), use_container_width=True)
    st.caption("🔶 橘線: 87MA | 🔷 藍線: 284MA")


def _render_god_orbit(ticker):
    """[FIX #4] 上帝軌道 — 全歷史對數線性回歸 (RESTORED)"""
    df_daily = st.session_state.get('daily_price_data', {}).get(ticker)
    if df_daily is None or df_daily.empty:
        st.toast("⚠️ 請先執行掃描以載入數據。", icon="⚡")
        return
    df_c = df_daily.copy()
    if isinstance(df_c.columns, pd.MultiIndex):
        df_c.columns = df_c.columns.get_level_values(0)
    df_c = df_c.reset_index()
    cols = df_c.columns.tolist()
    date_c = next((c for c in cols if str(c).lower() in ['date', 'index']), cols[0])
    df_c.rename(columns={date_c: 'Date'}, inplace=True)
    if 'Close' not in df_c.columns:
        return

    df_c['Days'] = np.arange(len(df_c))
    log_p = np.log(df_c['Close'].values.astype(float))
    slope, intercept, r_value, _, _ = linregress(df_c['Days'].values, log_p)
    df_c['Trendline'] = np.exp(intercept + slope * df_c['Days'])

    cur_p = float(df_c['Close'].iloc[-1])
    cur_t = float(df_c['Trendline'].iloc[-1])
    deviation = ((cur_p / cur_t) - 1) * 100

    c1, c2, c3 = st.columns(3)
    c1.metric("全歷史 R²", f"{r_value**2:.4f}")
    c2.metric("當前價格", f"${cur_p:.2f}")
    c3.metric("趨勢線乖離", f"{deviation:+.1f}%")

    st.toast("ℹ️ Y軸為對數座標，可更清楚觀察長期幾何趨勢。藍色虛線為全歷史回歸軌道。", icon="📡")
    price_line = alt.Chart(df_c).mark_line(color='#00FF00', strokeWidth=2).encode(
        x=alt.X('Date:T', title='時間', axis=alt.Axis(format='%Y')),
        y=alt.Y('Close:Q', title='收盤價 (對數座標)', scale=alt.Scale(type='log'),
                 axis=alt.Axis(tickCount=10)),
        tooltip=[
            alt.Tooltip('Date:T', title='日期', format='%Y-%m-%d'),
            alt.Tooltip('Close:Q', title='收盤價', format=',.2f'),
            alt.Tooltip('Trendline:Q', title='趨勢線', format=',.2f'),
        ]
    ).properties(height=500, title=f'{ticker} - 全歷史對數線性回歸分析 (上帝軌道)')
    trend_line = alt.Chart(df_c).mark_line(
        color='#4169E1', strokeWidth=2, strokeDash=[5, 5]
    ).encode(x='Date:T', y=alt.Y('Trendline:Q', scale=alt.Scale(type='log')))
    final_chart = (price_line + trend_line).configure_axis(
        gridColor='#333333', domainColor='#666666'
    ).configure_view(strokeWidth=0)
    st.altair_chart(final_chart, use_container_width=True)

    st.subheader("📊 幾何解讀")
    if abs(deviation) < 10:
        st.toast(f"✅ 價格貼近趨勢線 (乖離 {deviation:+.1f}%)，處於健康軌道。", icon="🎯")
    elif deviation > 30:
        st.toast(f"⚠️ 價格遠高於趨勢線 (乖離 +{deviation:.1f}%)，可能過熱，注意回調風險。", icon="⚡")
    elif deviation < -30:
        st.toast(f"ℹ️ 價格遠低於趨勢線 (乖離 {deviation:.1f}%)，若基本面無虞，可能是逢低機會。", icon="📡")
    else:
        st.toast(f"ℹ️ 價格略偏離趨勢線 (乖離 {deviation:+.1f}%)，屬正常波動範圍。", icon="📡")


# ═══════════════════════════════════════════════════════════════
# 宏觀對沖 + 回測引擎 (輔助函數)
# ═══════════════════════════════════════════════════════════════
@st.cache_data(ttl=3600)
def _fetch_prices(tickers, period="1y"):
    try:
        raw = yf.download(list(tickers), period=period, progress=False, auto_adjust=True)
        prices = raw["Close"] if isinstance(raw.columns, pd.MultiIndex) else raw
        return prices.dropna(how="all")
    except:
        return pd.DataFrame()


@st.cache_data(ttl=7200)
def _geo_backtest(ticker, thresh, period_k, start, capital):
    try:
        orig = ticker
        if ticker.isdigit() and len(ticker) >= 4:
            ticker = f"{ticker}.TW"
        df = yf.download(ticker, start=start, progress=False, auto_adjust=True)
        if df.empty and orig.isdigit():
            df = yf.download(f"{orig}.TWO", start=start, progress=False, auto_adjust=True)
        if df.empty or len(df) < 30:
            return None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        if "Close" not in df.columns:
            return None
        if not isinstance(df.index, pd.DatetimeIndex):
            df.index = pd.to_datetime(df.index)
        monthly = df.resample("ME").agg({"Close": "last"}).dropna()
        if len(monthly) < 6:
            return None
        nm = {"3M": 3, "6M": 6, "1Y": 12, "3Y": 36}.get(period_k, 3)
        sigs = []
        for i in range(nm, len(monthly)):
            sl = monthly.iloc[i - nm:i]
            lp = np.log(sl["Close"].values)
            x = np.arange(len(lp))
            s, *_ = linregress(x, lp)
            ang = float(np.arctan(s * 100) * (180 / np.pi))
            sigs.append({"Date": monthly.index[i], "Sig": 1 if ang > thresh else 0})
        sg = pd.DataFrame(sigs)
        if sg.empty:
            return None
        dfd = df.copy()
        dfd["Sig"] = 0
        for k in range(len(sg) - 1):
            mask = (dfd.index > sg.iloc[k]["Date"]) & (dfd.index <= sg.iloc[k + 1]["Date"])
            dfd.loc[mask, "Sig"] = sg.iloc[k]["Sig"]
        dfd.loc[dfd.index > sg.iloc[-1]["Date"], "Sig"] = sg.iloc[-1]["Sig"]
        dfd["Pct"] = dfd["Close"].pct_change()
        dfd["Strat"] = dfd["Sig"].shift(1) * dfd["Pct"]
        dfd["BH"] = dfd["Pct"]
        dfd["Eq"] = (1 + dfd["Strat"].fillna(0)).cumprod() * capital
        dfd["BH_Eq"] = (1 + dfd["BH"].fillna(0)).cumprod() * capital
        dfd["DD"] = (dfd["Eq"] / dfd["Eq"].cummax()) - 1
        ny = max(len(dfd) / 252, 0.01)
        tr = dfd["Eq"].iloc[-1] / capital - 1
        cagr = (1 + tr) ** (1 / ny) - 1
        dr = dfd["Strat"].dropna()
        sharpe = (dr.mean() * 252 - 0.02) / (dr.std() * np.sqrt(252)) if dr.std() > 0 else 0
        bh_r = dfd["BH_Eq"].iloc[-1] / capital - 1
        bh_cagr = (1 + bh_r) ** (1 / ny) - 1
        return {
            "cagr": cagr, "mdd": dfd["DD"].min(), "sharpe": sharpe,
            "fe": dfd["Eq"].iloc[-1], "bh_cagr": bh_cagr,
            "eq": dfd["Eq"], "bh": dfd["BH_Eq"], "dd": dfd["DD"]
        }
    except:
        return None


# ═══════════════════════════════════════════════════════════════
# CSS — CINEMATIC HOLOGRAM
# ═══════════════════════════════════════════════════════════════
def _inject_css():
    st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Rajdhani:wght@300;400;600;700&family=JetBrains+Mono:wght@300;400;700&family=Inter:wght@300;400;500;600;700;800;900&family=Orbitron:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
<style>
:root{--c-gold:#FFD700;--c-cyan:#00F5FF;--c-red:#FF3131;--c-green:#00FF7F;
  --f-d:'Bebas Neue',sans-serif;--f-b:'Rajdhani',sans-serif;--f-m:'JetBrains Mono',monospace;
  --f-i:'Inter',sans-serif;--f-o:'Orbitron',sans-serif;}
.t6-hero{padding:48px 40px 42px;background:linear-gradient(180deg,rgba(8,8,16,0) 0%,rgba(4,4,12,0.7) 50%,rgba(0,0,0,0.9) 100%);border-bottom:1px solid rgba(0,245,255,0.1);text-align:center;margin-bottom:30px;}
.t6-hero-surtitle{font-family:var(--f-o);font-size:11px;color:rgba(0,245,255,0.35);letter-spacing:8px;text-transform:uppercase;margin-bottom:14px;}
.t6-hero-status{font-family:var(--f-i);font-size:100px;font-weight:900;letter-spacing:-4px;line-height:1;margin-bottom:10px;}
.t6-hero-status.bull{color:#00FF7F;text-shadow:0 0 60px rgba(0,255,127,0.25);}
.t6-hero-status.bear{color:#FF3131;text-shadow:0 0 60px rgba(255,49,49,0.25);}
.t6-hero-status.neutral{color:#FFD700;text-shadow:0 0 60px rgba(255,215,0,0.2);}
.t6-hero-sub{font-family:var(--f-m);font-size:10px;color:rgba(160,176,208,0.35);letter-spacing:4px;text-transform:uppercase;margin-top:6px;}
.t6-poster{flex:1;min-width:110px;min-height:160px;background:rgba(255,255,255,0.015);border:1px solid rgba(255,255,255,0.05);border-radius:14px;padding:16px 10px 12px;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;}
.t6-poster.active{border-color:var(--c-cyan);background:rgba(0,245,255,0.04);box-shadow:0 0 30px rgba(0,245,255,0.08);}
.t6-poster-icon{font-size:26px;margin-bottom:6px;}
.t6-poster-title{font-family:var(--f-b);font-size:28px;font-weight:700;color:#FFF;letter-spacing:1px;}
.t6-poster-sub{font-family:var(--f-m);font-size:26px;color:rgba(140,155,178,0.4);letter-spacing:1px;text-transform:uppercase;margin-top:3px;}
.rank-badge{font-size:120px;font-weight:900;background:linear-gradient(135deg,#FFD700 0%,#B8860B 50%,#FFD700 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-family:var(--f-o);line-height:1;filter:drop-shadow(0 4px 12px rgba(255,215,0,0.3));}
.rank-badge-wrap{text-align:center;padding:30px 0 10px;}
.rank-badge-name{font-family:var(--f-b);font-size:20px;font-weight:700;color:rgba(255,215,0,0.7);letter-spacing:2px;margin-top:8px;}
.rank-badge-desc{font-family:var(--f-m);font-size:10px;color:rgba(160,176,192,0.4);letter-spacing:2px;text-transform:uppercase;margin-top:4px;}
.trend-bar-container{display:flex;gap:10px;justify-content:space-between;margin:24px 0;}
.trend-card{background:#111;border:1px solid #333;flex:1;padding:16px 10px;text-align:center;border-radius:10px;position:relative;overflow:hidden;}
.trend-card::after{content:'';position:absolute;bottom:0;left:0;right:0;height:4px;background:var(--tc-accent,#555);border-radius:0 0 10px 10px;}
.trend-card.up{--tc-accent:#00FF7F;border-color:rgba(0,255,127,0.2);}
.trend-card.dn{--tc-accent:#FF3131;border-color:rgba(255,49,49,0.2);}
.trend-card.flat{--tc-accent:#FFD700;border-color:rgba(255,215,0,0.15);}
.trend-card-period{font-family:var(--f-o);font-size:11px;color:rgba(160,176,208,0.5);letter-spacing:2px;margin-bottom:8px;}
.trend-val{font-size:26px;font-weight:800;font-family:var(--f-i);letter-spacing:-1px;line-height:1;}
.trend-val.up{color:#00FF7F;} .trend-val.dn{color:#FF6B6B;} .trend-val.flat{color:#FFD700;}
.trend-r2{font-family:var(--f-m);font-size:9px;color:rgba(160,176,208,0.35);letter-spacing:1px;margin-top:6px;}
.terminal-box{background:#0D1117;border:1px solid #30363d;border-left:4px solid #00F5FF;border-radius:0 10px 10px 0;padding:22px 24px;font-family:var(--f-m);color:#00F5FF;font-size:12px;line-height:1.6;margin:16px 0;}
.terminal-box::before{content:'> VALKYRIE INTEL TERMINAL';display:block;font-size:9px;letter-spacing:3px;color:rgba(0,245,255,0.3);margin-bottom:12px;padding-bottom:8px;border-bottom:1px solid rgba(0,245,255,0.08);}
.hunt-rank-card{display:flex;align-items:center;gap:16px;background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.05);border-radius:12px;padding:14px 18px;margin-bottom:8px;}
.hunt-rank-num{font-family:var(--f-i);font-size:36px;font-weight:900;color:rgba(255,215,0,0.25);min-width:50px;text-align:center;}
.hunt-rank-ticker{font-family:var(--f-d);font-size:22px;color:#FFF;letter-spacing:2px;}
.hunt-rank-detail{font-family:var(--f-m);font-size:10px;color:rgba(160,176,208,0.45);letter-spacing:1px;margin-top:2px;}
.t6-sec-head{display:flex;align-items:center;gap:14px;padding-bottom:14px;border-bottom:1px solid rgba(255,255,255,.052);margin-bottom:20px;}
.t6-sec-num{font-family:var(--f-d);font-size:56px;color:rgba(0,245,255,.06);letter-spacing:2px;line-height:1;}
.t6-sec-title{font-family:var(--f-d);font-size:22px;color:var(--sa,#00F5FF);letter-spacing:2px;}
.t6-sec-sub{font-family:var(--f-m);font-size:9px;color:rgba(0,245,255,.28);letter-spacing:2px;text-transform:uppercase;margin-top:2px;}
.t6-foot{font-family:var(--f-m);font-size:9px;color:rgba(70,90,110,.28);letter-spacing:2px;text-align:right;margin-top:28px;text-transform:uppercase;}
</style>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# HERO + NAV + SPECTRUM
# ═══════════════════════════════════════════════════════════════
def _render_hero():
    status, css_cls, sub_text = "SCANNING", "neutral", "Awaiting analysis"
    if 'deep_geo' in st.session_state and st.session_state.get('deep_geo'):
        geo = st.session_state['deep_geo']
        tk = st.session_state.get('deep_ticker', '')
        a3 = geo['3M']['angle']
        if a3 > 15:
            status, css_cls = "BULL", "bull"
        elif a3 < -15:
            status, css_cls = "BEAR", "bear"
        else:
            status, css_cls = "NEUTRAL", "neutral"
        sub_text = f"{tk} 3M: {a3:+.1f}°"
    st.markdown(f'<div class="t6-hero"><div class="t6-hero-surtitle">META-TREND HOLOGRAPHIC DECK V300</div><div class="t6-hero-status {css_cls}">{status}</div><div class="t6-hero-sub">{sub_text} · {datetime.now().strftime("%Y-%m-%d %H:%M")}</div></div>', unsafe_allow_html=True)


def _render_nav_rail():
    if 't6_active' not in st.session_state:
        st.session_state.t6_active = "6.1"
    cards = [
        ("6.1", "🌍", "全球視野", "Global View"), ("6.2", "💎", "個股深鑽", "Deep Dive"),
        ("6.3", "📜", "獵殺百倍股", "Hunter List"), ("6.4", "⚔️", "全境獵殺", "Full Scan"),
        ("6.5", "🛡️", "宏觀對沖", "Hedge"), ("6.6", "🧪", "回測沙盒", "Sandbox"),
    ]
    cols = st.columns(6)
    for i, (sid, icon, title, sub) in enumerate(cards):
        with cols[i]:
            ac = "active" if st.session_state.t6_active == sid else ""
            st.markdown(f'<div class="t6-poster {ac}"><div class="t6-poster-icon">{icon}</div><div class="t6-poster-title">{sid} {title}</div><div class="t6-poster-sub">{sub}</div></div>', unsafe_allow_html=True)
            if st.button(f"Open {sid}", key=f"t6nav_{sid}", use_container_width=True):
                st.session_state.t6_active = sid
                st.rerun()


def _render_spectrum(geo, ticker):
    periods = ['35Y', '10Y', '5Y', '3Y', '1Y', '6M', '3M']
    html = '<div class="trend-bar-container">'
    for p in periods:
        g = geo.get(p, {})
        a = g.get('angle', 0)
        r2 = g.get('r2', 0)
        cls = "up" if a > 5 else ("dn" if a < -5 else "flat")
        html += f'<div class="trend-card {cls}"><div class="trend-card-period">{p}</div><div class="trend-val {cls}">{a:+.1f}°</div><div class="trend-r2">R² {r2:.3f}</div></div>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# SECTION 6.1 — 全球視野
# ═══════════════════════════════════════════════════════════════
def _s61():
    st.markdown(
        '<div class="t6-sec-head" style="--sa:#00F5FF">'
        '<div class="t6-sec-num">6.1</div>'
        '<div><div class="t6-sec-title">全球視野 — 機構級多標的掃描</div>'
        '<div class="t6-sec-sub">Multi-Asset 7D Geometry · Rating · Acceleration · FFT Cycle · 10 Watchlist Templates</div>'
        '</div></div>',
        unsafe_allow_html=True
    )

    # ═══════════════════════════════════════════════════════════
    # BLOCK A: 10 WATCHLIST TEMPLATES (from 4.1 Portfolio Bank)
    # ═══════════════════════════════════════════════════════════
    st.markdown(
        '<div style="font-family:\'JetBrains Mono\',monospace;font-size:9px;'
        'color:rgba(0,245,255,.35);letter-spacing:4px;text-transform:uppercase;'
        'margin-bottom:12px;">⚡ 快速戰區範本 — 點擊即載入</div>',
        unsafe_allow_html=True
    )

    SCAN_TEMPLATES = {
        "🦅 Mag7 七巨頭":        "AAPL,MSFT,GOOGL,AMZN,META,NVDA,TSLA",
        "💻 Tech10 科技十傑":     "AAPL,MSFT,GOOGL,AMZN,META,NVDA,TSLA,AVGO,ORCL,AMD",
        "🤖 AI 革命主題":         "NVDA,AMD,AVGO,PLTR,MSFT,GOOGL,META,ORCL,ARM,SMCI",
        "🇹🇼 台股半導體":        "2330.TW,2454.TW,2303.TW,3711.TW,6531.TW,2308.TW,3034.TW,2379.TW",
        "🇹🇼 台股核心組合":      "2330.TW,006208.TW,2454.TW,2317.TW,00675L.TW,2882.TW,2412.TW",
        "💎 量子科技":            "IONQ,RGTI,QBTS,NVDA,MSFT,GOOGL,IBM",
        "🛡️ 防禦型配置":         "VYM,SCHD,BND,JNJ,PG,KO,XLU,LMT",
        "🌏 全球分散":            "VTI,VEA,VWO,GLD,BND,EEM,FXI,EWJ",
        "🚀 高成長動能":          "NVDA,TSLA,META,PLTR,CRWD,MSTR,COIN,RKLB",
        "⚡ 美股+台股混合":       "NVDA,MSFT,2330.TW,2454.TW,00631L.TW,TSLA,GOOGL,2317.TW",
    }

    # 2 rows × 5 buttons
    tpl_keys = list(SCAN_TEMPLATES.keys())
    for row in range(2):
        cols = st.columns(5)
        for col_i, col in enumerate(cols):
            idx = row * 5 + col_i
            if idx < len(tpl_keys):
                k = tpl_keys[idx]
                with col:
                    if st.button(k, key=f"t6_tpl_{idx}", use_container_width=True):
                        st.session_state['globe_tickers'] = SCAN_TEMPLATES[k]
                        st.rerun()

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════════
    # BLOCK B: INPUT + SCAN CONTROLS
    # ═══════════════════════════════════════════════════════════
    # 確保 session_state 有預設值（首次載入）
    if 'globe_tickers' not in st.session_state:
        st.session_state['globe_tickers'] = "NVDA,TSLA,2330.TW,2454.TW"
    col_in, col_sort, col_btn = st.columns([3, 1, 1])
    tickers_raw = col_in.text_input(
        "標的代號 (逗號分隔，台股自動補 .TW/.TWO)",
        key="globe_tickers"
    )
    sort_by = col_sort.selectbox(
        "排序依據", ["1Y角度", "3M角度", "加速度", "信評"],
        key="globe_sort"
    )
    do_scan = col_btn.button("🔍 掃描", type="primary",
                              key="globe_scan", use_container_width=True)

    # Persist input

    if do_scan and tickers_raw:
        tickers = [t.strip() for t in tickers_raw.split(",") if t.strip()]
        results = []
        prog   = st.progress(0)
        status = st.empty()

        for i, t in enumerate(tickers):
            status.text(f"⬡ 解碼 {t}… ({i+1}/{len(tickers)})")
            geo = compute_7d_geometry(t)
            if geo:
                rating = titan_rating_system(geo)
                price  = 0.0
                dp = st.session_state.get('daily_price_data', {}).get(t)
                if dp is not None and not dp.empty:
                    price = float(dp['Close'].iloc[-1])

                # Signal composite badge
                acc   = geo['acceleration']
                a1    = geo['1Y']['angle']
                a3    = geo['3M']['angle']
                phx   = geo['phoenix_signal']

                if phx:
                    signal = "🔥 Phoenix"
                elif acc > 20 and a3 > 30:
                    signal = "🚀 爆發加速"
                elif acc > 10 and a1 > 20:
                    signal = "⚡ 動能增強"
                elif acc < -20 and a3 < -20:
                    signal = "💀 崩潰加速"
                elif acc < -10 and a1 < 0:
                    signal = "🔴 動能衰竭"
                elif -5 < acc < 5 and -5 < a3 < 15:
                    signal = "⚖️ 橫盤整理"
                else:
                    signal = "📊 正常運行"

                results.append({
                    '代號':     t,
                    '現價':     price,
                    '信評':     f"{rating[0]} {rating[1]}",
                    '訊號':     signal,
                    '35Y°':    geo['35Y']['angle'],
                    '10Y°':    geo['10Y']['angle'],
                    '1Y角度':  geo['1Y']['angle'],
                    '6M°':     geo['6M']['angle'],
                    '3M角度':  geo['3M']['angle'],
                    '加速度':   geo['acceleration'],
                    '1Y R²':   geo['1Y']['r2'],
                    'Phoenix':  '🔥' if phx else '—',
                })
            else:
                results.append({
                    '代號': t, '現價': 0, '信評': 'N/A —', '訊號': '❓ 無資料',
                    '35Y°': 0, '10Y°': 0, '1Y角度': 0, '6M°': 0,
                    '3M角度': 0, '加速度': 0, '1Y R²': 0, 'Phoenix': '—',
                })
            prog.progress((i + 1) / len(tickers))

        status.text("✅ 掃描完成")
        prog.empty()

        if results:
            res_df = pd.DataFrame(results)
            # Sort
            sort_map = {"1Y角度": "1Y角度", "3M角度": "3M角度",
                        "加速度": "加速度", "信評": "信評"}
            sort_col = sort_map.get(sort_by, "1Y角度")
            if sort_col in res_df.columns:
                res_df = res_df.sort_values(sort_col, ascending=(sort_col == "信評"))

            st.session_state['globe_scan_results'] = res_df

            # ── KPI summary row ───────────────────────────────
            n_bull   = (res_df['1Y角度'] > 20).sum()
            n_bear   = (res_df['1Y角度'] < -10).sum()
            n_phx    = (res_df['Phoenix'] == '🔥').sum()
            avg_acc  = res_df['加速度'].mean()
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("多頭標的", f"{n_bull} / {len(res_df)}",  "1Y角度 > 20°")
            k2.metric("空頭警示", f"{n_bear}",                   "1Y角度 < -10°")
            k3.metric("Phoenix 訊號", f"{n_phx}",               "長空短多逆轉")
            k4.metric("平均加速度", f"{avg_acc:+.1f}°",
                       "↑動能增強" if avg_acc > 0 else "↓動能衰竭",
                       delta_color="normal" if avg_acc > 0 else "inverse")

            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

            # ── Styled dataframe ──────────────────────────────
            def _color_angle(val):
                try:
                    v = float(val)
                    if v > 35:   return 'color:#00FF7F;font-weight:700'
                    if v > 15:   return 'color:#ADFF2F'
                    if v > 0:    return 'color:#FFD700'
                    if v > -15:  return 'color:#FF9A3C'
                    return 'color:#FF3131;font-weight:700'
                except:
                    return ''

            def _color_acc(val):
                try:
                    v = float(val)
                    if v > 15:  return 'color:#00FF7F;font-weight:700'
                    if v > 0:   return 'color:#ADFF2F'
                    if v > -15: return 'color:#FF9A3C'
                    return 'color:#FF3131;font-weight:700'
                except:
                    return ''

            styled = res_df.style\
                .applymap(_color_angle, subset=['35Y°','10Y°','1Y角度','6M°','3M角度'])\
                .applymap(_color_acc,   subset=['加速度'])\
                .format({
                    '現價':  '{:.2f}',
                    '35Y°': '{:.1f}°',
                    '10Y°': '{:.1f}°',
                    '1Y角度':'{:.1f}°',
                    '6M°':  '{:.1f}°',
                    '3M角度':'{:.1f}°',
                    '加速度':'{:+.1f}°',
                    '1Y R²': '{:.3f}',
                })

            st.dataframe(styled, use_container_width=True, hide_index=True)

            # ── Download button ───────────────────────────────
            csv_data = res_df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                "📥 下載掃描報表 (CSV)", csv_data,
                f"titan_scan_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.csv",
                key="dl_scan_csv"
            )

            # ── Scatter: 1Y角度 vs 加速度 (bubble = R²) ──────
            st.markdown(
                '<div style="font-family:\'JetBrains Mono\',monospace;font-size:9px;'
                'color:rgba(0,245,255,.35);letter-spacing:3px;text-transform:uppercase;'
                'margin:16px 0 4px;">🎯 動能矩陣 — 1Y趨勢 vs 近期加速度</div>',
                unsafe_allow_html=True
            )
            fig_sc = go.Figure()
            for _, row in res_df.iterrows():
                col_dot = (
                    "#FF3131" if row['1Y角度'] < 0
                    else "#FFD700" if row['1Y角度'] < 20
                    else "#00FF7F"
                )
                fig_sc.add_trace(go.Scatter(
                    x=[row['1Y角度']], y=[row['加速度']],
                    mode='markers+text',
                    marker=dict(
                        size=max(8, min(28, row['1Y R²'] * 30)),
                        color=col_dot, opacity=0.85,
                        line=dict(color='rgba(0,0,0,0.4)', width=1)
                    ),
                    text=[row['代號']], textposition='top center',
                    textfont=dict(color='#DDD', size=10, family='JetBrains Mono'),
                    name=row['代號'],
                    hovertemplate=(
                        f"<b>{row['代號']}</b><br>"
                        f"1Y: {row['1Y角度']:.1f}° | Acc: {row['加速度']:+.1f}°<br>"
                        f"R²: {row['1Y R²']:.3f} | {row['信評']}<extra></extra>"
                    )
                ))

            # Quadrant lines
            fig_sc.add_hline(y=0,  line_color='rgba(255,255,255,0.12)', line_dash='dot')
            fig_sc.add_vline(x=20, line_color='rgba(255,255,255,0.12)', line_dash='dot')
            # Quadrant labels — font color uses safe hex, bgcolor uses rgba for transparency
            for qx, qy, ql, qfont, qbg in [
                (35,  25,  "🚀 加速多頭", "#00FF7F", "rgba(0,255,127,0.18)"),
                (-20, 25,  "⚡ 反轉嘗試", "#FFD700", "rgba(255,215,0,0.15)"),
                (35,  -25, "⚠️ 高位減速", "#FF9A3C", "rgba(255,165,0,0.15)"),
                (-20, -25, "💀 加速下跌", "#FF6B6B", "rgba(255,49,49,0.15)"),
            ]:
                fig_sc.add_annotation(
                    x=qx, y=qy, text=ql,
                    showarrow=False,
                    font=dict(color=qfont, size=10, family="JetBrains Mono"),
                    bgcolor=qbg, borderpad=4
                )

            fig_sc.update_layout(
                template="plotly_dark",
                height=380,
                showlegend=False,
                xaxis=dict(title="1Y 趨勢角度 (°)", gridcolor="rgba(255,255,255,0.05)",
                           zeroline=False),
                yaxis=dict(title="近期加速度 (3M-1Y, °)", gridcolor="rgba(255,255,255,0.05)",
                           zeroline=False),
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                margin=dict(t=20, b=50, l=60, r=20),
                hovermode="closest",
            )
            st.plotly_chart(fig_sc, use_container_width=True)


    # ═══════════════════════════════════════════════════════════
    # BLOCK C: FFT 量子週期引擎 (First Principles — Pro Edition)
    # ═══════════════════════════════════════════════════════════
    st.divider()
    st.markdown("### 📡 FFT 量子週期引擎 (Quantum Cycle Engine)")
    st.markdown(
        '<div style="font-family:\'JetBrains Mono\',monospace;font-size:10px;'
        'color:rgba(160,176,208,0.45);letter-spacing:1px;line-height:1.8;margin-bottom:12px;">'
        '第一性原理：市場價格 = 長期趨勢 + 多重週期疊加 + 隨機雜訊。<br>'
        'FFT 將時域信號分解到頻域，萃取出隱藏的機構操作週期（月結/季結/半年結）。<br>'
        '複合波前向預測告訴你「幾天後到達下一個波峰或波谷」——這才是實戰核心。'
        '</div>',
        unsafe_allow_html=True
    )

    fft_col_in, fft_col_btn = st.columns([3, 1])
    fft_symbol_raw = fft_col_in.text_input(
        "FFT 標的代號",
        value="NVDA",
        key="fft_symbol_input",
        placeholder="NVDA / 2330.TW / 5274 / 00631L …"
    )
    do_fft = fft_col_btn.button(
        "⚡ 啟動週期引擎", type="primary",
        key="fft_scan", use_container_width=True
    )

    if do_fft:
        if not fft_symbol_raw.strip():
            st.warning("請輸入標的代號。")
        else:
            import re as _re
            import traceback as _tb

            # ── 台股後綴解析 ─────────────────────────────────────
            raw_sym  = fft_symbol_raw.strip().upper()
            base_sym = raw_sym.replace(".TW","").replace(".TWO","")
            is_tw    = bool(_re.fullmatch(r'\d{4,6}[A-Z0-9]*', base_sym))

            if is_tw and not (raw_sym.endswith(".TW") or raw_sym.endswith(".TWO")):
                fft_sym = None
                for sfx in [".TW", ".TWO"]:
                    try:
                        _p = yf.download(base_sym+sfx, period="1mo",
                                         progress=False, auto_adjust=True)
                        if isinstance(_p.columns, pd.MultiIndex):
                            _p.columns = _p.columns.get_level_values(0)
                        if "Close" in _p.columns and _p["Close"].dropna().shape[0] >= 5:
                            fft_sym = base_sym + sfx
                            break
                    except Exception:
                        continue
                if fft_sym is None:
                    st.error(f"❌ 無法解析台股代號 {raw_sym}（嘗試 .TW/.TWO 均無資料）。")
                    fft_sym = None
            else:
                fft_sym = raw_sym

            if fft_sym:
                with st.spinner(f"🧠 正在對 {fft_sym} 進行量子頻譜解碼..."):
                    try:
                        # ══════════════════════════════════════════════════════
                        # STEP 1: 取 3 年日K（足夠捕捉長週期，又不失近期結構）
                        # ══════════════════════════════════════════════════════
                        raw_dl = yf.download(fft_sym, period="3y",
                                             progress=False, auto_adjust=True)
                        if raw_dl.empty:
                            st.error(f"❌ 無法取得 {fft_sym} 資料。")
                        else:
                            if isinstance(raw_dl.columns, pd.MultiIndex):
                                raw_dl.columns = raw_dl.columns.get_level_values(0)
                            if "Close" not in raw_dl.columns:
                                st.error(f"❌ 缺少 Close 欄：{list(raw_dl.columns)}")
                            else:
                                close = raw_dl["Close"].dropna()
                                if len(close) < 150:
                                    st.error(f"❌ 資料不足 150 日（現有 {len(close)} 日）。")
                                else:
                                    # ══════════════════════════════════════════
                                    # STEP 2: 去趨勢 — 對數收益率（正確做法）
                                    # 原因：log return 是定態序列，去除了價格水準
                                    # 和指數成長趨勢，FFT 才能捕捉純週期成分。
                                    # price-MA 法會保留趨勢殘差，污染頻譜。
                                    # ══════════════════════════════════════════
                                    log_r = np.log(close / close.shift(1)).dropna()
                                    n     = len(log_r)
                                    dates = close.index[1:]  # align with log_r

                                    # ══════════════════════════════════════════
                                    # STEP 3: Hanning 窗 — 消除頻譜洩漏
                                    # 原因：有限長度信號的邊界不連續，會產生
                                    # 假頻率峰值。Hanning 窗讓兩端漸變到 0。
                                    # ══════════════════════════════════════════
                                    window    = np.hanning(n)
                                    windowed  = log_r.values * window
                                    # 補償窗函數的能量衰減（乘以 2/mean(window)）
                                    win_gain  = 2.0 / window.mean()

                                    # ══════════════════════════════════════════
                                    # STEP 4: FFT + 正頻率濾波 + 功率譜
                                    # ══════════════════════════════════════════
                                    fft_raw   = np.fft.rfft(windowed)
                                    freqs     = np.fft.rfftfreq(n, d=1)
                                    power     = (np.abs(fft_raw) * win_gain) ** 2

                                    # 濾窗：5-252 交易日（1週到1年）
                                    with np.errstate(divide='ignore', invalid='ignore'):
                                        cycle_len = np.where(freqs > 0, 1.0/freqs, 0)
                                    valid = (cycle_len >= 5) & (cycle_len <= 252)
                                    v_freqs = freqs[valid]
                                    v_power = power[valid]
                                    v_mags  = np.abs(fft_raw)[valid]
                                    v_len   = cycle_len[valid]

                                    if len(v_mags) < 3:
                                        st.warning("⚠️ 頻譜解析失敗，資料不足或市場近期高度隨機。")
                                    else:
                                        # ══════════════════════════════════════
                                        # STEP 5: 萃取 Top-5 週期（分頻段捕捉）
                                        # 短週期 5-30d: 月效應/機構月結
                                        # 中週期 30-90d: 季結/財報週期
                                        # 長週期 90-252d: 半年/年度週期
                                        # ══════════════════════════════════════
                                        top5_idx = np.argsort(v_power)[::-1][:5]
                                        cycles   = []
                                        for idx in top5_idx:
                                            freq_i   = v_freqs[idx]
                                            period_i = int(round(v_len[idx]))
                                            phase_i  = np.angle(fft_raw[valid][idx])
                                            amp_i    = v_mags[idx] * win_gain * 2.0 / n
                                            # 重建完整時間軸上的波形
                                            t_full   = np.arange(n)
                                            wave_i   = amp_i * np.cos(
                                                2*np.pi*freq_i*t_full + phase_i)
                                            # R²: 此單一週期解釋去趨勢序列的能力
                                            resid    = log_r.values - wave_i
                                            ss_res   = np.sum(resid**2)
                                            ss_tot   = np.sum((log_r.values - log_r.mean())**2)
                                            r2_i     = max(0, 1 - ss_res/ss_tot) if ss_tot>0 else 0

                                            # 分類
                                            if period_i <= 30:
                                                cat = "短週期"
                                            elif period_i <= 90:
                                                cat = "中週期"
                                            else:
                                                cat = "長週期"

                                            cycles.append({
                                                'period': period_i,
                                                'freq':   freq_i,
                                                'amp':    amp_i,
                                                'phase':  phase_i,
                                                'wave':   wave_i,
                                                'r2':     r2_i,
                                                'cat':    cat,
                                                'power':  float(v_power[idx]),
                                            })

                                        # ══════════════════════════════════════
                                        # STEP 6: 複合波 = Top-3 加權疊加
                                        # 加權依據：功率佔比（能量最強的成分貢獻最大）
                                        # ══════════════════════════════════════
                                        top3       = cycles[:3]
                                        total_pwr  = sum(c['power'] for c in top3)
                                        weights    = [c['power']/total_pwr for c in top3]
                                        composite  = sum(w*c['wave'] for w,c in zip(weights, top3))

                                        # 複合波整體 R²
                                        ss_res_comp = np.sum((log_r.values - composite)**2)
                                        r2_comp     = max(0, 1 - ss_res_comp/ss_tot) if ss_tot>0 else 0

                                        # ══════════════════════════════════════
                                        # STEP 7: 前向預測 30 交易日
                                        # 每個週期是確定性正弦波，可直接外推相位
                                        # ══════════════════════════════════════
                                        fwd_days  = 30
                                        t_fwd     = np.arange(n, n + fwd_days)
                                        fwd_comp  = sum(
                                            w * c['amp'] * np.cos(2*np.pi*c['freq']*t_fwd + c['phase'])
                                            for w, c in zip(weights, top3)
                                        )

                                        # 預測日期軸
                                        last_date  = dates[-1]
                                        fwd_dates  = pd.bdate_range(
                                            start=last_date + pd.Timedelta(days=1),
                                            periods=fwd_days
                                        )

                                        # ══════════════════════════════════════
                                        # STEP 8: 相位分析 — 距離下一波峰/波谷
                                        # ══════════════════════════════════════
                                        dom = cycles[0]
                                        dom_period = dom['period']

                                        # 在未來 2 個週期內找到最近的極值點
                                        t_future2  = np.arange(n, n + dom_period * 2)
                                        wave_fut2  = dom['amp'] * np.cos(
                                            2*np.pi*dom['freq']*t_future2 + dom['phase'])

                                        # 尋找第一個波峰 (local max) 和波谷 (local min)
                                        days_to_peak   = None
                                        days_to_trough = None
                                        for ti in range(1, len(wave_fut2)-1):
                                            if wave_fut2[ti] > wave_fut2[ti-1] and wave_fut2[ti] > wave_fut2[ti+1]:
                                                if days_to_peak is None:
                                                    days_to_peak = ti
                                            if wave_fut2[ti] < wave_fut2[ti-1] and wave_fut2[ti] < wave_fut2[ti+1]:
                                                if days_to_trough is None:
                                                    days_to_trough = ti

                                        # 當前相位（-1 到 +1）
                                        cur_phase_val = float(composite[-1])
                                        cur_amp       = float(max(abs(composite[-dom_period:]))) if dom_period <= len(composite) else float(dom['amp'])
                                        phase_pct     = cur_phase_val / cur_amp if cur_amp > 0 else 0
                                        phase_pct     = max(-1, min(1, phase_pct))
                                        phase_deg     = phase_pct * 180  # -180°到+180°

                                        # 週期共振判定（多週期同向）
                                        slopes = [
                                            float(c['wave'][-1] - c['wave'][-2])
                                            for c in top3
                                        ]
                                        n_up   = sum(1 for s in slopes if s > 0)
                                        n_dn   = sum(1 for s in slopes if s < 0)
                                        if n_up == 3:
                                            resonance = ("🔥 三週期共振向上", "#00FF7F", "HIGH")
                                        elif n_up == 2:
                                            resonance = ("⚡ 多數週期向上",   "#ADFF2F", "MED")
                                        elif n_dn == 3:
                                            resonance = ("💀 三週期共振向下", "#FF3131", "HIGH")
                                        elif n_dn == 2:
                                            resonance = ("🔴 多數週期向下",   "#FF9A3C", "MED")
                                        else:
                                            resonance = ("⚖️ 週期相互抵消",   "#888888", "LOW")

                                        # ══════════════════════════════════════
                                        # 圖表 1: 功率譜（頻率識別圖）
                                        # ══════════════════════════════════════
                                        fig_spec = go.Figure()
                                        # 背景功率譜
                                        fig_spec.add_trace(go.Scatter(
                                            x=v_len, y=v_power,
                                            mode='lines',
                                            line=dict(color='rgba(0,245,255,0.3)', width=1),
                                            fill='tozeroy',
                                            fillcolor='rgba(0,245,255,0.04)',
                                            name='功率譜',
                                            hovertemplate='週期 %{x:.0f}天 | 功率 %{y:.4f}<extra></extra>'
                                        ))
                                        # Top-5 週期標記
                                        clrs = ['#FFD700','#FF9A3C','#00FF7F','#B77DFF','#00F5FF']
                                        for ci, c in enumerate(cycles):
                                            fig_spec.add_vline(
                                                x=c['period'],
                                                line_color=clrs[ci],
                                                line_width=2 if ci==0 else 1,
                                                line_dash="solid" if ci==0 else "dot"
                                            )
                                            fig_spec.add_annotation(
                                                x=c['period'],
                                                y=0.95 - ci*0.15,
                                                yref='paper',
                                                text=f"C{ci+1}<br>{c['period']}d",
                                                showarrow=False,
                                                font=dict(color=clrs[ci], size=9,
                                                          family='JetBrains Mono'),
                                                bgcolor='rgba(0,0,0,0.5)',
                                                borderpad=2
                                            )
                                        # 頻段背景色
                                        fig_spec.add_vrect(x0=5,  x1=30,
                                            fillcolor='rgba(0,255,127,0.03)',
                                            line_width=0, annotation_text='短',
                                            annotation_font_color='rgba(0,255,127,0.3)',
                                            annotation_font_size=9)
                                        fig_spec.add_vrect(x0=30, x1=90,
                                            fillcolor='rgba(255,215,0,0.03)',
                                            line_width=0, annotation_text='中',
                                            annotation_font_color='rgba(255,215,0,0.3)',
                                            annotation_font_size=9)
                                        fig_spec.add_vrect(x0=90, x1=252,
                                            fillcolor='rgba(183,125,255,0.03)',
                                            line_width=0, annotation_text='長',
                                            annotation_font_color='rgba(183,125,255,0.3)',
                                            annotation_font_size=9)
                                        fig_spec.update_layout(
                                            template='plotly_dark', height=230,
                                            title=dict(
                                                text=f'⚡ {fft_sym}  週期功率譜（Hanning 窗 · 3年日K）',
                                                font=dict(size=13, color='#CDD', family='Rajdhani')
                                            ),
                                            xaxis=dict(title='週期長度 (交易日)', range=[5,252],
                                                       gridcolor='rgba(255,255,255,0.05)'),
                                            yaxis=dict(title='功率', gridcolor='rgba(255,255,255,0.05)'),
                                            plot_bgcolor='rgba(0,0,0,0)',
                                            paper_bgcolor='rgba(0,0,0,0)',
                                            showlegend=False,
                                            margin=dict(t=40, b=40, l=65, r=20),
                                        )
                                        st.plotly_chart(fig_spec, use_container_width=True)

                                        # ══════════════════════════════════════
                                        # 圖表 2: 複合波 + 前向預測（核心實戰圖）
                                        # ══════════════════════════════════════
                                        lookback    = min(120, len(composite))
                                        hist_dates  = dates[-lookback:]
                                        hist_comp   = composite[-lookback:]
                                        hist_logr   = log_r.values[-lookback:]

                                        fig_wave = go.Figure()

                                        # 真實對數收益率（雜訊信號）
                                        fig_wave.add_trace(go.Bar(
                                            x=hist_dates, y=hist_logr,
                                            marker_color=[
                                                'rgba(0,255,127,0.3)' if v>=0
                                                else 'rgba(255,49,49,0.3)'
                                                for v in hist_logr
                                            ],
                                            name='實際日收益率', yaxis='y1',
                                            hovertemplate='%{x|%Y-%m-%d}<br>%{y:.4f}<extra>收益率</extra>'
                                        ))

                                        # 歷史複合波
                                        fig_wave.add_trace(go.Scatter(
                                            x=hist_dates, y=hist_comp,
                                            mode='lines',
                                            line=dict(color='#00F5FF', width=2.5),
                                            name=f'複合波 (Top-3, R²={r2_comp:.3f})',
                                            hovertemplate='%{x|%Y-%m-%d}<br>%{y:.4f}<extra>複合波</extra>'
                                        ))

                                        # 前向預測（30日）—— 最核心的實戰輸出
                                        fig_wave.add_trace(go.Scatter(
                                            x=fwd_dates, y=fwd_comp,
                                            mode='lines',
                                            line=dict(color='#FFD700', width=2.5, dash='dash'),
                                            name='🎯 前向預測 (+30日)',
                                            hovertemplate='%{x|%Y-%m-%d}<br>%{y:.4f}<extra>預測</extra>'
                                        ))

                                        # 預測區間填色
                                        fig_wave.add_vrect(
                                            x0=str(fwd_dates[0].date()),
                                            x1=str(fwd_dates[-1].date()),
                                            fillcolor='rgba(255,215,0,0.04)',
                                            line_width=0,
                                            annotation_text='📡 預測區間',
                                            annotation_font_color='rgba(255,215,0,0.5)',
                                            annotation_font_size=9,
                                        )

                                        # 標記前向最高/最低點
                                        fwd_peak_idx   = int(np.argmax(fwd_comp))
                                        fwd_trough_idx = int(np.argmin(fwd_comp))
                                        fig_wave.add_annotation(
                                            x=fwd_dates[fwd_peak_idx],
                                            y=float(fwd_comp[fwd_peak_idx]),
                                            text=f"▲ +{fwd_peak_idx+1}天",
                                            showarrow=True, arrowhead=2,
                                            arrowcolor='#00FF7F',
                                            font=dict(color='#00FF7F', size=10),
                                            bgcolor='rgba(0,0,0,0.6)', borderpad=3
                                        )
                                        fig_wave.add_annotation(
                                            x=fwd_dates[fwd_trough_idx],
                                            y=float(fwd_comp[fwd_trough_idx]),
                                            text=f"▼ +{fwd_trough_idx+1}天",
                                            showarrow=True, arrowhead=2,
                                            arrowcolor='#FF6B6B',
                                            font=dict(color='#FF6B6B', size=10),
                                            bgcolor='rgba(0,0,0,0.6)', borderpad=3
                                        )

                                        # 零軸
                                        fig_wave.add_hline(
                                            y=0,
                                            line_color='rgba(255,255,255,0.15)',
                                            line_dash='dot', line_width=1
                                        )

                                        fig_wave.update_layout(
                                            template='plotly_dark', height=420,
                                            title=dict(
                                                text=(
                                                    f'🎯 {fft_sym}  複合週期波 + 30日前向預測'
                                                    f'  |  複合R²={r2_comp:.3f}'
                                                    f'  |  {resonance[0]}'
                                                ),
                                                font=dict(size=13, color='#CDD', family='Rajdhani')
                                            ),
                                            xaxis=dict(gridcolor='rgba(255,255,255,0.04)'),
                                            yaxis=dict(
                                                title='日對數收益率',
                                                gridcolor='rgba(255,255,255,0.04)'
                                            ),
                                            plot_bgcolor='rgba(0,0,0,0)',
                                            paper_bgcolor='rgba(0,0,0,0)',
                                            hovermode='x unified',
                                            barmode='overlay',
                                            legend=dict(
                                                orientation='h', y=1.02,
                                                font=dict(color='#AAB', size=10)
                                            ),
                                            margin=dict(t=55, b=40, l=65, r=20),
                                        )
                                        st.plotly_chart(fig_wave, use_container_width=True)

                                        # ══════════════════════════════════════
                                        # KPI 儀表板
                                        # ══════════════════════════════════════
                                        st.markdown("##### 📊 量子週期戰略儀表板")

                                        k1, k2, k3, k4, k5 = st.columns(5)
                                        k1.metric(
                                            "主週期 C1",
                                            f"{cycles[0]['period']} 交易日",
                                            f"≈ {cycles[0]['period']/21:.1f} 個月 · {cycles[0]['cat']}"
                                        )
                                        k2.metric(
                                            "C1 可靠度 R²",
                                            f"{cycles[0]['r2']:.3f}",
                                            "≥0.03 有效" if cycles[0]['r2'] >= 0.03 else "< 0.03 弱訊號",
                                            delta_color="normal" if cycles[0]['r2'] >= 0.03 else "inverse"
                                        )
                                        k3.metric(
                                            "複合波 R²",
                                            f"{r2_comp:.3f}",
                                            "Top-3週期解釋力"
                                        )
                                        k4.metric(
                                            "預測波峰",
                                            f"+{fwd_peak_idx+1} 交易日",
                                            f"複合波最高點"
                                        )
                                        k5.metric(
                                            "預測波谷",
                                            f"+{fwd_trough_idx+1} 交易日",
                                            f"複合波最低點"
                                        )

                                        # ══════════════════════════════════════
                                        # Top-5 週期明細表
                                        # ══════════════════════════════════════
                                        st.markdown(
                                            '<div style="font-family:\'JetBrains Mono\','
                                            'monospace;font-size:9px;color:rgba(0,245,255,.35);'
                                            'letter-spacing:3px;text-transform:uppercase;'
                                            'margin:16px 0 6px;">🔬 Top-5 週期解析</div>',
                                            unsafe_allow_html=True
                                        )
                                        total_top5_pwr = sum(c['power'] for c in cycles)
                                        rows = []
                                        for ci, c in enumerate(cycles):
                                            cur_slope = float(c['wave'][-1] - c['wave'][-2])
                                            direction = "⬆ 上升" if cur_slope > 0 else "⬇ 下降"
                                            pwr_pct   = c['power'] / total_top5_pwr * 100 if total_top5_pwr > 0 else 0
                                            rows.append({
                                                '#':     f"C{ci+1}",
                                                '週期':  f"{c['period']} 日",
                                                '分類':  c['cat'],
                                                '功率佔比': f"{pwr_pct:.1f}%",
                                                '振幅':  f"{c['amp']*100:.4f}%",
                                                'R²':    f"{c['r2']:.4f}",
                                                '當前方向': direction,
                                            })
                                        cycle_df = pd.DataFrame(rows)
                                        st.dataframe(
                                            cycle_df,
                                            use_container_width=True,
                                            hide_index=True
                                        )

                                        # ══════════════════════════════════════
                                        # 週期共振 + Valkyrie 戰術判斷
                                        # ══════════════════════════════════════
                                        st.divider()

                                        # 共振橫幅
                                        st.markdown(
                                            f'<div style="padding:14px 20px;'
                                            f'background:rgba(0,0,0,0.3);'
                                            f'border:1px solid {resonance[1]}44;'
                                            f'border-left:4px solid {resonance[1]};'
                                            f'border-radius:0 10px 10px 0;margin-bottom:14px;">'
                                            f'<span style="font-family:\'JetBrains Mono\','
                                            f'monospace;font-size:11px;color:{resonance[1]};'
                                            f'letter-spacing:2px;">週期共振強度 [{resonance[2]}]'
                                            f'</span>'
                                            f'<span style="font-family:\'Rajdhani\',sans-serif;'
                                            f'font-size:18px;font-weight:700;color:#FFF;'
                                            f'margin-left:16px;">{resonance[0]}</span>'
                                            f'</div>',
                                            unsafe_allow_html=True
                                        )

                                        # Valkyrie 戰術判斷（整合相位 + 前向預測 + 共振）
                                        is_near_trough  = fwd_trough_idx < fwd_peak_idx and fwd_trough_idx <= 10
                                        is_near_peak    = fwd_peak_idx  < fwd_trough_idx and fwd_peak_idx  <= 10
                                        is_upward_comp  = float(fwd_comp[0]) < float(fwd_comp[min(5, len(fwd_comp)-1)])
                                        is_downward_comp= not is_upward_comp

                                        if resonance[2] in ("HIGH", "MED") and n_up >= 2 and is_upward_comp:
                                            st.success(
                                                f"⚡ [Valkyrie AI · 週期引擎] 多週期共振向上，且複合波正處於上升段。\n\n"
                                                f"📌 **主週期 C1 = {cycles[0]['period']} 交易日**（{cycles[0]['cat']}），"
                                                f"前向預測顯示複合波峰在 **+{fwd_peak_idx+1} 個交易日後**到達。\n\n"
                                                f"🎯 **操作建議**：{resonance[0]}，{3 - n_up} 個週期仍逆向，"
                                                f"但多數力量支撐上行。建議在 +{fwd_trough_idx+1} 日附近的回落點積極佈局，"
                                                f"目標 +{fwd_peak_idx+1} 日前出場。\n\n"
                                                f"📐 複合波可靠度 R²={r2_comp:.3f}（"
                                                f"{'高可信' if r2_comp >= 0.05 else '中等可信' if r2_comp >= 0.02 else '供參考'}）。"
                                            )
                                        elif resonance[2] in ("HIGH", "MED") and n_dn >= 2 and is_downward_comp:
                                            st.error(
                                                f"🔴 [Valkyrie AI · 週期引擎] 多週期共振向下，複合波持續下行。\n\n"
                                                f"📌 **主週期 C1 = {cycles[0]['period']} 交易日**（{cycles[0]['cat']}），"
                                                f"前向預測顯示複合波谷在 **+{fwd_trough_idx+1} 個交易日後**到達。\n\n"
                                                f"🎯 **操作建議**：{resonance[0]}，下行動能強勁，"
                                                f"嚴禁逆勢做多。等待複合波谷後（約 +{fwd_trough_idx+1} 日）"
                                                f"觀察底部訊號再考慮介入。\n\n"
                                                f"⚠️ C1 可靠度 R²={cycles[0]['r2']:.3f}，"
                                                f"複合 R²={r2_comp:.3f}。"
                                            )
                                        elif is_near_trough and not (n_dn >= 2):
                                            st.warning(
                                                f"⚖️ [Valkyrie AI · 週期引擎] 複合波即將在 "
                                                f"**+{fwd_trough_idx+1} 個交易日**觸及局部波谷，隨後反轉向上。\n\n"
                                                f"📌 **主週期 {cycles[0]['period']} 日**，週期共振訊號為：{resonance[0]}。\n\n"
                                                f"🎯 **操作建議**：等待 {fwd_trough_idx+1} 天後的底部確認訊號（放量止跌 / RSI 超賣），"
                                                f"屆時搭配 5.1 籌碼信號進場，預計 +{fwd_peak_idx+1} 日前達到峰值。"
                                            )
                                        else:
                                            next_event = (
                                                f"波峰 +{fwd_peak_idx+1}日" if fwd_peak_idx < fwd_trough_idx
                                                else f"波谷 +{fwd_trough_idx+1}日"
                                            )
                                            st.info(
                                                f"⚖️ [Valkyrie AI · 週期引擎] 週期方向混沌，多空力量相互抵消。\n\n"
                                                f"📌 **主週期 {cycles[0]['period']} 日**，"
                                                f"前向最近極值：**{next_event}**。\n\n"
                                                f"🎯 **操作建議**：當前不宜主動進場。等待週期共振訊號出現"
                                                f"（三週期同向）後再動作。可在 6.2 上帝軌道確認長期趨勢位置。\n\n"
                                                f"複合波 R²={r2_comp:.3f}（周期解釋力偏低，當前市場偏隨機）。"
                                            )

                    except Exception as _e:
                        st.error(f"週期引擎運算失敗: {_e}")
                        with st.expander("🔍 Debug Traceback"):
                            st.code(_tb.format_exc())







# ═══════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════
# SECTION 6.2 — 個股深鑽 V400 (CROWN JEWEL — FULLY ENHANCED)
# ═══════════════════════════════════════════════════════════════

def _s62_geo_interpretation_panel(geo, ticker_in, price):
    """幾何解讀面板 — 將原始角度翻譯成人類語言"""
    a35 = geo['35Y']['angle'];  a10 = geo['10Y']['angle']
    a5  = geo['5Y']['angle'];   a3y = geo['3Y']['angle']
    a1  = geo['1Y']['angle'];   a6  = geo['6M']['angle']
    a3  = geo['3M']['angle'];   acc = geo['acceleration']
    r2_1 = geo['1Y']['r2'];     r2_3 = geo['3M']['r2']
    phx = geo['phoenix_signal']

    consistency_score = sum([a35>0, a10>0, a5>0, a3y>0, a1>0, a6>0, a3>0])
    trend_divergence  = abs(a1 - a3)
    long_short_gap    = a10 - a3
    momentum_ratio    = (a3 / a1) if a1 != 0 else 0

    st.markdown("""
    <div style="font-family:'JetBrains Mono',monospace;font-size:9px;
    color:rgba(0,245,255,.35);letter-spacing:4px;text-transform:uppercase;
    margin:16px 0 8px;">
    ◈ 幾何解讀矩陣 — Geometry Interpretation Matrix
    </div>""", unsafe_allow_html=True)

    ka, kb, kc, kd = st.columns(4)

    cs_color = "#00FF7F" if consistency_score >= 6 else ("#FFD700" if consistency_score >= 4 else "#FF6B6B")
    cs_label = "全週期共振" if consistency_score == 7 else (
               "強勢共振" if consistency_score >= 5 else (
               "部分背離" if consistency_score >= 3 else "多空混沌"))
    ka.markdown(f"""
    <div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);
    border-radius:10px;padding:12px;text-align:center;">
    <div style="font-size:9px;color:rgba(160,176,208,0.4);letter-spacing:2px;margin-bottom:4px;">趨勢一致性</div>
    <div style="font-size:28px;font-weight:900;color:{cs_color};line-height:1.1;">{consistency_score}<span style="font-size:14px;opacity:0.5;">/7</span></div>
    <div style="font-size:10px;color:{cs_color};margin-top:4px;">{cs_label}</div>
    </div>""", unsafe_allow_html=True)

    mr_color = "#00FF7F" if momentum_ratio > 1.2 else ("#FF6B6B" if momentum_ratio < 0 else "#FFD700")
    mr_label = "加速上攻" if momentum_ratio > 1.2 else (
               "加速下行" if momentum_ratio < -0.5 else (
               "動能減退" if 0 < momentum_ratio < 0.8 else "方向背離" if momentum_ratio < 0 else "正常巡航"))
    kb.markdown(f"""
    <div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);
    border-radius:10px;padding:12px;text-align:center;">
    <div style="font-size:9px;color:rgba(160,176,208,0.4);letter-spacing:2px;margin-bottom:4px;">動能比率 3M/1Y</div>
    <div style="font-size:28px;font-weight:900;color:{mr_color};line-height:1.1;">{momentum_ratio:+.2f}<span style="font-size:12px;opacity:0.5;">x</span></div>
    <div style="font-size:10px;color:{mr_color};margin-top:4px;">{mr_label}</div>
    </div>""", unsafe_allow_html=True)

    div_color = "#FF9A3C" if trend_divergence > 20 else ("#FFD700" if trend_divergence > 10 else "#00FF7F")
    div_label = "高度背離⚠️" if trend_divergence > 20 else ("輕微背離" if trend_divergence > 10 else "高度一致✅")
    kc.markdown(f"""
    <div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);
    border-radius:10px;padding:12px;text-align:center;">
    <div style="font-size:9px;color:rgba(160,176,208,0.4);letter-spacing:2px;margin-bottom:4px;">短長背離指數</div>
    <div style="font-size:28px;font-weight:900;color:{div_color};line-height:1.1;">{trend_divergence:.1f}<span style="font-size:12px;opacity:0.5;">°</span></div>
    <div style="font-size:10px;color:{div_color};margin-top:4px;">{div_label}</div>
    </div>""", unsafe_allow_html=True)

    lsg_color = "#FF9A3C" if long_short_gap > 15 else ("#00BFFF" if long_short_gap < -15 else "#D3D3D3")
    lsg_label = "長強短弱→高位" if long_short_gap > 15 else ("長弱短強→反彈" if long_short_gap < -15 else "長短一致")
    kd.markdown(f"""
    <div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);
    border-radius:10px;padding:12px;text-align:center;">
    <div style="font-size:9px;color:rgba(160,176,208,0.4);letter-spacing:2px;margin-bottom:4px;">10Y−3M 差值</div>
    <div style="font-size:28px;font-weight:900;color:{lsg_color};line-height:1.1;">{long_short_gap:+.1f}<span style="font-size:12px;opacity:0.5;">°</span></div>
    <div style="font-size:10px;color:{lsg_color};margin-top:4px;">{lsg_label}</div>
    </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    with st.expander("📖 幾何指標完整解讀說明（點此展開）", expanded=False):
        st.markdown("""
**▸ 趨勢角度（°）是什麼？**
將股價取自然對數後做線性回歸，斜率換算成角度。
- **> 45°** = 極強上升通道（年化回報通常 > 50%）
- **20°–45°** = 健康上升（年化 15%–50%）
- **0°–20°** = 弱上升或橫盤（年化 0%–15%）
- **< 0°** = 下降趨勢，角度越負越危險

**▸ R²（線性度）是什麼？**
趨勢的「可預測性」。R²=1.0 表示完全線性，R²=0 表示完全混沌。
- **> 0.90** = 機構資金流入，趨勢高度可靠
- **0.70–0.90** = 趨勢存在但有波動
- **< 0.50** = 震盪行情，趨勢角度意義有限

**▸ 加速度（Acceleration）是什麼？**
= 3M角度 − 1Y角度。衡量近期動能是否在增強。
- **> +15°** = 動能急速加速，可能過熱
- **0°–15°** = 溫和加速，健康
- **< 0°** = 動能衰退，需謹慎

**▸ 動能比率（Momentum Ratio）是什麼？**
= 3M角度 / 1Y角度。
- **> 1.2** = 近期突破加速，短多訊號
- **0.8–1.2** = 正常運行
- **< 0** = 長多短空，趨勢背離，危險訊號

**▸ Phoenix 訊號是什麼？**
= 10Y角度 < 0 且 6M角度 > 25°。長期趨勢疲弱但短期突然爆發。
高風險高報酬，可能真正反轉，也可能死貓反彈，需配合基本面驗證。

**▸ 趨勢一致性評分（0–7）**
7個時間窗口中，有幾個角度為正。
- **7/7** = 全週期共振多頭
- **5–6/7** = 強勢，有個別分歧
- **3–4/7** = 多空拉鋸
- **< 3/7** = 空頭主導
        """)

    if a1 > 30 and acc > 15 and r2_1 > 0.8:
        ctx_icon, ctx_color, ctx_txt, ctx_detail = (
            "🚀", "#00FF7F", "上升加速期",
            f"趨勢強勁且加速（1Y={a1:+.1f}°，加速度={acc:+.1f}°，R²={r2_1:.3f}）。主要風險是過熱後的急回調。策略：追趨勢但設緊停損。"
        )
    elif a1 > 15 and -10 < acc < 10:
        ctx_icon, ctx_color, ctx_txt, ctx_detail = (
            "📈", "#ADFF2F", "穩定上升期",
            f"趨勢健康，加速度平穩（1Y={a1:+.1f}°，加速度={acc:+.1f}°）。適合持倉。策略：回調至趨勢線附近加碼，不追高。"
        )
    elif -10 < a1 < 15 and abs(acc) < 10:
        ctx_icon, ctx_color, ctx_txt, ctx_detail = (
            "⚖️", "#FFD700", "橫盤整理期",
            f"方向不明（1Y={a1:+.1f}°，一致性={consistency_score}/7）。等待突破前不宜重倉。策略：觀望，等待加速度轉向。"
        )
    elif a1 < 0 and acc < -10:
        ctx_icon, ctx_color, ctx_txt, ctx_detail = (
            "💀", "#FF3131", "下跌加速期",
            f"趨勢負向且惡化（1Y={a1:+.1f}°，加速度={acc:+.1f}°）。任何反彈都是逃命機會。策略：清倉或做空。"
        )
    elif phx:
        ctx_icon, ctx_color, ctx_txt, ctx_detail = (
            "🔥", "#FF6347", "Phoenix 反轉期",
            f"長期趨勢疲弱但短期動能急升（10Y={a10:+.1f}°，6M={a6:+.1f}°）。高風險高報酬。必須配合基本面驗證才敢進場。"
        )
    else:
        ctx_icon, ctx_color, ctx_txt, ctx_detail = (
            "🌪️", "#B0B0B0", "複雜混沌期",
            f"多空訊號混雜（一致性={consistency_score}/7，加速度={acc:+.1f}°）。低倉位或觀望。"
        )

    st.markdown(f"""
    <div style="background:rgba(255,255,255,0.02);border:1px solid {ctx_color}33;
    border-left:4px solid {ctx_color};border-radius:0 10px 10px 0;padding:14px 18px;margin:10px 0;">
    <div style="display:flex;align-items:center;gap:10px;">
    <span style="font-size:22px;">{ctx_icon}</span>
    <div>
    <div style="font-family:'JetBrains Mono',monospace;font-size:11px;font-weight:700;
    color:{ctx_color};letter-spacing:2px;text-transform:uppercase;">{ctx_txt}</div>
    <div style="font-size:12px;color:rgba(200,210,220,0.7);margin-top:3px;">{ctx_detail}</div>
    </div></div></div>""", unsafe_allow_html=True)


def _s62():
    st.markdown('<div class="t6-sec-head" style="--sa:#FFD700"><div class="t6-sec-num">6.2</div><div><div class="t6-sec-title" style="color:#FFD700;">個股深鑽 V400 — 幾何解讀 + 情境判定 + 法庭級分析提示詞</div><div class="t6-sec-sub">Deep Dive · Interpretation · Tribunal Prompt Engine · God Orbit</div></div></div>', unsafe_allow_html=True)

    c_in, c_btn = st.columns([4, 1])
    ticker_in = c_in.text_input(
        "🎯 輸入代號（支援台股上市/上櫃/美股）",
        value=st.session_state.get('deep_ticker', 'NVDA'),
        key="deep_ticker_v300"
    ).strip().upper()

    if c_btn.button("🚀 啟動深鑽", type="primary", use_container_width=True, key="btn_deep_v300"):
        with st.spinner(f"▶ 解碼 {ticker_in} 全維度幾何…"):
            geo    = compute_7d_geometry(ticker_in)
            rating = titan_rating_system(geo) if geo else ("N/A", "N/A", "N/A", "#808080")
        st.session_state['deep_geo']    = geo
        st.session_state['deep_rating'] = rating
        st.session_state['deep_ticker'] = ticker_in
        st.session_state.pop('valkyrie_report_v300', None)
        st.session_state.pop('battle_prompt_v300',   None)

    if 'deep_geo' not in st.session_state or st.session_state.get('deep_ticker') != ticker_in:
        st.info("ℹ️ 請輸入代號後點擊「啟動深鑽」。")
        return

    geo    = st.session_state['deep_geo']
    rating = st.session_state['deep_rating']
    lvl, name, desc, color = rating

    if geo is None:
        st.error(f"❌ 無法取得 {ticker_in} 的歷史數據，請確認代號是否正確。")
        return

    # ── 信評徽章 ──
    st.markdown(f'<div class="rank-badge-wrap"><div class="rank-badge" style="background:linear-gradient(135deg,{color} 0%,#333 50%,{color} 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">{lvl}</div><div class="rank-badge-name" style="color:{color};">{name}</div><div class="rank-badge-desc">{desc}</div></div>', unsafe_allow_html=True)

    _render_spectrum(geo, ticker_in)

    acc = geo['acceleration']
    phx = geo['phoenix_signal']
    r2_1 = geo['1Y']['r2']

    c1, c2, c3 = st.columns(3)
    acc_c = "#00FF7F" if acc > 10 else ("#FFD700" if acc > 0 else "#FF6B6B")
    c1.markdown(f'<div style="text-align:center;padding:14px;background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);border-radius:12px;"><div style="font-family:var(--f-m);font-size:9px;color:rgba(160,176,208,0.4);letter-spacing:3px;margin-bottom:6px;">ACCELERATION (G-FORCE)</div><div style="font-family:var(--f-i);font-size:44px;font-weight:900;color:{acc_c};line-height:1;">{acc:+.1f}°</div><div style="font-size:10px;color:{acc_c};margin-top:4px;">{"動能急速加速 🚀" if acc>15 else ("溫和加速" if acc>0 else ("動能衰退 ⚠️" if acc>-15 else "動能崩潰 💀"))}</div></div>', unsafe_allow_html=True)

    phx_c = "#FF6347" if phx else "rgba(100,115,135,0.3)"
    c2.markdown(f'<div style="text-align:center;padding:14px;background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);border-radius:12px;"><div style="font-family:var(--f-m);font-size:9px;color:rgba(160,176,208,0.4);letter-spacing:3px;margin-bottom:6px;">PHOENIX SIGNAL</div><div style="font-family:var(--f-i);font-size:22px;font-weight:800;color:{phx_c};line-height:1.3;">{"🔥 TRIGGERED" if phx else "— INACTIVE"}</div><div style="font-size:10px;color:{phx_c};margin-top:4px;">{"長空短多逆轉！需基本面驗證" if phx else "長短趨勢尚未出現逆轉格局"}</div></div>', unsafe_allow_html=True)

    r2_c = "#00FF7F" if r2_1 > 0.9 else ("#FFD700" if r2_1 > 0.7 else "#FF9A3C")
    c3.markdown(f'<div style="text-align:center;padding:14px;background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);border-radius:12px;"><div style="font-family:var(--f-m);font-size:9px;color:rgba(160,176,208,0.4);letter-spacing:3px;margin-bottom:6px;">1Y R² 線性度</div><div style="font-family:var(--f-i);font-size:44px;font-weight:900;color:{r2_c};line-height:1;">{r2_1:.3f}</div><div style="font-size:10px;color:{r2_c};margin-top:4px;">{"趨勢極可靠 ✅" if r2_1>0.9 else ("趨勢可靠" if r2_1>0.7 else "趨勢震盪")}</div></div>', unsafe_allow_html=True)

    # ── 幾何解讀矩陣 ──
    st.divider()
    price_now = 0.0
    dp_data = st.session_state.get('daily_price_data', {}).get(ticker_in)
    if dp_data is not None and not dp_data.empty:
        price_now = float(dp_data['Close'].iloc[-1])
    _s62_geo_interpretation_panel(geo, ticker_in, price_now)

    # ── 圖表 Tabs ──
    st.divider()
    tab_radar, tab_orbit, tab_monthly = st.tabs(["🕸️ 7D 雷達圖", "🌌 上帝軌道", "📊 月K線圖"])
    with tab_radar:
        _render_radar(geo, ticker_in)
    with tab_orbit:
        st.caption("📡 對數線性回歸：股價在長期成長通道中的位置。藍線=趨勢通道，綠線=實際價格。")
        _render_god_orbit(ticker_in)
    with tab_monthly:
        st.caption("🕯️ 月K線 + MA87（橘）+ MA284（藍）。長期均線方向代表資金長期趨勢。")
        _render_monthly_chart(ticker_in)

    # ── 智能連結 ──
    st.divider()
    with st.expander("🔗 智能快捷連結（9 個必備研究資源）", expanded=False):
        tk_clean = ticker_in.replace('.TW', '').replace('.TWO', '')
        lc1, lc2, lc3 = st.columns(3)
        with lc1:
            st.markdown(f"**[📈 TradingView](https://www.tradingview.com/chart/?symbol={ticker_in})** — 技術圖表")
            st.markdown(f"**[📊 Finviz](https://finviz.com/quote.ashx?t={ticker_in})** — 美股看板")
            st.markdown(f"**[📉 StockCharts](https://stockcharts.com/h-sc/ui?s={ticker_in})** — 技術分析")
        with lc2:
            if ticker_in.endswith(('.TW', '.TWO')):
                st.markdown(f"**[🇹🇼 Yahoo 台股](https://tw.stock.yahoo.com/quote/{tk_clean})** — 即時報價")
                st.markdown(f"**[📰 鉅亨網](https://invest.cnyes.com/twstock/TWS/{tk_clean})** — 台股新聞")
                st.markdown(f"**[💰 Goodinfo](https://goodinfo.tw/tw/StockDetail.asp?STOCK_ID={tk_clean})** — 財務指標")
            else:
                st.markdown(f"**[💹 Yahoo Finance](https://finance.yahoo.com/quote/{ticker_in})** — 財務報表")
                st.markdown(f"**[📋 SEC Edgar](https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={ticker_in})** — 官方文件")
                st.markdown(f"**[🔬 Macrotrends](https://www.macrotrends.net/stocks/charts/{ticker_in.split('.')[0]})** — 長期財務圖表")
        with lc3:
            st.markdown(f"**[🏛️ 公開資訊觀測站](https://mops.twse.com.tw/mops/web/t05st03)** — 官方財報")
            st.markdown(f"**[🤖 AlphaMemo](https://www.alphamemo.ai/free-transcripts)** — AI 法說逐字稿")
            if ticker_in.endswith(('.TW', '.TWO')):
                st.markdown(f"**[📌 TWSE](https://www.twse.com.tw/zh/trading/historical/stock-day.html)** — 歷史成交")
            else:
                st.markdown(f"**[📌 Seeking Alpha](https://seekingalpha.com/symbol/{ticker_in})** — 深度研究報告")

    # ════════════════════════════════════════════════════
    # 戰略工廠 V400 — Tribunal Prompt Engine
    # ════════════════════════════════════════════════════
    st.divider()
    st.markdown("""
    <div style="font-family:'JetBrains Mono',monospace;font-size:9px;
    color:rgba(255,215,0,.5);letter-spacing:4px;text-transform:uppercase;margin-bottom:4px;">
    ◈ 戰略工廠 V400 — Tribunal Prompt Engine
    </div>
    <div style="font-size:14px;font-weight:700;color:#FFD700;margin-bottom:6px;">
    🏭 AI 法庭級分析提示詞生成器
    </div>
    <div style="font-size:11px;color:rgba(180,190,210,0.65);line-height:1.7;margin-bottom:14px;">
    <b>V400 核心升級：</b>從「戲劇化角色扮演」→「專業法庭審訊」格式。<br>
    每位分析師有<b>強制量化輸出子項目</b>（代碼 [Q1]–[V5]），AI 不得跳過、不得模糊，
    必須給出具體數字、明確方向判斷，並逐一反駁上一位分析師的論點。<br>
    裁判官最後輸出的「<b>一句定論</b>」是整份報告的錨點，也是最重要的輸出。
    </div>""", unsafe_allow_html=True)

    MODE_CONFIGS = {
        "⚖️ 完整法庭": {
            "mode": "full_tribunal",
            "desc": "5 位專家證人完整出庭，量化審訊 + 逐一反駁 + 最終裁決。最深度、最全面。",
            "icon": "⚖️", "color": "#FFD700",
        },
        "🚀 多頭論文": {
            "mode": "bull_thesis",
            "desc": "從量化/基本面/創新 3 個維度建構最強多頭投資論文，含 12M 價格目標。",
            "icon": "🚀", "color": "#00FF7F",
        },
        "🐻 空頭論文": {
            "mode": "bear_thesis",
            "desc": "從量化/估值/宏觀 3 個維度尋找致命弱點，含做空進場邏輯與目標。",
            "icon": "🐻", "color": "#FF6B6B",
        },
        "💀 極限壓測": {
            "mode": "stress_test",
            "desc": "模擬 4 種極端情境（崩盤/升息/顛覆/高管出逃），評估標的生存能力。",
            "icon": "💀", "color": "#FF9A3C",
        },
        "⚡ 快速裁決": {
            "mode": "quick_verdict",
            "desc": "Apex 裁判官獨自審閱所有數據，500-800 字直接輸出操作指令。最快速。",
            "icon": "⚡", "color": "#00BFFF",
        },
    }

    st.markdown("**📌 選擇分析模式：**")
    mode_cols = st.columns(len(MODE_CONFIGS))
    selected_mode_key = st.session_state.get('s62_mode_key', "⚖️ 完整法庭")
    for i, (mk, mv) in enumerate(MODE_CONFIGS.items()):
        with mode_cols[i]:
            is_sel = (mk == selected_mode_key)
            bdr = f"border:2px solid {mv['color']};" if is_sel else "border:1px solid rgba(255,255,255,0.08);"
            bg  = "background:rgba(255,255,255,0.04);" if is_sel else "background:rgba(255,255,255,0.015);"
            st.markdown(f"""<div style="{bg}{bdr}border-radius:10px;padding:10px 6px;text-align:center;">
            <div style="font-size:18px;">{mv['icon']}</div>
            <div style="font-size:10px;font-weight:700;color:{mv['color']};margin-top:4px;">{mk}</div>
            </div>""", unsafe_allow_html=True)
            if st.button(mk, key=f"mode_btn_62_{i}", use_container_width=True):
                st.session_state['s62_mode_key'] = mk
                st.rerun()

    selected_mode_cfg  = MODE_CONFIGS.get(selected_mode_key, MODE_CONFIGS["⚖️ 完整法庭"])
    selected_mode_code = selected_mode_cfg["mode"]
    st.caption(f"🎯 **{selected_mode_key}** — {selected_mode_cfg['desc']}")

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    col_params, col_output = st.columns([1, 2])

    with col_params:
        st.markdown("**⚙️ 情報注入與參數**")

        has_valkyrie   = 'valkyrie_report_v300' in st.session_state
        has_principles = len(st.session_state.get('principles_v300_msel', [])) > 0
        has_note       = bool(st.session_state.get('note_v300_ta', '').strip())
        data_score     = sum([bool(geo), has_valkyrie, has_principles, has_note])
        score_color    = "#00FF7F" if data_score == 4 else ("#FFD700" if data_score >= 2 else "#FF9A3C")
        score_label    = "資料充足，分析品質最佳 🎯" if data_score == 4 else (
                         "基本充足" if data_score >= 2 else "建議補充瓦爾基里情報")
        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.02);border:1px solid {score_color}33;
        border-radius:8px;padding:10px 14px;margin-bottom:10px;">
        <div style="font-size:9px;color:rgba(160,176,208,0.4);letter-spacing:2px;margin-bottom:4px;">📊 提示詞資料品質</div>
        <div style="display:flex;align-items:center;gap:8px;">
        <div style="font-size:24px;font-weight:900;color:{score_color};">{data_score}<span style="font-size:12px;opacity:0.5;">/4</span></div>
        <div style="font-size:10px;color:{score_color};">{score_label}</div>
        </div>
        <div style="display:flex;gap:4px;margin-top:6px;">
        {''.join([f'<div style="flex:1;height:4px;background:{"#00FF7F" if j<data_score else "rgba(255,255,255,0.1)"};border-radius:2px;"></div>' for j in range(4)])}
        </div>
        </div>""", unsafe_allow_html=True)

        with st.expander("🕵️ 瓦爾基里情報注入", expanded=True):
            st.caption("**Step 1**：自動抓取財務數據與新聞 | **Step 2**：可手動補充")
            if st.button("🤖 啟動瓦爾基里 Auto-Fetch", type="primary", use_container_width=True, key="btn_valk_v300"):
                with st.spinner("🤖 瓦爾基里正在抓取情報..."):
                    agency = TitanIntelAgency()
                    st.session_state['valkyrie_report_v300'] = agency.fetch_full_report(ticker_in)
                st.toast("✅ 情報抓取完成！", icon="🎯")
                st.rerun()
            if 'valkyrie_report_v300' in st.session_state:
                intel_text = st.text_area(
                    "📝 瓦爾基里情報（可編輯補充）",
                    value=st.session_state['valkyrie_report_v300'],
                    height=220, key="intel_v300_valk"
                )
            else:
                intel_text = st.text_area(
                    "📝 手動貼上情報（法說摘要/財報數字/新聞）",
                    height=130,
                    placeholder="例如：\n- 毛利率 73.5%（YoY +2.1%）\n- Data Center 營收 $18.4B（QoQ +17%）\n- 管理層 2025 指引上調",
                    key="intel_v300_manual"
                )
            uploaded = st.file_uploader(
                "📎 上傳文件（PDF/xlsx/docx/txt）",
                type=['pdf', 'xlsx', 'xls', 'docx', 'doc', 'txt'],
                accept_multiple_files=True, key="intel_files_v300"
            )
            uploaded_extra = ""
            if uploaded:
                for uf in uploaded:
                    uploaded_extra += f"\n[上傳檔案: {uf.name}]\n"
                    st.caption(f"✅ 已附加: {uf.name}")

        with st.expander("🎯 第一性原則（20 條）", expanded=False):
            st.caption("選後每位分析師都必須回答。建議選 2–4 條。")
            sel_p = st.multiselect(
                "選擇第一性原則",
                FIRST_PRINCIPLES_20, default=[],
                key="principles_v300_msel"
            )

        with st.expander("✍️ 統帥特別指令", expanded=False):
            st.caption("最高優先級指令，裁判官必須遵守。")
            commander_note = st.text_area(
                "特別指令",
                height=100,
                placeholder="例如：\n- 重點分析 AI 算力的長期護城河\n- 假設 TSMC 限制出貨，影響有多大？\n- 現在離 52 週高點多遠？",
                key="note_v300_ta"
            )

    with col_output:
        st.markdown("**📋 提示詞生成與輸出**")

        full_intel = intel_text if 'intel_text' in dir() else ""
        if 'uploaded_extra' in dir() and uploaded_extra:
            full_intel += uploaded_extra
        if 'commander_note' not in dir():
            commander_note = ""
        if 'sel_p' not in dir():
            sel_p = []

        gc1, gc2 = st.columns([3, 1])
        with gc1:
            gen_btn = st.button(
                f"🚀 生成 {selected_mode_cfg['icon']} {selected_mode_key} 提示詞",
                type="primary", use_container_width=True, key="gen_prompt_v300"
            )
        with gc2:
            if 'battle_prompt_v300' in st.session_state:
                if st.button("🗑️ 清除", use_container_width=True, key="clear_prompt_v300"):
                    st.session_state.pop('battle_prompt_v300', None)
                    st.rerun()

        if gen_btn:
            if not geo:
                st.error("❌ 請先啟動深鑽分析。")
            else:
                council = TitanAgentCouncil()
                with st.spinner("⚙️ 正在生成法庭級提示詞…"):
                    prompt = council.generate_battle_prompt(
                        ticker_in, price_now, geo, rating,
                        full_intel, commander_note, sel_p,
                        mode=selected_mode_code
                    )
                st.session_state['battle_prompt_v300']  = prompt
                st.session_state['battle_prompt_mode']  = selected_mode_key
                st.toast(f"✅ {selected_mode_key} 提示詞已生成！共 {len(prompt):,} 字元", icon="🎯")
                st.rerun()

        if 'battle_prompt_v300' in st.session_state:
            pt        = st.session_state['battle_prompt_v300']
            mode_used = st.session_state.get('battle_prompt_mode', '')

            st.markdown(f"""
            <div style="background:rgba(0,245,255,0.04);border:1px solid rgba(0,245,255,0.15);
            border-radius:8px;padding:10px 14px;margin:8px 0;display:flex;gap:20px;flex-wrap:wrap;">
            <div><span style="font-size:9px;color:rgba(0,245,255,0.4);letter-spacing:2px;">模式</span><br>
            <span style="font-size:12px;font-weight:700;color:#00F5FF;">{mode_used}</span></div>
            <div><span style="font-size:9px;color:rgba(0,245,255,0.4);letter-spacing:2px;">字元數</span><br>
            <span style="font-size:12px;font-weight:700;color:#00F5FF;">{len(pt):,}</span></div>
            <div><span style="font-size:9px;color:rgba(0,245,255,0.4);letter-spacing:2px;">標的</span><br>
            <span style="font-size:12px;font-weight:700;color:#00F5FF;">{ticker_in} @ ${price_now:.2f}</span></div>
            </div>""", unsafe_allow_html=True)

            with st.expander("📌 如何正確使用此提示詞（必讀）", expanded=False):
                st.markdown(f"""
**✅ 最佳使用流程：**
1. 點下方「下載提示詞」按鈕保存文件
2. 打開 **Claude.ai / Gemini Advanced / ChatGPT-4o**（任一，開**新對話**）
3. 直接貼上全部文字（Ctrl+A → Ctrl+C → 貼上）
4. 等待 AI 完整輸出（完整法庭模式約需 3–5 分鐘）

**🔧 如果 AI 輸出不符預期，追加以下指令：**
- AI 給模糊結論：`「禁止使用迴避性語言，必須選擇一個明確方向並給出具體價位」`
- AI 跳過某個子項目：`「[Q3] 動能比率分析尚未完成，請補充 300 字以上的分析」`
- AI 角色流於形式：`「[B2] Burry 的回答過於表面，請針對財務數據進行更深入的均值回歸計算」`
- 想要補充情報：直接在後面加上 `「以下是新增情報，請裁判官重新裁決：[你的資訊]」`

**🎯 閱讀 AI 輸出時，重點關注順序：**
1. 裁判官的【一句定論】（最後一句，整份報告的錨點）
2. 裁判官的【最終操作指令】（進場/停損/停利/倉位）
3. Burry 的【B4 宏觀死亡威脅】（最客觀的風險評估）
4. Quant 的【Q2 R² 審計】（趨勢可信度）
                """)

            st.markdown(f'<div class="terminal-box"><pre style="white-space:pre-wrap;margin:0;color:#c9d1d9;font-size:10.5px;line-height:1.6;">{pt[:3500]}{"\\n\\n⋯⋯（以下內容請下載完整版查看）⋯⋯" if len(pt) > 3500 else ""}</pre></div>', unsafe_allow_html=True)

            c_copy, c_dl = st.columns(2)
            with c_copy:
                st.text_area("📋 複製全文（Ctrl+A → Ctrl+C）", value=pt, height=180, key="prompt_out_v300")
            with c_dl:
                st.download_button(
                    f"💾 下載提示詞 (.txt)",
                    data=pt,
                    file_name=f"TITAN_V400_{ticker_in}_{selected_mode_code}_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                    mime="text/plain", use_container_width=True, key="dl_prompt_v400"
                )
                st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
                st.write_stream(stream_generator(
                    f"提示詞已就緒 ({len(pt):,} 字元)。"
                    f"開新對話，貼上全文，等待 AI 完整輸出。"
                    f"如 AI 回答不夠深入，直接點名子項目代碼要求補充。"
                ))


# ═══════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════
# SECTION 6.3 — 百倍股雷達 V2 (100-Bagger · First Principles)
# ═══════════════════════════════════════════════════════════════
def _s63():
    """6.3 百倍股雷達 V2 — 捕獲下一個景氣循環的百倍股"""

    # ── CSS ──
    st.markdown("""<style>
    .bg28{font-size:28px!important;font-weight:900;color:#FFD700;letter-spacing:2px;line-height:1.35;margin-bottom:6px;}
    .bg26{font-size:26px!important;font-weight:700;color:rgba(210,220,235,.88);line-height:1.75;margin-bottom:6px;}
    .bg26c{font-size:26px!important;font-weight:800;color:#00F5FF;letter-spacing:1px;line-height:1.4;}
    .bgf{font-size:26px!important;font-weight:800;color:#00FF9D;background:rgba(0,255,157,.06);
         border-left:4px solid #00FF9D;padding:10px 16px;border-radius:0 8px 8px 0;margin:10px 0;line-height:1.6;}
    .bgw{font-size:26px!important;color:#FF9A3C;font-weight:700;line-height:1.5;}
    .bgcard{background:rgba(255,255,255,.025);border:1px solid rgba(255,255,255,.07);border-radius:14px;padding:20px 22px;margin-bottom:12px;}
    .bgml{font-size:22px!important;color:rgba(160,176,208,.5);letter-spacing:2px;text-transform:uppercase;margin-bottom:2px;}
    .bgmv{font-size:28px!important;font-weight:800;line-height:1.2;}
    .bgscore{font-size:54px!important;font-weight:900;line-height:1;text-align:center;}
    .bgrow{display:flex;justify-content:space-between;border-bottom:1px solid rgba(255,255,255,.04);padding:5px 0;}
    .bgrl{font-size:21px!important;color:rgba(180,190,210,.55);}
    .bgrv{font-size:23px!important;font-weight:700;}
    </style>""", unsafe_allow_html=True)

    # ── 頁首 ──
    st.markdown('<div class="t6-sec-head" style="--sa:#FF9A3C"><div class="t6-sec-num">6.3</div><div>'
                '<div class="t6-sec-title" style="color:#FF9A3C;">百倍股雷達 V2 — 捕獲下一個景氣循環</div>'
                '<div class="t6-sec-sub">7-Dimension DNA · Cycle Position · 100x Path Engine</div>'
                '</div></div>', unsafe_allow_html=True)

    # ════════════════════════════════════════════════════
    # BLOCK A：第一性原則理論面板
    # ════════════════════════════════════════════════════
    with st.expander("📖 第一性原則：百倍股的物理學（必讀，點此展開）", expanded=False):

        st.markdown('<div class="bg28">🔬 百倍股的物理學——從最基本的數學開始</div>', unsafe_allow_html=True)
        st.markdown('<div class="bg26">一支股票漲 100 倍只有兩條路徑，且必須<b>同時發生</b>才能達到最強爆發力：</div>', unsafe_allow_html=True)
        st.markdown('<div class="bgf">📐 百倍公式：股價 = EPS（每股盈餘）× PE（市場給的倍數）<br>'
                    '要漲 100 倍 → EPS 漲 10 倍 × PE 漲 10 倍 = 100x<br>'
                    '或者 → EPS 漲 50 倍 × PE 擴張 2 倍 = 100x<br>'
                    '關鍵洞見：<b>只有 EPS 成長是不夠的。PE 擴張才是百倍股的催化劑。</b></div>', unsafe_allow_html=True)
        st.markdown('<div class="bg26">PE 擴張發生的條件，正是市場從「不相信」轉為「深信不疑」的那一刻。'
                    '這意味著你必須在<b>市場還不相信</b>的時候就進場佈局——也就是景氣循環的黎明期。</div>', unsafe_allow_html=True)

        st.divider()
        st.markdown('<div class="bg28">📅 景氣循環的位置決定命運</div>', unsafe_allow_html=True)
        st.markdown('<div class="bg26">Chris Mayer 研究 365 支歷史百倍股後發現：大多數百倍股在被發現時，'
                    '都處於景氣循環的「黎明期」——行業剛剛被市場忽視，或正從谷底反彈，估值極低，機構持倉幾乎為零。</div>', unsafe_allow_html=True)

        col_cyc1, col_cyc2 = st.columns(2)
        with col_cyc1:
            st.markdown("""<div class="bgcard" style="border-color:rgba(0,255,157,.25)">
            <div class="bg26c" style="color:#00FF9D;">🌅 黎明期（最佳買點）</div>
            <div class="bg26" style="margin-top:8px;">
            • 行業剛從衰退中復甦，市場仍充滿懷疑<br>
            • 市值極小，機構尚未關注<br>
            • 營收開始加速，但市場還不信<br>
            • PE 處於歷史低位（甚至虧損）<br>
            • <b style="color:#00FF9D;">→ PE 擴張 + EPS 成長 雙引擎同時啟動</b>
            </div></div>""", unsafe_allow_html=True)
        with col_cyc2:
            st.markdown("""<div class="bgcard" style="border-color:rgba(255,107,107,.25)">
            <div class="bg26c" style="color:#FF6B6B;">🌇 黃昏期（最危險陷阱）</div>
            <div class="bg26" style="margin-top:8px;">
            • 人人都在談論這個行業，雜誌封面效應<br>
            • 機構持倉已達高峰<br>
            • PE 處於歷史高位<br>
            • 營收成長開始放緩，競爭者湧入<br>
            • <b style="color:#FF6B6B;">→ PE 收縮 + EPS 放緩 = 估值雙殺</b>
            </div></div>""", unsafe_allow_html=True)

        st.divider()
        st.markdown('<div class="bg28">🧬 下一個景氣循環的 5 大賽道（2024–2035）</div>', unsafe_allow_html=True)
        st.markdown('<div class="bg26">基於第一性原則，以下 5 條賽道在未來 10 年最可能誕生下一批百倍股：</div>', unsafe_allow_html=True)

        tracks = [
            ("⚡ AI 基礎設施（算力 + 散熱 + ASIC）", "#FFD700",
             "GPU 伺服器、液冷散熱、自研 ASIC 晶片設計。AI 所有應用都依賴這層基礎建設。"
             "TAM 從 $500B 擴張至 $5T（10 年）。現在仍是早期基礎建設期，大多數贏家尚未誕生。"
             "第一性原則：算力是 AI 時代的電力，電力公司在工業革命初期都是百倍股。"),
            ("☢️ 核能復興（SMR 小型模組化反應爐）", "#00FF9D",
             "碳中和政策 + AI 耗電量爆炸 + 能源安全三重驅動。SMR 市場目前接近於零，"
             "但 2030 後將爆發。第一性原則：每 AI 訓練中心耗電量等於一個城市，"
             "可再生能源無法 24/7 供電，核能是唯一的基載零碳能源。"),
            ("🤖 機器人自動化（具身智能 + 工業 AI）", "#00BFFF",
             "人力成本上升（全球老齡化）+ AI 感知突破使機器人真正「看得見、想得到」。"
             "製造業、物流、農業、醫療機器人。TAM 從 $50B → $500B。"
             "第一性原則：人口老齡化是不可逆的物理事實，機器人是唯一的解藥。"),
            ("🛡️ 國防科技（無人機 + 太空 + 網路安全）", "#FF9A3C",
             "地緣政治緊張長期化（烏克蘭、台海）。無人機、衛星通訊、AI 偵測系統。"
             "各國國防預算 GDP 佔比持續提升，且具有政府長期合約的護城河。"
             "第一性原則：戰爭改變武器需求，無人化是不可逆的軍事趨勢。"),
            ("🧬 生物科技（AI 藥物研發 + 精準醫療）", "#FF6B6B",
             "AI 將藥物研發時間從 12 年壓縮至 3 年，成本下降 80%。RNA 療法、個人化癌症治療、"
             "長壽科技。第一性原則：人類最大的恐懼是死亡，能延長高質量壽命的技術擁有無限定價權。"),
            ("🌐 AI 物理化實踐（AI Physicalization）", "#E040FB",
             "AI 不只活在伺服器裡。它正在滲透進每一個物理世界的節點：自動駕駛、智慧工廠、AI 眼鏡、"
             "AI 手機、智慧電網、精準農業。這一波百倍股的邏輯不是「誰做出最強的模型」，"
             "而是「誰把 AI 能力最深度嵌入一個每天被數十億人使用的物理場景」。"
             "Tesla 當年的邏輯正是如此——不是最快的電動車，而是把軟體定義汽車物理化。"
             "第一性原則：模型的價值由部署規模決定，物理世界才是 AI 最終的戰場。"),
            ("⚛️ 量子應用（Quantum Applications）", "#00FFFF",
             "【統帥核心觀點——尚待市場驗證，但第一性原則支持】"
             "量子的百倍股邏輯不是「最快的量子電腦」，而是兩個尚未被市場定價的應用場景：\n\n"
             "❶ 月球量子計算平台：月球永久陰影區溫度接近 -233°C（接近絕對零度），"
             "是地球最貴的量子冷卻系統的免費替代品。量子計算最大的工程瓶頸是維持量子態需要極低溫環境，"
             "地球上每台量子電腦都需要昂貴的稀釋冷凍機。月球提供天然超低溫基礎設施，"
             "可讓超導量子比特穩定運行時間從微秒級延長至秒級以上。"
             "這不只是技術突破——這是讓量子計算從「實驗室里的玩具」變成「商業化現實」的基礎設施革命。"
             "NASA 阿提米斯計劃 + 私人月球任務（ispace、Intuitive Machines、Astrobotic）正在建立月球基礎設施，"
             "量子計算部署時間表可能比市場預期提前 10 年。"
             "第一性原則：量子計算的物理極限是量子退相干時間，而溫度是退相干最大的敵人——月球解決了這個物理問題。\n\n"
             "❷ 全自動駕駛的量子中樞神經系統：當市場上大部分車輛都實現全自動駕駛（L5）時，"
             "一個根本性的問題出現了——每台自動駕駛車都搭載自己品牌的 AI 模型"
             "（特斯拉 FSD、Waymo、小鵬 XNGP、Mobileye、百度 Apollo），"
             "它們說不同的「語言」，無法即時協同。"
             "想象十字路口同時有 100 台來自 10 個品牌的自動駕駛車，誰決定誰先走？"
             "經典計算面臨的挑戰：跨品牌 AI 模型的即時通訊需要接近零延遲的訊號同步，"
             "5G 的最低延遲約 1ms，但量子通訊理論上可實現更快的狀態同步（量子纏繞）。"
             "量子金鑰分發（QKD）已可商業部署，可作為安全通訊層的基礎。"
             "量子隨機數生成器可解決多 AI 決策衝突的公平仲裁問題。"
             "這個賽道的百倍股邏輯：誰建立起跨品牌自動駕駛協調的量子通訊層，"
             "就相當於擁有了整個自動駕駛時代的「電信基礎設施」——這是一個贏者通吃的壟斷市場。"
             "目前能做這件事的公司極少，且市值仍在億美元級別，百倍空間物理上成立。"
             "第一性原則：每一次交通革命都誕生了基礎設施壟斷者（鐵路時代→電報網路，汽車時代→高速公路），"
             "自動駕駛時代的基礎設施壟斷者尚未誕生，這就是百倍股的空白地帶。"),
        ]
        for title, color, desc in tracks:
            st.markdown(f"""<div style="background:rgba(255,255,255,.02);border-left:4px solid {color};
            border-radius:0 10px 10px 0;padding:14px 18px;margin-bottom:10px;">
            <div class="bg26c" style="color:{color};">{title}</div>
            <div class="bg26" style="margin-top:6px;">{desc}</div>
            </div>""", unsafe_allow_html=True)

        st.divider()
        st.markdown('<div class="bg28">📊 7 維度 DNA 評分系統——為什麼是這 7 個指標？</div>', unsafe_allow_html=True)
        st.markdown('<div class="bg26">本系統整合 Chris Mayer《100-Baggers》、Peter Lynch《One Up on Wall Street》、'
                    'Baillie Gifford 成長框架三大體系，萃取出預測力最強的 7 個指標，總分 100 分：</div>', unsafe_allow_html=True)

        dna_theory = [
            ("D1", "ROE / 資本效率引擎", "30 分", "#FFD700",
             "ROE > 20% 意味著公司每投入 1 元能創造 0.20 元以上回報，並且可以把這個回報繼續再投入，"
             "形成<b>複利飛輪</b>。巴菲特說：「一家公司的長期股價回報率，長期趨近於它的 ROE。」"
             "這是百倍股最核心、最持久的驅動力。高 ROE + 高再投資率 = 時間的朋友。",
             "ROE > 25%: 30分 ｜ ROE > 20%: 22分 ｜ ROE > 15%: 12分 ｜ ROE > 10%: 5分"),
            ("D2", "營收加速度", "25 分", "#00FF9D",
             "不只看營收成長率，更看<b>加速度</b>——成長率本身是否在加快？"
             "從 20% 加速到 40% 的公司，比穩定 30% 的公司更值得關注，因為加速度代表需求正在超越所有人的預期。"
             "加速成長觸發 PE 擴張——當市場意識到預測模型全都低估了，他們會瘋狂上修。",
             "成長 > 30%: 25分 ｜ 成長 > 20%: 18分 ｜ 成長 > 10%: 10分 ｜ 成長 > 5%: 4分"),
            ("D3", "毛利率護城河", "20 分", "#00BFFF",
             "毛利率是護城河的 X 光片。毛利率 > 60% 說明公司有<b>定價權</b>，競爭對手無法靠打價格戰消滅你。"
             "軟體、平台、品牌、網路效應是高毛利護城河的典型。"
             "低毛利行業幾乎不可能出現百倍股——競爭者會把所有超額利潤榨乾至零。",
             "毛利率 > 60%: 20分 ｜ > 40%: 14分 ｜ > 25%: 7分 ｜ > 10%: 2分"),
            ("D4", "市值天花板空間", "15 分", "#FF9A3C",
             "一支 1000 億美元的公司要漲 100 倍，需要市值達到 10 兆——接近全美所有上市公司的總值。"
             "這在數學上幾乎不可能。因此<b>百倍股只能從小市值開始</b>，"
             "這是物理定律而非偏好。機構不買小市值是百倍股存在的根本原因——沒有人注意，才有機會。",
             "台股 < 50億: 15分 ｜ < 200億: 10分 ｜ 美股 < 3億: 15分 ｜ < 15億: 10分"),
            ("D5", "再投資能力 / 零配息", "5 分", "#B77DFF",
             "百倍股<b>幾乎不配息</b>。每一分錢都要再投入以創造更高回報。"
             "高股息等於公司在告訴你：「我找不到比分錢給你更好的用途了。」"
             "這與百倍股的複利飛輪根本矛盾。Amazon 從不配息，Apple 在成長最快的時期也不配息。",
             "配息率 < 0.5%: 5分 ｜ < 2%: 3分 ｜ < 4%: 1分"),
            ("D6", "盈利品質 / FCF", "3 分", "#FF6B6B",
             "自由現金流（FCF）是盈利真實性的最終測試。公司可以透過調整折舊、攤銷美化淨利，"
             "但<b>現金不會說謊</b>。FCF Margin > 15% 說明盈利是真實的，公司不是在玩數字遊戲。"
             "尤其對於高成長公司，FCF 轉正是從「燒錢故事」轉為「真實商業機器」的關鍵拐點。",
             "FCF Margin > 15%: 3分 ｜ > 5%: 1分"),
            ("D7", "估值安全邊際 / PEG", "2 分", "#00F5FF",
             "PEG 比率（PE ÷ 成長率）< 1 是 Peter Lynch 定義的合理買點。"
             "對於真正的破壞式創新公司，PEG < 0.5 是難得的黃金機會。"
             "這個指標防止你在頂部追買「已知的好故事」——當所有人都知道這是好公司，PE 已反映了未來 5 年的成長。",
             "PEG < 0.5: 2分 ｜ PEG < 1.0: 1分"),
        ]

        for code, name, pts, color, theory, scoring in dna_theory:
            with st.expander(f"[{code}] {name} — 最高 {pts}", expanded=False):
                st.markdown(f'<div class="bg26c" style="color:{color};">[{code}] {name} · 最高 {pts}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="bg26" style="margin-top:8px;">{theory}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="bgf" style="border-left-color:{color};">計分規則：{scoring}</div>', unsafe_allow_html=True)

        st.divider()
        st.markdown('<div class="bg28">🔴 燒錢公司特別說明（Pre-Profit Mode）</div>', unsafe_allow_html=True)
        st.markdown('<div class="bg26">許多歷史上最偉大的百倍股，在被發現的早期都是虧損的。用傳統 EPS 框架分析它們，只會得出「別碰」的結論。</div>', unsafe_allow_html=True)

        col_pp1, col_pp2 = st.columns(2)
        with col_pp1:
            st.markdown("""<div class="bgcard" style="border-color:rgba(255,107,107,.25)">
            <div class="bg26c" style="color:#FF6B6B;">📌 歷史案例</div>
            <div class="bg26" style="margin-top:8px;">
            • <b>Tesla（2018–2019）</b>：EPS 大幅虧損，但毛利率提升、交車量加速。誰看 EPS 就錯過了 100 倍。<br>
            • <b>Palantir（PLTR 2020–2021）</b>：上市時虧損，但政府合約黏性極高、商業客戶加速。<br>
            • <b>Amazon（1999–2002）</b>：燒錢燒了整個網路泡沫，但毛利率和用戶留存從未動搖。<br>
            • <b>Netflix（2010–2013）</b>：大量投入內容，EPS 極低，但訂閱人數加速是真實信號。
            </div></div>""", unsafe_allow_html=True)
        with col_pp2:
            st.markdown("""<div class="bgcard" style="border-color:rgba(0,255,157,.2)">
            <div class="bg26c" style="color:#00FF9D;">📐 燒錢公司的正確評估框架</div>
            <div class="bg26" style="margin-top:8px;">
            燒錢不是問題，<b>燒的方式</b>才是關鍵：<br><br>
            ✅ <b>好的燒錢</b>：毛利率高且提升 → 規模化後自然盈利<br>
            ✅ <b>好的燒錢</b>：營收加速成長 → 每一分錢都在換客戶<br>
            ✅ <b>好的燒錢</b>：高客戶黏性（NDR > 120%）→ 留住的客戶越來越值錢<br>
            ❌ <b>壞的燒錢</b>：毛利率低且下降 → 商業模式根本不成立<br>
            ❌ <b>壞的燒錢</b>：營收成長放緩 → 市場在收縮<br>
            ❌ <b>壞的燒錢</b>：現金跑道 < 18 個月 → 稀釋風險
            </div></div>""", unsafe_allow_html=True)

        st.markdown('<div class="bgf">🔧 本系統偵測到 EPS < 0 時自動切換為「燒錢替代計分法」：<br>'
                    'D1 → 用毛利率代替 ROE（驗證商業模式可行性）<br>'
                    'D6 → 用 P/S 比率代替 FCF Margin（評估估值是否合理）<br>'
                    'D7 → 用 P/S÷成長率代替 PEG（替代安全邊際計算）<br>'
                    '100x 估算 → 純用營收 CAGR×0.7（含不確定性折扣，盈利後可上修）</div>', unsafe_allow_html=True)

        st.divider()
        st.markdown('<div class="bgw">⚠️ 重要警告：百倍股需要 7–20 年的持有期。本工具是「識別潛力」的雷達，'
                    '不是「預測短期漲跌」的工具。找到 DNA ≥ 65 分的公司後，'
                    '下一步是深度研究其護城河可持續性、創辦人是否仍在主導公司、'
                    '以及行業景氣循環是否處於黎明期。這三個問題比任何財務指標都重要。</div>', unsafe_allow_html=True)

    # ════════════════════════════════════════════════════
    # BLOCK B：景氣循環定位器
    # ════════════════════════════════════════════════════
    st.divider()
    st.markdown('<div class="bg28">🌐 景氣循環定位器——先定位，再選股</div>', unsafe_allow_html=True)
    st.markdown('<div class="bg26">在啟動掃描前，先確認你聚焦的賽道處於哪個循環位置，以判斷 PE 擴張的可能性大小。</div>', unsafe_allow_html=True)

    cycle_map = [
        ("⚡ AI 基礎設施", "成長加速期 🚀", "#FF4500", "機構持倉仍低，TAM 剛開始擴張，PE 擴張空間仍存在"),
        ("☢️ 核能 / SMR",  "黎明早期 🌅",  "#FFD700", "多數機構仍迴避，政策拐點已現，最佳佈局窗口"),
        ("🤖 機器人 / 具身AI","黎明期 🌅",  "#FFD700", "技術突破剛發生，商業化仍早期，高風險高潛力"),
        ("🌐 AI 物理化實踐","黎明加速 🌅🚀","#E040FB", "AI 嵌入物理場景剛開始，Tesla/PLTR 模式複製中，PE 擴張最強烈"),
        ("⚛️ 量子應用",    "黎明前夜 🌑🌅","#00FFFF", "【統帥看好】月球量子計算 + 自駕中樞神經，市場幾乎未定價，極高風險極高潛力"),
        ("🛡️ 國防 / 無人機", "成長早期 📈", "#ADFF2F", "地緣驅動持續，但部分標的估值已反映預期"),
        ("🧬 AI 生物科技",   "萌芽期 🌱",   "#00BFFF", "技術驗證仍早，需 3–5 年，極高風險極高潛力"),
        ("🏭 工業自動化",    "成長期 📈",   "#ADFF2F", "政策補貼驅動，但週期性風險存在"),
        ("💊 傳統製藥 / 高股息","成熟期 ⚠️","#FF9A3C", "百倍股不在此，PE 擴張空間極小"),
        ("🏦 傳統金融 / 銀行","週期底部 📉", "#FF6B6B", "利率敏感，非破壞式創新，不適合百倍框架"),
    ]
    c1c, c2c = st.columns(2)
    for i, (sec, stage, color, note) in enumerate(cycle_map):
        col = c1c if i % 2 == 0 else c2c
        with col:
            st.markdown(f"""<div style="background:rgba(255,255,255,.02);border:1px solid {color}33;
            border-left:3px solid {color};border-radius:0 8px 8px 0;padding:10px 14px;margin-bottom:8px;">
            <div class="bgml">{sec}</div>
            <div class="bgmv" style="color:{color};">{stage}</div>
            <div style="font-size:22px;color:rgba(180,190,210,.6);margin-top:3px;">{note}</div>
            </div>""", unsafe_allow_html=True)

    # ════════════════════════════════════════════════════
    # 量子百倍股深度研究專區 (統帥特別指令)
    # ════════════════════════════════════════════════════
    st.divider()
    st.markdown('<div class="bg28" style="color:#00FFFF;">⚛️ 量子百倍股深度研究——統帥看好的兩條路徑</div>', unsafe_allow_html=True)
    st.markdown(
        '<div style="background:rgba(0,255,255,0.04);border:1px solid rgba(0,255,255,0.2);'
        'border-left:4px solid #00FFFF;border-radius:0 10px 10px 0;padding:16px 20px;margin-bottom:14px;">'
        '<span style="font-family:\'JetBrains Mono\',monospace;font-size:10px;color:rgba(0,255,255,.5);'
        'letter-spacing:3px;text-transform:uppercase;">⚠️ 統帥聲明</span>'
        '<div style="font-size:14px;color:rgba(200,220,235,.85);margin-top:6px;line-height:1.8;">'
        '以下分析代表統帥個人判斷框架，<b style="color:#FFD700;">是否帶來破壞式創新有待市場驗證</b>。'
        '量子股波動極大，需配合第 6.2 節法庭級 AI 分析提示詞深度研究後再做決策。'
        '放入此處的原因：市場幾乎未定價的空白地帶，才是百倍股誕生的土壤。'
        '</div></div>',
        unsafe_allow_html=True
    )

    qcol1, qcol2 = st.columns(2)

    with qcol1:
        st.markdown("""<div class="bgcard" style="border-color:rgba(0,255,255,.3);min-height:420px;">
        <div class="bg26c" style="color:#00FFFF;">🌕 路徑一：月球量子計算平台</div>
        <div class="bg26" style="margin-top:10px;line-height:1.85;">
        <b>核心物理邏輯：</b><br>
        量子計算最大的工程瓶頸是「量子退相干」——量子比特極容易受到溫度、振動、電磁干擾破壞。
        地球上每台量子電腦都需要稀釋冷凍機將溫度降至 <b>-273.13°C（接近絕對零度 15 mK）</b>，
        設備成本高達數百萬美元，且維護困難。<br><br>
        <b>月球提供的天然優勢：</b><br>
        • 月球永久陰影區（Permanently Shadowed Regions）溫度：<b>-233°C to -258°C</b><br>
        • 幾乎沒有大氣層 → 振動雜訊接近零<br>
        • 遠離地球電磁污染 → 量子態維持時間可大幅延長<br>
        • 月球表面重力僅 1/6 → 機械振動傷害更低<br><br>
        <b>這意味著什麼？</b><br>
        月球可能讓量子計算的商業化時間從 2040 年提前至 <b>2032-2035 年</b>。
        NASA 阿提米斯計劃 + ispace / Intuitive Machines 正在建立月球基礎設施，
        量子硬體部署窗口比市場預期快得多。<br><br>
        <b>潛在受益公司（需深度研究）：</b><br>
        IONQ（離子阱量子電腦）、RGTI（超導量子）、IBM Quantum、
        Quantinuum（Honeywell 子公司）、Rigetti Computing
        </div>
        </div>""", unsafe_allow_html=True)

    with qcol2:
        st.markdown("""<div class="bgcard" style="border-color:rgba(0,255,255,.3);min-height:420px;">
        <div class="bg26c" style="color:#00FFFF;">🚗 路徑二：全自動駕駛量子中樞神經</div>
        <div class="bg26" style="margin-top:10px;line-height:1.85;">
        <b>問題定義（第一性原則）：</b><br>
        當市場上數千萬台全自動駕駛（L5）車輛同時上路時，每台車都搭載自己品牌的 AI 模型：
        Tesla FSD、Waymo Driver、小鵬 XNGP、Mobileye SuperVision、百度 Apollo——
        它們說不同的「語言」，無法即時協同。<br><br>
        <b>這是一個物理問題，不是軟體問題：</b><br>
        • 十字路口 100 台不同品牌自動駕駛同時決策 → 誰優先？<br>
        • 5G 最低延遲 1ms，但高速場景中 1ms 等於 3.6cm 的位移誤差<br>
        • 各品牌 AI 決策衝突需要即時、公平、品牌中立的仲裁層<br><br>
        <b>量子的角色：</b><br>
        • <b>量子金鑰分發（QKD）</b>：建立跨品牌安全通訊標準層<br>
        • <b>量子隨機數生成器（QRNG）</b>：公平仲裁多 AI 決策衝突，防止任何品牌偏袒<br>
        • <b>量子感應器網路</b>：V2X（車對一切通訊）的量子加強版<br><br>
        <b>百倍股邏輯：</b><br>
        誰建立這個跨品牌協調層，就等於擁有整個自動駕駛時代的
        <b>「電信基礎設施壟斷」</b>——這是歷史上每次交通革命都誕生的那種壟斷。
        目前市場上幾乎沒有公司在做這件事，市值在億美元級，百倍空間物理成立。<br><br>
        <b>相關公司（QRNG / QKD 領域）：</b><br>
        ARQQ（量子加密）、ID Quantique（私人/QRNG）、Quantinuum
        </div>
        </div>""", unsafe_allow_html=True)

    # ─── 5 條預想發展路徑（根據現有量子公司研究方向外推）─────────────────
    st.divider()
    st.markdown(
        '<div class="bg28" style="color:#00FFFF;">'
        '🔭 預想中的量子破壞式創新——你可能還沒想到的 5 條路徑</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div class="bg26" style="margin-bottom:14px;">'
        '基於 IonQ、Rigetti、IBM Quantum、D-Wave、Quantinuum、ARQQ、ID Quantique 等公司'
        '當前正在解決的問題，統帥外推出以下 5 個市場幾乎完全未定價的破壞式創新方向——'
        '這些不是遙遠的幻想，它們的物理基礎已被實驗室證實，缺的只是工程規模化。</div>',
        unsafe_allow_html=True
    )

    q_paths = [
        (
            "⚔️ 路徑三：密碼學末日 + 後量子重建（Post-Quantum Cryptography）",
            "#FF3131",
            "確定性最高、時間最近的量子破壞式創新",
            """<b>這是唯一「確定會發生」的量子革命，不是 IF，是 WHEN。</b><br><br>
            <b>問題的物理本質：</b>今天全球所有的網路安全（銀行系統、軍事通訊、政府機密、區塊鏈）
            都建立在 RSA 和 ECC 加密演算法上，而這兩種演算法依賴一個數學假設：
            <b>「大數因式分解在傳統電腦上是不可能的」</b>。<br><br>
            Shor 演算法已在理論上證明：一台足夠大的量子電腦可在數分鐘內破解 RSA-2048。
            目前的量子電腦還不夠大，但每年量子比特數量呈指數成長。
            NIST（美國國家標準局）在 2024 年已正式發佈後量子密碼學（PQC）標準，
            美國 CISA 要求所有聯邦機構在 2030 年前完成遷移。<br><br>
            <b>這意味著什麼？</b><br>
            <b style="color:#FF3131;">全球所有使用 RSA/ECC 的系統必須升級</b>——這是一個沒有選擇、
            不能拖延、預算確定的市場。銀行、國防、電信、雲端服務商全部在列。
            TAM 估計 $20B-$100B（未來 10 年的合規支出）。<br><br>
            <b>百倍股邏輯：</b>提供 PQC 遷移解決方案的公司現在市值極低，
            但它們服務的是一個「監管強制執行的剛需市場」——這是最確定的成長曲線。<br><br>
            <b>受益公司：</b>ARQQ（量子安全通訊）、ID Quantique（QRNG + QKD）、
            PQShield（私人）、SandboxAQ（Google 分拆，私人）""",
        ),
        (
            "🔬 路徑四：量子感應器革命（Quantum Sensing）——不需要量子電腦",
            "#ADFF2F",
            "最被市場忽視、最快可商業化的量子硬體賽道",
            """<b>關鍵洞見：量子感應器不需要等待「容錯量子電腦」——它們現在就能用。</b><br><br>
            量子力學讓我們能測量物理量到前所未有的精度。這不是理論，是已經在實驗室外部署的技術：<br><br>
            <b>① 量子重力儀（Quantum Gravimeter）：</b><br>
            測量重力梯度的精度比傳統儀器高 1000 倍。應用：
            <b>不需要鑽探就能探測地下石油、礦藏、地下水、空洞</b>。
            全球礦業公司每年花費數百億美元在地質勘探，量子重力儀可讓成功率提升 10 倍。
            另一應用：地震預警（比現有系統提前 20-30 秒感測地殼形變）。<br><br>
            <b>② 量子磁力儀（Quantum Magnetometer）：</b><br>
            敏感度比現有儀器高出 10 萬倍。應用一：
            <b>無創腦部掃描</b>——在室溫下測量神經元磁場，不需要昂貴的 MRI 機器，
            可穿戴式設備就能做到，顛覆 $300B 醫學影像市場。
            應用二：<b>水下潛艦偵測</b>（軍事應用，國防預算剛需）。<br><br>
            <b>③ 量子 LiDAR / 單光子偵測：</b><br>
            在<b>完全黑暗、濃霧、暴雨環境下</b>偵測障礙物，靈敏度是傳統 LiDAR 的 100 倍以上。
            這是自動駕駛最後一個未解決的感知瓶頸——天候惡劣時傳統 LiDAR 失效的問題。<br><br>
            <b>④ 量子原子鐘（Quantum Clock）：</b><br>
            誤差小於 10⁻¹⁸ 秒。應用：<b>GPS 替代方案</b>——不需要衛星訊號的精準導航
            （軍事反制 GPS 干擾、深海潛艦、地下隧道導航）。<br><br>
            <b>受益公司：</b>Infleqtion（私人）、Vescent Photonics（私人）、
            M-Squared Lasers（英國）、Muquans（法國）、
            以及以 ARQQ、IONQ 的感測器研究部門為潛在受益方""",
        ),
        (
            "💊 路徑五：量子分子模擬 → 材料與藥物的第一性原則（Quantum Simulation）",
            "#FF9A3C",
            "Feynman 在 1982 年預言的量子電腦原始用途，正在接近現實",
            """<b>第一性原則：化學反應是量子現象，用古典電腦模擬它是在用直尺量曲線。</b><br><br>
            化學的本質是電子的量子力學行為。傳統電腦模擬分子相互作用時，
            每增加一個原子，計算複雜度就指數爆炸——模擬 50 個原子的分子，
            需要比宇宙中原子數還多的記憶體。這是物理限制，不是工程問題。<br><br>
            量子電腦天生就是在做量子計算，因此可以<b>精確模擬任意大小分子</b>。<br><br>
            <b>三個改變世界的應用：</b><br><br>
            <b>① 固態電池材料發現（Battery Revolution）：</b><br>
            現有鋰電池能量密度接近物理極限。下一代固態電池需要發現新的電解質材料，
            而傳統試誤法需要 20 年。量子模擬可在 2-3 年內找到最優材料。
            一旦突破：EV 續航里程翻倍、充電時間縮至 5 分鐘、電池壽命延長至 20 年。
            <b style="color:#FF9A3C;">這是 $5T 電動車革命的「最後一塊拼圖」。</b><br><br>
            <b>② 氮固化催化劑（Fertilizer Revolution）：</b><br>
            哈伯法合成氨（全球糧食的基礎）耗費全球能源的 2%，每年排放 5 億噸 CO₂。
            自然界中固氮菌在常溫常壓下用鉬鐵蛋白催化完成這個反應——但為什麼有效，
            我們用傳統電腦算不出來。量子模擬可以精確解析這個機制，
            複製出人工催化劑，徹底淘汰哈伯法。影響：全球農業革命 + 氣候革命同時發生。<br><br>
            <b>③ 精準藥物設計（Drug Discovery 2.0）：</b><br>
            AlphaFold 解決了蛋白質結構預測，但「蛋白質如何動態折疊 + 藥物如何與目標蛋白精準結合」
            仍是傳統電腦的極限。量子模擬讓藥物設計從「碰運氣」變成「工程設計」，
            癌症、阿茲海默症、帕金森症的靶向療法開發時間從 12 年壓縮至 2-3 年。<br><br>
            <b>受益公司：</b>Quantinuum（前身 Cambridge Quantum，已有量子化學成果）、
            IONQ（生物醫藥合作管線）、IBM Quantum（材料科學計劃）、
            QSimulate（私人，Harvard 量子化學 spinout）""",
        ),
        (
            "📈 路徑六：量子金融霸權（Quantum Financial Supremacy）",
            "#B77DFF",
            "最快商業化的量子計算應用——金融機構已在秘密部署",
            """<b>第一性原則：金融市場的核心計算問題是 NP-hard 問題，傳統電腦只能近似解。</b><br><br>
            <b>① 投資組合優化（Portfolio Optimization）：</b><br>
            管理 10,000 支股票的最優配置問題，傳統電腦需要嘗試的組合數遠超宇宙原子數。
            量子退火（D-Wave 的核心技術）已被 Volkswagen、Fujitsu、富士通用於
            實際的物流和金融優化問題。當這個技術達到量子優越性，
            <b>擁有量子最優化引擎的基金，將系統性地榨乾所有用傳統演算法的競爭對手</b>。<br><br>
            <b>② 量子蒙地卡羅（Quantum Monte Carlo）：</b><br>
            衍生性商品定價（期權、期貨、結構性商品）依賴蒙地卡羅模擬，
            傳統方法收斂速度是 1/√N，量子版本是 1/N——<b>指數級加速</b>。
            摩根大通、高盛、匯豐已公開發表量子金融研究論文，秘密部署更早。<br><br>
            <b>③ 即時風險計算（Real-Time Risk Management）：</b><br>
            2008 年金融危機的部分原因是銀行無法即時計算跨資產類別的相關風險。
            量子電腦可在毫秒內完成全行業壓力測試，讓「下一次金融危機」的系統性風險可被即時偵測。<br><br>
            <b>百倍股邏輯：</b>金融業有錢、有動機、受監管壓力，是量子計算最快付費的買方市場。
            第一家提供量子金融 SaaS 的公司，將面對一個<b>無限預算的客戶群</b>。<br><br>
            <b>受益公司：</b>D-Wave Systems（量子退火，已上市）、Zapata Computing（已合併）、
            QC Ware（私人，Goldman Sachs 投資）、Multiverse Computing（私人，BBVA 合作）""",
        ),
        (
            "🌍 路徑七：量子氣候工程（Quantum Climate Intelligence）",
            "#00FF9D",
            "最大的 TAM——解決人類文明級別的問題，政府預算是後盾",
            """<b>第一性原則：氣候變遷是分子層面的量子問題，傳統電腦的氣候模型本質上是粗糙近似。</b><br><br>
            <b>① 碳捕捉催化劑設計（Carbon Capture 2.0）：</b><br>
            現有 DAC（直接空氣碳捕捉）成本約 $400-$1000/噸 CO₂，太貴無法規模化。
            成本瓶頸在於催化劑效率——而找到最優催化劑就是一個分子模擬問題。
            量子電腦可在原子層面設計出效率高 10 倍的碳捕捉材料，
            讓 DAC 成本降至 $50/噸以下，打開 <b>$10T 級別的碳市場</b>。<br><br>
            <b>② 量子氣候模型（Quantum Climate Simulation）：</b><br>
            現有最先進氣候模型（如 CMIP6）解析度約 100km，無法預測區域性極端氣候。
            量子計算可將解析度提升至 1km，讓農業、保險業、城市規劃獲得前所未有的
            氣候預測精度——<b>這是一個每年 $500B 的風險管理市場</b>。<br><br>
            <b>③ 量子智慧電網（Quantum Grid Optimization）：</b><br>
            當太陽能 + 風能 + 電池 + 電動車充電站構成複雜的動態電網，
            傳統優化算法在毫秒內無法求解最優調度。量子算法可實現<b>零浪費的即時電網調度</b>，
            讓可再生能源滲透率從 40% 突破至 90% 以上，徹底解決棄電問題。<br><br>
            <b>百倍股邏輯：</b>氣候問題有<b>政府強制預算（全球碳稅、ESG 合規）</b>做為後盾，
            不是依賴市場自願購買——這是最確定的長期需求之一。
            解決氣候問題的公司，其 TAM 是無上限的，因為問題的規模就是整個地球經濟體。<br><br>
            <b>受益公司：</b>Quantinuum（化學模擬）、IBM Quantum（與 Boeing 合作航空材料）、
            SandboxAQ（Google 分拆，量子 AI 應用）、
            以及間接受益的 CEG/VST 核能股（量子優化電網後，核能的 24/7 穩定電力優勢更大）""",
        ),
    ]

    for title, color, subtitle, body in q_paths:
        with st.expander(f"**{title}**", expanded=False):
            st.markdown(
                f'<div style="display:inline-block;background:rgba(0,0,0,0.3);'
                f'border:1px solid {color}55;border-radius:6px;'
                f'padding:4px 12px;margin-bottom:10px;">'
                f'<span style="font-family:\'JetBrains Mono\',monospace;font-size:10px;'
                f'color:{color};letter-spacing:2px;">{subtitle}</span></div>',
                unsafe_allow_html=True
            )
            st.markdown(
                f'<div style="background:rgba(255,255,255,0.02);border:1px solid {color}22;'
                f'border-left:3px solid {color};border-radius:0 10px 10px 0;'
                f'padding:16px 20px;font-size:22px;color:rgba(200,215,230,0.85);line-height:1.85;">'
                f'{body}</div>',
                unsafe_allow_html=True
            )

    # 量子百倍股整體投資邏輯總結
    st.markdown(
        '<div style="margin-top:20px;background:rgba(0,255,255,0.03);'
        'border:1px solid rgba(0,255,255,0.2);border-radius:12px;padding:20px 24px;">'
        '<div class="bg26c" style="color:#00FFFF;margin-bottom:10px;">'
        '⚛️ 量子百倍股七條路徑總覽 — 確定性排序</div>'
        '<div style="font-size:22px;color:rgba(200,215,230,0.8);line-height:2.0;">'
        '🔴 <b style="color:#FF3131;">最確定（5年內）</b>：路徑三 密碼學末日重建（監管強制，無法逃避）<br>'
        '🟠 <b style="color:#ADFF2F;">高確定（5-8年）</b>：路徑四 量子感應器（不需量子電腦，現在就能商業化）<br>'
        '🟡 <b style="color:#FF9A3C;">中確定（8-12年）</b>：路徑六 量子金融霸權（金融業已秘密部署）<br>'
        '🔵 <b style="color:#00BFFF;">需要突破（10-15年）</b>：路徑五 分子模擬、路徑七 氣候工程<br>'
        '🟣 <b style="color:#E040FB;">高風險高潛力（不確定）</b>：路徑一 月球量子計算、路徑二 自駕中樞<br><br>'
        '<b>統帥建議倉位配置：</b>密碼學重建（40%）+ 量子感應器（30%）+ 月球/自駕中樞（20%）+ 其他（10%）<br>'
        '<span style="font-size:18px;color:rgba(160,176,208,0.5);">'
        '每條路徑總倉位控制在 1-2%，量子板塊合計不超過 5-8% 的總資金。</span>'
        '</div></div>',
        unsafe_allow_html=True
    )

    # 量子百倍股風險警告
    st.markdown("""<div class="bgw" style="margin-top:10px;">
    ⚠️ 量子百倍股特別風險警告：量子股是「技術期權」，不是「確定性成長股」。
    持倉應以總資金 2-5% 為上限，虧損 50% 不罕見。必須搭配 6.2 節法庭分析提示詞深度研究後再決策。
    統帥看好這個賽道的邏輯是「物理可行性 + 市場未定價」的組合——這才是百倍股的基因，
    但需要 5-10 年的持有耐心與對本金歸零風險的心理承受能力。
    </div>""", unsafe_allow_html=True)

    # ════════════════════════════════════════════════════
    # BLOCK C：DNA 掃描引擎輸入區
    # ════════════════════════════════════════════════════
    st.divider()
    st.markdown('<div class="bg28">🧬 7D DNA 掃描引擎</div>', unsafe_allow_html=True)

    PRESETS = {
        "⚡ AI 算力": "NVDA, AMD, AVGO, ARM, SMCI, ALAB",
        "☢️ 核能/SMR": "CEG, VST, NNE, OKLO, SMR",
        "🤖 機器人": "TSLA, ISRG, RXRX, ACMR, BDTX",
        "🌐 AI 物理化": "TSLA, PLTR, AAPL, GOOGL, META, SOUN",
        "⚛️ 量子中樞": "IONQ, RGTI, QBTS, QUBT, ARQQ, IBM, GOOGL, MSFT",
        "🛡️ 國防太空": "RKLB, LUNR, PLTR, HII, ACHR",
        "🇹🇼 台股潛力": "3529.TW, 2382.TW, 6531.TW, 3231.TW, 6550.TW",
    }

    in_col, pre_col = st.columns([2, 1])
    with pre_col:
        st.markdown('<div class="bgml" style="margin-top:10px;">快速賽道範本</div>', unsafe_allow_html=True)
        preset_sel = st.selectbox("", list(PRESETS.keys()), key="bg_preset_sel", label_visibility="collapsed")
        if st.button("📥 載入範本", key="bg_load", use_container_width=True):
            # ✅ 直接寫入 text_input 的 session_state key，才能正確更新
            st.session_state['bagger_tickers_in'] = PRESETS[preset_sel]
            st.rerun()
    with in_col:
        tickers_input = st.text_input(
            "🎯 輸入股票代號（逗號分隔，台股加 .TW/.TWO）",
            value="NVDA, PLTR, 3529.TW, 2382.TW, RKLB, IONQ",
            key="bagger_tickers_in"
        )

    # ════════════════════════════════════════════════════
    # BLOCK C-1：範本第一性原則深度論述（依選中範本動態渲染）
    # ════════════════════════════════════════════════════

    PRESET_THESIS = {

        "⚡ AI 算力": {
            "color": "#FFD700",
            "stage": "成長加速期 🚀",
            "tagline": "算力是 AI 時代的電力——工業革命中所有電力公司都是百倍股",
            "why_100x": """
            <b>百倍股物理邏輯：</b>AI 每一層應用（大模型訓練、推論、邊緣部署）都必須經過算力這一層。
            不管誰贏得 AI 應用層競爭，算力基礎設施都是贏家。這是「賣鏟子」的邏輯，
            但比賣鏟子更好——因為 AI 時代的鏟子有<b>網路效應與標準壟斷</b>。<br><br>
            <b>萊特定律驗證：</b>GPU 算力每 2 年翻倍、每 FLOP 成本每年下降 ~30%，
            但市場對算力的需求增速更快（每年 +40-60%），形成「成本下降但需求更快增長」的完美飛輪。<br><br>
            <b>TAM 計算：</b>2024 年全球 AI 算力市場 ~$100B → 2030 年預估 $1T+，
            CAGR 約 40%。按百倍公式：EPS 成長 10x × PE 擴張 10x = 100x。
            在 TAM 從 $100B → $1T 的過程中，龍頭企業的 EPS 有充分空間成長 10 倍以上。<br><br>
            <b>護城河分析：</b><br>
            • NVDA：CUDA 生態系鎖定效應，15 年積累，競爭者需要 5-10 年才能打破<br>
            • AVGO：客製化 ASIC（Google TPU、Meta MTIA、Apple Neural Engine），毛利率 >70%<br>
            • ARM：每台 AI 裝置（手機、邊緣 AI）都需要 ARM 架構，收授權費，輕資產高毛利<br>
            • SMCI：AI 伺服器直接冷卻（液冷），受益算力密度提升，市場分額快速擴張
            """,
            "risk": "AMD 追趕速度、客製化 ASIC 侵蝕 NVIDIA 份額、AI 泡沫週期性回調、中國禁令影響",
            "companies": [
                ("NVDA", "算力帝國", "CUDA 生態壟斷，Data Center 年營收 $80B+，最確定的 AI 基礎設施龍頭"),
                ("AMD", "挑戰者", "MI300X 搶占推論市場，PE 擴張空間大於 NVDA，勝在估值"),
                ("AVGO", "隱形冠軍", "客製化 ASIC + 網路晶片，Google/Meta/Apple 都是大客戶，毛利率 >70%"),
                ("ARM", "授權壟斷者", "所有 AI 邊緣裝置的架構授權，輕資產商業模式，真正的躺贏型公司"),
                ("SMCI", "算力散熱王", "液冷伺服器市場第一，算力密度越高越有利，高成長但波動極大"),
                ("ALAB", "光子互連", "AI 算力叢集內部通訊的下一代基礎設施，規模還小但增速驚人"),
            ],
        },

        "☢️ 核能/SMR": {
            "color": "#00FF9D",
            "stage": "黎明早期 🌅 — 最佳佈局窗口",
            "tagline": "AI 的電力危機 × 碳中和 × 能源安全——三股力量同時推動核能復興",
            "why_100x": """
            <b>第一性原則：能量密度決定一切。</b><br>
            1 公斤鈾的能量 = 1 公斤煤炭的 300 萬倍。這不是觀點，是物理定律。<br><br>
            <b>AI 電力危機的量化：</b>一個 ChatGPT 回應消耗的電力是 Google 搜尋的 10 倍。
            ChatGPT 一天的電力消耗相當於 17 萬個美國家庭。
            到 2030 年，全球 AI 數據中心電力需求將超過法國全國用電量。
            太陽能和風能無法提供 24/7 穩定的基載電力——核能是唯一解答。<br><br>
            <b>SMR 的破壞式創新邏輯：</b><br>
            傳統大型核電站：$10B+ 成本，15+ 年建設，只有主權國家才建得起。<br>
            SMR（小型模組反應爐）：$300M-$1B 成本，5 年建設，像工廠一樣批量製造，
            直接部署在數據中心旁邊。Microsoft/Google/Amazon 已簽署 SMR 採購協議。<br><br>
            <b>PE 擴張的催化劑：</b>市場 10 年前認為核能是「夕陽產業」，PE 被壓到底部。
            當共識逆轉（已開始發生），PE 從 10x 擴張到 30-50x，本身就是 3-5 倍。
            再加上 EPS 成長，百倍空間成立。<br><br>
            <b>TAM：</b>全球電力市場 $3T，核能目前佔 ~10%，
            SMR 目標 2040 年佔據新增電力 30% = $300B+ 新市場
            """,
            "risk": "核能監管不確定性、SMR 技術商業化延遲、可再生能源成本持續下降競爭、政治風向逆轉",
            "companies": [
                ("CEG", "美國核電龍頭", "最大核電運營商，Microsoft 長期購電協議，Three Mile Island 重啟，現金流確定"),
                ("VST", "核 + 天然氣", "德州電力市場龍頭，AI 數據中心電力採購熱點，近期股價強勁"),
                ("NNE", "SMR 純種股", "純 SMR 開發商，市值極小，高風險高潛力，技術驗證是關鍵里程碑"),
                ("OKLO", "Sam Altman 背書", "OpenAI CEO 擔任董事會主席，微型核反應爐，技術前沿但商業化仍早期"),
                ("SMR", "NuScale Power", "全球第一個獲 NRC 認證的 SMR 設計，但近期有客戶取消訂單的風險，需深研"),
            ],
        },

        "🤖 機器人": {
            "color": "#00BFFF",
            "stage": "黎明期 🌅 — 技術突破剛發生",
            "tagline": "人口老齡化是不可逆的物理事實——機器人是唯一解藥，且 AI 讓它終於看得見想得到",
            "why_100x": """
            <b>為什麼現在是黎明期而不是更早？</b><br>
            機器人不是新技術，工廠機器人已存在 50 年。但過去的機器人是「盲目的」——
            只能在嚴格控制的環境中執行預設動作，遇到意外就停機。<br><br>
            <b>2023-2024 年發生了什麼？</b><br>
            大語言模型 + 視覺模型（GPT-4V、Gemini、Claude）讓機器人第一次真正「看得見」：
            辨識不規則物體、理解人類指令、在混沌環境中自主決策。
            這是質變，不是量變。之前 50 年的機器人技術積累突然變得可用。<br><br>
            <b>人口老齡化的不可逆性：</b><br>
            日本：65 歲以上人口 30%，勞動力短缺已是國家緊急問題。
            中國：人口拐點已過，2030 年勞動人口絕對減少。
            德國/韓國/台灣：製造業嚴重缺工。
            這不是政策可以逆轉的趨勢——機器人是唯一的數學解。<br><br>
            <b>TAM 計算：</b><br>
            全球製造業用工成本 $5T/年 → 機器人替代率若達 20% = $1T TAM<br>
            醫療護理機器人（老年照護）$500B+ TAM<br>
            物流/倉儲機器人（Amazon 效應全球複製）$300B TAM<br><br>
            <b>萊特定律驗證：</b>工業機器人每 10 年成本下降 50%，
            現在 AI 視覺系統的加入讓功能指數提升，但成本繼續下降——典型的破壞式創新軌跡
            """,
            "risk": "AI 視覺在非結構化環境的可靠性、機器人訓練數據缺乏、勞工政策阻力、資本密集度高",
            "companies": [
                ("TSLA", "Optimus 人形機器人", "Elon 宣稱 Optimus 比汽車業務更大。FSD 的電腦視覺技術直接遷移，工廠先試點"),
                ("ISRG", "手術機器人壟斷者", "Da Vinci 手術機器人市佔率 >80%，裝機量飛輪效應，ROE >20%，最確定的醫療機器人龍頭"),
                ("RXRX", "AI 藥物機器人", "用 AI 機器人做藥物篩選，整合量子模擬方向，燒錢期但毛利率結構良好"),
                ("ACMR", "半導體清洗機器人", "晶圓清洗設備，台積電/三星供應商，國產替代概念 + AI 擴產受益"),
                ("BDTX", "精準醫療機器人", "蛋白降解靶向藥物，用 AI 機器人加速研發管線，小市值高風險"),
            ],
        },

        "🌐 AI 物理化": {
            "color": "#E040FB",
            "stage": "黎明加速 🌅🚀 — PE 擴張最強烈的賽道",
            "tagline": "模型的價值由部署規模決定——誰把 AI 最深度嵌入物理世界，誰就是下一個 Tesla",
            "why_100x": """
            <b>核心論點：AI 應用層的百倍股不是「最強模型」，而是「最深物理化」。</b><br><br>
            <b>Tesla 模式的本質：</b>Tesla 不是最快的電動車，也不是最聰明的 AI 公司，
            但它是第一個把「軟體定義」深度嵌入物理產品（汽車）的公司。
            結果：硬體賣一次，軟體升級永遠收費，數據護城河不斷加深。
            這個模式正在被複製到所有物理場景。<br><br>
            <b>物理化 AI 的百倍股方程式：</b><br>
            物理場景（每天被數十億人使用）× AI 深度嵌入（不可替代）× 軟體化收費 = 無限複利<br><br>
            <b>五個物理化前線：</b><br>
            ① <b>自動駕駛</b>：Tesla FSD、Waymo → 汽車變成「帶輪子的 AI 訂閱服務」<br>
            ② <b>AI 眼鏡/穿戴</b>：Meta Ray-Ban → 現實世界的 AI 入口，永遠在線，數據飛輪<br>
            ③ <b>AI 手機</b>：Apple Intelligence → 最大的 AI 分發平台（16 億台裝置），App Store 2.0<br>
            ④ <b>智慧工廠</b>：PLTR AIP → 把 AI 嵌入每個製造決策，政府/軍事長期合約<br>
            ⑤ <b>語音 AI 物聯網</b>：SoundHound → 汽車/餐廳/醫院的語音 AI 界面，不被大廠直接替代<br><br>
            <b>PE 擴張邏輯：</b>AI 物理化公司目前的 PE 反映的是「傳統硬體公司」，
            市場尚未定價「軟體化訂閱」的 ARR 飛輪。一旦市場共識轉換，
            PE 重估就是 3-10 倍，再加 EPS 成長 = 百倍
            """,
            "risk": "AI 監管（自駕事故/隱私）、大廠自研替代（Google/Amazon 自建語音 AI）、估值泡沫化後的回調",
            "companies": [
                ("TSLA", "AI 物理化原型", "Optimus + FSD + Dojo = 三條 AI 物理化飛輪，但估值已大幅反映，需等回調"),
                ("PLTR", "政府/企業 AI 作業系統", "AIP 把 AI 嵌入決策流程，政府合約黏性極高，ROE 剛轉正，成長加速"),
                ("AAPL", "AI 最大分發管道", "16 億台裝置 × Apple Intelligence = 史上最大 AI 應用商店，但增速偏慢"),
                ("GOOGL", "AI 多面手", "Waymo（自駕）+ Gemini（模型）+ 量子計算，但龐大體量限制百倍空間"),
                ("META", "AI 穿戴物理化", "Ray-Ban 智慧眼鏡正在創造新的 AI 入口，廣告 AI 優化已貢獻財報"),
                ("SOUN", "語音 AI 純種股", "汽車/醫療/餐飲的語音界面，市值小、成長快、燒錢中，高風險高潛力"),
            ],
        },

        "⚛️ 量子中樞": {
            "color": "#00FFFF",
            "stage": "黎明前夜 🌑🌅 — 市場幾乎未定價",
            "tagline": "7 條破壞式創新路徑已在上方「量子百倍股深度研究」專區完整呈現",
            "why_100x": """
            <b>統帥聲明：量子是本系統中風險最高、潛力最大的賽道。</b><br><br>
            量子百倍股的完整第一性原則論述已在本節上方「量子百倍股深度研究」專區詳細呈現，
            包含 7 條破壞式創新路徑：<br><br>
            🌕 <b>路徑一</b>：月球量子計算平台（天然超低溫環境解決退相干瓶頸）<br>
            🚗 <b>路徑二</b>：全自動駕駛量子中樞神經（跨品牌 AI 協調層）<br>
            ⚔️ <b>路徑三</b>：密碼學末日重建 PQC（最確定，監管強制，2030 年前）<br>
            🔬 <b>路徑四</b>：量子感應器革命（不需量子電腦，現在就能商業化）<br>
            💊 <b>路徑五</b>：量子分子模擬（固態電池 + 藥物設計 + 氮固化）<br>
            📈 <b>路徑六</b>：量子金融霸權（投資組合優化 + 衍生品定價）<br>
            🌍 <b>路徑七</b>：量子氣候工程（碳捕捉 + 電網優化）<br><br>
            <b>投資組合建議：</b>以路徑三（ARQQ）和路徑四（感應器公司）作為確定性錨點，
            以路徑一/二（IONQ、RGTI）作為技術期權倉位。<br><br>
            <b>注意：IBM 和 GOOGL 在此名單中代表「量子計算大廠進度追蹤指標」，
            而非純量子百倍股——它們的量子業務對整體市值影響極小。</b>
            """,
            "risk": "量子退相干尚未工程化解決、商業化時間表持續延後、政府補貼縮減、被大廠研究部門邊緣化",
            "companies": [
                ("IONQ", "離子阱量子先鋒", "最高量子體積指標，與 Airbus/Hyundai/摩根大通有合作，商業化最積極"),
                ("RGTI", "量子感測 + 計算", "超導量子比特路線，量子感應器應用有近期商業化機會，市值小波動大"),
                ("QBTS", "D-Wave 量子退火", "量子退火（非通用量子電腦），已用於物流/金融優化，是最接近商業化的量子應用"),
                ("QUBT", "光子量子計算", "室溫運作的光子量子網路，不需要稀釋冷凍機，若技術成立是革命性的"),
                ("ARQQ", "量子密碼學", "PQC + QKD 商業部署，路徑三的最直接受益者，確定性最高的量子純種股"),
                ("IBM", "量子計算標準制定者", "IBM Quantum 路線圖最透明，1000+ 量子比特，適合追蹤量子進度基準"),
                ("GOOGL", "量子霸權宣告者", "Willow 晶片，量子計算研究領先，但對整體估值影響小，追蹤技術進度用"),
                ("MSFT", "拓撲量子押注", "Majorana 拓撲量子比特路線，錯誤率比超導量子比特低 1000 倍，若成立是顛覆性的"),
            ],
        },

        "🛡️ 國防太空": {
            "color": "#ADFF2F",
            "stage": "成長早期 📈 — 地緣政治長期驅動",
            "tagline": "戰爭改變武器需求，太空成為新戰場——政府預算是最確定的護城河",
            "why_100x": """
            <b>第一性原則：每一次戰爭技術革命都誕生了百倍股。</b><br><br>
            一戰：化工 + 坦克 → 百倍股誕生<br>
            二戰：航空 + 雷達 → Boeing/Raytheon 前身<br>
            冷戰：核武 + 衛星 → 洛克希德/諾斯羅普<br>
            <b>AI 戰爭時代（2024-2040）：無人機 + 太空 + AI 偵測 → 下一批百倍股</b><br><br>
            <b>烏克蘭戰爭的啟示（第一性原則驗證）：</b><br>
            Starlink 讓烏克蘭軍隊在失去傳統通訊後仍能指揮 → 衛星通訊是現代戰爭的神經系統<br>
            廉價無人機擊落昂貴坦克 → 戰爭成本結構正在被顛覆，低成本智能武器贏<br>
            AI 偵測 + 無人機蜂群 → 傳統空軍優勢消失，AI 反應速度勝過人類飛行員<br><br>
            <b>太空的百倍股邏輯：</b><br>
            地球軌道正在商業化，衛星部署成本從 $10B → $1M（SpaceX Falcon 9 效應）。
            這意味著以前只有主權國家才能做的衛星應用，現在私人公司可以做：<br>
            • 全球即時監控（任何地點每 30 分鐘重訪一次）<br>
            • 衛星寬頻（偏遠地區的網路基礎設施）<br>
            • 精確導航替代（GPS 備份）<br>
            • 月球/火星任務（NASA 外包計劃）<br><br>
            <b>政府合約的護城河：</b>美國國防預算 $886B/年，五年期合約，不受景氣循環影響，
            比任何商業客戶都穩定。一旦進入供應商名單，替換成本極高。
            """,
            "risk": "和平進展導致國防預算縮減、政府合約延遲/取消、SpaceX 未上市導致最大受益者無法直接投資",
            "companies": [
                ("RKLB", "火箭實驗室", "Neutron 中型火箭 + Electron 小型火箭，太空版 SpaceX，衛星部署 + 月球任務，市值仍小"),
                ("LUNR", "月球快遞", "Intuitive Machines，NASA 月球著陸任務承包商，阿提米斯計劃直接受益"),
                ("PLTR", "AI 戰場作業系統", "Maven Smart System + AIP，美軍 AI 決策系統的核心供應商，政府合約黏性最高"),
                ("HII", "航母製造壟斷者", "全美唯一的核動力航母製造商，技術壟斷 + 政府剛需，類公用事業的穩健成長"),
                ("ACHR", "城市空中交通", "電動垂直起降飛行器（eVTOL），軍事後勤 + 民用航空，技術驗證關鍵期"),
            ],
        },

        "🇹🇼 台股潛力": {
            "color": "#FF9A3C",
            "stage": "特殊賽道 🇹🇼 — AI 供應鏈深度受益",
            "tagline": "台灣是全球 AI 供應鏈的不可替代樞紐——沒有台灣半導體，AI 革命就沒有零件",
            "why_100x": """
            <b>第一性原則：AI 算力的每一個 FLOP 都必須先經過台灣製造。</b><br><br>
            <b>台灣的不可替代性（物理現實）：</b><br>
            TSMC 持有全球 90%+ 的先進製程（3nm/2nm）產能。
            NVIDIA H100/H200/B200 全部在 TSMC 生產。
            AMD、Apple、Qualcomm 的 AI 晶片也在 TSMC。
            這不是市場選擇，是 10 年技術累積造成的物理壁壘。<br><br>
            <b>台股中小型 AI 受益股的百倍基因：</b><br>
            大公司（台積電）的百倍機會已過，但 AI 供應鏈的長尾受益者仍在早期：<br>
            ① 封裝測試（CoWoS 先進封裝）→ AI 晶片需要 HBM 記憶體與 GPU 封裝在一起<br>
            ② PCB/散熱（液冷板、銅箔基板）→ 算力密度提升，熱管理成為瓶頸<br>
            ③ 電源管理（PMIC / VR）→ 每台 AI 伺服器有 10-20 個電源模組<br>
            ④ 連接器/線纜（高速傳輸）→ GPU 叢集內部通訊的「毛細血管」<br><br>
            <b>台股與美股的差異定價機會：</b><br>
            相同的 AI 供應鏈概念，台股的本益比通常比美股低 30-50%，
            加上台幣升值效應（AI 美元收入），雙重紅利。<br><br>
            <b>個股說明（依代號）：</b><br>
            3529（力旺電子）：IP 授權商業模式，嵌入式非揮發記憶體，每台 AI 晶片都需要<br>
            2382（廣達）：AI 伺服器最大 ODM，NVIDIA GB200 NVL 主要代工夥伴<br>
            6531（愛普）：高頻測試介面，AI 晶片測試必需，高毛利率<br>
            3231（緯創）：AI 伺服器 + 機器人，正在轉型高毛利 AI 硬體<br>
            6550（北極星藥業）：AI 醫療賽道，生技 × AI 雙引擎，但需獨立評估
            """,
            "risk": "台海地緣政治風險（最大尾端風險）、客戶集中度（NVIDIA 訂單變化直接衝擊）、人民幣貶值競爭",
            "companies": [
                ("3529.TW", "力旺電子", "嵌入式非揮發記憶體 IP 授權，每顆 AI 晶片都需要，輕資產高毛利，台版 ARM"),
                ("2382.TW", "廣達電腦", "全球最大 AI 伺服器代工，GB200 NVL 的核心製造夥伴，受益 NVIDIA 擴產"),
                ("6531.TW", "愛普科技", "高頻測試介面卡，AI 晶片測試必需，毛利率 >60%，市值仍偏小"),
                ("3231.TW", "緯創資通", "AI 伺服器 + 機器人雙主軸，股價已啟動但本益比仍低於美股同業"),
                ("6550.TW", "北極星藥業", "AI 藥物研發賽道，生技 × AI，需獨立深度研究基本面"),
            ],
        },
    }

    # 動態渲染選中範本的深度分析
    if preset_sel in PRESET_THESIS:
        thesis = PRESET_THESIS[preset_sel]
        tc = thesis["color"]

        with st.expander(
            f"📖 {preset_sel} 第一性原則深度論述 — 為什麼這個賽道能誕生百倍股？（點此展開）",
            expanded=False
        ):
            # 標頭
            st.markdown(
                f'<div style="background:rgba(0,0,0,0.3);border:1px solid {tc}33;'
                f'border-left:4px solid {tc};border-radius:0 10px 10px 0;'
                f'padding:14px 20px;margin-bottom:16px;">'
                f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:9px;'
                f'color:{tc}88;letter-spacing:4px;text-transform:uppercase;margin-bottom:4px;">'
                f'景氣循環位置</div>'
                f'<div style="font-size:18px;font-weight:800;color:{tc};">{thesis["stage"]}</div>'
                f'<div style="font-size:13px;color:rgba(200,215,235,0.75);margin-top:6px;">'
                f'{thesis["tagline"]}</div>'
                f'</div>',
                unsafe_allow_html=True
            )

            # 百倍股論述
            st.markdown(
                f'<div style="background:rgba(255,255,255,0.02);border:1px solid {tc}22;'
                f'border-left:3px solid {tc};border-radius:0 10px 10px 0;'
                f'padding:16px 20px;font-size:22px;color:rgba(200,215,230,0.85);'
                f'line-height:1.85;margin-bottom:16px;">'
                f'{thesis["why_100x"]}</div>',
                unsafe_allow_html=True
            )

            # 風險警告
            st.markdown(
                f'<div style="background:rgba(255,100,100,0.04);border:1px solid rgba(255,100,100,0.2);'
                f'border-radius:8px;padding:10px 16px;margin-bottom:16px;">'
                f'<span style="font-family:\'JetBrains Mono\',monospace;font-size:10px;'
                f'color:rgba(255,107,107,0.7);letter-spacing:2px;">⚠️ 核心風險</span>'
                f'<div style="font-size:22px;color:rgba(255,170,170,0.75);margin-top:4px;">'
                f'{thesis["risk"]}</div></div>',
                unsafe_allow_html=True
            )

            # 個股速覽表
            st.markdown(
                f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:9px;'
                f'color:{tc}88;letter-spacing:4px;text-transform:uppercase;margin-bottom:8px;">'
                f'📊 範本個股速覽</div>',
                unsafe_allow_html=True
            )
            for sym, name, desc in thesis["companies"]:
                st.markdown(
                    f'<div style="display:flex;align-items:flex-start;gap:14px;'
                    f'border-bottom:1px solid rgba(255,255,255,0.04);padding:8px 0;">'
                    f'<div style="min-width:70px;font-family:\'JetBrains Mono\',monospace;'
                    f'font-size:13px;font-weight:700;color:{tc};">{sym}</div>'
                    f'<div style="min-width:100px;font-size:13px;font-weight:600;'
                    f'color:rgba(220,230,245,0.9);">{name}</div>'
                    f'<div style="font-size:13px;color:rgba(160,176,208,0.6);flex:1;">{desc}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )

    run_scan = st.button("🧬 啟動 7D DNA 基因掃描", type="primary", use_container_width=True, key="run_bg_scan")

    if run_scan:
        tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]
        if not tickers:
            st.warning("⚠️ 請輸入至少一檔股票。")
            st.stop()

        results = []
        prog     = st.progress(0)
        stat_ph  = st.empty()

        import math as _math

        with st.spinner("🧠 正在解碼企業財務 DNA…"):
            for idx, sym in enumerate(tickers):
                stat_ph.markdown(f'<div class="bg26">▶ 解碼 {sym}… ({idx+1}/{len(tickers)})</div>', unsafe_allow_html=True)
                try:
                    fetch_sym = sym
                    bare = sym.replace('.TW','').replace('.TWO','')
                    if bare.isdigit() and len(bare) >= 4 and not sym.endswith(('.TW','.TWO')):
                        fetch_sym = sym + '.TW'

                    tk   = yf.Ticker(fetch_sym)
                    info = tk.info

                    # .TWO fallback：上櫃股（純數字且 .TW 抓不到）
                    if (bare.isdigit() and len(bare) >= 4
                            and not sym.endswith('.TWO')
                            and not info.get('marketCap') and not info.get('shortName')):
                        _tk2 = yf.Ticker(bare + '.TWO')
                        _i2  = _tk2.info
                        if _i2.get('marketCap') or _i2.get('shortName'):
                            tk, info, fetch_sym = _tk2, _i2, bare + '.TWO'

                    def _g(k, d=0):
                        v = info.get(k, d)
                        return d if v is None else v

                    currency     = info.get("currency", "USD")
                    mkt_cap_b    = _g("marketCap", 0) / 1e9
                    name_s       = info.get("shortName", sym)[:24]
                    industry_s   = info.get("industry", "N/A")
                    roe          = _g("returnOnEquity")
                    rev_growth   = _g("revenueGrowth")
                    gross_margin = _g("grossMargins")
                    op_margin    = _g("operatingMargins")
                    fcf_raw      = _g("freeCashflow", 0)
                    total_rev    = _g("totalRevenue", 1)
                    fcf_pct      = (fcf_raw / total_rev) if total_rev > 0 and fcf_raw != 0 else 0
                    div_yield    = _g("dividendYield")
                    peg          = _g("pegRatio")
                    fwd_pe       = _g("forwardPE")
                    trail_pe     = _g("trailingPE")
                    price        = _g("currentPrice", _g("regularMarketPrice"))
                    ps_ratio     = _g("priceToSalesTrailing12Months")   # P/S for pre-profit
                    eps_trail    = _g("trailingEps")                     # detect pre-profit
                    insider_pct  = _g("heldPercentInsiders")             # D8: Skin in the Game

                    # ── 判斷是否為「燒錢 / 預盈利」公司 ──
                    # 條件：EPS < 0 或 ROE < 0（虧損）且 trailingPE 不存在
                    is_pre_profit = (eps_trail < 0) or (roe < 0 and trail_pe == 0)

                    # ── D1: ROE 引擎 OR 燒錢替代指標 (22) ──
                    if is_pre_profit:
                        # 燒錢公司：用「毛利率改善軌跡」替代 ROE，上限調至 15（不確定折扣）
                        d1 = 15 if gross_margin > 0.60 else 10 if gross_margin > 0.40 else 6 if gross_margin > 0.20 else 0
                    else:
                        d1 = 22 if roe > 0.25 else 17 if roe > 0.20 else 10 if roe > 0.15 else 4 if roe > 0.10 else 0

                    # ── D2: 營收加速度 (20) — 對燒錢公司更重要 ──
                    d2 = 20 if rev_growth > 0.30 else 14 if rev_growth > 0.20 else 8 if rev_growth > 0.10 else 3 if rev_growth > 0.05 else 0

                    # ── D3: 毛利護城河 (17) ──
                    d3 = 17 if gross_margin > 0.60 else 12 if gross_margin > 0.40 else 6 if gross_margin > 0.25 else 2 if gross_margin > 0.10 else 0

                    # ── D4: 市值空間 (15) ──
                    d4 = 0
                    if currency in ("TWD","HKD"):
                        d4 = 15 if mkt_cap_b < 5 else 10 if mkt_cap_b < 20 else 5 if mkt_cap_b < 100 else 2 if mkt_cap_b < 500 else 0
                    else:
                        d4 = 15 if mkt_cap_b < 0.5 else 12 if mkt_cap_b < 3 else 7 if mkt_cap_b < 15 else 3 if mkt_cap_b < 50 else 0

                    # ── D5: 再投資力 (5) — 燒錢公司幾乎必然 0 配息，自動得滿分 ──
                    d5 = 5 if div_yield < 0.005 else 3 if div_yield < 0.02 else 1 if div_yield < 0.04 else 0

                    # ── D6: 盈利品質 OR 現金跑道代理 (3) ──
                    if is_pre_profit:
                        # 燒錢公司：用 P/S 比率評估「市場給的信任溢價」是否合理
                        # P/S < 10 代表估值相對保守（對高成長公司而言），給分
                        d6 = 3 if (ps_ratio > 0 and ps_ratio < 5) else 2 if (ps_ratio > 0 and ps_ratio < 15) else 1 if rev_growth > 0.30 else 0
                    else:
                        d6 = 3 if fcf_pct > 0.15 else 1 if fcf_pct > 0.05 else 0

                    # ── D7: 安全邊際 (2) — 燒錢公司 PEG 無意義，改用 P/S vs 成長率 ──
                    if is_pre_profit:
                        # 燒錢替代：若 P/S < 2× 營收成長率（%），視為有安全邊際
                        ps_growth_ratio = ps_ratio / (rev_growth * 100) if (ps_ratio > 0 and rev_growth > 0) else 999
                        d7 = 2 if ps_growth_ratio < 0.3 else 1 if ps_growth_ratio < 0.7 else 0
                    else:
                        d7 = 2 if (peg > 0 and peg < 0.5) else 1 if (peg > 0 and peg < 1.0) else 0

                    # ════════════════════════════════════════════════════════
                    # ── D8: 🩸 創辦人利益綁定 / Skin in the Game (8) ──
                    # Chris Mayer：幾乎所有百倍股都有 Owner-Operator 在掌舵
                    # ════════════════════════════════════════════════════════
                    if insider_pct >= 0.20:
                        d8 = 8   # 創辦人仍大量持股，利益高度綁定
                    elif insider_pct >= 0.10:
                        d8 = 6   # 達 10% 門檻，有明顯的內部人利益
                    elif insider_pct >= 0.05:
                        d8 = 3   # 適度持股
                    elif insider_pct >= 0.01:
                        d8 = 1   # 少量持股
                    else:
                        d8 = 0   # 純職業經理人，無利益綁定

                    # ════════════════════════════════════════════════════════
                    # ── D9: 📈 估值擴張潛力 / Valuation Multiple Expansion (5) ──
                    # 低估值 × 高成長 = 百倍股最強催化劑；高 P/E 壓縮未來漲幅
                    # ════════════════════════════════════════════════════════
                    if is_pre_profit:
                        # 燒錢公司：用 P/S 評估估值合理性（D9 已部分重疊 D6，但維度不同）
                        d9 = 5 if (ps_ratio > 0 and ps_ratio < 5)  else \
                             3 if (ps_ratio > 0 and ps_ratio < 10) else \
                             1 if (ps_ratio > 0 and ps_ratio < 20) else 0
                    else:
                        # 盈利公司：P/E 或 PEG 複合評分
                        pe_val = fwd_pe if fwd_pe > 0 else trail_pe
                        if pe_val > 0 and pe_val < 20 and peg > 0 and peg < 1.0:
                            d9 = 5   # P/E 低 + PEG 優秀：最大估值擴張空間
                        elif pe_val > 0 and pe_val < 30:
                            d9 = 4   # P/E < 30：合理估值，有擴張空間
                        elif peg > 0 and peg < 1.5:
                            d9 = 3   # PEG < 1.5：成長相對便宜
                        elif pe_val > 0 and pe_val < 50:
                            d9 = 2   # P/E < 50：輕度高估，擴張有限
                        elif pe_val <= 0 or pe_val == 0:
                            d9 = 1   # 無 P/E 數據，保守給分
                        else:
                            d9 = 0   # P/E ≥ 50：估值過高，易收縮

                    # ════════════════════════════════════════════════════════
                    # ── D10: 🛡️ Rule of 40 / 薩斯定律 — 營業利益擴張 (3) ──
                    # SaaS/高成長公司：Rev Growth(%) + Op Margin(%) > 40 才合格
                    # 防止高毛利但燒錢黑洞的陷阱
                    # ════════════════════════════════════════════════════════
                    rule40_val = (rev_growth * 100) + (op_margin * 100) if (rev_growth and op_margin) else None
                    if rule40_val is not None:
                        if rule40_val >= 60:
                            d10 = 3   # 遠超 Rule of 40，世界級效率
                        elif rule40_val >= 40:
                            d10 = 2   # 通過 Rule of 40，SaaS 合格線
                        elif rule40_val >= 20:
                            d10 = 1   # 未達標但接近，持續觀察
                        else:
                            d10 = 0   # 不達標：成長燒錢但利益率太低
                    else:
                        d10 = 1 if rev_growth and rev_growth > 0.20 else 0  # 數據不足但高成長時保守給分

                    # ── D11: 季度轉折訊號雷達 ──
                    d11_data = {"available":False,"rev_series":[],"gm_series":[],
                                "fcf_series":[],"rev_accel":None,"gm_slope":None,
                                "fcf_slope":None,"inflection_signal":False,
                                "inflection_label":"","trend_cagr":None,
                                "qtrs_to_fcf_positive":None,"rev_qoq_list":[],"quarters":[]}
                    try:
                        import numpy as _np
                        qi = tk.quarterly_income_stmt
                        qc = tk.quarterly_cashflow
                        if qi is not None and not qi.empty and qi.shape[1] >= 4:
                            _RN = ["Total Revenue","Revenue","Net Revenue","Operating Revenue"]
                            _GN = ["Gross Profit","Gross Income"]
                            rv  = next((qi.loc[n] for n in _RN if n in qi.index), None)
                            gv  = next((qi.loc[n] for n in _RN if n in qi.index), None)
                            gp  = next((qi.loc[n] for n in _GN if n in qi.index), None)
                            if rv is not None:
                                rvv = rv.dropna().iloc[:8][::-1]
                                n   = len(rvv)
                                if n >= 4:
                                    d11_data["available"] = True
                                    d11_data["quarters"]  = [str(x)[:7] for x in rvv.index]
                                    rb = [float(v)/1e9 for v in rvv.values]
                                    d11_data["rev_series"] = [round(v,3) for v in rb]
                                    ql = []
                                    for i in range(1,n):
                                        ql.append(round((rb[i]-rb[i-1])/abs(rb[i-1]),4) if rb[i-1]>0 else None)
                                    d11_data["rev_qoq_list"] = ql
                                    yl = []
                                    if n>=5:
                                        for i in range(4,n):
                                            if rb[i-4]>0: yl.append((rb[i]-rb[i-4])/abs(rb[i-4]))
                                    if len(yl)>=2: d11_data["rev_accel"] = round(yl[-1]-yl[-2],4)
                                    if n>=4 and all(v>0 for v in rb):
                                        _sl,_ = _np.polyfit(_np.arange(n),_np.log(rb),1)
                                        _tc = _math.exp(_sl*4)-1
                                        if _tc>0: d11_data["trend_cagr"] = round(_tc,4)
                                    if gp is not None and gv is not None:
                                        gpv = gp.dropna().iloc[:8][::-1]
                                        gvv = gv.dropna().iloc[:8][::-1]
                                        ml  = min(len(gpv),len(gvv))
                                        if ml>=4:
                                            gml = [float(gpv.iloc[i])/float(gvv.iloc[i])
                                                   for i in range(ml) if float(gvv.iloc[i])>0]
                                            if len(gml)>=4:
                                                d11_data["gm_series"] = [round(v,4) for v in gml]
                                                _s,_ = _np.polyfit(_np.arange(len(gml)),gml,1)
                                                d11_data["gm_slope"] = round(float(_s),5)
                                    if qc is not None and not qc.empty:
                                        _FN  = ["Free Cash Flow","FreeCashFlow","Operating Cash Flow"]
                                        fcfr = next((qc.loc[n] for n in _FN if n in qc.index), None)
                                        if fcfr is not None:
                                            fv = fcfr.dropna().iloc[:8][::-1]
                                            nf = len(fv)
                                            if nf>=4:
                                                fb = [float(v)/1e9 for v in fv.values]
                                                d11_data["fcf_series"] = [round(v,3) for v in fb]
                                                _sf,_ = _np.polyfit(_np.arange(nf),fb,1)
                                                d11_data["fcf_slope"] = round(float(_sf),4)
                                                if fb[-1]<0 and _sf>0:
                                                    _q = -fb[-1]/_sf
                                                    if 0<_q<20: d11_data["qtrs_to_fcf_positive"]=round(_q,1)
                                    sigs = []
                                    qv3  = [q for q in ql[-3:] if q is not None]
                                    if len(qv3)>=2 and all(q>0 for q in qv3[-2:]):
                                        sigs.append("🚀 營收連續加速" if (len(qv3)>=3 and qv3[-1]>qv3[-3]) else "📈 營收連續正成長")
                                    if d11_data["gm_slope"] and d11_data["gm_slope"]>0.005: sigs.append("📊 毛利率向上")
                                    if d11_data["fcf_slope"] and d11_data["fcf_slope"]>0.05:
                                        sigs.append("💰 FCF快速收窄" if (d11_data["fcf_series"] and d11_data["fcf_series"][-1]<0) else "💰 FCF持續改善")
                                    if d11_data["rev_accel"] and d11_data["rev_accel"]>0.05: sigs.append("⚡ YoY加速")
                                    if len(sigs)>=2:
                                        d11_data["inflection_signal"]=True
                                        d11_data["inflection_label"]=" · ".join(sigs)
                                    elif len(sigs)==1: d11_data["inflection_label"]=sigs[0]+"（單訊號，觀察）"
                                    else:              d11_data["inflection_label"]="暫無明確轉折訊號"
                    except Exception as _e11:
                        d11_data["inflection_label"] = "季度資料讀取失敗"

                    total = min(d1+d2+d3+d4+d5+d6+d7+d8+d9+d10, 100)

                    if total >= 80:   grade, gcolor = "🔥 SUPER NOVA",  "#FF4500"
                    elif total >= 65: grade, gcolor = "⚡ 百倍候選",    "#FFD700"
                    elif total >= 50: grade, gcolor = "📈 成長潛力",    "#ADFF2F"
                    elif total >= 35: grade, gcolor = "⚖️ 觀察名單",   "#00BFFF"
                    else:             grade, gcolor = "❄️ 不符條件",   "#808080"

                    # ── 市值現實校驗 ──
                    if currency in ("TWD","HKD"):
                        if   mkt_cap_b<5:   cap_tier,realistic_max_x,cap_warn="🔬 微型",  100,None
                        elif mkt_cap_b<20:  cap_tier,realistic_max_x,cap_warn="🌱 小型",   50,None
                        elif mkt_cap_b<100: cap_tier,realistic_max_x,cap_warn="📊 中型",   20,None
                        elif mkt_cap_b<500: cap_tier,realistic_max_x,cap_warn="🏢 大型",   10,"10x"
                        else:               cap_tier,realistic_max_x,cap_warn="🐋 巨型",    5,"5x"
                    else:
                        if   mkt_cap_b<0.5: cap_tier,realistic_max_x,cap_warn="🔬 微型",  100,None
                        elif mkt_cap_b<3:   cap_tier,realistic_max_x,cap_warn="🌱 小型",   50,None
                        elif mkt_cap_b<15:  cap_tier,realistic_max_x,cap_warn="📊 中型",   20,None
                        elif mkt_cap_b<50:  cap_tier,realistic_max_x,cap_warn="🏢 大型",   10,"10x"
                        elif mkt_cap_b<200: cap_tier,realistic_max_x,cap_warn="🚀 超大型",  5,"5x"
                        else:               cap_tier,realistic_max_x,cap_warn="🐋 巨型",    3,"3-5x"
                    target_100x_b = mkt_cap_b * 100
                    target_100x_t = target_100x_b / 1000

                    # ── CAGR（優先趨勢回歸，退化年度快照）──
                    _tc = d11_data.get("trend_cagr")
                    cagr_source = "趨勢回歸" if _tc and _tc>0.05 else "年度快照"
                    if is_pre_profit:
                        cagr_est = (_tc*0.8 if _tc and _tc>0.05 else (rev_growth*0.7 if rev_growth and rev_growth>0 else None))
                    else:
                        _b = _tc if _tc and _tc>0.05 else (rev_growth or 0)
                        cagr_est = (_b*0.6+roe*0.4) if (_b>0 and roe and roe>0) else None
                    yrs100 = _math.log(100)/_math.log(1+cagr_est) if cagr_est and cagr_est>0.05 else None
                    yrs20  = _math.log(20) /_math.log(1+cagr_est) if cagr_est and cagr_est>0.05 else None
                    yrs10  = _math.log(10) /_math.log(1+cagr_est) if cagr_est and cagr_est>0.05 else None

                    results.append(dict(
                        sym=sym, name=name_s, industry=industry_s, currency=currency,
                        price=price, mkt_cap_b=mkt_cap_b,
                        roe=roe, rev_growth=rev_growth, gross_margin=gross_margin,
                        op_margin=op_margin, fcf_pct=fcf_pct, div_yield=div_yield,
                        peg=peg, pe=(fwd_pe if fwd_pe > 0 else trail_pe),
                        ps_ratio=ps_ratio, is_pre_profit=is_pre_profit,
                        insider_pct=insider_pct, rule40_val=rule40_val,
                        d1=d1, d2=d2, d3=d3, d4=d4, d5=d5, d6=d6, d7=d7,
                        d8=d8, d9=d9, d10=d10,
                        total=total, grade=grade, gcolor=gcolor,
                        yrs100=yrs100, yrs20=yrs20, yrs10=yrs10,
                        cagr_est=cagr_est, cagr_source=cagr_source,
                        cap_tier=cap_tier, realistic_max_x=realistic_max_x,
                        cap_warn=cap_warn, target_100x_b=target_100x_b, target_100x_t=target_100x_t,
                        d11=d11_data,
                    ))
                except Exception as e:
                    st.toast(f"⚠️ {sym} 讀取失敗: {e}")

                prog.progress((idx+1) / len(tickers))

        prog.empty(); stat_ph.empty()

        if not results:
            st.error("❌ 掃描失敗，請確認代號格式。")
            st.stop()

        results.sort(key=lambda x: x['total'], reverse=True)
        st.session_state['bg_results'] = results

    # ════════════════════════════════════════════════════
    # BLOCK D：結果渲染
    # ════════════════════════════════════════════════════
    if 'bg_results' not in st.session_state:
        st.info("ℹ️ 輸入代號後點擊「啟動 7D DNA 基因掃描」。")
        return

    results = st.session_state['bg_results']
    st.divider()
    st.markdown('<div class="bg28">📊 DNA 掃描報告</div>', unsafe_allow_html=True)

    # ── 總排行表 ──
    rows = []
    for r in results:
        cur  = r['currency']
        cap  = f"{r['mkt_cap_b']:.1f}B {cur}" if r['mkt_cap_b'] > 0 else "N/A"
        mode_tag = "🔴 燒錢模式" if r.get('is_pre_profit') else "🟢 盈利模式"
        _rmx = r.get('realistic_max_x', 100)
        if   _rmx>=100 and r.get('yrs100') and r['yrs100']<50: _xe=f"100x:~{r['yrs100']:.0f}年"
        elif _rmx>=20  and r.get('yrs20')  and r['yrs20'] <50: _xe=f"20x:~{r['yrs20']:.0f}年"
        elif _rmx>=10  and r.get('yrs10')  and r['yrs10'] <30: _xe=f"10x:~{r['yrs10']:.0f}年"
        else: _xe="市值過大/待評估"
        rows.append({
            "代號": r['sym'], "公司": r['name'],
            "模式": mode_tag,
            "DNA 分數": r['total'], "等級": r['grade'],
            "市值級別": r.get('cap_tier','—'),
            "ROE": f"{r['roe']:.1%}" if r['roe'] and not r.get('is_pre_profit') else ("虧損" if r.get('is_pre_profit') else "N/A"),
            "營收成長": f"{r['rev_growth']:+.1%}" if r['rev_growth'] else "N/A",
            "毛利率": f"{r['gross_margin']:.1%}"  if r['gross_margin'] else "N/A",
            "🩸 內部人持股": f"{r['insider_pct']:.1%}" if r.get('insider_pct', 0) > 0 else "N/A",
            "📈 P/E": f"{r['pe']:.1f}x" if r.get('pe', 0) > 0 else "N/A",
            "🛡️ Rule of 40": f"{r['rule40_val']:.0f}%" if r.get('rule40_val') is not None else "N/A",
            "市值": cap,
            "現實目標": _xe,
        })
    df_tbl = pd.DataFrame(rows)

    def _cd(v):
        if v>=80: return 'color:#FF4500;font-weight:900'
        if v>=65: return 'color:#FFD700;font-weight:800'
        if v>=50: return 'color:#ADFF2F;font-weight:700'
        if v>=35: return 'color:#00BFFF'
        return 'color:#808080'

    def _cg(v):
        try:
            n = float(str(v).replace('%','').replace('+',''))
            if n>25: return 'color:#00FF9D;font-weight:700'
            if n>10: return 'color:#ADFF2F'
            if n<0:  return 'color:#FF6B6B'
        except: pass
        return ''

    st.dataframe(
        df_tbl.style.map(_cd, subset=['DNA 分數']).map(_cg, subset=['營收成長']),
        use_container_width=True, hide_index=True
    )

    # ── 個股深度 DNA 卡片 ──
    st.divider()
    st.markdown('<div class="bg28">🔬 個股 DNA 深度解剖</div>', unsafe_allow_html=True)

    for r in results:
        gc   = r['gcolor']
        sc   = r['total']
        with st.expander(f"**{r['sym']}** — {r['grade']} ({sc}/100) · {r['name']}", expanded=(sc>=65)):

            # ── 燒錢模式警示橫幅 ──
            if r.get('is_pre_profit'):
                st.markdown(f"""<div style="background:rgba(255,107,107,.08);border:1px solid rgba(255,107,107,.3);
                border-radius:8px;padding:10px 16px;margin-bottom:10px;">
                <span style="font-size:22px;font-weight:800;color:#FF6B6B;">🔴 預盈利模式（Pre-Profit Mode）</span>
                <span style="font-size:20px;color:rgba(200,210,220,.7);margin-left:10px;">
                — EPS 為負，採用「燒錢替代計分法」（Tesla 2018、PLTR 2020 均屬此類）</span><br>
                <span style="font-size:20px;color:rgba(180,190,210,.55);">
                D1 以毛利率代替 ROE ｜ D6 以 P/S 估值合理性代替 FCF ｜ D7 以 P/S÷成長率代替 PEG ｜
                D8 創辦人持股仍有效 ｜ D9 P/S 替代 P/E ｜ D10 Rule of 40 仍適用 ｜
                100x 估算僅用營收 CAGR×0.7（含不確定折扣）</span>
                </div>""", unsafe_allow_html=True)

            # ── D11 季度轉折訊號面板 ──
            d11 = r.get('d11', {})
            if d11.get('available'):
                _il  = d11.get('inflection_label','')
                _is  = d11.get('inflection_signal', False)
                _src = r.get('cagr_source','年度快照')
                _pc  = "#00FF9D" if _is else "#FF9A3C"
                st.markdown(
                    f'<div style="background:rgba(0,0,0,.25);border:1px solid {_pc}44;'
                    f'border-left:4px solid {_pc};border-radius:0 10px 10px 0;'
                    f'padding:10px 16px;margin-bottom:10px;">'
                    f'<div style="font-family:monospace;font-size:9px;color:{_pc}88;'
                    f'letter-spacing:3px;text-transform:uppercase;margin-bottom:4px;">'
                    f'🔄 D11 季度轉折雷達 · CAGR來源：{_src}</div>'
                    f'<div style="font-size:19px;font-weight:700;color:{_pc};">{_il}</div>'
                    f'</div>', unsafe_allow_html=True)
                _c1,_c2,_c3 = st.columns(3)
                with _c1:
                    _ac = d11.get('rev_accel')
                    _as = f"+{_ac:.1%}" if _ac and _ac>0 else (f"{_ac:.1%}" if _ac else "N/A")
                    _tc = d11.get('trend_cagr')
                    st.markdown(f'''<div class="bgcard" style="padding:10px;">
                    <div class="bgml">營收加速度(YoY差)</div>
                    <div class="bgmv" style="color:{"#00FF9D" if _ac and _ac>0 else "#FF6B6B"};">{_as}</div>
                    <div style="font-size:16px;color:rgba(160,176,208,.5);">趨勢CAGR：{"N/A" if not _tc else f"{_tc:.1%}/年"}</div>
                    </div>''', unsafe_allow_html=True)
                with _c2:
                    _gs  = d11.get('gm_slope')
                    _gss = f"+{_gs*100:.2f}%/季" if _gs and _gs>0 else (f"{_gs*100:.2f}%/季" if _gs else "N/A")
                    _lgm = f"{d11['gm_series'][-1]:.1%}" if d11.get('gm_series') else "N/A"
                    _gc  = "#00FF9D" if _gs and _gs>0.003 else ("#FF9A3C" if _gs and _gs>0 else "#FF6B6B")
                    st.markdown(f'''<div class="bgcard" style="padding:10px;">
                    <div class="bgml">毛利率趨勢(季斜率)</div>
                    <div class="bgmv" style="color:{_gc};">{_gss}</div>
                    <div style="font-size:16px;color:rgba(160,176,208,.5);">最新季：{_lgm}</div>
                    </div>''', unsafe_allow_html=True)
                with _c3:
                    _fs  = d11.get('fcf_series',[])
                    _qf  = d11.get('qtrs_to_fcf_positive')
                    _fcs = ("✅ 已轉正" if _fs and _fs[-1]>=0 else
                            (f"約{_qf:.0f}季後轉正" if _fs and _fs[-1]<0 and _qf else "N/A"))
                    _fcc = "#00FF9D" if _fs and _fs[-1]>=0 else ("#FFD700" if _qf else "#808080")
                    _lfcf= f"${_fs[-1]:.2f}B" if _fs else "N/A"
                    st.markdown(f'''<div class="bgcard" style="padding:10px;">
                    <div class="bgml">FCF拐點預估</div>
                    <div class="bgmv" style="color:{_fcc};">{_fcs}</div>
                    <div style="font-size:16px;color:rgba(160,176,208,.5);">最新季FCF：{_lfcf}</div>
                    </div>''', unsafe_allow_html=True)
                _rs = d11.get('rev_series',[])
                _qs = d11.get('quarters',[])
                if len(_rs)>=4 and len(_qs)>=len(_rs):
                    _fig = go.Figure()
                    _fig.add_trace(go.Scatter(x=_qs,y=_rs,name="季度營收($B)",
                        mode="lines+markers",line=dict(color="#00FF9D",width=2.5),marker=dict(size=7)))
                    _gms = d11.get('gm_series',[])
                    if _gms and len(_gms)==len(_rs):
                        _fig.add_trace(go.Scatter(x=_qs,y=[v*100 for v in _gms],name="毛利率(%)",
                            mode="lines+markers",line=dict(color="#00BFFF",width=2,dash="dot"),
                            marker=dict(size=6),yaxis="y2"))
                    if _fs and len(_fs)==len(_rs):
                        _fig.add_trace(go.Scatter(x=_qs,y=_fs,name="FCF($B)",
                            mode="lines+markers",line=dict(color="#B77DFF",width=2,dash="dash"),marker=dict(size=6)))
                        _fig.add_hline(y=0,line_dash="dot",line_color="rgba(255,255,255,.2)")
                    _ql = d11.get('rev_qoq_list',[])
                    for _i,(_qt,_rv) in enumerate(zip(_qs,_rs)):
                        if _i<len(_ql) and _ql[_i] is not None:
                            _fig.add_annotation(x=_qt,y=_rv,text=f"QoQ {_ql[_i]:+.0%}",
                                showarrow=False,yshift=14,
                                font=dict(size=10,color="#00FF9D" if _ql[_i]>0 else "#FF6B6B"))
                    _fig.update_layout(template="plotly_dark",
                        paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
                        height=260,margin=dict(t=15,b=30,l=55,r=55),hovermode="x unified",
                        legend=dict(orientation="h",y=-0.28,font=dict(size=11)),
                        yaxis=dict(title="營收($B)"),
                        yaxis2=dict(title="毛利率(%)",overlaying="y",side="right"))
                    st.plotly_chart(_fig,use_container_width=True)
            elif d11.get('inflection_label'):
                st.markdown(f'''<div style="font-size:17px;color:rgba(160,176,208,.45);padding:6px 12px;margin-bottom:8px;">
                📊 D11：{d11["inflection_label"]}</div>''', unsafe_allow_html=True)

            ca, cb, cc = st.columns([1,2,2])

            with ca:
                st.markdown(f"""<div class="bgcard" style="text-align:center;border-color:{gc}44;">
                <div class="bgml">DNA 分數</div>
                <div class="bgscore" style="color:{gc};">{sc}</div>
                <div style="background:rgba(255,255,255,.08);border-radius:4px;height:10px;margin:10px 0 6px;">
                  <div style="background:{gc};width:{sc}%;height:10px;border-radius:4px;"></div></div>
                <div style="font-size:22px;font-weight:700;color:{gc};">{r['grade']}</div>
                </div>""", unsafe_allow_html=True)

            with cb:
                st.markdown('<div class="bgml">10 維度分解 (Chris Mayer × Baillie Gifford)</div>', unsafe_allow_html=True)
                dims = [
                    ("D1 ROE 引擎",        r['d1'], 22, "#FFD700"),
                    ("D2 營收加速",        r['d2'], 20, "#00FF9D"),
                    ("D3 毛利護城河",      r['d3'], 17, "#00BFFF"),
                    ("D4 市值空間",        r['d4'], 15, "#FF9A3C"),
                    ("D5 再投資力",        r['d5'],  5, "#B77DFF"),
                    ("D6 盈利品質",        r['d6'],  3, "#FF6B6B"),
                    ("D7 安全邊際",        r['d7'],  2, "#00F5FF"),
                    ("D8 🩸 創辦人綁定",   r['d8'],  8, "#FF1493"),
                    ("D9 📈 估值擴張",     r['d9'],  5, "#FFAA00"),
                    ("D10 🛡️ Rule of 40", r['d10'], 3, "#00FF7F"),
                ]
                for dn, dg, dm, dc in dims:
                    fp = int((dg/dm)*100) if dm>0 else 0
                    st.markdown(f"""<div style="margin-bottom:7px;">
                    <div style="display:flex;justify-content:space-between;margin-bottom:2px;">
                    <span style="font-size:21px;color:rgba(200,210,220,.75);">{dn}</span>
                    <span style="font-size:22px;font-weight:800;color:{dc};">{dg}/{dm}</span></div>
                    <div style="background:rgba(255,255,255,.08);border-radius:3px;height:7px;">
                    <div style="background:{dc};width:{fp}%;height:7px;border-radius:3px;"></div>
                    </div></div>""", unsafe_allow_html=True)

            with cc:
                st.markdown('<div class="bgml">財務快照 + 三大百倍股關鍵</div>', unsafe_allow_html=True)
                # ── 共用的三大百倍股指標 (D8/D9/D10) ──
                insider_disp = f"{r['insider_pct']:.1%}" if r.get('insider_pct', 0) > 0 else "無資料"
                insider_flag = " 🔥" if r.get('insider_pct', 0) >= 0.10 else (" ⚠️" if r.get('insider_pct', 0) >= 0.05 else "")
                r40_disp     = f"{r['rule40_val']:.1f}%" if r.get('rule40_val') is not None else "無資料"
                r40_flag     = " ✅" if (r.get('rule40_val') or 0) >= 40 else (" ❌" if (r.get('rule40_val') or 0) < 20 else "")
                pe_disp      = f"{r['pe']:.1f}x" if r.get('pe', 0) > 0 else "N/A (虧損)"
                peg_disp     = f"{r['peg']:.2f}" if r.get('peg', 0) > 0 else "N/A"

                if r.get('is_pre_profit'):
                    snaps = [
                        ("毛利率（D1代理）",           f"{r['gross_margin']:.1%}"  if r['gross_margin'] else "N/A", "#FFD700"),
                        ("營收成長 YoY",                f"{r['rev_growth']:+.1%}"   if r['rev_growth']   else "N/A", "#00FF9D"),
                        ("營業利益率",                  f"{r['op_margin']:.1%}"     if r['op_margin']    else "N/A", "#ADFF2F"),
                        ("P/S 比率（D6/D9代理）",      f"{r['ps_ratio']:.1f}x"    if r.get('ps_ratio',0)>0 else "N/A", "#00BFFF"),
                        ("🩸 內部人持股（D8）",         insider_disp + insider_flag, "#FF1493"),
                        ("🛡️ Rule of 40（D10）",       r40_disp + r40_flag,        "#00FF7F"),
                        ("市值",                        f"{r['mkt_cap_b']:.1f}B {r['currency']}",                    "#00F5FF"),
                    ]
                else:
                    snaps = [
                        ("ROE 資本效率",                f"{r['roe']:.1%}"          if r['roe']          else "N/A", "#FFD700"),
                        ("營收成長 YoY",                f"{r['rev_growth']:+.1%}"   if r['rev_growth']   else "N/A", "#00FF9D"),
                        ("毛利率",                      f"{r['gross_margin']:.1%}"  if r['gross_margin'] else "N/A", "#00BFFF"),
                        ("📈 P/E（D9估值）",            pe_disp,                                                      "#FFAA00"),
                        ("📈 PEG（D9估值）",            peg_disp,                                                     "#FF9A3C"),
                        ("🩸 內部人持股（D8）",         insider_disp + insider_flag, "#FF1493"),
                        ("🛡️ Rule of 40（D10）",       r40_disp + r40_flag,        "#00FF7F"),
                    ]
                for sl, sv, sc2 in snaps:
                    st.markdown(f"""<div class="bgrow">
                    <span class="bgrl">{sl}</span>
                    <span class="bgrv" style="color:{sc2};">{sv}</span>
                    </div>""", unsafe_allow_html=True)

            # ── 100x 路徑估算 ──
            st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
            if r['yrs100'] and r['yrs100'] < 60:
                yc = "#00FF9D" if r['yrs100']<12 else ("#FFD700" if r['yrs100']<20 else "#FF9A3C")
                cagr_note = "（燒錢模式：純用營收 CAGR×0.7，含高不確定折扣，盈利後實際 CAGR 可能更高）" if r.get('is_pre_profit') else "（CAGR = 營收成長×60% + ROE×40%，樂觀情境）"
                st.markdown(f"""<div class="bgf" style="border-left-color:{yc};">
                📐 100x 路徑估算：若 CAGR 維持 <b>{r['cagr_est']:.1%}</b>，
                需 <b style="color:{yc};font-size:32px;">~{r['yrs100']:.0f} 年</b> 達到百倍。<br>
                <span style="font-size:22px;opacity:.7;">{cagr_note}</span>
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown('<div class="bgw">⚠️ 當前財務數據不足以估算 100x 路徑，需要正向毛利率與正向營收成長同時存在。</div>', unsafe_allow_html=True)

            # ── Valkyrie 判定 ──
            pre_tag = "（燒錢模式，Tesla/PLTR 型）" if r.get('is_pre_profit') else ""
            if sc >= 80:
                skin_note = f"內部人持股 {r.get('insider_pct',0):.1%}，{'創辦人仍掌舵。' if r.get('insider_pct',0)>=0.10 else '持股偏低，注意代理人風險。'}"
                r40_note  = f"{r['rule40_val']:.0f}%" if r.get('rule40_val') is not None else 'N/A'
                pre_body  = ('高毛利商業模式已驗證 + 高速營收加速 + 市值天花板巨大，即使尚未盈利，其燒錢是「規模化投資」而非「商業模式失敗」。'
                             if r.get('is_pre_profit') else
                             '高 ROE 複利引擎 + 高速營收加速 + 高毛利護城河三者兼備，且市值仍在百倍可行的早期階段。')
                st.success(f"🔥 **SUPER NOVA！{pre_tag}** {r['sym']} 的財務 DNA 極為罕見——{pre_body}{skin_note} Rule of 40：{r40_note}。若產業景氣循環位於「黎明期」，這正是教科書級別的百倍股候選。**下一步：深研護城河可持續性、創辦人是否仍在主導、現金跑道還有多久。**")
            elif sc >= 65:
                pre_msg = "燒錢期具備部分核心成長基因，毛利率顯示商業模式可行。關鍵問題：現金跑道是否足夠撐到盈利？管理層是否有明確的盈利時間表？" if r.get('is_pre_profit') else "具備核心成長基因，但部分維度尚未達最高標準。建議持續追蹤，等待財務數據改善或估值回落。"
                st.warning(f"⚡ **百倍候選{pre_tag}** — {r['sym']} {pre_msg}")
            elif sc >= 50:
                pre_msg = "燒錢期有部分優秀指標，但整體 DNA 組合不夠完整。研究其毛利率趨勢——若毛利率持續提升，盈利後將快速釋放價值。" if r.get('is_pre_profit') else "有部分優秀指標，但整體 DNA 組合不夠完整。研究其能否在未來 2–3 年提升 ROE 或毛利率。"
                st.info(f"📈 **成長潛力{pre_tag}** — {r['sym']} {pre_msg}")
            else:
                pre_msg = f"燒錢且財務 DNA 不足，高風險標的。建議尋找毛利率更高、成長加速更明確的燒錢公司。" if r.get('is_pre_profit') else "目前不符合百倍股 DNA 特徵。可能是成熟企業、高配息或成長動能不足。"
                st.markdown(f'<div class="bgw">❄️ {r["sym"]} {pre_msg}</div>', unsafe_allow_html=True)

    # ── CSV 下載 ──
    st.divider()
    export = []
    for r in results:
        export.append({
            "代號":r['sym'],"公司":r['name'],"產業":r['industry'],
            "模式": "燒錢(Pre-Profit)" if r.get('is_pre_profit') else "盈利",
            "DNA總分":r['total'],"等級":r['grade'],
            "D1_ROE或毛利引擎":r['d1'],"D2_營收加速":r['d2'],"D3_毛利護城河":r['d3'],
            "D4_市值空間":r['d4'],"D5_再投資":r['d5'],"D6_盈利或PS品質":r['d6'],"D7_安全邊際":r['d7'],
            "D8_創辦人綁定(Skin)":r['d8'],"D9_估值擴張(PE/PEG)":r['d9'],"D10_Rule_of_40":r['d10'],
            "ROE":r['roe'],"營收成長":r['rev_growth'],"毛利率":r['gross_margin'],
            "營業利益率":r['op_margin'],"Rule_of_40值":r.get('rule40_val'),
            "內部人持股":r.get('insider_pct'),"P/E":r.get('pe'),"PEG":r['peg'],
            "FCF_Margin":r['fcf_pct'],"P/S比率":r.get('ps_ratio'),"殖利率":r['div_yield'],
            "市值B":r['mkt_cap_b'],"幣別":r['currency'],
            "100x估算年": round(r['yrs100'],1) if r['yrs100'] else None,
        })
    df_exp = pd.DataFrame(export)
    st.download_button(
        "📥 下載完整 DNA 掃描報告 (CSV)",
        df_exp.to_csv(index=False).encode('utf-8-sig'),
        f"Titan_100Bagger_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        use_container_width=True, key="dl_bg_csv"
    )



# SECTION 6.4 — 全境獵殺
# ═══════════════════════════════════════════════════════════════
def _s64():
    st.markdown('<div class="t6-sec-head" style="--sa:#FF3131"><div class="t6-sec-num">6.4</div><div><div class="t6-sec-title" style="color:#FF3131;">全境獵殺雷達 (The Hunter)</div><div class="t6-sec-sub">War Theater Scan · Phoenix / Awakening / Rocket · Valkyrie</div></div></div>', unsafe_allow_html=True)

    with st.expander("🎯 獵殺控制台 (Mission Control)", expanded=True):
        theater = st.selectbox("選擇掃描戰區", list(WAR_THEATERS.keys()), key="theater_v300")
        count = len(WAR_THEATERS.get(theater, []))
        st.info(f"已選擇戰區 **{theater}**，包含 **{count}** 檔潛力標的。")

        if st.button("🚀 啟動全境掃描", type="primary", use_container_width=True, key="btn_hunt_v300"):
            tickers = WAR_THEATERS[theater]
            results = []
            prog = st.progress(0, text=f"掃描進度: 0/{len(tickers)}")
            for i, t in enumerate(tickers):
                geo = compute_7d_geometry(t)
                prog.progress((i + 1) / len(tickers), text=f"掃描進度: {t} ({i + 1}/{len(tickers)})")
                if geo:
                    cp = 0.0
                    dp = st.session_state.get('daily_price_data', {}).get(t)
                    if dp is not None and not dp.empty:
                        cp = float(dp['Close'].iloc[-1])
                    mt = None
                    if geo['10Y']['angle'] < 10 and geo['3M']['angle'] > 45:
                        mt = "🔥 Phoenix"
                    elif abs(geo['35Y']['angle']) < 15 and geo['acceleration'] > 20:
                        mt = "🦁 Awakening"
                    elif geo['3M']['angle'] > 60:
                        mt = "🚀 Rocket"
                    if mt:
                        results.append({
                            "代號": t, "現價": cp, "35Y角度": geo['35Y']['angle'],
                            "10Y角度": geo['10Y']['angle'], "3M角度": geo['3M']['angle'],
                            "G力": geo['acceleration'], "型態": mt
                        })
            prog.empty()
            st.session_state[f'hunt_{theater}'] = pd.DataFrame(results)
            st.success(f"✅ {theater} 戰區掃描完成，發現 **{len(results)}** 個潛在目標！")

    key = f'hunt_{theater}'
    if key in st.session_state:
        hr = st.session_state[key]
        if not hr.empty:
            st.dataframe(hr.style.format({
                "現價": "{:.2f}", "35Y角度": "{:.1f}°", "10Y角度": "{:.1f}°",
                "3M角度": "{:.1f}°", "G力": "{:+.1f}°"
            }), use_container_width=True)
            st.download_button("📥 下載戰果 CSV", hr.to_csv(index=False).encode(),
                               file_name=f"hunt_{theater}_{datetime.now().strftime('%Y%m%d')}.csv")

            # 索敵模式
            st.divider()
            st.subheader("🎯 索敵模式 (Target Acquisition)")
            target = st.selectbox("選擇目標", hr['代號'].tolist(), key="hunt_target_v300")
            if st.button("🔍 鎖定目標", type="primary", key="lock_v300"):
                with st.spinner(f"鎖定 {target}…"):
                    tgeo = compute_7d_geometry(target)
                if tgeo:
                    tr = titan_rating_system(tgeo)
                    st.session_state['hunt_tgeo'] = tgeo
                    st.session_state['hunt_trating'] = tr
                    st.session_state['hunt_target_name'] = target
                    st.success(f"✅ 目標已鎖定！信評: **{tr[0]} - {tr[1]}**")
                else:
                    st.toast(f"❌ 無法載入 {target} 的數據", icon="💀")

            if 'hunt_tgeo' in st.session_state and st.session_state.get('hunt_target_name') == target:
                tgeo = st.session_state['hunt_tgeo']
                tr = st.session_state['hunt_trating']
                st.markdown(f'<div class="rank-badge-wrap"><div class="rank-badge" style="font-size:80px;">{tr[0]}</div><div class="rank-badge-name">{tr[1]}</div><div class="rank-badge-desc">{tr[2]}</div></div>', unsafe_allow_html=True)
                _render_spectrum(tgeo, target)
                _render_radar(tgeo, target)

                st.markdown("---")
                st.subheader("⚙️ 戰略參數設定 (索敵版)")
                col_h_left, col_h_right = st.columns(2)
                with col_h_left:
                    if st.button("🤖 啟動瓦爾基里", type="primary", use_container_width=True, key="valk_hunt_v300"):
                        with st.spinner("抓取情報…"):
                            agency = TitanIntelAgency()
                            st.session_state['hunt_valk'] = agency.fetch_full_report(target)
                        st.success("✅ 情報抓取完成！")
                    if 'hunt_valk' in st.session_state:
                        intel_h = st.text_area("瓦爾基里情報 (可編輯)", value=st.session_state['hunt_valk'], height=200, key="intel_hunt_valk_v300")
                    else:
                        intel_h = st.text_area("法說會/財報內容", height=120, placeholder="貼上情報或點擊瓦爾基里...", key="intel_hunt_manual_v300")
                    commander_note_h = st.text_area("統帥筆記", height=80, placeholder="補充分析指令...", key="note_hunt_v300")
                with col_h_right:
                    st.markdown("**🎯 第一性原則 (精選版)**")
                    sel_p_h = st.multiselect("選擇第一性原則", ESSENTIAL_PRINCIPLES_10, default=[], key="principles_hunt_v300")

                st.markdown("---")
                if st.button("🚀 生成索敵戰略提示詞", type="primary", use_container_width=True, key="gen_hunt_v300"):
                    ph = 0.0
                    dp = st.session_state.get('daily_price_data', {}).get(target)
                    if dp is not None and not dp.empty:
                        ph = float(dp['Close'].iloc[-1])
                    council = TitanAgentCouncil()
                    pt = council.generate_battle_prompt(target, ph, tgeo, tr, intel_h, commander_note_h, sel_p_h)
                    st.success("✅ 索敵戰略提示詞已生成！")
                    st.text_area("📋 複製此提示詞", value=pt, height=350, key="hunt_prompt_v300")
                    st.download_button("💾 下載提示詞", pt,
                                       file_name=f"TITAN_HUNT_{target}_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                                       mime="text/plain", use_container_width=True)
        else:
            st.info("未發現符合條件的目標，請嘗試其他戰區。")


# ═══════════════════════════════════════════════════════════════
# SECTION 6.5 — 宏觀對沖 (ENHANCED — was placeholder)
# ═══════════════════════════════════════════════════════════════

def _s65():
    """6.5 宏觀對沖 + PCA 隱藏因子降維 (First Principles — Institutional Edition)"""
    st.markdown(
        '<div class="t6-sec-head" style="--sa:#00FF7F">'
        '<div class="t6-sec-num">6.5</div>'
        '<div><div class="t6-sec-title" style="color:#00FF7F;">'
        '宏觀對沖 + 主成分因子輪動</div>'
        '<div class="t6-sec-sub">'
        'Global Snapshot · Correlation · Beta Hedge · PCA Eigen-Decomposition · Pairs Signal'
        '</div></div></div>',
        unsafe_allow_html=True
    )

    # ═══════════════════════════════════════════════════════════════
    # BLOCK A: 全球宏觀快照 HUD (原版保留)
    # ═══════════════════════════════════════════════════════════════
    SNAPS = [
        ("SPY",       "S&P500"),
        ("QQQ",       "NASDAQ100"),
        ("GLD",       "黃金"),
        ("TLT",       "美債20Y"),
        ("BTC-USD",   "比特幣"),
        ("^TWII",     "台灣加權"),
        ("DX-Y.NYB",  "美元指數"),
        ("^VIX",      "VIX恐慌"),
    ]
    with st.spinner("載入市場快照…"):
        try:
            snap_raw = yf.download(
                [s for s, _ in SNAPS], period="5d",
                progress=False, auto_adjust=True
            )
            if isinstance(snap_raw.columns, pd.MultiIndex):
                snap_px = snap_raw["Close"]
            else:
                snap_px = snap_raw
            snap_px = snap_px.dropna(how="all")
        except Exception:
            snap_px = pd.DataFrame()

    if not snap_px.empty and len(snap_px) >= 2:
        hud_cols = st.columns(len(SNAPS))
        for idx, (tk, lbl) in enumerate(SNAPS):
            if tk not in snap_px.columns:
                continue
            s_col = snap_px[tk].dropna()
            if len(s_col) < 2:
                continue
            cur  = float(s_col.iloc[-1])
            prev = float(s_col.iloc[-2])
            chg  = (cur - prev) / prev * 100
            hud_cols[idx].metric(lbl, f"{cur:,.2f}", f"{chg:+.2f}%",
                                 delta_color="normal" if chg >= 0 else "inverse")
    else:
        st.warning("市場快照無法取得。")

    st.divider()

    # ═══════════════════════════════════════════════════════════════
    # BLOCK B: 多資產相關性矩陣 (原版保留)
    # ═══════════════════════════════════════════════════════════════
    st.markdown("#### 🔗 多資產相關性矩陣")
    DEF_A = ["SPY", "QQQ", "GLD", "TLT", "BTC-USD", "DX-Y.NYB"]
    ca, cb = st.columns([3, 1])
    corr_tickers = ca.multiselect(
        "選擇資產",
        options=DEF_A + ["IWM","EEM","HYG","SOXX","NVDA","AAPL","TSLA","^VIX"],
        default=DEF_A, key="corr_v300"
    )
    corr_period = cb.selectbox("區間", ["1y","2y","3y","5y"], key="corr_per_v300")
    if st.button("計算相關性矩陣", use_container_width=True, key="run_corr_v300"):
        if len(corr_tickers) >= 2:
            with st.spinner("計算…"):
                px_data = _fetch_prices(tuple(corr_tickers), corr_period)
            if not px_data.empty:
                cm = px_data.pct_change().dropna().corr().round(3)
                st.session_state["corr_mat_v300"] = cm
    if "corr_mat_v300" in st.session_state:
        cm = st.session_state["corr_mat_v300"]
        fig_hm = go.Figure(go.Heatmap(
            z=cm.values, x=cm.columns.tolist(), y=cm.index.tolist(),
            colorscale=[[0,"#FF3131"],[.5,"#1a1a2e"],[1,"#00FF7F"]],
            zmin=-1, zmax=1, zmid=0,
            text=cm.values.round(2), texttemplate="%{text:.2f}",
            textfont=dict(size=11, family="JetBrains Mono")
        ))
        fig_hm.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            height=420, margin=dict(t=10, b=40, l=80, r=20)
        )
        st.plotly_chart(fig_hm, use_container_width=True)

    st.divider()

    # ═══════════════════════════════════════════════════════════════
    # BLOCK C: Beta 對沖 + 滾動 Beta (原版保留)
    # ═══════════════════════════════════════════════════════════════
    st.markdown("#### ⚖️ Beta 對沖 + 滾動 60 日 Beta")
    BENCH_MAP = {
        "SPY (S&P 500)": "SPY",
        "QQQ (NASDAQ 100)": "QQQ",
        "^TWII (台灣加權)": "^TWII",
        "GLD (黃金)": "GLD",
    }
    ba, bb, bc = st.columns([2, 1, 1])
    bench_name  = ba.selectbox("基準指數", list(BENCH_MAP.keys()), key="bench_v300")
    beta_period = bb.selectbox("區間", ["1y","2y","3y"], key="beta_per_v300")
    beta_ticker = bc.text_input("標的", "NVDA", key="beta_tk_v300")
    bench_tk    = BENCH_MAP[bench_name]
    if st.button("計算 Beta", use_container_width=True, key="run_beta_v300"):
        with st.spinner("計算…"):
            beta_px = _fetch_prices(tuple([beta_ticker, bench_tk]), beta_period)
        if (not beta_px.empty
                and beta_ticker in beta_px.columns
                and bench_tk in beta_px.columns):
            br = beta_px.pct_change().dropna()
            bv = (
                round(br[beta_ticker].cov(br[bench_tk]) / br[bench_tk].var(), 3)
                if br[bench_tk].var() > 0 else 0
            )
            st.session_state["beta_v300"] = {
                "beta": bv,
                "corr": round(br[beta_ticker].corr(br[bench_tk]), 3),
                "avol": round(br[beta_ticker].std() * np.sqrt(252) * 100, 2),
                "ret":  br, "tk": beta_ticker, "bk": bench_tk,
            }
    if "beta_v300" in st.session_state:
        b  = st.session_state["beta_v300"]
        bv = b["beta"]
        bk1, bk2, bk3, bk4 = st.columns(4)
        bk1.metric("Beta",   f"{bv:.3f}")
        bk2.metric("相關性", f"{b['corr']:.3f}")
        bk3.metric("年化波動", f"{b['avol']:.2f}%")
        bk4.metric("對沖比例", f"{abs(bv):.3f}x")

        rb_ret  = b["ret"]
        tk_b, bk_b = b["tk"], b["bk"]
        W = 60
        if len(rb_ret) > W:
            roll_b = []
            for i in range(W, len(rb_ret)):
                chunk  = rb_ret.iloc[i-W:i]
                bk_var = chunk[bk_b].var()
                rb_val = (chunk[tk_b].cov(chunk[bk_b]) / bk_var
                          if bk_var > 0 else 0)
                roll_b.append({"Date": rb_ret.index[i], "Rolling Beta": rb_val})
            rb_df  = pd.DataFrame(roll_b)
            fig_rb = px.line(
                rb_df, x="Date", y="Rolling Beta",
                title=f"{tk_b} — 60日 Rolling Beta vs {bk_b}"
            )
            fig_rb.update_traces(line_color="#FF9A3C", line_width=1.8)
            fig_rb.add_hline(y=1, line_dash="dash",
                             line_color="rgba(255,255,255,.2)")
            fig_rb.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                height=270, margin=dict(t=30, b=40, l=60, r=10)
            )
            st.plotly_chart(fig_rb, use_container_width=True)

    st.divider()

    # ═══════════════════════════════════════════════════════════════
    # BLOCK D: PCA 主成分因子輪動 (First Principles — Institutional)
    # ═══════════════════════════════════════════════════════════════
    st.markdown("#### 🧊 PCA 隱藏因子降維 — 機構版")
    st.markdown(
        '<div style="font-family:\'JetBrains Mono\',monospace;font-size:10px;'
        'color:rgba(160,176,208,0.45);letter-spacing:1px;line-height:1.9;margin-bottom:12px;">'
        '第一性原理：股價波動 = <b style="color:rgba(0,245,255,.6)">系統性因子（PC1/PC2）</b>'
        ' + <b style="color:rgba(255,154,60,.6)">特異性風險（殘差）</b>。<br>'
        '特徵值分解將高維相關矩陣壓縮到2D，讓「隱藏的資金陣營」一覽無遺。<br>'
        'PC 分數時間序列揭示「輪動什麼時候發生」；風險分解表告訴你哪些是 Beta 工具、哪些有 Alpha。'
        '</div>',
        unsafe_allow_html=True
    )

    # 預設：台股跨產業 12 標的（半導體/金融/航運/鋼鐵/石化/電子代工）
    PCA_DEFAULT = (
        "2330.TW, 2317.TW, 2454.TW, 2382.TW, 2308.TW, "
        "2881.TW, 2882.TW, 2891.TW, 2603.TW, 2002.TW, 1301.TW, 1101.TW"
    )
    pa, pb = st.columns([3, 1])
    pca_input  = pa.text_input(
        "觀測矩陣標的（建議跨產業，≥ 6 檔）",
        value=PCA_DEFAULT, key="pca_tickers_v300"
    )
    pca_period = pb.selectbox(
        "觀測區間", ["6mo","1y","2y"], index=1,
        key="pca_period_v300"
    )
    if st.button(
        "🌌 啟動特徵值分解 (Run Eigen-Decomposition)",
        use_container_width=True, key="run_pca_v300"
    ):
        raw_tickers = [t.strip() for t in pca_input.split(",") if t.strip()]
        if len(raw_tickers) < 3:
            st.error("❌ 至少需要 3 檔標的。")
        else:
            with st.spinner("🧠 正在計算協方差矩陣與特徵向量…"):
                try:
                    import traceback as _tb

                    # ─────────────────────────────────────────────
                    # STEP 1: 取日K，對數收益率，Z-score 標準化
                    # 原因：PCA 對量綱敏感；Z-score 讓不同價位的股票
                    # 在同等地位上競爭，避免高波動股主導協方差。
                    # ─────────────────────────────────────────────
                    raw_dl = yf.download(
                        raw_tickers, period=pca_period,
                        progress=False, auto_adjust=True
                    )
                    if isinstance(raw_dl.columns, pd.MultiIndex):
                        px_raw = raw_dl["Close"]
                    else:
                        px_raw = raw_dl

                    # forward-fill 缺漏（最多 3 日）再去頭
                    px_raw = px_raw.ffill(limit=3).dropna(axis=1, thresh=int(len(px_raw)*0.8))
                    px_raw = px_raw.dropna()

                    valid_tks = list(px_raw.columns)
                    if len(valid_tks) < 3:
                        st.error("❌ 有效標的不足 3 檔（資料缺漏過多）。")
                    else:
                        # Log returns
                        log_ret = np.log(px_raw / px_raw.shift(1)).dropna()
                        n_obs, n_assets = log_ret.shape
                        dates = log_ret.index

                        # Z-score 標準化
                        ret_mean = log_ret.mean()
                        ret_std  = log_ret.std().replace(0, 1e-8)
                        ret_norm = (log_ret - ret_mean) / ret_std  # shape: (T, N)

                        # ─────────────────────────────────────────
                        # STEP 2: 純 numpy 協方差 → 特徵值分解
                        # eigh 比 eig 更穩定（對稱矩陣專用）
                        # ─────────────────────────────────────────
                        cov_mat  = np.cov(ret_norm.values.T)  # (N, N)
                        eig_vals, eig_vecs = np.linalg.eigh(cov_mat)

                        # 降序排列
                        order    = np.argsort(eig_vals)[::-1]
                        eig_vals = eig_vals[order]
                        eig_vecs = eig_vecs[:, order]

                        total_var = np.sum(eig_vals)
                        var_exp   = eig_vals / total_var * 100
                        cum_var   = np.cumsum(var_exp)

                        # Top-5 PC loadings
                        n_pc      = min(5, n_assets)
                        loadings  = eig_vecs[:, :n_pc]         # (N, 5)
                        pc1_load  = loadings[:, 0]
                        pc2_load  = loadings[:, 1]

                        # ─────────────────────────────────────────
                        # STEP 3: PC 分數時間序列（核心實戰工具）
                        # scores = 標準化收益率矩陣 × 特徵向量
                        # 告訴你每天「系統性因子強度」如何演變
                        # ─────────────────────────────────────────
                        scores = ret_norm.values @ loadings  # (T, n_pc)
                        pc1_ts = pd.Series(scores[:, 0], index=dates, name="PC1")
                        pc2_ts = pd.Series(scores[:, 1], index=dates, name="PC2")

                        # 滾動 20 日 PC2 均值（偵測輪動轉折）
                        pc2_roll = pc2_ts.rolling(20).mean()

                        # ─────────────────────────────────────────
                        # STEP 4: 風險分解
                        # 系統性方差 = Σ_k λ_k * loading_ik²
                        # 特異方差   = 總方差 - 系統性方差
                        # R² = 系統性方差 / 總方差（越高 = 越是 Beta）
                        # ─────────────────────────────────────────
                        risk_rows = []
                        for i, tk in enumerate(valid_tks):
                            total_v_i   = float(np.var(ret_norm.values[:, i]))
                            sys_v_i     = float(sum(
                                eig_vals[k] * loadings[i, k]**2
                                for k in range(n_pc)
                            ))
                            idio_v_i    = max(0, total_v_i - sys_v_i)
                            r2_i        = sys_v_i / total_v_i if total_v_i > 0 else 0
                            label       = tk.replace(".TW","").replace(".TWO","")
                            nature      = (
                                "🔵 純 Beta 工具" if r2_i >= 0.8
                                else "🟡 Beta 為主" if r2_i >= 0.6
                                else "🟠 混合型"    if r2_i >= 0.4
                                else "🟢 Alpha 來源"
                            )
                            risk_rows.append({
                                "代號":    label,
                                "PC1 載荷": round(float(pc1_load[i]), 4),
                                "PC2 載荷": round(float(pc2_load[i]), 4),
                                "系統性R²": round(r2_i, 4),
                                "性質":    nature,
                            })
                        risk_df = pd.DataFrame(risk_rows).sort_values(
                            "系統性R²", ascending=False
                        )

                        # ─────────────────────────────────────────
                        # STEP 5: 配對交易信號
                        # 找 PC2 載荷最大差異的兩股 → 最強負相關對
                        # 近 30 日 PC2 分數累積差 → 判斷誰被壓、誰被拉
                        # ─────────────────────────────────────────
                        max_pc2_i  = int(np.argmax(pc2_load))
                        min_pc2_i  = int(np.argmin(pc2_load))
                        pair_long  = valid_tks[max_pc2_i]
                        pair_short = valid_tks[min_pc2_i]
                        pc2_spread = pc2_ts.iloc[-30:].cumsum()
                        pair_dir   = "做多" if float(pc2_ts.iloc[-1]) > 0 else "做空"

                        # 近 30d PC2 方向偵測
                        pc2_recent_slope = float(
                            pc2_roll.iloc[-1] - pc2_roll.iloc[-20]
                        ) if len(pc2_roll.dropna()) >= 20 else 0

                        # 儲存結果
                        st.session_state["pca_result_v300"] = {
                            "valid_tks": valid_tks,
                            "var_exp": var_exp, "cum_var": cum_var,
                            "pc1_load": pc1_load, "pc2_load": pc2_load,
                            "pc1_ts": pc1_ts, "pc2_ts": pc2_ts,
                            "pc2_roll": pc2_roll,
                            "risk_df": risk_df,
                            "pair_long": pair_long, "pair_short": pair_short,
                            "pc2_spread": pc2_spread, "pair_dir": pair_dir,
                            "pc2_recent_slope": pc2_recent_slope,
                            "n_pc": n_pc, "n_obs": n_obs,
                        }

                except Exception as _e:
                    st.error(f"PCA 計算失敗：{_e}")
                    with st.expander("🔍 Debug"):
                        st.code(_tb.format_exc())

    # ── 結果渲染（持久顯示）──────────────────────────────────────
    if "pca_result_v300" in st.session_state:
        R = st.session_state["pca_result_v300"]
        valid_tks = R["valid_tks"]
        var_exp   = R["var_exp"]
        cum_var   = R["cum_var"]
        pc1_load  = R["pc1_load"]
        pc2_load  = R["pc2_load"]
        labels    = [t.replace(".TW","").replace(".TWO","") for t in valid_tks]

        # ── 圖1: 碎石圖 (Scree Plot) ─────────────────────────────
        # 實戰意義：PC1 解釋力 > 50% 代表市場高度連動（難做 Alpha）
        # PC1 < 35% 代表個股分化嚴重（精選個股機會浮現）
        st.markdown(
            '<div style="font-family:\'JetBrains Mono\',monospace;font-size:9px;'
            'color:rgba(0,245,255,.35);letter-spacing:3px;text-transform:uppercase;'
            'margin:16px 0 6px;">① 解釋方差碎石圖 — 市場集中度儀表板</div>',
            unsafe_allow_html=True
        )
        n_show = min(R["n_pc"], len(var_exp))
        fig_scree = go.Figure()
        bar_colors = [
            "#FFD700" if i == 0 else "#FF9A3C" if i == 1 else "#00F5FF"
            for i in range(n_show)
        ]
        fig_scree.add_trace(go.Bar(
            x=[f"PC{i+1}" for i in range(n_show)],
            y=var_exp[:n_show],
            marker_color=bar_colors,
            name="個別解釋力 (%)",
            text=[f"{v:.1f}%" for v in var_exp[:n_show]],
            textposition="outside",
            textfont=dict(color="#CDD", size=11, family="JetBrains Mono"),
        ))
        fig_scree.add_trace(go.Scatter(
            x=[f"PC{i+1}" for i in range(n_show)],
            y=cum_var[:n_show],
            mode="lines+markers",
            line=dict(color="#00FF7F", width=2, dash="dot"),
            marker=dict(size=7, color="#00FF7F"),
            name="累積解釋力 (%)",
            yaxis="y2",
        ))
        # 50%/80% 警戒線
        fig_scree.add_hline(
            y=50, line_color="rgba(255,215,0,0.3)", line_dash="dot",
            annotation_text="50%",
            annotation_font_color="rgba(255,215,0,0.5)",
            annotation_font_size=9
        )
        fig_scree.update_layout(
            template="plotly_dark", height=280,
            title=dict(
                text=(
                    f"市場系統性集中度  |  PC1={var_exp[0]:.1f}%  PC2={var_exp[1]:.1f}%  "
                    f"前2PC累積={cum_var[1]:.1f}%"
                ),
                font=dict(size=12, color="#CDD", family="Rajdhani")
            ),
            yaxis=dict(title="解釋方差 (%)", gridcolor="rgba(255,255,255,0.05)"),
            yaxis2=dict(
                title="累積解釋力 (%)",
                overlaying="y", side="right",
                gridcolor="rgba(0,0,0,0)", showgrid=False
            ),
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            barmode="overlay",
            legend=dict(orientation="h", y=1.02,
                        font=dict(color="#AAB", size=10)),
            margin=dict(t=45, b=40, l=60, r=60),
        )
        st.plotly_chart(fig_scree, use_container_width=True)

        # PC1 集中度解讀
        pc1_conc = float(var_exp[0])
        if pc1_conc >= 55:
            st.error(
                f"⚠️ PC1 解釋力高達 {pc1_conc:.1f}%，市場處於**高度系統性連動**狀態。"
                "個股分化極低，此時做 Alpha 勝算差——以 Beta 策略為主，追隨大盤方向。"
            )
        elif pc1_conc >= 40:
            st.warning(
                f"⚖️ PC1={pc1_conc:.1f}%，市場中度連動。"
                "部分板塊已開始分化，可開始關注 PC2 正負極端標的的相對強弱。"
            )
        else:
            st.success(
                f"✅ PC1={pc1_conc:.1f}%，市場個股分化顯著。"
                "精選個股的 Alpha 機會豐富，適合主動操作。"
            )

        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

        # ── 圖2: Loading Biplot (資金陣營雷達圖) ─────────────────
        st.markdown(
            '<div style="font-family:\'JetBrains Mono\',monospace;font-size:9px;'
            'color:rgba(0,245,255,.35);letter-spacing:3px;text-transform:uppercase;'
            'margin:16px 0 6px;">② 資金陣營雷達圖 — PC1 vs PC2 因子載荷</div>',
            unsafe_allow_html=True
        )
        # 顏色：PC2 正值 = 綠（多頭陣營）；負值 = 紅（空頭陣營）
        dot_colors = [
            "#00FF7F" if v > 0.05 else "#FF3131" if v < -0.05 else "#FFD700"
            for v in pc2_load
        ]
        fig_bp = go.Figure()
        # 圓形邊界參考
        theta_circ = np.linspace(0, 2*np.pi, 100)
        for r_circ in [0.1, 0.2, 0.3]:
            fig_bp.add_trace(go.Scatter(
                x=r_circ * np.cos(theta_circ),
                y=r_circ * np.sin(theta_circ),
                mode='lines',
                line=dict(color='rgba(255,255,255,0.05)', width=1),
                showlegend=False, hoverinfo='skip'
            ))
        # 箭頭（向量）
        for i, lbl in enumerate(labels):
            fig_bp.add_annotation(
                x=float(pc1_load[i]),
                y=float(pc2_load[i]),
                ax=0, ay=0, xref='x', yref='y', axref='x', ayref='y',
                arrowhead=3, arrowsize=1.2,
                arrowcolor=dot_colors[i], arrowwidth=1.5,
                showarrow=True
            )
        # 標籤點
        fig_bp.add_trace(go.Scatter(
            x=pc1_load.tolist(),
            y=pc2_load.tolist(),
            mode="markers+text",
            text=labels,
            textposition="top center",
            marker=dict(
                size=13, color=dot_colors,
                line=dict(color='rgba(255,255,255,0.3)', width=1)
            ),
            textfont=dict(color="#DDE", size=10, family="JetBrains Mono"),
            hovertemplate=[
                f"<b>{lbl}</b><br>PC1:{float(pc1_load[i]):.3f}<br>"
                f"PC2:{float(pc2_load[i]):.3f}<extra></extra>"
                for i, lbl in enumerate(labels)
            ]
        ))
        fig_bp.add_hline(y=0, line_color="rgba(255,255,255,0.1)", line_dash="dot")
        fig_bp.add_vline(x=0, line_color="rgba(255,255,255,0.1)", line_dash="dot")
        # 象限標籤
        for qx, qy, ql, qc in [
            ( 0.22,  0.22, "PC2↑ 避險/輪動受益",  "#00FF7F"),
            (-0.22,  0.22, "大盤空/板塊多",        "#FFD700"),
            ( 0.22, -0.22, "大盤多/板塊空",        "#FF9A3C"),
            (-0.22, -0.22, "雙空（高風險）",        "#FF3131"),
        ]:
            fig_bp.add_annotation(
                x=qx, y=qy, text=ql,
                showarrow=False,
                font=dict(color=qc, size=8, family="JetBrains Mono"),
                bgcolor="rgba(0,0,0,0.55)", borderpad=3
            )
        fig_bp.update_layout(
            template="plotly_dark", height=480,
            title=dict(
                text=(
                    f"PC1（大盤系統因子 {var_exp[0]:.1f}%）vs "
                    f"PC2（板塊輪動因子 {var_exp[1]:.1f}%）"
                ),
                font=dict(size=13, color="#CDD", family="Rajdhani")
            ),
            xaxis=dict(
                title=f"PC1 載荷  →  越右 = 越跟著大盤漲跌",
                gridcolor="rgba(255,255,255,0.04)", zeroline=False
            ),
            yaxis=dict(
                title=f"PC2 載荷  ↑↓ = 蹺蹺板資金對立",
                gridcolor="rgba(255,255,255,0.04)", zeroline=False,
                scaleanchor="x", scaleratio=1
            ),
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            showlegend=False,
            margin=dict(t=50, b=50, l=70, r=20),
        )
        st.plotly_chart(fig_bp, use_container_width=True)

        # ── 圖3: PC 分數時間序列（因子強度演變）────────────────────
        st.markdown(
            '<div style="font-family:\'JetBrains Mono\',monospace;font-size:9px;'
            'color:rgba(0,245,255,.35);letter-spacing:3px;text-transform:uppercase;'
            'margin:16px 0 6px;">③ 因子強度時間序列 — 板塊輪動時鐘</div>',
            unsafe_allow_html=True
        )
        pc1_ts = R["pc1_ts"]
        pc2_ts = R["pc2_ts"]
        pc2_roll = R["pc2_roll"]

        fig_ts = go.Figure()
        # PC1（大盤）
        fig_ts.add_trace(go.Scatter(
            x=pc1_ts.index, y=pc1_ts.values,
            mode='lines',
            line=dict(color='rgba(255,215,0,0.5)', width=1),
            fill='tozeroy',
            fillcolor='rgba(255,215,0,0.03)',
            name='PC1 大盤系統因子',
        ))
        # PC2（輪動）
        fig_ts.add_trace(go.Scatter(
            x=pc2_ts.index, y=pc2_ts.values,
            mode='lines',
            line=dict(color='rgba(0,245,255,0.45)', width=1),
            name='PC2 板塊輪動因子',
        ))
        # PC2 滾動均線（輪動趨勢）
        fig_ts.add_trace(go.Scatter(
            x=pc2_roll.index, y=pc2_roll.values,
            mode='lines',
            line=dict(color='#00F5FF', width=2.5),
            name='PC2 滾動20日均線（輪動趨勢）',
        ))
        fig_ts.add_hline(y=0, line_color="rgba(255,255,255,0.1)", line_dash="dot")
        fig_ts.update_layout(
            template="plotly_dark", height=320,
            title=dict(
                text="PC1（黃=大盤情緒）vs PC2（藍=板塊輪動）— 輪動轉折看20日均線穿越零軸",
                font=dict(size=12, color="#CDD", family="Rajdhani")
            ),
            xaxis=dict(gridcolor="rgba(255,255,255,0.04)"),
            yaxis=dict(
                title="因子強度（標準差單位）",
                gridcolor="rgba(255,255,255,0.04)"
            ),
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            hovermode="x unified",
            legend=dict(orientation="h", y=1.02,
                        font=dict(color="#AAB", size=10)),
            margin=dict(t=45, b=40, l=65, r=20),
        )
        st.plotly_chart(fig_ts, use_container_width=True)

        # ── 圖4: 配對交易 PC2 累積擴散圖 ────────────────────────
        pair_long  = R["pair_long"]
        pair_short = R["pair_short"]
        pc2_spread = R["pc2_spread"]

        st.markdown(
            '<div style="font-family:\'JetBrains Mono\',monospace;font-size:9px;'
            'color:rgba(0,245,255,.35);letter-spacing:3px;text-transform:uppercase;'
            'margin:16px 0 6px;">④ 配對交易信號 — PC2 最強對立資金對</div>',
            unsafe_allow_html=True
        )
        fig_pair = go.Figure()
        fig_pair.add_trace(go.Scatter(
            x=pc2_spread.index, y=pc2_spread.values,
            mode='lines',
            line=dict(color='#B77DFF', width=2),
            fill='tozeroy',
            fillcolor='rgba(183,125,255,0.06)',
            name=f'PC2 累積擴散 ({pair_long.replace(".TW","")}'
                 f' vs {pair_short.replace(".TW","")})',
        ))
        fig_pair.add_hline(y=0, line_color="rgba(255,255,255,0.15)", line_dash="dot")
        fig_pair.update_layout(
            template="plotly_dark", height=230,
            title=dict(
                text=(
                    f"近30日 PC2 累積擴散：{pair_long.replace('.TW','')} ⬆  vs  "
                    f"{pair_short.replace('.TW','')} ⬇  — 蹺蹺板資金對立"
                ),
                font=dict(size=12, color="#CDD", family="Rajdhani")
            ),
            xaxis=dict(gridcolor="rgba(255,255,255,0.04)"),
            yaxis=dict(gridcolor="rgba(255,255,255,0.04)"),
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            showlegend=False,
            margin=dict(t=45, b=40, l=65, r=20),
        )
        st.plotly_chart(fig_pair, use_container_width=True)

        # ── 風險分解表 ────────────────────────────────────────────
        st.markdown(
            '<div style="font-family:\'JetBrains Mono\',monospace;font-size:9px;'
            'color:rgba(0,245,255,.35);letter-spacing:3px;text-transform:uppercase;'
            'margin:16px 0 6px;">⑤ 風險分解矩陣 — 系統性 vs 特異性</div>',
            unsafe_allow_html=True
        )
        st.dataframe(R["risk_df"], use_container_width=True, hide_index=True)

        # ── Valkyrie AI 整合判斷 ──────────────────────────────────
        st.divider()
        pc2_slope     = R["pc2_recent_slope"]
        pair_dir      = R["pair_dir"]
        pc2_cur_val   = float(pc2_ts.iloc[-1])
        alpha_stocks  = R["risk_df"][R["risk_df"]["系統性R²"] < 0.4]["代號"].tolist()
        beta_stocks   = R["risk_df"][R["risk_df"]["系統性R²"] >= 0.8]["代號"].tolist()

        rotation_signal = (
            "🔄 板塊加速輪動（PC2 均線向上穿越）"  if pc2_slope > 0.05
            else "🔄 板塊反向輪動（PC2 均線向下穿越）" if pc2_slope < -0.05
            else "⚖️ 輪動趨勢平緩，方向不明"
        )

        st.markdown(
            f'<div style="padding:16px 20px;background:rgba(0,0,0,0.35);'
            f'border:1px solid rgba(0,245,255,0.15);border-left:4px solid #00F5FF;'
            f'border-radius:0 12px 12px 0;margin-bottom:14px;">'
            f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:9px;'
            f'color:rgba(0,245,255,.4);letter-spacing:3px;text-transform:uppercase;'
            f'margin-bottom:8px;">⚡ Valkyrie AI · PCA 戰略解析</div>'
            f'<div style="font-family:\'Rajdhani\',sans-serif;font-size:16px;'
            f'font-weight:600;color:#FFF;">{rotation_signal}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

        col_v1, col_v2 = st.columns(2)
        with col_v1:
            st.markdown(
                f"**📐 市場結構（碎石圖）**\n\n"
                f"PC1 解釋力 **{float(var_exp[0]):.1f}%**，"
                f"前 2 PC 累積 **{float(cum_var[1]):.1f}%**。\n\n"
                f"{'高度系統連動，個股 Alpha 空間壓縮，建議 Beta 策略為主。' if pc1_conc >= 50 else '市場分化明顯，主動選股機會浮現。'}"
            )
            st.markdown(
                f"**🧲 Beta 工具股**（系統R²≥0.8）：{', '.join(beta_stocks) if beta_stocks else '本次觀測無純Beta股'}\n\n"
                f"**🎯 Alpha 來源股**（系統R²<0.4）：{', '.join(alpha_stocks) if alpha_stocks else '本次觀測無高Alpha股'}"
            )
        with col_v2:
            st.markdown(
                f"**🔀 配對交易訊號**\n\n"
                f"PC2 最強資金對立：做多 **{pair_long.replace('.TW','')}** / "
                f"做空 **{pair_short.replace('.TW','')}**\n\n"
                f"近 30 日 PC2 擴散方向：**{pair_dir} {pair_long.replace('.TW','')}**\n\n"
                f"PC2 滾動趨勢斜率：**{pc2_slope:+.4f}**（正值=輪動向{pair_long.replace('.TW','')}，負值=反向）"
            )




# ═══════════════════════════════════════════════════════════════
# SECTION 6.6 — 回測沙盒 (ENHANCED — was placeholder)
# ═══════════════════════════════════════════════════════════════
def _s66():
    st.markdown('<div class="t6-sec-head" style="--sa:#B77DFF"><div class="t6-sec-num">6.6</div><div><div class="t6-sec-title" style="color:#B77DFF;">幾何回測沙盒</div><div class="t6-sec-sub">Angle Signal · Equity Curve · Threshold Sweep · vs Buy & Hold</div></div></div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        bt_ticker = st.text_input("回測標的", "NVDA", key="bt_tk_v300")
        bt_start = st.date_input("起始日期", value=datetime(2015, 1, 1), key="bt_start_v300")
        bt_cap = st.number_input("初始資金", value=1_000_000, step=100_000, key="bt_cap_v300")
    with c2:
        bt_win = st.selectbox("窗口", ["3M", "6M", "1Y", "3Y"], key="bt_win_v300")
        bt_thresh = st.slider("門檻 (°)", -90, 90, 10, key="bt_thresh_v300")
        st.info(f"策略：{bt_win} 角度 > {bt_thresh}° 則持倉")

    if st.button("🚀 啟動回測", type="primary", use_container_width=True, key="run_bt_v300"):
        with st.spinner(f"回測 {bt_ticker}…"):
            r = _geo_backtest(bt_ticker, float(bt_thresh), bt_win, bt_start.strftime("%Y-%m-%d"), float(bt_cap))
        if r:
            st.session_state["gbt"] = r
            st.session_state["gbt_lbl"] = f"{bt_ticker}-{bt_win}->{bt_thresh}°"
            st.success(f"CAGR {r['cagr']:.2%} | Sharpe {r['sharpe']:.2f} | MDD {r['mdd']:.2%}")
        else:
            st.toast("❌ 回測失敗", icon="💀")

    if "gbt" in st.session_state:
        r = st.session_state["gbt"]
        lbl = st.session_state.get("gbt_lbl", "")
        b1, b2, b3, b4, b5 = st.columns(5)
        b1.metric("CAGR", f"{r['cagr']:.2%}")
        b2.metric("Sharpe", f"{r['sharpe']:.2f}")
        b3.metric("MDD", f"{r['mdd']:.2%}")
        b4.metric("期末資金", f"{r['fe']:,.0f}")
        b5.metric("B&H CAGR", f"{r['bh_cagr']:.2%}")
        alpha = r["cagr"] - r["bh_cagr"]
        if alpha >= 0:
            st.success(f"Alpha: +{alpha:.2%}")
        else:
            st.warning(f"Alpha: {alpha:.2%}")

        st.divider()
        eq_df = r["eq"].reset_index()
        eq_df.columns = ["Date", "Equity"]
        bh_df = r["bh"].reset_index()
        bh_df.columns = ["Date", "BH"]
        fig_eq = go.Figure()
        fig_eq.add_trace(go.Scatter(x=eq_df["Date"], y=eq_df["Equity"], name="幾何策略", line=dict(color="#00F5FF", width=2)))
        fig_eq.add_trace(go.Scatter(x=bh_df["Date"], y=bh_df["BH"], name="Buy & Hold", line=dict(color="rgba(255,215,0,.6)", width=1.5, dash="dot")))
        fig_eq.update_layout(title=dict(text=f"權益曲線 - {lbl}"), template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=360, margin=dict(t=30, b=40, l=70, r=10), hovermode="x unified")
        st.plotly_chart(fig_eq, use_container_width=True)

        dd_df = r["dd"].reset_index()
        dd_df.columns = ["Date", "DD"]
        dd_df["DD_pct"] = dd_df["DD"] * 100
        fig_dd = px.area(dd_df, x="Date", y="DD_pct", title="Underwater 回撤曲線")
        fig_dd.update_traces(fillcolor="rgba(255,49,49,.22)", line_color="rgba(255,49,49,.75)")
        fig_dd.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=230, margin=dict(t=30, b=40, l=60, r=10))
        st.plotly_chart(fig_dd, use_container_width=True)

        st.divider()
        st.subheader("🔬 多門檻掃描")
        if st.button("啟動門檻掃描", use_container_width=True, key="run_sweep_v300"):
            sweep_list = list(range(-30, 55, 5))
            sweep_rows = []
            sp = st.progress(0)
            for si, sw in enumerate(sweep_list):
                sr = _geo_backtest(bt_ticker, float(sw), bt_win, bt_start.strftime("%Y-%m-%d"), float(bt_cap))
                sp.progress((si + 1) / len(sweep_list), text=f"門檻 {sw}°…")
                if sr:
                    sweep_rows.append({"門檻(°)": sw, "CAGR": sr["cagr"], "Sharpe": sr["sharpe"], "MDD": sr["mdd"]})
            sp.empty()
            if sweep_rows:
                sw_df = pd.DataFrame(sweep_rows)
                best = sw_df.loc[sw_df["CAGR"].idxmax()]
                st.success(f"最優: {int(best['門檻(°)'])}° → CAGR {best['CAGR']:.2%} | Sharpe {best['Sharpe']:.2f}")
                st.session_state["sweep_df"] = sw_df

        if "sweep_df" in st.session_state:
            sw_df = st.session_state["sweep_df"]
            fig_sw = go.Figure()
            fig_sw.add_trace(go.Scatter(x=sw_df["門檻(°)"], y=sw_df["CAGR"] * 100, name="CAGR(%)", mode="lines+markers", line=dict(color="#00FF7F", width=2)))
            fig_sw.add_trace(go.Scatter(x=sw_df["門檻(°)"], y=sw_df["Sharpe"], name="Sharpe", mode="lines+markers", line=dict(color="#FFD700", width=1.5, dash="dash"), yaxis="y2"))
            fig_sw.update_layout(
                template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=310,
                yaxis=dict(title="CAGR(%)", ticksuffix="%"),
                yaxis2=dict(title="Sharpe", overlaying="y", side="right"),
                margin=dict(t=30, b=40, l=70, r=70), hovermode="x unified"
            )
            st.plotly_chart(fig_sw, use_container_width=True)
            st.dataframe(sw_df.style.format({"CAGR": "{:.2%}", "Sharpe": "{:.2f}", "MDD": "{:.2%}"}), use_container_width=True)
            st.download_button("下載掃描報表 (CSV)", sw_df.to_csv(index=False).encode(), f"{bt_ticker}_sweep.csv", use_container_width=True)


# ═══════════════════════════════════════════════════════════════
# MAIN ENTRY
# ═══════════════════════════════════════════════════════════════
def render():
    """Tab 6 — 元趨勢戰法 Global Market Hologram V300"""
    
    # ══════════════════════════════════════════════════════════════
    # 🎯 FEATURE 1: Show tactical guide modal on first visit
    # ══════════════════════════════════════════════════════════════
    if "guide_shown_" + __name__ not in st.session_state:
        show_guide_modal()
        st.session_state["guide_shown_" + __name__] = True
    
    _inject_css()
    _render_hero()
    _render_nav_rail()

    section_map = {"6.1": _s61, "6.2": _s62, "6.3": _s63, "6.4": _s64, "6.5": _s65, "6.6": _s66}
    active = st.session_state.get('t6_active', '6.1')
    fn = section_map.get(active, _s61)
    try:
        fn()
    except Exception as exc:
        import traceback
        st.toast(f"❌ Section {active} error: {exc}", icon="💀")
        st.error(f"❌ Section {active} error: {exc}")
        with st.expander("Debug"):
            st.code(traceback.format_exc())

    st.markdown(f'<div class="t6-foot">Titan MetaTrend Holographic Deck V300 · {datetime.now().strftime("%Y-%m-%d %H:%M")}</div>', unsafe_allow_html=True)
