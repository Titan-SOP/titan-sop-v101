# core_logic.py
# Titan SOP V100.0 — Core Logic Engine
# 包含：7D 幾何引擎、22 階泰坦信評系統、輔助計算函式
# 所有 Tab 的共用後端邏輯集中於此

import numpy as np
import pandas as pd
import yfinance as yf
import streamlit as st
from scipy.stats import linregress
from datetime import datetime


# ═══════════════════════════════════════════════════════════════
#  [SLOT-6.1] 月K 下載引擎 (支援台股雙軌)
# ═══════════════════════════════════════════════════════════════

@st.cache_data(ttl=3600, show_spinner=False)
def download_full_history(ticker: str, start: str = "1990-01-01") -> pd.DataFrame | None:
    """
    下載完整歷史月K線。支援台股上市(.TW)與上櫃(.TWO)自動切換。
    同時將日K快取到 st.session_state.daily_price_data[ticker]。
    """
    orig = ticker
    if ticker.isdigit() and len(ticker) >= 4:
        ticker = f"{ticker}.TW"
    try:
        df = yf.download(ticker, start=start, progress=False, auto_adjust=True)
        if df.empty and orig.isdigit() and len(orig) >= 4:
            ticker = f"{orig}.TWO"
            df = yf.download(ticker, start=start, progress=False, auto_adjust=True)
        if df.empty:
            return None

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        if not isinstance(df.index, pd.DatetimeIndex):
            df.index = pd.to_datetime(df.index)

        # 快取日K
        if 'daily_price_data' not in st.session_state:
            st.session_state.daily_price_data = {}
        st.session_state.daily_price_data[orig] = df

        # 轉為月K
        try:
            monthly = df.resample('ME').agg({'Open':'first','High':'max','Low':'min','Close':'last','Volume':'sum'}).dropna()
        except Exception:
            monthly = df.resample('M').agg({'Open':'first','High':'max','Low':'min','Close':'last','Volume':'sum'}).dropna()
        return monthly
    except Exception as e:
        return None


# ═══════════════════════════════════════════════════════════════
#  [SLOT-6.2] 幾何計算引擎
# ═══════════════════════════════════════════════════════════════

def _calc_geometry(df: pd.DataFrame, months: int) -> dict:
    """計算指定月數窗口的對數線性回歸幾何指標"""
    if df is None or df.empty:
        return {'angle': 0.0, 'r2': 0.0, 'slope': 0.0}
    sl = df.iloc[-months:] if len(df) >= months else df
    if len(sl) < 3:
        return {'angle': 0.0, 'r2': 0.0, 'slope': 0.0}
    log_p = np.log(sl['Close'].values)
    x = np.arange(len(log_p))
    slope, _, rv, _, _ = linregress(x, log_p)
    angle = float(np.clip(np.arctan(slope * 100) * (180 / np.pi), -90, 90))
    return {'angle': round(angle, 2), 'r2': round(rv**2, 4), 'slope': round(slope, 6)}


def compute_7d_geometry(ticker: str) -> dict | None:
    """
    V90.2 核心：計算 7 維度完整幾何掃描
    Returns dict with keys: 35Y / 10Y / 5Y / 3Y / 1Y / 6M / 3M / acceleration / phoenix_signal
    """
    df = download_full_history(ticker)
    if df is None:
        return None

    periods = {'35Y': 420, '10Y': 120, '5Y': 60, '3Y': 36, '1Y': 12, '6M': 6, '3M': 3}
    results = {label: _calc_geometry(df, months) for label, months in periods.items()}

    results['acceleration']   = round(results['3M']['angle'] - results['1Y']['angle'], 2)
    results['phoenix_signal'] = (results['10Y']['angle'] < 0) and (results['6M']['angle'] > 25)
    return results


# ═══════════════════════════════════════════════════════════════
#  [SLOT-6.3] 22 階泰坦信評系統
# ═══════════════════════════════════════════════════════════════

