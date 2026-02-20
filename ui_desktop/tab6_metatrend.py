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
    *建議：先執行 6.1 全局掃描，再針對目標標的進入 6.2 深度分析*
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
                               intel_text="", commander_note="", selected_principles=None):
        level, name, desc, color = rating_info
        # 幾何數據格式化
        geo_str = f"""
1. 超長期視角 (35 年): 角度 {geo_data.get('35Y',{}).get('angle',0)}°, R² {geo_data.get('35Y',{}).get('r2',0)}, 斜率 {geo_data.get('35Y',{}).get('slope',0)}
2. 長期視角 (10 年): 角度 {geo_data.get('10Y',{}).get('angle',0)}°, R² {geo_data.get('10Y',{}).get('r2',0)}, 斜率 {geo_data.get('10Y',{}).get('slope',0)}
3. 中長期視角 (5 年): 角度 {geo_data.get('5Y',{}).get('angle',0)}°, R² {geo_data.get('5Y',{}).get('r2',0)}, 斜率 {geo_data.get('5Y',{}).get('slope',0)}
4. 中期視角 (3 年): 角度 {geo_data.get('3Y',{}).get('angle',0)}°, R² {geo_data.get('3Y',{}).get('r2',0)}, 斜率 {geo_data.get('3Y',{}).get('slope',0)}
5. 短中期視角 (1 年): 角度 {geo_data.get('1Y',{}).get('angle',0)}°, R² {geo_data.get('1Y',{}).get('r2',0)}, 斜率 {geo_data.get('1Y',{}).get('slope',0)}
6. 短期視角 (6 個月): 角度 {geo_data.get('6M',{}).get('angle',0)}°, R² {geo_data.get('6M',{}).get('r2',0)}, 斜率 {geo_data.get('6M',{}).get('slope',0)}
7. 極短期視角 (3 個月): 角度 {geo_data.get('3M',{}).get('angle',0)}°, R² {geo_data.get('3M',{}).get('r2',0)}, 斜率 {geo_data.get('3M',{}).get('slope',0)}

加速度: {geo_data.get('acceleration',0)}° (3M角度 - 1Y角度)
Phoenix 信號: {'🔥 觸發' if geo_data.get('phoenix_signal') else '❄️ 未觸發'}
"""
        principles_str = ""
        if selected_principles:
            principles_str = "\n## 🎯 統帥指定第一性原則 (必須回答)\n"
            for idx, p in enumerate(selected_principles, 1):
                principles_str += f"{idx}. {p}\n"
        prompt = f"""
# 🏛️ Titan Protocol V300: 諸神黃昏戰情室 (The Ragnarök War Room)
# 目標代號: {ticker} | 現價: ${price:.2f}

你現在是 Titan 基金的「最高參謀本部」。我們正在決定是否要將此標的納入「2033 百倍股」的核心持倉。
這不是普通的分析，這是一場 **生死辯論**。

## 📊 戰場地形 (幾何數據)
{geo_str}

## 🏆 泰坦信評 (Titan Rating)
評級等級：{level}
評級名稱：{name}
評級描述：{desc}
(這是基於 22 階信評系統的初步判定，各位角鬥士可以挑戰或支持此評級)

## 🕵️ 實彈情報 (Insider Intel)
(以下資料來自法說會/財報/新聞/瓦爾基里自動抓取，必須被引用作為攻擊或防禦的武器)
{intel_text if intel_text else "無外部情報注入，請基於幾何數據與你的知識庫進行推演。"}
{principles_str}

## ✍️ 統帥第一性原則 (Commander's Override)
(這是最高指令，Arbiter 必須以此為最終裁決的邏輯基石)
{commander_note if commander_note else "無特殊指令，請依據最大利益原則裁決。"}

---

## ⚔️ 五大角鬥士戰鬥程序 (Battle Protocol)

請扮演以下五位角色，進行一場**史詩級的對話 (Epic Debate)**。

**【絕對規則 (Anti-Laziness Protocol)】**
1. **字數強制**：每一位角色的發言 **不得少於 800 字** (Arbiter 需 1000 字以上)。
2. **禁止客套**：這是一場你死我活的辯論。Burry 必須尖酸刻薄，Visionary 必須狂熱，Insider 必須狡猾。
3. **第一性原則**：所有論點必須回歸物理極限、現金流本質與技術邊界，禁止使用模糊的金融術語。
4. **數據引用**：每個論點必須明確引用上方的幾何數據或實彈情報。
5. **互動續寫**：每位角色發言時，必須引用前一位角色的觀點並進行反駁或補充，確保辯論連續性。

### 角色定義：

**1. 【幾何死神】(The Quant - 冷血數學家)**
* **性格**：冷血、無情、只相信數學。
* **任務**：根據上方的幾何數據 (35Y, 10Y, 3M 斜率與加速度)，判斷股價是否過熱？R² 是否穩定？
* **口頭禪**：「數據不會說謊，人類才會。」
* **論點要求**：至少 800 字，必須引用具體角度與 R² 數值。必須分析 7 個時間窗口的趨勢一致性。

**2. 【內部操盤手】(The Insider - CEO/CFO 化身)**
* **性格**：防禦性強、報喜不報憂、擅長畫大餅。
* **任務**：利用「實彈情報」中的數據，護航公司的成長故事。解釋為何現在是買點？
* **對抗**：當 Burry 攻擊估值時，你要拿出營收成長率反擊。並且必須引用 Quant 的幾何數據來支持你的觀點。
* **論點要求**：至少 800 字，若無實彈情報則從行業趨勢切入。必須引用瓦爾基里提供的基本面數據 (如毛利率、ROE)。

**3. 【大賣空獵人】(The Big Short - Michael Burry 化身)**
* **性格**：極度悲觀、被害妄想、尋找崩盤的前兆。
* **任務**：攻擊「內部人」的謊言。找出估值泡沫、毛利下滑、宏觀衰退的訊號。你必須引用 Insider 的論點並逐一駁斥。
* **第一性原則**：均值回歸是宇宙鐵律。所有拋物線最終都會墜毀。
* **論點要求**：至少 800 字，必須質疑信評等級的合理性。必須指出瓦爾基里數據中的風險點 (如負債比過高)。

**4. 【創世紀先知】(The Visionary - Cathie Wood/Elon Musk 化身)**
* **性格**：狂熱、指數級思維、無視短期虧損。
* **任務**：使用「萊特定律 (Wright's Law)」與「破壞式創新」來碾壓 Burry 的傳統估值。你必須引用 Burry 的悲觀論點並展示為何他錯了。
* **論點**：別跟我談 PE，看 2033 年的 TAM (潛在市場)。
* **論點要求**：至少 800 字，必須展望未來 5-10 年的產業變革。必須引用瓦爾基里提供的產業資訊與新聞動態。

**5. 【地球頂點·全知者】(The Apex Arbiter - 查理·蒙格 + 科技七巨頭創辦人)**
* **腦袋**：查理·蒙格 (反向思考) + 貝佐斯/馬斯克 (極致商業直覺)。
* **任務**：你是最終法官。聽完前面四人的血戰後，結合「統帥第一性原則」，給出最終判決。你必須引用各方論點，並解釋為何某方的邏輯更有說服力。
* **輸出格式**：
    * **【戰場總結】**：(300 字評析各方論點的強弱，明確指出誰的論點最有力、誰的論點有漏洞)
    * **【第一性原則裁決】**：(400 字回歸物理與商業本質的判斷，必須回答統帥指定的第一性原則問題)
    * **【操作指令】**：
        - 行動方針：Strong Buy / Buy / Wait / Sell / Strong Sell
        - 進場價位：基於趨勢線乖離率建議 (具體數字)
        - 停損價位：明確數字
        - 停利價位：明確數字
        - 持倉建議：輕倉/標準倉/重倉/空倉
        - 風險提示：[3 個關鍵風險]
* **論點要求**：至少 1000 字，必須展現真正的智慧而非模板化結論。必須整合瓦爾基里的基本面、新聞與幾何數據。

---

## 📋 輸出格式要求

請按照以下結構輸出：

## 🤖 幾何死神 (The Quant)
[800+ 字的冷血數學分析，必須分析 7 個時間窗口]

---

## 💼 內部操盤手 (The Insider)
[800+ 字的成長故事護航，並引用 Quant 的數據與瓦爾基里基本面]

---

## 🐻 大賣空獵人 (The Big Short)
[800+ 字的悲觀攻擊，並駁斥 Insider 的論點，指出瓦爾基里數據中的風險]

---

## 🚀 創世紀先知 (The Visionary)
[800+ 字的狂熱展望，並反駁 Burry 的悲觀，引用產業趨勢與新聞]

---

## ⚖️ 地球頂點·全知者 (The Apex Arbiter)

### 【戰場總結】
[300+ 字，評析各方論點，指出誰最有力]

### 【第一性原則裁決】
[400+ 字，回答統帥指定問題，整合瓦爾基里數據]

### 【操作指令】
- **行動方針**: [Strong Buy / Buy / Wait / Sell / Strong Sell]
- **進場價位**: $XXX (基於趨勢線 ±Y%)
- **停損價位**: $XXX
- **停利價位**: $XXX
- **持倉建議**: [輕倉/標準倉/重倉/空倉]
- **風險提示**: [3 個關鍵風險]

---

請以繁體中文回答。確保每個角色的論述都具有深度與獨特性，避免重複論點，並且每位角色都必須引用前面角色的觀點進行互動。字數要求是最低門檻，請盡量詳細展開論述。
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
    "[終極] 百倍股基因：2033 年若活著，它會變成什麼樣子？",
]

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
        ("6.3", "📜", "獵殺清單", "Hunter List"), ("6.4", "⚔️", "全境獵殺", "Full Scan"),
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
                        st.session_state['globe_tickers_val'] = SCAN_TEMPLATES[k]
                        st.rerun()

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════════
    # BLOCK B: INPUT + SCAN CONTROLS
    # ═══════════════════════════════════════════════════════════
    default_val = st.session_state.get('globe_tickers_val', "NVDA,TSLA,2330.TW,2454.TW")
    col_in, col_sort, col_btn = st.columns([3, 1, 1])
    tickers_raw = col_in.text_input(
        "標的代號 (逗號分隔，台股自動補 .TW/.TWO)",
        value=default_val,
        key="globe_tickers"
    )
    sort_by = col_sort.selectbox(
        "排序依據", ["1Y角度", "3M角度", "加速度", "信評"],
        key="globe_sort"
    )
    do_scan = col_btn.button("🔍 掃描", type="primary",
                              key="globe_scan", use_container_width=True)

    # Persist input
    st.session_state['globe_tickers_val'] = tickers_raw

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
    # BLOCK C: FFT CYCLE EXTRACTION
    # ═══════════════════════════════════════════════════════════
    st.divider()
    st.markdown("### 📡 快速傅立葉轉換 (FFT 週期頻譜萃取)")
    st.caption("將股價走勢視為複合聲波，透過 numpy.fft 濾除市場雜訊，萃取出隱藏的「絕對漲跌週期」。")

    fft_col_in, fft_col_btn = st.columns([3, 1])
    fft_symbol_raw = fft_col_in.text_input(
        "FFT 單一標的代號", value="NVDA",
        key="fft_symbol_input",
        placeholder="NVDA / 2330.TW / 5274 …"
    )
    do_fft = fft_col_btn.button(
        "🌊 頻譜掃描", type="primary",
        key="fft_scan", use_container_width=True
    )

    if do_fft:
        if not fft_symbol_raw.strip():
            st.warning("請輸入標的代號。")
        else:
            # ── 台股後綴解析（與 5.1/5.3 相同邏輯）─────────────────
            import re as _re
            raw_sym  = fft_symbol_raw.strip().upper()
            base_sym = raw_sym.replace(".TW", "").replace(".TWO", "")
            is_tw    = bool(_re.fullmatch(r'\d{4,6}[A-Z0-9]*', base_sym))

            if is_tw and not (raw_sym.endswith(".TW") or raw_sym.endswith(".TWO")):
                symbol = None
                for sfx in [".TW", ".TWO"]:
                    try:
                        _probe = yf.download(base_sym + sfx, period="1mo",
                                             progress=False, auto_adjust=True)
                        if isinstance(_probe.columns, pd.MultiIndex):
                            _probe.columns = _probe.columns.get_level_values(0)
                        if "Close" in _probe.columns and _probe["Close"].dropna().shape[0] >= 5:
                            symbol = base_sym + sfx
                            break
                    except Exception:
                        continue
                if symbol is None:
                    st.error(f"❌ 無法解析台股代號 {raw_sym}，請確認（如 2330.TW / 5274.TWO）。")
                    symbol = None
            else:
                symbol = raw_sym

            if symbol:
                with st.spinner(f"🧠 正在對 {symbol} 進行傅立葉頻譜解碼..."):
                    try:
                        # 1. Fetch 2-year data
                        raw_dl = yf.download(symbol, period="2y",
                                             progress=False, auto_adjust=True)
                        if raw_dl.empty:
                            st.error(f"❌ 無法取得 {symbol} 的歷史數據。")
                        else:
                            if isinstance(raw_dl.columns, pd.MultiIndex):
                                raw_dl.columns = raw_dl.columns.get_level_values(0)

                            if "Close" not in raw_dl.columns:
                                st.error(f"❌ {symbol} 資料缺少 Close 欄：{list(raw_dl.columns)}")
                            else:
                                df_fft = raw_dl["Close"].dropna()
                                if len(df_fft) < 100:
                                    st.error(f"❌ {symbol} 有效資料不足 100 日 (現有 {len(df_fft)} 日)。")
                                else:
                                    # 2. Detrend — subtract 50-day MA
                                    ma50      = df_fft.rolling(window=50).mean()
                                    detrended = (df_fft - ma50).dropna()

                                    # 3. numpy FFT
                                    n         = len(detrended)
                                    fft_vals  = np.fft.fft(detrended.values)
                                    fft_freqs = np.fft.fftfreq(n, d=1)

                                    # Positive frequencies only
                                    pos_mask  = fft_freqs > 0
                                    pos_freqs = fft_freqs[pos_mask]
                                    pos_mags  = np.abs(fft_vals)[pos_mask]

                                    # Filter: 5–200 day cycles
                                    valid_mask  = (1 / pos_freqs <= 200) & (1 / pos_freqs >= 5)
                                    valid_freqs = pos_freqs[valid_mask]
                                    valid_mags  = pos_mags[valid_mask]

                                    if len(valid_mags) == 0:
                                        st.warning("⚠️ 無法萃取出明顯的中短期週期，市場可能處於高度隨機狀態。")
                                    else:
                                        # 4. Top-3 dominant cycles
                                        top3_idx     = np.argsort(valid_mags)[::-1][:3]
                                        dom_idx      = top3_idx[0]
                                        dom_freq     = valid_freqs[dom_idx]
                                        dom_period   = int(round(1 / dom_freq))
                                        dom_mag      = valid_mags[dom_idx]

                                        # Reconstruct dominant wave
                                        phase     = np.angle(fft_vals[pos_mask][valid_mask][dom_idx])
                                        amplitude = 2.0 * dom_mag / n
                                        t_full    = np.arange(n)
                                        dom_wave  = amplitude * np.cos(
                                            2 * np.pi * dom_freq * t_full + phase)

                                        lookback     = min(120, len(detrended))
                                        recent_det   = detrended.iloc[-lookback:]
                                        recent_wave  = dom_wave[-lookback:]

                                        # Top-3 secondary cycles info
                                        sec_periods = []
                                        for si in top3_idx[1:]:
                                            sp = int(round(1 / valid_freqs[si]))
                                            sec_periods.append(sp)

                                        # 5. Full frequency spectrum chart
                                        cycle_days = np.where(pos_freqs > 0, 1 / pos_freqs, 0)
                                        fig_spec = go.Figure()
                                        fig_spec.add_trace(go.Scatter(
                                            x=cycle_days, y=pos_mags,
                                            mode='lines',
                                            line=dict(color='rgba(0,245,255,0.5)', width=1),
                                            fill='tozeroy',
                                            fillcolor='rgba(0,245,255,0.06)',
                                            name='頻譜強度',
                                            hovertemplate='週期: %{x:.0f}天<br>強度: %{y:.2f}<extra></extra>'
                                        ))
                                        # Mark dominant cycle
                                        fig_spec.add_vline(
                                            x=dom_period,
                                            line_color="#FFD700", line_width=2, line_dash="dash",
                                            annotation_text=f"主週期 {dom_period}天",
                                            annotation_font_color="#FFD700"
                                        )
                                        for sp in sec_periods:
                                            fig_spec.add_vline(
                                                x=sp, line_color="rgba(255,154,60,0.6)",
                                                line_width=1, line_dash="dot",
                                                annotation_text=f"{sp}天",
                                                annotation_font_color="rgba(255,154,60,0.8)",
                                                annotation_font_size=9
                                            )
                                        fig_spec.update_layout(
                                            template="plotly_dark", height=220,
                                            title=dict(
                                                text=f"{symbol} 頻率功率譜 (5–200天週期)",
                                                font=dict(size=13, color="#AAB", family="Rajdhani")
                                            ),
                                            xaxis=dict(
                                                title="週期長度 (交易日)",
                                                range=[0, 200],
                                                gridcolor="rgba(255,255,255,0.05)"
                                            ),
                                            yaxis=dict(
                                                title="頻譜強度",
                                                gridcolor="rgba(255,255,255,0.05)"
                                            ),
                                            plot_bgcolor="rgba(0,0,0,0)",
                                            paper_bgcolor="rgba(0,0,0,0)",
                                            margin=dict(t=40, b=40, l=60, r=20),
                                            showlegend=False,
                                        )
                                        st.plotly_chart(fig_spec, use_container_width=True)

                                        # 6. Detrended vs dominant wave chart
                                        fig_wave = go.Figure()
                                        fig_wave.add_trace(go.Scatter(
                                            x=recent_det.index, y=recent_det.values,
                                            mode='lines',
                                            line=dict(color='rgba(255,255,255,0.35)', width=1.5),
                                            name='去趨勢股價 (真實雜訊)',
                                            hovertemplate='%{y:.2f}<extra>去趨勢股價</extra>'
                                        ))
                                        fig_wave.add_trace(go.Scatter(
                                            x=recent_det.index, y=recent_wave,
                                            mode='lines',
                                            line=dict(color='#00F5FF', width=2.5),
                                            name=f'FFT 主週期 ({dom_period} 天)',
                                            hovertemplate='%{y:.2f}<extra>FFT 主週期</extra>'
                                        ))
                                        # Zero line
                                        fig_wave.add_hline(
                                            y=0, line_color='rgba(255,255,255,0.1)',
                                            line_dash='dot'
                                        )
                                        fig_wave.update_layout(
                                            template="plotly_dark", height=380,
                                            title=dict(
                                                text=f"🎯 {symbol} 週期共振分析（近 {lookback} 交易日）",
                                                font=dict(size=14, color="#CDD", family="Rajdhani")
                                            ),
                                            xaxis=dict(
                                                title="時間",
                                                gridcolor="rgba(255,255,255,0.04)"
                                            ),
                                            yaxis=dict(
                                                title="震盪振幅",
                                                gridcolor="rgba(255,255,255,0.04)"
                                            ),
                                            plot_bgcolor="rgba(0,0,0,0)",
                                            paper_bgcolor="rgba(0,0,0,0)",
                                            hovermode="x unified",
                                            legend=dict(
                                                orientation="h", y=1.02,
                                                font=dict(color="#AAB", size=11)
                                            ),
                                            margin=dict(t=50, b=40, l=60, r=20),
                                        )
                                        st.plotly_chart(fig_wave, use_container_width=True)

                                        # 7. Strategic metrics
                                        current_wave_val = float(recent_wave[-1])
                                        prev_wave_val    = float(recent_wave[-2])
                                        cycle_position   = (current_wave_val / amplitude
                                                            if amplitude > 0 else 0)

                                        st.markdown("##### 📊 頻譜共振戰略解析")
                                        c1, c2, c3, c4 = st.columns(4)
                                        c1.metric("主要循環週期", f"{dom_period} 交易日",
                                                  f"≈ {dom_period/21:.1f} 個月")
                                        c2.metric("次要週期 #2", f"{sec_periods[0]} 日" if sec_periods else "—")
                                        c3.metric("次要週期 #3",
                                                  f"{sec_periods[1]} 日" if len(sec_periods) > 1 else "—")

                                        if current_wave_val > prev_wave_val:
                                            wave_dir, wave_col = "📈 上升波段", "normal"
                                        else:
                                            wave_dir, wave_col = "📉 下降波段", "inverse"
                                        c4.metric("目前相位", wave_dir,
                                                  f"週期位置 {cycle_position:+.2f}",
                                                  delta_color=wave_col)

                                        # 8. Valkyrie AI Tactical
                                        st.divider()
                                        is_trough = cycle_position < -0.7 and current_wave_val > prev_wave_val
                                        is_peak   = cycle_position >  0.7 and current_wave_val < prev_wave_val

                                        if is_trough:
                                            st.success(
                                                f"⚡ [Valkyrie AI 判定] 完美買點浮現！"
                                                f"{symbol} 正處於 {dom_period} 天循環的【波谷反轉區】"
                                                f"（相位 {cycle_position:.2f}，正開始回升）。"
                                                f"若上帝軌道（6.2）未破底，結合此訊號勝率極高，可積極建倉。"
                                            )
                                        elif is_peak:
                                            st.error(
                                                f"🔴 [Valkyrie AI 判定] 居高思危！"
                                                f"{symbol} 處於 {dom_period} 天循環的【波峰衰退區】"
                                                f"（相位 {cycle_position:.2f}，動能開始衰竭）。"
                                                f"建議逢高減碼，{sec_periods[0] if sec_periods else '?'} 天次週期確認方向後再重新介入。"
                                            )
                                        else:
                                            mid_dir = "上半段（偏多）" if cycle_position > 0 else "下半段（偏空）"
                                            st.info(
                                                f"⚖️ [Valkyrie AI 判定] {symbol} 運行於 {dom_period} 天循環"
                                                f"的中段 {mid_dir}（相位 {cycle_position:+.2f}）。"
                                                f"請順勢操作，耐心等待極端相位（波峰 >+0.7 或波谷 <-0.7）浮現再行動。"
                                            )

                    except Exception as e:
                        import traceback as _tb
                        st.error(f"頻譜轉換失敗: {e}")
                        with st.expander("🔍 Debug Traceback"):
                            st.code(_tb.format_exc())




# ═══════════════════════════════════════════════════════════════
# SECTION 6.2 — 個股深鑽 (CROWN JEWEL — FULLY RESTORED)
# ═══════════════════════════════════════════════════════════════
def _s62():
    st.markdown('<div class="t6-sec-head" style="--sa:#FFD700"><div class="t6-sec-num">6.2</div><div><div class="t6-sec-title" style="color:#FFD700;">個股深鑽 — 7D 幾何 + 信評 + 上帝軌道 + 戰略工廠</div><div class="t6-sec-sub">Deep Dive · Spectrum · God Orbit · Strategy Factory</div></div></div>', unsafe_allow_html=True)
    ticker_in = st.text_input("🎯 輸入代號 (支援上市/上櫃/美股)", "NVDA", key="deep_ticker_v300").strip()

    if st.button("🚀 啟動深鑽分析", type="primary", key="btn_deep_v300"):
        with st.spinner(f"正在分析 {ticker_in}…"):
            geo = compute_7d_geometry(ticker_in)
            rating = titan_rating_system(geo) if geo else ("N/A", "N/A", "N/A", "#808080")
        st.session_state['deep_geo'] = geo
        st.session_state['deep_rating'] = rating
        st.session_state['deep_ticker'] = ticker_in

    if 'deep_geo' not in st.session_state or st.session_state.get('deep_ticker') != ticker_in:
        st.toast("ℹ️ 請輸入代號並啟動分析。", icon="📡")
        return
    geo = st.session_state['deep_geo']
    rating = st.session_state['deep_rating']
    lvl, name, desc, color = rating

    # ── RANK BADGE ──
    st.markdown(f'<div class="rank-badge-wrap"><div class="rank-badge">{lvl}</div><div class="rank-badge-name">{name}</div><div class="rank-badge-desc">{desc}</div></div>', unsafe_allow_html=True)

    if geo:
        _render_spectrum(geo, ticker_in)
        c1, c2 = st.columns(2)
        acc = geo['acceleration']
        acc_c = "#00FF7F" if acc > 0 else "#FF6B6B"
        c1.markdown(f'<div style="text-align:center;padding:12px;background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.05);border-radius:12px;"><div style="font-family:var(--f-m);font-size:9px;color:rgba(160,176,208,0.4);letter-spacing:3px;margin-bottom:6px;">ACCELERATION (G-FORCE)</div><div style="font-family:var(--f-i);font-size:42px;font-weight:800;color:{acc_c};line-height:1;">{acc:+.1f}°</div></div>', unsafe_allow_html=True)
        phx = geo['phoenix_signal']
        phx_c = "#FF6347" if phx else "rgba(100,115,135,0.3)"
        c2.markdown(f'<div style="text-align:center;padding:12px;background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.05);border-radius:12px;"><div style="font-family:var(--f-m);font-size:9px;color:rgba(160,176,208,0.4);letter-spacing:3px;margin-bottom:6px;">PHOENIX SIGNAL</div><div style="font-family:var(--f-i);font-size:28px;font-weight:800;color:{phx_c};line-height:1;">{"🔥 TRIGGERED" if phx else "— INACTIVE"}</div></div>', unsafe_allow_html=True)

        _render_radar(geo, ticker_in)

        # ── [FIX #4] 上帝軌道 ──
        st.divider()
        st.subheader("📈 全歷史對數線性回歸 (上帝軌道)")
        _render_god_orbit(ticker_in)

        _render_monthly_chart(ticker_in)

    # ── [FIX #5] 9 Smart Links ──
    st.divider()
    with st.expander("🔗 智能快捷連結 (9 個必備資源)", expanded=False):
        tk_clean = ticker_in.replace('.TW', '').replace('.TWO', '')
        st.markdown(f"1. **[TradingView](https://www.tradingview.com/chart/?symbol={ticker_in})** — 技術圖表與指標分析")
        st.markdown(f"2. **[Finviz](https://finviz.com/quote.ashx?t={ticker_in})** — 美股視覺化看板")
        if ticker_in.endswith(('.TW', '.TWO')):
            st.markdown(f"3. **[Yahoo 台股](https://tw.stock.yahoo.com/quote/{tk_clean})** — 台股即時報價與新聞")
        else:
            st.markdown(f"3. **[Yahoo Finance](https://finance.yahoo.com/quote/{ticker_in})** — 完整財務報表與預測")
        st.markdown(f"4. **[StockCharts](https://stockcharts.com/h-sc/ui?s={ticker_in})** — 專業技術分析工具")
        st.markdown(f"5. **[鉅亨網](https://invest.cnyes.com/twstock/TWS/{tk_clean})** — 台股即時新聞與財報")
        st.markdown(f"6. **[Goodinfo](https://goodinfo.tw/tw/StockDetail.asp?STOCK_ID={tk_clean})** — 台股財務指標寶庫")
        st.markdown(f"7. **[公開資訊觀測站](https://mops.twse.com.tw/mops/web/t05st03)** — 官方財報與法說會公告")
        st.markdown(f"8. **[AlphaMemo](https://www.alphamemo.ai/free-transcripts)** — AI 法說會逐字稿分析")
        if not ticker_in.endswith(('.TW', '.TWO')):
            st.markdown(f"9. **[SEC Edgar](https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={ticker_in})** — 美股官方 10-K/10-Q 文件")
        else:
            st.markdown(f"9. **[證券櫃檯買賣中心](https://www.tpex.org.tw/web/stock/aftertrading/otc_quotes_no1430/stk_wn1430.php?l=zh-tw)** — 上櫃股票資訊")

    # ── 戰略工廠 (Strategy Factory) ──
    st.divider()
    st.subheader("🏭 戰略工廠 (Strategy Factory)")
    st.caption("🤖 V90.2 瓦爾基里：自動情報抓取 × 20 條第一性原則 × 9 個快捷連結")
    col_params, col_output = st.columns([1, 2])

    with col_params:
        st.subheader("⚙️ 戰略參數設定")
        # Valkyrie
        with st.expander("🕵️ 多源情報注入 + 🤖 瓦爾基里", expanded=True):
            st.caption("**選項 1**: 點擊瓦爾基里自動抓取 | **選項 2**: 手動貼上/上傳")
            if st.button("🤖 啟動瓦爾基里 (Auto-Fetch)", type="primary", use_container_width=True, key="btn_valk_v300"):
                with st.spinner("🤖 瓦爾基里正在抓取情報..."):
                    agency = TitanIntelAgency()
                    st.session_state['valkyrie_report_v300'] = agency.fetch_full_report(ticker_in)
                st.toast("✅ 瓦爾基里情報抓取完成！", icon="🎯")
            if 'valkyrie_report_v300' in st.session_state:
                intel_text = st.text_area("📝 瓦爾基里情報 (可編輯)", value=st.session_state['valkyrie_report_v300'], height=250, key="intel_v300_valk")
            else:
                intel_text = st.text_area("📝 手動貼上情報", height=150, placeholder="例如：Q3 法說會重點 - AI 伺服器營收 YoY +150%...", key="intel_v300_manual")
            # [FIX #7] 檔案上傳
            uploaded = st.file_uploader("📎 上傳文件 (PDF/Excel/Word/Txt)", type=['pdf', 'xlsx', 'xls', 'docx', 'doc', 'txt'], accept_multiple_files=True, key="intel_files_v300")
            uploaded_extra = ""
            if uploaded:
                for f in uploaded:
                    uploaded_extra += f"\n[上傳檔案: {f.name}]\n"
                    st.caption(f"✅ 已上傳: {f.name}")
        st.divider()
        # [FIX #6] 20 First Principles
        with st.expander("🎯 統帥第一性原則 (20 條完整清單)", expanded=True):
            st.caption("選擇需要 AI 參謀團回答的原則 (可多選)")
            sel_p = st.multiselect("選擇第一性原則 (可多選)", FIRST_PRINCIPLES_20, default=[], key="principles_v300")
            st.caption(f"✅ 已選擇 {len(sel_p)} 條原則")
        st.divider()
        with st.expander("✍️ 統帥自由筆記 (Commander's Note)", expanded=False):
            st.caption("補充任何額外的分析指令或偏好")
            commander_note = st.text_area("統帥筆記", height=120, placeholder="例如：重點關注現金流與毛利率趨勢...", key="note_v300")

    with col_output:
        st.subheader("📋 戰略提示詞輸出")
        price = 0.0
        if ticker_in in st.session_state.get('daily_price_data', {}):
            dp = st.session_state.daily_price_data[ticker_in]
            if dp is not None and not dp.empty:
                price = float(dp['Close'].iloc[-1])
        st.toast(f"ℹ️ 當前標的: {ticker_in} | 現價: ${price:.2f} | 信評: {lvl} - {name} | 已選原則: {len(sel_p)} 條", icon="📡")
        st.markdown("---")
        if st.button("🚀 生成戰略提示詞", type="primary", use_container_width=True, key="gen_prompt_v300"):
            combined = intel_text
            if uploaded_extra:
                combined += uploaded_extra
            council = TitanAgentCouncil()
            prompt = council.generate_battle_prompt(ticker_in, price, geo or {}, rating, combined, commander_note, sel_p)
            st.session_state['battle_prompt_v300'] = prompt
            st.toast("✅ 史詩級戰略提示詞已生成！", icon="🎯")
        if 'battle_prompt_v300' in st.session_state:
            pt = st.session_state['battle_prompt_v300']
            st.markdown(f'<div class="terminal-box"><pre style="white-space:pre-wrap;margin:0;color:#c9d1d9;font-size:11px;">{pt[:2000]}{"…" if len(pt) > 2000 else ""}</pre></div>', unsafe_allow_html=True)
            st.text_area("📋 複製此提示詞 (Ctrl+A, Ctrl+C)", value=pt, height=350, key="prompt_out_v300")
            st.download_button("💾 下載戰略提示詞 (.txt)", pt, file_name=f"TITAN_VALKYRIE_{ticker_in}_{datetime.now().strftime('%Y%m%d_%H%M')}.txt", mime="text/plain", use_container_width=True)
            # FEATURE 3: Valkyrie Typewriter for prompt display
            st.markdown("**📌 使用方法**")
            st.write_stream(stream_generator("複製提示詞 → 貼到 Gemini/Claude → 獲得五大角鬥士完整辯論"))
            st.caption(f"📊 提示詞統計：{len(pt)} 字元")


# ═══════════════════════════════════════════════════════════════
# SECTION 6.3 — 獵殺清單 [FIX #8] st.form + drop_duplicates
# ═══════════════════════════════════════════════════════════════
def _s63():
    st.markdown('<div class="t6-sec-head" style="--sa:#FF9A3C"><div class="t6-sec-num">6.3</div><div><div class="t6-sec-title" style="color:#FF9A3C;">獵殺清單 (Kill List Dashboard)</div><div class="t6-sec-sub">V90.3 · Form Entry + Real-time PnL Tracking + drop_duplicates</div></div></div>', unsafe_allow_html=True)

    with st.expander("📝 錄入新獵殺目標 (Log New Target)", expanded=False):
        with st.form("target_form_v300", clear_on_submit=True):
            log_ticker = st.text_input("代號 (Ticker)")
            log_action = st.selectbox("操作 (Action)", ["Buy", "Sell"])
            log_entry = st.number_input("進場價 (Entry Price)", min_value=0.0, format="%.2f")
            log_target = st.number_input("目標價 (Target Price)", min_value=0.0, format="%.2f")
            log_stop = st.number_input("停損價 (Stop Loss)", min_value=0.0, format="%.2f")
            log_note = st.text_area("理由 (Rationale)", placeholder="簡述進場的核心邏輯...")
            submitted = st.form_submit_button("💾 存入戰情室", type="primary")
            if submitted:
                if not log_ticker or log_entry <= 0:
                    st.toast("⚠️ 請輸入有效的代號與進場價。", icon="⚡")
                else:
                    if 'watchlist' not in st.session_state:
                        st.session_state.watchlist = pd.DataFrame(columns=[
                            "Date", "Ticker", "Action", "Entry Price", "Target Price",
                            "Stop Loss", "Rationale", "Status", "Current Price", "PnL %"
                        ])
                    new_row = pd.DataFrame([{
                        "Date": datetime.now().strftime("%Y-%m-%d"),
                        "Ticker": log_ticker.upper(),
                        "Action": log_action,
                        "Entry Price": log_entry,
                        "Target Price": log_target,
                        "Stop Loss": log_stop,
                        "Rationale": log_note,
                        "Status": "⏳ Holding",
                        "Current Price": np.nan,
                        "PnL %": np.nan
                    }])
                    st.session_state.watchlist = pd.concat(
                        [st.session_state.watchlist, new_row], ignore_index=True
                    ).drop_duplicates(subset=['Ticker', 'Entry Price'], keep='last')
                    st.toast(f"✅ {log_ticker} 已成功存入戰情室！", icon="🎯")

    st.markdown("---")

    # Mirror Engine
    if st.button("🔄 更新最新戰況 (Refresh PnL)", use_container_width=True, key="refresh_kl_v300"):
        if 'watchlist' in st.session_state and not st.session_state.watchlist.empty:
            with st.spinner("啟動鏡像結算引擎..."):
                wl = st.session_state.watchlist.copy()
                tks = wl['Ticker'].unique().tolist()
                try:
                    prices_data = yf.download(tks, period="1d", progress=False)
                    rows = []
                    for _, row in wl.iterrows():
                        try:
                            if len(tks) > 1:
                                cp = float(prices_data['Close'][row['Ticker']].iloc[-1])
                            else:
                                cp = float(prices_data['Close'].iloc[-1])
                            if pd.isna(cp):
                                rows.append(row); continue
                            row['Current Price'] = cp
                            if row['Action'] == 'Buy':
                                pnl = ((cp / row['Entry Price']) - 1) * 100
                            else:
                                pnl = ((row['Entry Price'] / cp) - 1) * 100
                            row['PnL %'] = pnl
                            if row['Action'] == 'Buy':
                                if cp >= row['Target Price']:
                                    row['Status'] = '🏆 Win'
                                elif cp <= row['Stop Loss']:
                                    row['Status'] = '💀 Loss'
                                else:
                                    row['Status'] = '⏳ Holding'
                            else:
                                if cp <= row['Target Price']:
                                    row['Status'] = '🏆 Win'
                                elif cp >= row['Stop Loss']:
                                    row['Status'] = '💀 Loss'
                                else:
                                    row['Status'] = '⏳ Holding'
                        except Exception:
                            pass
                        rows.append(row)
                    st.session_state.watchlist = pd.DataFrame(rows)
                    st.toast("戰況已更新！", icon="🔄")
                except Exception as e:
                    st.toast(f"❌ 更新失敗: {e}", icon="💀")
        else:
            st.toast("ℹ️ 清單為空，無可更新的戰況。", icon="📡")

    # Scoreboard
    if 'watchlist' not in st.session_state or st.session_state.watchlist.empty:
        st.toast("ℹ️ 戰情室目前無獵殺目標。", icon="📡")
    else:
        wl = st.session_state.watchlist.copy()
        holding = len(wl[wl['Status'] == '⏳ Holding'])
        wins = len(wl[wl['Status'] == '🏆 Win'])
        losses = len(wl[wl['Status'] == '💀 Loss'])
        avg_pnl = wl['PnL %'].mean()
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("目前持倉", f"{holding} 檔")
        m2.metric("勝場", f"{wins} 檔")
        m3.metric("敗場", f"{losses} 檔")
        m4.metric("平均 PnL", f"{avg_pnl:.2f}%" if not pd.isna(avg_pnl) else "N/A")

        # Rank cards
        for idx, (_, row) in enumerate(wl.iterrows()):
            pnl_v = row.get('PnL %', 0)
            pnl_d = f"{pnl_v:+.2f}%" if pd.notna(pnl_v) else "N/A"
            pnl_c = "#00FF7F" if pd.notna(pnl_v) and pnl_v >= 0 else "#FF6B6B"
            st.markdown(f'<div class="hunt-rank-card"><div class="hunt-rank-num">{idx + 1}</div><div style="flex:1"><div class="hunt-rank-ticker">{row.get("Ticker", "")}</div><div class="hunt-rank-detail">{row.get("Action", "")} @ {row.get("Entry Price", 0):.2f} → Target {row.get("Target Price", 0):.2f} | Stop {row.get("Stop Loss", 0):.2f}</div></div><div style="text-align:right"><div style="font-family:var(--f-i);font-size:22px;font-weight:800;color:{pnl_c};">{pnl_d}</div><div style="font-size:12px;color:rgba(180,180,180,0.6);">{row.get("Status", "")}</div></div></div>', unsafe_allow_html=True)

        with st.expander("📋 完整數據表"):
            st.dataframe(wl.style.format({
                "Entry Price": "{:.2f}", "Target Price": "{:.2f}",
                "Stop Loss": "{:.2f}", "Current Price": "{:.2f}", "PnL %": "{:+.2f}%"
            }), use_container_width=True)

        if st.button("🗑️ 清空清單", type="secondary", use_container_width=True, key="clear_kl_v300"):
            st.session_state.watchlist = pd.DataFrame(columns=wl.columns)
            st.toast("獵殺清單已清空！", icon="🗑️")
            st.rerun()


# ═══════════════════════════════════════════════════════════════
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
    st.markdown('<div class="t6-sec-head" style="--sa:#00FF7F"><div class="t6-sec-num">6.5</div><div><div class="t6-sec-title" style="color:#00FF7F;">宏觀對沖 (Macro Hedge)</div><div class="t6-sec-sub">Global Snapshot · Correlation Matrix · Beta Hedge + Rolling Beta</div></div></div>', unsafe_allow_html=True)

    SNAPS = [("SPY", "S&P500"), ("QQQ", "NASDAQ100"), ("GLD", "黃金"), ("TLT", "美債20Y"),
             ("BTC-USD", "比特幣"), ("^TWII", "台灣加權"), ("DX-Y.NYB", "美元指數"), ("^VIX", "VIX恐慌")]
    with st.spinner("載入市場快照…"):
        try:
            snap_raw = yf.download([s for s, _ in SNAPS], period="5d", progress=False, auto_adjust=True)
            snap_px = (snap_raw["Close"] if isinstance(snap_raw.columns, pd.MultiIndex) else snap_raw).dropna(how="all")
        except:
            snap_px = pd.DataFrame()
    if not snap_px.empty and len(snap_px) >= 2:
        hud_cols = st.columns(len(SNAPS))
        for idx, (tk, lbl) in enumerate(SNAPS):
            if tk not in snap_px.columns:
                continue
            s_col = snap_px[tk].dropna()
            if len(s_col) < 2:
                continue
            cur = float(s_col.iloc[-1])
            prev = float(s_col.iloc[-2])
            chg = (cur - prev) / prev * 100
            hud_cols[idx].metric(lbl, f"{cur:,.2f}", f"{chg:+.2f}%")
    else:
        st.warning("市場快照無法取得。")

    st.divider()
    st.markdown("#### 多資產相關性矩陣")
    DEF_A = ["SPY", "QQQ", "GLD", "TLT", "BTC-USD", "DX-Y.NYB"]
    ca, cb = st.columns([3, 1])
    corr_tickers = ca.multiselect("選擇資產", options=DEF_A + ["IWM", "EEM", "HYG", "SOXX", "NVDA", "AAPL", "TSLA", "^VIX"], default=DEF_A, key="corr_v300")
    corr_period = cb.selectbox("區間", ["1y", "2y", "3y", "5y"], key="corr_per_v300")
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
            colorscale=[[0, "#FF3131"], [.5, "#1a1a2e"], [1, "#00FF7F"]],
            zmin=-1, zmax=1, zmid=0,
            text=cm.values.round(2), texttemplate="%{text:.2f}",
            textfont=dict(size=11, family="JetBrains Mono")
        ))
        fig_hm.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=420, margin=dict(t=10, b=40, l=80, r=20))
        st.plotly_chart(fig_hm, use_container_width=True)

    st.divider()
    st.markdown("#### Beta 對沖 + 滾動 60 日 Beta")
    BENCH_MAP = {"SPY (S&P 500)": "SPY", "QQQ (NASDAQ 100)": "QQQ", "^TWII (台灣加權)": "^TWII", "GLD (黃金)": "GLD"}
    ba, bb, bc = st.columns([2, 1, 1])
    bench_name = ba.selectbox("基準指數", list(BENCH_MAP.keys()), key="bench_v300")
    beta_period = bb.selectbox("區間", ["1y", "2y", "3y"], key="beta_per_v300")
    beta_ticker = bc.text_input("標的", "NVDA", key="beta_tk_v300")
    bench_tk = BENCH_MAP[bench_name]
    if st.button("計算 Beta", use_container_width=True, key="run_beta_v300"):
        with st.spinner("計算…"):
            beta_px = _fetch_prices(tuple([beta_ticker, bench_tk]), beta_period)
        if not beta_px.empty and beta_ticker in beta_px.columns and bench_tk in beta_px.columns:
            br = beta_px.pct_change().dropna()
            bv = round(br[beta_ticker].cov(br[bench_tk]) / br[bench_tk].var(), 3) if br[bench_tk].var() > 0 else 0
            st.session_state["beta_v300"] = {
                "beta": bv, "corr": round(br[beta_ticker].corr(br[bench_tk]), 3),
                "avol": round(br[beta_ticker].std() * np.sqrt(252) * 100, 2),
                "ret": br, "tk": beta_ticker, "bk": bench_tk
            }
    if "beta_v300" in st.session_state:
        b = st.session_state["beta_v300"]
        bv = b["beta"]
        bk1, bk2, bk3, bk4 = st.columns(4)
        bk1.metric("Beta", f"{bv:.3f}")
        bk2.metric("相關性", f"{b['corr']:.3f}")
        bk3.metric("年化波動", f"{b['avol']:.2f}%")
        bk4.metric("對沖比例", f"{abs(bv):.3f}x")
        rb_ret = b["ret"]
        tk_b, bk_b = b["tk"], b["bk"]
        W = 60
        if len(rb_ret) > W:
            roll_b = []
            for i in range(W, len(rb_ret)):
                chunk = rb_ret.iloc[i - W:i]
                rb_val = chunk[tk_b].cov(chunk[bk_b]) / chunk[bk_b].var() if chunk[bk_b].var() > 0 else 0
                roll_b.append({"Date": rb_ret.index[i], "Rolling Beta": rb_val})
            rb_df = pd.DataFrame(roll_b)
            fig_rb = px.line(rb_df, x="Date", y="Rolling Beta", title=f"{tk_b} - 60日 Rolling Beta vs {bk_b}")
            fig_rb.update_traces(line_color="#FF9A3C", line_width=1.8)
            fig_rb.add_hline(y=1, line_dash="dash", line_color="rgba(255,255,255,.2)")
            fig_rb.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=270, margin=dict(t=30, b=40, l=60, r=10))
            st.plotly_chart(fig_rb, use_container_width=True)


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
