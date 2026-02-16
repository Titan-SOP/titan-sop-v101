# ui_desktop/tab2_radar.py
# Titan SOP V300 — 獵殺雷達 REWRITE（完全重寫版）
# ╔═══════════════════════════════════════════════════════════════════╗
# ║  直接使用 Excel 真實欄位名稱，不再依賴 rename_map               ║
# ║  Excel 欄位對應：                                                  ║
# ║    債券代號 → code                                                 ║
# ║    標的債券 → name                                                 ║
# ║    可轉債市價 → price                                              ║
# ║    轉換價格 → conv_price (已存在，直接使用)                       ║
# ║    轉換標的代碼 → stock_code                                       ║
# ║    餘額比例 → balance_ratio (100% 表示未轉換)                     ║
# ║    轉換價值 → conv_value (Excel 已計算好)                         ║
# ║    標的股票市價 → stock_price_real                                ║
# ╚═══════════════════════════════════════════════════════════════════╝

import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import yfinance as yf
import time


# ══════════════════════════════════════════════════════════════════════════════
#  [V300 UPGRADE #3] VALKYRIE AI TYPEWRITER
# ══════════════════════════════════════════════════════════════════════════════
def _stream_text(text, speed=0.018):
    """Character-by-character generator for st.write_stream"""
    for char in text:
        yield char
        time.sleep(speed)


# ══════════════════════════════════════════════════════════════════════════════
#  [V300 UPGRADE #1] TACTICAL GUIDE DIALOG
# ══════════════════════════════════════════════════════════════════════════════
@st.dialog("🔰 戰術指導 — Kill Radar Command Center")
def _show_tactical_guide():
    st.markdown("""
<div style="font-family:'Rajdhani',sans-serif;font-size:15px;color:#C8D8E8;line-height:1.8;">

### 🎯 歡迎進入獵殺雷達

本模組是 Titan OS 的**核心狙擊系統**，執行全市場普查與精準打擊：

**📡 2.1 自動獵殺 (AUTO SCAN)**
全市場雙軌普查 (.TW/.TWO)，自動篩選 SOP 黃金標準標的 (價格<120 + 多頭排列 + 轉換率<30%)。

**📈 2.2 核心檢核 (SNIPER SCOPE)**
輸入 CB 代號即時拉取 K 線 + 87MA/284MA，搭配四大天條檢核卡 (價格/趨勢/轉換率/評分)。

**⚠️ 2.3 風險雷達 / 💰 2.4 資金配置**
負面表列警示 (籌碼鬆動/高溢價/流動性陷阱) + Top 5 等權重 20% 資金配置試算。

</div>""", unsafe_allow_html=True)
    if st.button("✅ 收到，開始獵殺 (Roger That)", type="primary", use_container_width=True):
        st.session_state['tab2_guided'] = True
        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
#  [V300 CSS] DIRECTOR'S CUT VISUALS
# ══════════════════════════════════════════════════════════════════════════════
def _inject_v300_css():
    st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Rajdhani:wght@300;400;600;700&family=JetBrains+Mono:wght@300;400;600;700&display=swap" rel="stylesheet">
<style>
:root {
    --c-gold:#FFD700; --c-cyan:#00F5FF;
    --c-red:#FF3131;  --c-green:#00FF7F;
    --c-orange:#FF9A3C;
    --f-display:'Bebas Neue',sans-serif;
    --f-body:'Rajdhani',sans-serif;
    --f-mono:'JetBrains Mono',monospace;
}