def titan_rating_system(geo: dict) -> tuple[str, str, str, str]:
    """
    22 階信評邏輯樹
    Returns: (rating_level, rating_name, description, hex_color)
    """
    if geo is None:
        return ("N/A", "無數據", "數據不足", "#808080")

    a35 = geo['35Y']['angle']
    a10 = geo['10Y']['angle']
    a5  = geo['5Y']['angle']
    a1  = geo['1Y']['angle']
    a6m = geo['6M']['angle']
    a3m = geo['3M']['angle']
    r2_1y  = geo['1Y']['r2']
    r2_3m  = geo['3M']['r2']
    acc    = geo['acceleration']
    phx    = geo['phoenix_signal']

    # SSS
    if all([a35 > 45, a10 > 45, a1 > 45, a3m > 45]):
        return ("SSS", "Titan (泰坦)", "全週期超過45度，神級標的", "#FFD700")
    # AAA
    if a1 > 40 and a6m > 45 and a3m > 50 and acc > 20:
        return ("AAA", "Dominator (統治者)", "短期加速向上，完美趨勢", "#FF4500")
    # Phoenix
    if phx and a3m > 30:
        return ("Phoenix", "Phoenix (浴火重生)", "長空短多，逆轉信號", "#FF6347")
    # Launchpad
    if r2_1y > 0.95 and 20 < a1 < 40 and acc > 0:
        return ("Launchpad", "Launchpad (發射台)", "線性度極高，蓄勢待發", "#32CD32")
    # AA+
    if a1 > 35 and a3m > 40 and r2_3m > 0.85:
        return ("AA+", "Elite (精英)", "一年期強勢上攻", "#FFA500")
    # AA
    if a1 > 30 and a6m > 35:
        return ("AA", "Strong Bull (強多)", "中短期穩定上升", "#FFD700")
    # AA-
    if a1 > 25 and a3m > 30:
        return ("AA-", "Steady Bull (穩健多)", "趨勢健康向上", "#ADFF2F")
    # A+
    if a6m > 20 and a3m > 25:
        return ("A+", "Moderate Bull (溫和多)", "短期表現良好", "#7FFF00")
    # A
    if a3m > 15:
        return ("A", "Weak Bull (弱多)", "短期微幅上揚", "#98FB98")
    # BBB+
    if -5 < a3m < 15 and a1 > 0:
        return ("BBB+", "Neutral+ (中性偏多)", "盤整偏多", "#F0E68C")
    # BBB
    if -10 < a3m < 10 and -10 < a1 < 10:
        return ("BBB", "Neutral (中性)", "橫盤震蕩", "#D3D3D3")
    # BBB-
    if -15 < a3m < 5 and a1 < 0:
        return ("BBB-", "Neutral- (中性偏空)", "盤整偏弱", "#DDA0DD")
    # Divergence
    if a1 > 20 and a3m < -10:
        return ("Divergence", "Divergence (背離)", "價格創高但動能衰竭", "#FF1493")
    # BB+
    if -25 < a3m < -15 and a1 > -10:
        return ("BB+", "Weak Bear (弱空)", "短期下跌", "#FFA07A")
    # BB
    if -35 < a3m < -25:
        return ("BB", "Moderate Bear (中等空)", "下跌趨勢明確", "#FF6347")
    # BB-
    if -45 < a3m < -35:
        return ("BB-", "Strong Bear (強空)", "跌勢凌厲", "#DC143C")
    # B+
    if a3m < -45 and a1 < -30:
        return ("B+", "Severe Bear (重度空)", "崩跌模式", "#8B0000")
    # B
    if a10 < -30 and a3m < -40:
        return ("B", "Depression (蕭條)", "長期熊市", "#800000")
    # C
    if a35 < -20 and a10 < -35:
        return ("C", "Structural Decline (結構衰退)", "世代熊市", "#4B0082")
    # D
    if a3m < -60:
        return ("D", "Collapse (崩盤)", "極度危險", "#000000")
    # Reversal
    if a10 < -20 and a3m > 15 and acc > 30:
        return ("Reversal", "Reversal (觸底反彈)", "熊市中的V型反轉", "#00CED1")

    return ("N/A", "Unknown (未分類)", "無法歸類", "#808080")


# ═══════════════════════════════════════════════════════════════
#  輔助：格蘭碧法則
# ═══════════════════════════════════════════════════════════════

def get_advanced_granville(cp: float, op: float, ma87_curr: float, ma87_prev5: float) -> str:
    """格蘭碧八大法則快速判讀"""
    if ma87_curr <= 0:
        return "📊 無法判讀 (數據不足)"
    is_breakout = (cp > ma87_curr) and (op < ma87_curr) or (ma87_curr > ma87_prev5 and cp > ma87_curr)
    bias = ((cp - ma87_curr) / ma87_curr) * 100
    if is_breakout:               return "🔥 突破生命線 (買1)"
    if -20 < bias < 0:            return "🟢 回測支撐 (買2)"
    if bias < -20:                return "🟢 乖離過大 (買4 - 假摔)"
    if bias > 20:                 return "🔴 乖離過大 (賣4 - 過熱)"
    return "👍 趨勢健康 (持有)"


