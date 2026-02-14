# data_engine.py
# Titan SOP V100.0 — Data Engine
# 包含：CB 清單解析、欄位標準化、yfinance 快取下載

import re
import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta


# ═══════════════════════════════════════════════════════════════
#  CB 清單上傳 & 解析
# ═══════════════════════════════════════════════════════════════

def load_cb_data_from_upload(uploaded_file) -> pd.DataFrame | None:
    """
    解析上傳的 CB 清單 (Excel / CSV)。
    輸出標準化欄位：
      code, name, stock_code, close, underlying_price,
      conversion_price, converted_ratio, avg_volume,
      list_date, put_date, outstanding_balance, issue_amount
    """
    try:
        if uploaded_file.name.endswith('.xlsx') or uploaded_file.name.endswith('.xls'):
            df_raw = pd.read_excel(uploaded_file)
        else:
            try:
                df_raw = pd.read_csv(uploaded_file, encoding='utf-8')
            except UnicodeDecodeError:
                df_raw = pd.read_csv(uploaded_file, encoding='big5')

        df = df_raw.copy()
        df.columns = [str(c).strip().replace(" ", "") for c in df.columns]

        rename_map = {}
        cb_price_col       = next((c for c in df.columns if "可轉債市價" in c), None)
        underlying_col     = next((c for c in df.columns if "標的股票市價" in c), None)
        balance_ratio_col  = next((c for c in df.columns if "餘額比例" in c), None)

        if cb_price_col:     rename_map[cb_price_col] = 'close'
        if underlying_col:   rename_map[underlying_col] = 'underlying_price'
        if balance_ratio_col: rename_map[balance_ratio_col] = 'balance_ratio'

        for col in df.columns:
            if col in rename_map: continue
            cl = col.lower()
            if "代號" in col and "標的" not in col:       rename_map[col] = 'code'
            elif "名稱" in col or "標的債券" in col:      rename_map[col] = 'name'
            elif cb_price_col is None and any(k in cl for k in ["市價","收盤","close","成交"]):
                rename_map[col] = 'close'
            elif any(k in cl for k in ["標的","stock_code"]) and "市價" not in col:
                rename_map[col] = 'stock_code'
            elif "發行" in col and "總額" not in col:     rename_map[col] = 'list_date'
            elif "賣回" in col:                           rename_map[col] = 'put_date'
            elif any(k in col for k in ["轉換價","轉換價格","最新轉換價"]): rename_map[col] = 'conversion_price'
            elif any(k in col for k in ["已轉換比例","轉換比例","轉換率"]):  rename_map[col] = 'converted_ratio'
            elif any(k in col for k in ["發行餘額","流通餘額"]):            rename_map[col] = 'outstanding_balance'
            elif "發行總額" in col:                       rename_map[col] = 'issue_amount'
            elif any(k in cl for k in ["均量","成交量","avg_vol"]):         rename_map[col] = 'avg_volume'

        df.rename(columns=rename_map, inplace=True)
        df = df.loc[:, ~df.columns.duplicated()]

        # ── 必要欄位檢查 ─────────────────────────────────────
        required = ['code', 'name', 'stock_code', 'close']
        missing  = [c for c in required if c not in df.columns]
        if missing:
            st.error(f"❌ 缺少必要欄位！請確認包含：{', '.join(missing)}")
            return None

        # ── 欄位清洗 ─────────────────────────────────────────
        df['code']       = df['code'].astype(str).str.extract(r'(\d+)')
        df['stock_code'] = df['stock_code'].astype(str).str.extract(r'(\d+)')
        df.dropna(subset=['code', 'stock_code'], inplace=True)

        # ── 補齊缺失欄位 ──────────────────────────────────────
        if 'conversion_price' not in df.columns:
            df['conversion_price'] = 0.0

        # 已轉換率 = 100 - 餘額比例（優先）
        if 'converted_ratio' not in df.columns:
            if 'balance_ratio' in df.columns:
                bal = pd.to_numeric(df['balance_ratio'], errors='coerce').fillna(100.0)
                df['converted_ratio'] = 100.0 - bal
            elif 'outstanding_balance' in df.columns and 'issue_amount' in df.columns:
                ob = pd.to_numeric(df['outstanding_balance'], errors='coerce').fillna(0)
                ia = pd.to_numeric(df['issue_amount'], errors='coerce').replace(0, np.nan).fillna(1)
                df['converted_ratio'] = ((ia - ob) / ia * 100).clip(0, 100)
            else:
                df['converted_ratio'] = 0.0

        if 'avg_volume' not in df.columns:
            vol_col = next((c for c in df.columns if '量' in c or 'volume' in c.lower()), None)
            df['avg_volume'] = df[vol_col] if vol_col else 100

        for dcol in ['list_date', 'put_date']:
            if dcol not in df.columns:
                df[dcol] = None
            else:
                df[dcol] = pd.to_datetime(df[dcol], errors='coerce')

        df['close']           = pd.to_numeric(df['close'], errors='coerce')
        df['conversion_price']= pd.to_numeric(df['conversion_price'], errors='coerce').fillna(0)
        df['converted_ratio'] = pd.to_numeric(df['converted_ratio'], errors='coerce').fillna(0)

        return df.reset_index(drop=True)

    except Exception as e:
        st.error(f"檔案讀取失敗: {e}")
        return None