/* ── SNIPER CHECKLIST CARDS ────────────────────────────────────────── */
.t2-rule-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:10px; margin-bottom:20px; }
.t2-rule-card {
    background:rgba(255,255,255,.022); border:1px solid rgba(255,255,255,.062);
    border-radius:14px; padding:16px 12px 13px; text-align:center;
    position:relative; overflow:hidden; transition:transform .18s ease;
}
.t2-rule-card:hover { transform:translateY(-2px); }
.t2-rule-card.pass { border-color:rgba(0,255,127,.32); background:rgba(0,255,127,.03); }
.t2-rule-card.fail { border-color:rgba(255,49,49,.32);  background:rgba(255,49,49,.03); }
.t2-rule-card.warn { border-color:rgba(255,215,0,.30);  background:rgba(255,215,0,.025); }
.t2-rule-icon  { font-size:28px; margin-bottom:9px; }
.t2-rule-title { font-family:var(--f-mono); font-size:8.5px; color:rgba(145,162,185,.55); text-transform:uppercase; letter-spacing:1.5px; margin-bottom:7px; }
.t2-rule-val   { font-family:var(--f-display); font-size:24px; color:#FFF; margin-bottom:6px; }
.t2-rule-badge { font-family:var(--f-body); font-size:12px; font-weight:700; display:inline-block; padding:3px 10px; border-radius:20px; }
.pass .t2-rule-badge { background:rgba(0,255,127,.14); color:#00FF7F; }
.fail .t2-rule-badge { background:rgba(255,49,49,.14);  color:#FF6B6B; }
.warn .t2-rule-badge { background:rgba(255,215,0,.12);  color:#FFD700; }

/* ── CHART WRAPPER ────────────────────────────────────────────────── */
.t2-chart-wrap {
    background:rgba(0,0,0,.32); border:1px solid rgba(255,255,255,.055);
    border-radius:16px; padding:14px 8px 5px; margin:14px 0; overflow:hidden;
}

/* ── V300 BUTTON STYLE ────────────────────────────────────────────── */
div.stButton > button {
    background:linear-gradient(135deg, rgba(0,245,255,0.08), rgba(0,245,255,0.02)) !important;
    border:1px solid rgba(0,245,255,0.28) !important;
    color:rgba(0,245,255,0.92) !important;
    font-family:'JetBrains Mono',monospace !important;
    font-size:11px !important;
    font-weight:600 !important;
    letter-spacing:1.5px !important;
    text-transform:uppercase !important;
    border-radius:10px !important;
    padding:10px 20px !important;
    transition:all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
}
div.stButton > button:hover {
    background:linear-gradient(135deg, rgba(0,245,255,0.15), rgba(0,245,255,0.05)) !important;
    border-color:rgba(0,245,255,0.45) !important;
    color:#00F5FF !important;
    box-shadow:0 0 20px rgba(0,245,255,0.2), 0 4px 12px rgba(0,0,0,0.3) !important;
    transform:translateY(-1px) !important;
}
div.stButton > button[kind="primary"] {
    background:linear-gradient(135deg, rgba(255,215,0,0.12), rgba(255,215,0,0.04)) !important;
    border:1px solid rgba(255,215,0,0.35) !important;
    color:rgba(255,215,0,0.95) !important;
}
div.stButton > button[kind="primary"]:hover {
    background:linear-gradient(135deg, rgba(255,215,0,0.18), rgba(255,215,0,0.08)) !important;
    border-color:rgba(255,215,0,0.55) !important;
    color:#FFD700 !important;
    box-shadow:0 0 20px rgba(255,215,0,0.25), 0 4px 12px rgba(0,0,0,0.3) !important;
}
</style>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  [核心] 欄位對應函數 - 直接使用 Excel 真實欄位名稱
# ══════════════════════════════════════════════════════════════════════════════
def normalize_dataframe(df):
    """
    將 Excel 的欄位名稱標準化為程式內部使用的名稱
    
    關鍵對應：
    - 可轉債市價 → price (最重要！)
    - 轉換價值 → conv_value
    - 標的股票市價 → stock_price_real
    """
    df = df.copy()
    
    # 完整的欄位對應字典
    rename_dict = {
        # 基本資訊
        '債券代號': 'code',
        '標的債券': 'name',
        '發行日期': 'issue_date',
        '最新賣回日': 'put_date',
        
        # 核心價格欄位（最重要！）
        '可轉債市價': 'price',           # ← 關鍵！
        '標的股票市價': 'stock_price_real',
        '轉換價格': 'conv_price',
        '轉換價值': 'conv_value',
        
        # 其他欄位
        '轉換標的代碼': 'stock_code',
        '餘額比例': 'balance_ratio',
        '流通餘額(張數)': 'outstanding_balance',
        '可轉債成交量': 'volume',
        '可轉債日均量(5D)': 'avg_volume_5d',
        '可轉債日均量(20D)': 'avg_volume_20d',
    }
    
    # 執行改名
    df.rename(columns=rename_dict, inplace=True)
    
    # Debug: 顯示改名後的欄位
    print("🔍 normalize_dataframe 執行後的欄位:")
    print(df.columns.tolist())
    
    # 檢查關鍵欄位是否存在
    critical_cols = ['price', 'conv_price', 'conv_value', 'stock_price_real']
    for col in critical_cols:
        if col not in df.columns:
            print(f"⚠️ 警告：關鍵欄位 '{col}' 不存在！")
            # 嘗試從其他欄位推導
            if col == 'price':
                # 可能的替代欄位名稱
                candidates = ['close', 'Close', '收盤價', '市價', 'underlying_price']
                for cand in candidates:
                    if cand in df.columns:
                        print(f"  → 使用 '{cand}' 作為 'price'")
                        df['price'] = df[cand]
                        break
                else:
                    print(f"  → 創建空欄位 'price' = 0.0")
                    df['price'] = 0.0
    
    # 計算已轉換比例（100 - 餘額比例）
    if 'balance_ratio' in df.columns:
        df['balance_ratio'] = pd.to_numeric(df['balance_ratio'], errors='coerce').fillna(100.0)
        df['conv_rate'] = 100.0 - df['balance_ratio']
    else:
        df['conv_rate'] = 0.0
    
    # 確保數值欄位為正確類型
    numeric_cols = ['price', 'conv_price', 'conv_value', 'stock_price_real', 'conv_rate']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)
    
    # 處理日期欄位
    for date_col in ['issue_date', 'put_date']:
        if date_col in df.columns:
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
    
    return df


# ══════════════════════════════════════════════════════════════════════════════
#  [核心] 計算理論價與溢價率
# ══════════════════════════════════════════════════════════════════════════════
def calculate_metrics(row):
    """
    計算理論價和溢價率
    
    理論價 (Parity) = 標的股票市價 / 轉換價格 * 100
    溢價率 (Premium) = (可轉債市價 - 轉換價值) / 轉換價值 * 100
    """
    # 理論價
    stock_price = pd.to_numeric(row.get('stock_price_real', 0), errors='coerce') or 0.0
    conv_price = pd.to_numeric(row.get('conv_price', 0.01), errors='coerce') or 0.01
    parity = (stock_price / conv_price) * 100 if conv_price > 0 else 0.0
    
    # 溢價率
    cb_price = pd.to_numeric(row.get('price', 0), errors='coerce') or 0.0
    conv_value = pd.to_numeric(row.get('conv_value', 0.01), errors='coerce') or 0.01
    premium = ((cb_price - conv_value) / conv_value) * 100 if conv_value > 0 else 0.0
    
    return parity, premium


# ══════════════════════════════════════════════════════════════════════════════
#  [V300 HELPER] 四大天條檢核卡片
# ══════════════════════════════════════════════════════════════════════════════
def _render_four_commandments(row):
    """生成四大天條檢核卡片（V300 設計風格）"""
    price = pd.to_numeric(row.get('price'), errors='coerce') or 0.0
    ma87 = pd.to_numeric(row.get('ma87'), errors='coerce') or 0.0
    ma284 = pd.to_numeric(row.get('ma284'), errors='coerce') or 0.0
    score = pd.to_numeric(row.get('score'), errors='coerce') or 0
    conv_rate = pd.to_numeric(row.get('conv_rate', 0), errors='coerce') or 0.0
    
    is_bull = ma87 > ma284
    
    cards_html = f"""
<div class="t2-rule-grid">
  <div class="t2-rule-card {'pass' if price < 120 else 'fail'}">
    <div class="t2-rule-icon">{'✅' if price < 120 else '❌'}</div>
    <div class="t2-rule-title">1. 價格天條</div>
    <div class="t2-rule-val">{price:.1f}</div>
    <div class="t2-rule-badge">{'PASS <120' if price < 120 else 'FAIL ≥120'}</div>
  </div>
  <div class="t2-rule-card {'pass' if is_bull else 'warn'}">
    <div class="t2-rule-icon">{'✅' if is_bull else '⚠️'}</div>
    <div class="t2-rule-title">2. 中期多頭</div>
    <div class="t2-rule-val">{'87MA >' if is_bull else '87MA <'}</div>
    <div class="t2-rule-badge">{'BULLISH' if is_bull else 'BEARISH'}</div>
  </div>
  <div class="t2-rule-card {'pass' if conv_rate < 30 else 'fail'}">
    <div class="t2-rule-icon">{'✅' if conv_rate < 30 else '❌'}</div>
    <div class="t2-rule-title">3. 已轉換率</div>
    <div class="t2-rule-val">{conv_rate:.1f}%</div>
    <div class="t2-rule-badge">{'CLEAN' if conv_rate < 30 else 'HEAVY'}</div>
  </div>
  <div class="t2-rule-card {'pass' if score >= 60 else 'warn'}">
    <div class="t2-rule-icon">{'✅' if score >= 60 else '⚠️'}</div>
    <div class="t2-rule-title">4. 策略評分</div>
    <div class="t2-rule-val">{int(score)}</div>
    <div class="t2-rule-badge">{'ELITE ≥60' if score >= 60 else 'WATCH'}</div>
  </div>
</div>
"""
    st.markdown(cards_html, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  主入口函數
# ══════════════════════════════════════════════════════════════════════════════
@st.fragment
def render():
    """Tab 2 主入口函數"""
    render_radar()


@st.fragment  
def render_radar():
    # [V300 UPGRADE #1] Dialog on first visit
    if not st.session_state.get('tab2_guided', False):
        _show_tactical_guide()
        return
    
    # [V300 CSS] 注入樣式
    _inject_v300_css()
    
    if st.button("🏠 返回戰情總部"):
        st.session_state.page = 'home'
        st.rerun()
    
    st.title("🏹 獵殺雷達 (CB Hunter Zone)")
    
    df = st.session_state.get('df', pd.DataFrame())
    
    with st.expander("2.1 自動獵殺推薦 (Auto Sniper)", expanded=True):
        st.info("此模組執行「全市場雙軌普查 (.TW/.TWO)」，並同步更新全系統連動資料庫。")
        
        col1, col2 = st.columns(2)
        with col1: 
            min_score = st.slider("最低評分門檻", 0, 10, 5)
        with col2: 
            st.caption("普查將抓取即時行情，請耐心等候。")
        
        if not df.empty:
            if st.button("🚀 啟動 SOP 全市場普查", type="primary"):
                with st.spinner("執行全市場掃描..."):
                    # 1. 標準化 DataFrame
                    work_df = normalize_dataframe(df)
                    
                    # 2. 普查迴圈
                    records = work_df.to_dict('records')
                    total = len(records)
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    enriched_data = []
                    
                    for i, row in enumerate(records):
                        name = row.get('name', '')
                        status_text.text(f"普查進行中 ({i+1}/{total}): {name}...")
                        
                        code = str(row.get('stock_code', '')).strip()
                        
                        # 確保保留所有原始欄位
                        # 初始化新增欄位
                        row['ma87'] = 0.0
                        row['ma284'] = 0.0
                        row['trend_status'] = "⚠️ 資料不足"
                        row['score'] = 50  # 預設評分
                        
                        # 拉取 K 線資料
                        if code:
                            try:
                                hist = pd.DataFrame()
                                try: 
                                    hist = yf.Ticker(f"{code}.TW").history(period="2y")
                                except: 
                                    pass
                                
                                if hist.empty:
                                    try: 
                                        hist = yf.Ticker(f"{code}.TWO").history(period="2y")
                                    except: 
                                        pass
                                
                                if not hist.empty and len(hist) > 284:
                                    curr = float(hist['Close'].iloc[-1])
                                    ma87 = float(hist['Close'].rolling(87).mean().iloc[-1])
                                    ma284 = float(hist['Close'].rolling(284).mean().iloc[-1])
                                    
                                    row['stock_price_real'] = curr
                                    row['ma87'] = ma87
                                    row['ma284'] = ma284
                                    
                                    # 87MA > 284MA = 中期多頭
                                    if ma87 > ma284:
                                        row['trend_status'] = "✅ 中期多頭"
                                        row['score'] = min(100, row['score'] + 20)
                                    else:
                                        row['trend_status'] = "整理/空頭"
                            except: 
                                pass
                        
                        enriched_data.append(row)
                        progress_bar.progress((i + 1) / total)
                    
                    # 3. 資料分流
                    full_df_enriched = pd.DataFrame(enriched_data)
                    
                    # [Debug] 檢查欄位
                    st.write("🔍 Debug: DataFrame 欄位", full_df_enriched.columns.tolist())
                    
                    # 確保關鍵欄位存在
                    required_cols = ['price', 'conv_rate', 'trend_status', 'score']
                    for col in required_cols:
                        if col not in full_df_enriched.columns:
                            st.warning(f"⚠️ 缺少欄位 '{col}'，正在創建...")
                            if col == 'price':
                                full_df_enriched[col] = 0.0
                            elif col == 'conv_rate':
                                full_df_enriched[col] = 0.0
                            elif col == 'trend_status':
                                full_df_enriched[col] = "⚠️ 資料不足"
                            elif col == 'score':
                                full_df_enriched[col] = 0
                    
                    # SOP 標準篩選
                    sop_mask = (
                        (pd.to_numeric(full_df_enriched['price'], errors='coerce').fillna(999) < 120) &
                        (full_df_enriched['trend_status'].astype(str).str.contains("多頭", na=False)) &
                        (pd.to_numeric(full_df_enriched['conv_rate'], errors='coerce').fillna(999) < 30)
                    )
                    sop_results = full_df_enriched[sop_mask].sort_values('score', ascending=False)
                    
                    st.session_state['scan_results'] = sop_results
                    st.session_state['full_census_data'] = full_df_enriched.to_dict('records')
                    
                    status_text.text("✅ 普查完成！資料已同步至戰情室與全系統。")
                    st.toast(f"✅ 全市場掃描結束，符合 SOP 黃金標準共 {len(sop_results)} 檔", icon="🎯")
                    
                    if not sop_results.empty:
                        # 顯示結果
                        display_cols = ['code', 'name', 'price', 'stock_price_real', 
                                       'trend_status', 'conv_rate', 'score']
                        st.dataframe(sop_results[display_cols].head(20))
                        
                        # 顯示詳細報告
                        st.subheader("📊 詳細分析")
                        for _, row in sop_results.head(5).iterrows():
                            cb_name = row.get('name', '未知')
                            cb_code = str(row.get('code', '0000')).strip()
                            price = row.get('price', 0.0)
                            score = row.get('score', 0)
                            conv_rate = row.get('conv_rate', 0.0)
                            
                            # 計算理論價和溢價率
                            parity, premium = calculate_metrics(row)
                            
                            title = f"👑 {cb_name} ({cb_code}) | CB價: {price:.1f} | 評分: {int(score)}"
                            with st.expander(title):
                                st.markdown(f"### 🛡️ 天條檢核: `✅ 價格<120` | `✅ 均線多頭` | `✅ 已轉換率 {conv_rate:.2f}%`")
                                st.divider()
                                
                                # [V300] 四大天條卡片
                                _render_four_commandments(row)
                                
                                # 決策輔助
                                st.success("### 2. 決策輔助 (Decision Support)")
                                c1, c2, c3 = st.columns(3)
                                c1.metric("理論價 (Parity)", f"{parity:.2f}")
                                c2.metric("溢價率 (Premium)", f"{premium:.2f}%")
                                c3.metric("已轉換比例", f"{conv_rate:.2f}%")
                                
                                # Debug 資訊（可選）
                                with st.expander("🔍 數據來源（Debug）", expanded=False):
                                    st.write(f"標的股票市價: {row.get('stock_price_real', 0):.2f}")
                                    st.write(f"轉換價格: {row.get('conv_price', 0):.2f}")
                                    st.write(f"轉換價值: {row.get('conv_value', 0):.2f}")
                                    st.write(f"可轉債市價: {row.get('price', 0):.2f}")
                                    st.write(f"餘額比例: {row.get('balance_ratio', 0):.2f}%")
                                    st.write(f"已轉換比例: {conv_rate:.2f}%")
        else:
            st.info("請上傳 CB 清單以啟動自動獵殺掃描。")