# ═══════════════════════════════════════════════════════════════
#  輔助：Elliott Wave (ZigZag → 5波)
# ═══════════════════════════════════════════════════════════════

def calculate_zigzag(df: pd.DataFrame, deviation: float = 0.03) -> pd.DataFrame:
    """計算 ZigZag 轉折點"""
    if df.empty or 'Close' not in df.columns:
        return pd.DataFrame()
    prices = df['Close'].values
    pivots = [{'idx': 0, 'price': prices[0], 'type': 'high' if prices[0] > prices[1] else 'low'}]
    for i in range(1, len(prices) - 1):
        last = pivots[-1]
        cp   = prices[i]
        if last['type'] == 'high':
            if cp > last['price']:
                pivots[-1] = {'idx': i, 'price': cp, 'type': 'high'}
            elif cp < last['price'] * (1 - deviation):
                pivots.append({'idx': i, 'price': cp, 'type': 'low'})
        else:
            if cp < last['price']:
                pivots[-1] = {'idx': i, 'price': cp, 'type': 'low'}
            elif cp > last['price'] * (1 + deviation):
                pivots.append({'idx': i, 'price': cp, 'type': 'high'})
    pivot_df = pd.DataFrame(pivots)
    if pivot_df.empty:
        return pd.DataFrame()
    pivot_df['Date'] = [df.index[r['idx']] for _, r in pivot_df.iterrows()]
    return pivot_df


def calculate_5_waves(zigzag_df: pd.DataFrame) -> list[dict]:
    """從 ZigZag 計算 Elliott 5 波投影"""
    if zigzag_df.empty or len(zigzag_df) < 2:
        return []
    last = zigzag_df.iloc[-1]
    prev = zigzag_df.iloc[-2]
    w1_start = float(prev['price'])
    w1_end   = float(last['price'])
    w1_range = w1_end - w1_start
    if w1_range <= 0:
        return []
    w2_end = w1_end - w1_range * 0.382
    w3_end = w2_end + w1_range * 1.618
    w4_end = w3_end - (w3_end - w2_end) * 0.382
    w5_end = w4_end + w1_range * 1.0
    now    = zigzag_df['Date'].iloc[-1]
    step   = pd.Timedelta(days=20)
    return [
        {'wave': 'W1', 'price': w1_end,  'date': now},
        {'wave': 'W2', 'price': w2_end,  'date': now + step},
        {'wave': 'W3', 'price': w3_end,  'date': now + step*2},
        {'wave': 'W4', 'price': w4_end,  'date': now + step*3},
        {'wave': 'W5', 'price': w5_end,  'date': now + step*4},
    ]


# ═══════════════════════════════════════════════════════════════
#  輔助：DCF 估值
# ═══════════════════════════════════════════════════════════════

def calculate_ark_scenarios(rev_ttm, shares, cp, g, m, pe, years=5):
    """三情境 DCF (ARK 模式)"""
    results = {}
    for label, mult in [('Bear', 0.8), ('Base', 1.0), ('Bull', 1.2)]:
        future_rev = rev_ttm * ((1 + g * mult) ** years)
        future_eps = (future_rev * m * mult) / max(shares, 1)
        tv = future_eps * pe
        cagr = (tv / cp) ** (1 / years) - 1 if cp > 0 and tv > 0 else 0
        results[label] = {'target_price': round(tv, 2), 'cagr': round(cagr, 4)}
    return results


def calculate_smart_valuation(eps, rev, shares, g, m, pe, dr=0.1, y=10):
    """DCF 智能估值（10 年折現）"""
    if shares <= 0 or dr <= 0: return {'fair_value': 0}
    total_pv = 0
    for i in range(1, y + 1):
        proj_rev = rev * ((1 + g) ** i)
        proj_earn = proj_rev * m
        proj_eps  = proj_earn / shares
        pv = proj_eps / ((1 + dr) ** i)
        total_pv += pv
    terminal = (eps * (1 + g) ** y * pe) / ((1 + dr) ** y)
    return {'fair_value': round(total_pv + terminal, 2)}