# ═══════════════════════════════════════════════════════════════
#  yfinance 快取工具函式
# ═══════════════════════════════════════════════════════════════

@st.cache_data(ttl=300, show_spinner=False)
def get_stock_daily(ticker: str, period: str = "1y") -> pd.DataFrame:
    """下載日K線，支援台股雙軌，回傳標準 OHLCV DataFrame"""
    orig = ticker
    cands = []
    if re.match(r'^[0-9]', ticker) and 4 <= len(ticker) <= 6:
        cands = [f"{ticker}.TW", f"{ticker}.TWO"]
    elif re.match(r'^[0-9]', ticker) and len(ticker) == 5:
        # 可能是可轉債代號 → 取前4碼轉股票
        base = ticker[:4]
        cands = [f"{base}.TW", f"{base}.TWO"]
    else:
        cands = [ticker.upper()]

    for c in cands:
        try:
            df = yf.download(c, period=period, progress=False, auto_adjust=True)
            if not df.empty:
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)
                df.index = pd.to_datetime(df.index)
                return df
        except Exception:
            continue
    return pd.DataFrame()


@st.cache_data(ttl=300, show_spinner=False)
def get_latest_price(ticker: str) -> float:
    """取得最新收盤價，失敗回傳 0.0"""
    try:
        df = get_stock_daily(ticker, period="5d")
        return float(df['Close'].iloc[-1]) if not df.empty else 0.0
    except Exception:
        return 0.0


@st.cache_data(ttl=300, show_spinner=False)
def enrich_cb_row(row: dict) -> dict:
    """
    用 yfinance 補充單一 CB 行的即時數據：
    - stock_price (標的股價)
    - ma87, ma284 (均線)
    - trend_status, bias_pct
    Returns enriched dict
    """
    try:
        stock_code = str(row.get('stock_code', ''))
        if not stock_code: return row

        df = get_stock_daily(stock_code, period="2y")
        if df.empty: return row

        df['MA87']  = df['Close'].rolling(87).mean()
        df['MA284'] = df['Close'].rolling(284).mean()
        cp   = float(df['Close'].iloc[-1])
        m87  = float(df['MA87'].iloc[-1])  if not pd.isna(df['MA87'].iloc[-1])  else 0
        m284 = float(df['MA284'].iloc[-1]) if not pd.isna(df['MA284'].iloc[-1]) else 0

        row['stock_price']   = cp
        row['ma87']          = m87
        row['ma284']         = m284
        row['bias_pct']      = round(((cp - m87) / m87 * 100), 1) if m87 > 0 else 0
        row['trend_status']  = "✅ 中期多頭" if m87 > m284 else "❌ 空頭整理"

        # 溢價率
        cb_price = float(row.get('close', 0))
        conv_p   = float(row.get('conversion_price', 0))
        if conv_p > 0 and cp > 0:
            theo_v   = cp / conv_p * 100
            row['premium_pct'] = round((cb_price / theo_v - 1) * 100, 1) if theo_v > 0 else 0
        return row
    except Exception:
        return row


# ═══════════════════════════════════════════════════════════════
#  宏觀市場快取
# ═══════════════════════════════════════════════════════════════

@st.cache_data(ttl=600, show_spinner=False)
def get_macro_snapshot() -> dict:
    """
    快取：^TWII (台灣加權)、^GSPC (S&P500)、GC=F (黃金)
    回傳 {symbol: {price, change_pct}} dict
    """
    syms   = ['^TWII', '^GSPC', '^TNX', 'GC=F', 'CL=F', 'USDTWD=X']
    labels = ['台灣加權指數', 'S&P 500', '美國10年債 (%)', '黃金', '原油 (WTI)', 'USD/TWD']
    result = {}
    try:
        raw = yf.download(syms, period="5d", progress=False, auto_adjust=True)
        close = raw['Close'] if isinstance(raw.columns, pd.MultiIndex) else raw
        for sym, lbl in zip(syms, labels):
            try:
                s = close[sym].dropna() if sym in close.columns else pd.Series()
                if len(s) < 2: continue
                price  = float(s.iloc[-1])
                change = (s.iloc[-1] - s.iloc[-2]) / s.iloc[-2] * 100
                result[sym] = {'label': lbl, 'price': price, 'change_pct': float(change)}
            except Exception:
                pass
    except Exception:
        pass
    return result
