# ui_desktop/tab2_radar.py
# Titan SOP V100.0 — Tab 2: 獵殺雷達
# [靈魂注入 V82.0 → V100.0]
# 完整移植：
#   2.1 自動獵殺推薦 (全市場雙軌普查 + SOP菁英榜 + 新券蜜月 + 滿年沈澱 + 賣回保衛 + 產業風口地圖)
#   2.2 核心策略檢核 (互動式K線 + 4大天條 + 5子分頁)
#   2.3 潛在風險雷達 (籌碼鬆動 + 高溢價 + 流動性陷阱)
#   2.4 資金配置試算 (Kelly 倉位建議)

import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import plotly.express as px
from datetime import datetime
import yfinance as yf

# ── V82 引擎導入 ──────────────────────────────────────────────────────────────
from strategy import TitanStrategyEngine
from knowledge_base import TitanKnowledgeBase

@st.cache_resource
def _load_engines():
    kb = TitanKnowledgeBase()
    strat = TitanStrategyEngine()
    strat.kb = kb
    return strat, kb

@st.cache_data(ttl=600)
def _get_scan_result(_strat_id, df_json):
    """10分鐘緩存掃描結果"""
    strat, _ = _load_engines()
    df = pd.read_json(df_json)
    return strat.scan_entire_portfolio(df)


# ═══════════════════════════════════════════════════════════════
#  互動式 K 線圖 (5碼CB → 4碼股票，雙軌下載，Altair 紅漲綠跌)
# ═══════════════════════════════════════════════════════════════
def _plot_candle_chart(cb_code: str):
    """繪製 Altair 互動式 K 線圖，疊加 87MA / 284MA"""
    target_code = str(cb_code).strip()
    # 5碼CB代號 → 取前4碼為股票代號
    if len(target_code) == 5 and target_code.isdigit():
        target_code = target_code[:4]

    try:
        chart_df = yf.download(f"{target_code}.TW", period="2y", progress=False)
        if chart_df.empty:
            chart_df = yf.download(f"{target_code}.TWO", period="2y", progress=False)
        if chart_df.empty:
            st.error(f"❌ Yahoo Finance 查無此標的 K 線資料: {target_code}")
            return

        if isinstance(chart_df.columns, pd.MultiIndex):
            chart_df.columns = chart_df.columns.get_level_values(0)
        chart_df = chart_df.reset_index()
        chart_df['MA87']  = chart_df['Close'].rolling(87).mean()
        chart_df['MA284'] = chart_df['Close'].rolling(284).mean()

        base = alt.Chart(chart_df).encode(
            x=alt.X('Date:T', axis=alt.Axis(title='日期', format='%Y-%m-%d'))
        )
        color_cond = alt.condition(
            "datum.Open <= datum.Close",
            alt.value("#FF4B4B"),
            alt.value("#26A69A")
        )
        candles = (
            base.mark_rule().encode(
                y=alt.Y('Low', title='股價', scale=alt.Scale(zero=False)),
                y2='High'
            )
            + base.mark_bar().encode(
                y='Open', y2='Close',
                color=color_cond,
                tooltip=['Date:T', 'Open:Q', 'Close:Q', 'High:Q', 'Low:Q']
            )
        )
        line_87  = base.mark_line(color='orange',  strokeWidth=2).encode(y='MA87')
        line_284 = base.mark_line(color='#00bfff', strokeWidth=2).encode(y='MA284')

        st.altair_chart((candles + line_87 + line_284).interactive(), use_container_width=True)
        st.caption(f"📈 標的股票代碼: {target_code} | 🔶 橘線: 87MA | 🔷 藍線: 284MA")
    except Exception as e:
        st.warning(f"K 線圖生成失敗: {e}")


# ═══════════════════════════════════════════════════════════════
#  Tab 5 子分頁：產業風口地圖 (IC.TPEX 官方30大產業鏈 Treemap)
# ═══════════════════════════════════════════════════════════════
@st.cache_data(ttl=3600)
def _get_tpex_data(df_json: str) -> pd.DataFrame:
    full_data = pd.read_json(df_json)
    chain_map = {
        # 半導體
        '世芯': ('半導體','⬆️ 上游-IC設計','IP/ASIC'), '創意': ('半導體','⬆️ 上游-IC設計','IP/ASIC'),
        '聯發科': ('半導體','⬆️ 上游-IC設計','手機SoC'), '瑞昱': ('半導體','⬆️ 上游-IC設計','網通IC'),
        '台積': ('半導體','↔️ 中游-製造','晶圓代工'), '聯電': ('半導體','↔️ 中游-製造','晶圓代工'),
        '弘塑': ('半導體','↔️ 中游-設備','濕製程'), '辛耘': ('半導體','↔️ 中游-設備','CoWoS'),
        '萬潤': ('半導體','↔️ 中游-設備','封測設備'), '日月光': ('半導體','⬇️ 下游-封測','封裝'),
        # 通信網路
        '智邦': ('通信網路','⬇️ 下游-網通設備','交換器'), '啟碁': ('通信網路','⬇️ 下游-網通設備','衛星/車用'),
        '中磊': ('通信網路','⬇️ 下游-網通設備','寬頻'), '全新': ('通信網路','⬆️ 上游-元件','PA砷化鎵'),
        '穩懋': ('通信網路','⬆️ 上游-元件','PA代工'), '華星光': ('通信網路','↔️ 中游-光通訊','CPO模組'),
        '波若威': ('通信網路','↔️ 中游-光通訊','光纖元件'), '聯亞': ('通信網路','↔️ 中游-光通訊','雷射二極體'),
        # 電腦週邊
        '廣達': ('電腦週邊','⬇️ 下游-組裝','AI伺服器'), '緯創': ('電腦週邊','⬇️ 下游-組裝','AI伺服器'),
        '技嘉': ('電腦週邊','⬇️ 下游-品牌','板卡/Server'), '微星': ('電腦週邊','⬇️ 下游-品牌','電競'),
        '奇鋐': ('電腦週邊','↔️ 中游-散熱','3D VC'), '雙鴻': ('電腦週邊','↔️ 中游-散熱','水冷板'),
        '勤誠': ('電腦週邊','↔️ 中游-機殼','伺服器機殼'), '川湖': ('電腦週邊','↔️ 中游-機構','導軌'),
        '樺漢': ('電腦週邊','⬇️ 下游-工業電腦','IPC'), '研華': ('電腦週邊','⬇️ 下游-工業電腦','IPC'),
        # 電子零組件
        '台光電': ('電子零組件','⬆️ 上游-材料','CCL銅箔基板'), '台燿': ('電子零組件','⬆️ 上游-材料','CCL高頻'),
        '金像電': ('電子零組件','↔️ 中游-PCB','伺服器板'), '健鼎': ('電子零組件','↔️ 中游-PCB','HDI'),
        '欣興': ('電子零組件','↔️ 中游-PCB','ABF載板'), '南電': ('電子零組件','↔️ 中游-PCB','ABF載板'),
        '國巨': ('電子零組件','↔️ 中游-被動元件','MLCC'), '華新科': ('電子零組件','↔️ 中游-被動元件','MLCC'),
        '凡甲': ('電子零組件','↔️ 中游-連接器','車用/Server'), '嘉澤': ('電子零組件','↔️ 中游-連接器','CPU Socket'),
        # 光電
        '大立光': ('光電','⬆️ 上游-光學','鏡頭'), '玉晶光': ('光電','⬆️ 上游-光學','鏡頭'),
        '亞光': ('光電','⬆️ 上游-光學','車載鏡頭'), '群創': ('光電','↔️ 中游-面板','LCD'),
        '友達': ('光電','↔️ 中游-面板','LCD'), '中光電': ('光電','⬇️ 下游-背光','背光模組'),
        # 生技醫療
        '藥華藥': ('生技醫療','⬆️ 上游-新藥','新藥研發'), '合一': ('生技醫療','⬆️ 上游-新藥','新藥研發'),
        '保瑞': ('生技醫療','↔️ 中游-製造','CDMO'), '美時': ('生技醫療','↔️ 中游-製造','學名藥'),
        '晶碩': ('生技醫療','⬇️ 下游-醫材','隱形眼鏡'), '視陽': ('生技醫療','⬇️ 下游-醫材','隱形眼鏡'),
        # 電機機械
        '上銀': ('電機機械','⬆️ 上游-傳動','滾珠螺桿'), '亞德客': ('電機機械','⬆️ 上游-氣動','氣動元件'),
        '東元': ('電機機械','↔️ 中游-馬達','工業馬達'),
        # 建材營造
        '華固': ('建材營造','⬇️ 下游-建設','住宅商辦'), '長虹': ('建材營造','⬇️ 下游-建設','住宅商辦'),
        '興富發': ('建材營造','⬇️ 下游-建設','住宅'), '遠雄': ('建材營造','⬇️ 下游-建設','廠辦'),
        # 航運業
        '長榮': ('航運業','↔️ 中游-海運','貨櫃'), '陽明': ('航運業','↔️ 中游-海運','貨櫃'),
        '萬海': ('航運業','↔️ 中游-海運','貨櫃'), '長榮航': ('航運業','↔️ 中游-空運','航空'),
        '華航': ('航運業','↔️ 中游-空運','航空'), '星宇': ('航運業','↔️ 中游-空運','航空'),
        # 綠能環保 (含重電)
        '華城': ('綠能環保','↔️ 中游-重電','變壓器'), '士電': ('綠能環保','↔️ 中游-重電','配電盤'),
        '中興電': ('綠能環保','↔️ 中游-重電','GIS開關'), '亞力': ('綠能環保','↔️ 中游-重電','輸配電'),
        '世紀鋼': ('綠能環保','⬆️ 上游-風電','水下基礎'), '森崴': ('綠能環保','⬇️ 下游-能源','綠電開發'),
        # 汽車工業
        '東陽': ('汽車工業','↔️ 中游-零組件','AM保險桿'), '帝寶': ('汽車工業','↔️ 中游-零組件','AM車燈'),
        '裕隆': ('汽車工業','⬇️ 下游-整車','品牌製造'), '和泰車': ('汽車工業','⬇️ 下游-代理','TOYOTA'),
    }

    def classify(name):
        for k, v in chain_map.items():
            if k in name: return v
        if any(x in name for x in ['電', '科', '矽', '晶', '半']):
            if '光' in name: return ('光電','一般光電','光電')
            return ('半導體','其他半導體','半導體')
        if any(x in name for x in ['網', '通', '訊']): return ('通信網路','網通設備','通信')
        if any(x in name for x in ['腦', '機', '資']): return ('電腦週邊','系統','電腦')
        if any(x in name for x in ['板', '線', '器', '零']): return ('電子零組件','被動/連接','零組件')
        if any(x in name for x in ['生', '醫', '藥']): return ('生技醫療','生技','醫療')
        if any(x in name for x in ['綠', '能', '源']): return ('綠能環保','能源','綠能')
        if any(x in name for x in ['航', '運', '船']): return ('航運業','運輸','航運')
        if any(x in name for x in ['營', '建', '地']): return ('建材營造','建設','營造')
        if any(x in name for x in ['金', '銀', '保']): return ('金融業','金融','金控')
        if any(x in name for x in ['車', '汽']): return ('汽車工業','零組件','汽車')
        return ('其他','未分類','其他')

    d = full_data.copy()
    d[['L1','L2','L3']] = d['name'].apply(lambda x: pd.Series(classify(x)))
    d['ma87']  = pd.to_numeric(d.get('ma87',  pd.Series(dtype=float)), errors='coerce')
    d['price'] = pd.to_numeric(d.get('stock_price_real', pd.Series(dtype=float)), errors='coerce')
    d['bias']  = ((d['price'] - d['ma87']) / d['ma87'] * 100)
    d['bias_clean'] = d['bias'].fillna(0).clip(-25, 25)
    d['bias_label'] = d['bias'].apply(lambda x: f"{x:+.1f}%" if pd.notnull(x) else "N/A")
    d['size_metric'] = d['price'].fillna(10)
    return d


# ═══════════════════════════════════════════════════════════════
#  數值工具函式
# ═══════════════════════════════════════════════════════════════
def _safe_conv(row) -> float:
    """餘額比例 → 已轉換比例（智慧反轉邏輯）"""
    raw = pd.to_numeric(row.get('conv_rate', 100), errors='coerce') or 100.0
    converted = (100.0 - raw) if raw > 50 else raw
    return max(0.0, converted)


# ═══════════════════════════════════════════════════════════════
#  普查引擎 (核心手術區)
# ═══════════════════════════════════════════════════════════════
def _run_census(df: pd.DataFrame, min_score: int) -> tuple:
    """
    全市場雙軌普查 (.TW/.TWO)
    返回: (sop_results_df, full_enriched_df)
    """
    strat, _ = _load_engines()

    # ── Step 1: 欄位標準化 ──────────────────────────────────────
    work_df = df.copy()
    rename_map = {
        '代號': 'code', '名稱': 'name', '可轉債市價': 'price',
        '轉換價格': 'conv_price', '轉換標的': 'stock_code',
        '已轉換比例': 'conv_rate', '轉換價值': 'conv_value',
        '發行日': 'issue_date', '賣回日': 'put_date',
        '餘額比例': 'balance_ratio'
    }
    work_df.rename(columns=lambda c: rename_map.get(c.strip(), c.strip()), inplace=True)

    # 餘額比例 → 已轉換率
    if 'balance_ratio' in work_df.columns:
        bal = pd.to_numeric(work_df['balance_ratio'], errors='coerce').fillna(100.0)
        work_df['conv_rate'] = 100.0 - bal

    # 型別安全
    for col in ['price', 'conv_rate', 'conv_price', 'conv_value']:
        work_df[col] = pd.to_numeric(work_df.get(col, pd.Series(dtype=float)), errors='coerce').fillna(0.0)

    # 日期欄位
    for dcol in ['issue_date', 'put_date', 'list_date']:
        if dcol in work_df.columns:
            work_df[dcol] = pd.to_datetime(work_df[dcol], errors='coerce')
    if 'issue_date' not in work_df.columns and 'list_date' in work_df.columns:
        work_df['issue_date'] = work_df['list_date']

    # ── Step 2: 策略評分 ────────────────────────────────────────
    try:
        scan_df = strat.scan_entire_portfolio(work_df)
        records = scan_df.to_dict('records')
    except Exception as e:
        st.error(f"策略掃描失敗: {e}")
        return pd.DataFrame(), pd.DataFrame()

    # ── Step 3: 即時行情富集 ────────────────────────────────────
    total = len(records)
    progress_bar = st.progress(0)
    status_text  = st.empty()
    enriched = []

    for i, row in enumerate(records):
        name = row.get('name', '')
        status_text.text(f"普查進行中 ({i+1}/{total}): {name}…")

        code = str(row.get('stock_code', '')).strip()
        row['stock_price_real'] = 0.0
        row['ma87'] = 0.0
        row['ma284'] = 0.0
        row['trend_status'] = "⚠️ 資料不足"
        row['cb_price'] = row.get('price', 0.0)
        row['conv_price_val'] = row.get('conv_price', 0.0)
        row['conv_value_val'] = row.get('conv_value', 0.0)

        if code:
            try:
                hist = yf.Ticker(f"{code}.TW").history(period="2y")
                if hist.empty:
                    hist = yf.Ticker(f"{code}.TWO").history(period="2y")
                if not hist.empty and len(hist) > 284:
                    curr  = float(hist['Close'].iloc[-1])
                    ma87  = float(hist['Close'].rolling(87).mean().iloc[-1])
                    ma284 = float(hist['Close'].rolling(284).mean().iloc[-1])
                    row.update({'stock_price_real': curr, 'ma87': ma87, 'ma284': ma284})
                    if ma87 > ma284:
                        row['trend_status'] = "✅ 中期多頭"
                        row['score'] = min(100, row.get('score', 0) + 20)
                    else:
                        row['trend_status'] = "整理/空頭"
            except Exception:
                pass

        enriched.append(row)
        progress_bar.progress((i + 1) / total)

    status_text.text("✅ 普查完成！")
    full_df = pd.DataFrame(enriched)

    for col in ['price', 'conv_rate']:
        if col not in full_df.columns:
            full_df[col] = 0.0

    # ── Step 4: SOP 黃金篩選 ────────────────────────────────────
    sop_mask = (
        (full_df['price'] < 120) &
        (full_df['trend_status'].str.contains("多頭", na=False)) &
        (full_df['conv_rate'] < 30)
    )
    sop_df = full_df[sop_mask].sort_values('score', ascending=False)

    # 過濾最低分
    if 'score' in sop_df.columns:
        sop_df = sop_df[sop_df['score'] >= min_score]

    return sop_df, full_df


# ═══════════════════════════════════════════════════════════════
#  SOP 個股卡片 (4 天條 + K線)
# ═══════════════════════════════════════════════════════════════
def _render_cb_card(row, badge: str = "👑", report_title: str = "📄 查看詳細分析報告"):
    now = datetime.now()
    cb_code  = str(row.get('code', row.get('stock_code', '0000'))).strip()
    cb_name  = row.get('name', '未知')
    price    = pd.to_numeric(row.get('price'), errors='coerce') or 0.0
    ma87     = pd.to_numeric(row.get('ma87'),  errors='coerce') or 0.0
    ma284    = pd.to_numeric(row.get('ma284'), errors='coerce') or 0.0
    score    = pd.to_numeric(row.get('score'), errors='coerce') or 0
    conv_pct = _safe_conv(row)

    title = f"{badge} {cb_name} ({cb_code}) | CB價: {price:.1f} | 評分: {int(score)}"
    with st.expander(title):
        st.markdown(
            f"### 🛡️ 天條檢核: "
            f"`{'✅' if price < 120 else '⚠️'} 價格<120` | "
            f"`{'✅' if ma87 > ma284 else '⚠️'} 均線多頭` | "
            f"`✅ 已轉換率 {conv_pct:.2f}%`"
        )
        st.divider()
        with st.expander(report_title, expanded=False):
            st.markdown(f"## 📊 {cb_name} ({cb_code}) 策略分析")

            st.info("### 1. 核心策略檢核 (The 4 Commandments)")
            st.markdown(f"1. 價格天條 (<115): {'✅ 通過' if price < 115 else '⚠️ 警戒'} (目前 **{price:.1f}**)")
            is_bullish = ma87 > ma284
            st.markdown(f"2. 中期多頭排列: {'✅ 通過' if is_bullish else '⚠️ 整理中'}")
            st.markdown(f"> 均線數據: 87MA **{ma87:.2f}** {' > ' if is_bullish else ' < '} 284MA **{ma284:.2f}**")
            st.markdown("3. 身分認證 (Identity): ☐ 領頭羊 / ☐ 風口豬")
            st.markdown("> 💡 領頭羊: 族群中率先領漲的指標股 | 風口豬: 主流題材中的二軍低價股")
            st.markdown("4. 發債故事 (Story): ☐ 從無到有 / ☐ 擴產 / ☐ 政策事件")

            st.success("### 2. 決策輔助 (Decision Support)")
            conv_price  = pd.to_numeric(row.get('conv_price_val', 0.01), errors='coerce')
            stock_price = pd.to_numeric(row.get('stock_price_real', 0.0), errors='coerce')
            parity      = (stock_price / conv_price * 100) if conv_price > 0 else 0.0
            conv_value  = pd.to_numeric(row.get('conv_value_val', 0.0), errors='coerce')
            premium     = ((price - conv_value) / conv_value * 100) if conv_value > 0 else 0.0
            c1, c2, c3  = st.columns(3)
            c1.metric("理論價 (Parity)", f"{parity:.2f}")
            c2.metric("溢價率 (Premium)", f"{premium:.2f}%")
            c3.metric("已轉換比例", f"{conv_pct:.2f}%")

            st.markdown("### 4. 交易計畫 (Trading Plan)")
            st.warning("🕒 關鍵時段：09:00 開盤後30分鐘 (觀察大戶試撮) / 13:25 收盤前25分鐘 (尾盤定勝負)")
            st.markdown("* 🎯 進場佈局: 建議於 105~115 元區間佈局加碼。")
            st.markdown("* 🚀 加碼時機: 股價帶量突破 87MA 或 284MA 時。")

            st.markdown("### 5. 出場/風控 (Exit/Risk)")
            st.markdown("* 🛑 停損: CB 跌破 100 元 (保本天條)。")
            st.markdown("* 💰 停利: 目標價 152 元以上，嚴守「留魚尾」策略。")
            st.divider()
            _plot_candle_chart(cb_code)


# ═══════════════════════════════════════════════════════════════
#  主渲染入口
# ═══════════════════════════════════════════════════════════════
def render():
    """Tab 2: 獵殺雷達 — 全功能復原版 (V82 靈魂 + V100 外殼)"""

    df  = st.session_state.get('df', pd.DataFrame())
    now = datetime.now()

    # ─────────────────────────────────────────────────────────────
    # 2.1 自動獵殺推薦 (全市場雙軌普查)
    # ─────────────────────────────────────────────────────────────
    with st.expander("2.1 🚀 自動獵殺推薦 (Auto Sniper)", expanded=True):
        st.info("此模組執行「全市場雙軌普查 (.TW/.TWO)」，並同步更新全系統連動資料庫。")

        col1, col2 = st.columns(2)
        with col1:
            min_score = st.slider("最低評分門檻", 0, 100, 50)
        with col2:
            st.caption("普查將抓取即時行情，請耐心等候 (約 2-5 分鐘)。")

        if not df.empty:
            if st.button("🚀 啟動 SOP 全市場普查", type="primary", key="btn_census"):
                with st.spinner("執行全市場掃描…"):
                    sop_df, full_df = _run_census(df, min_score)
                    st.session_state['scan_results']    = sop_df
                    st.session_state['full_census_data'] = full_df.to_dict('records')

                st.success(f"✅ 掃描完成！符合「SOP 黃金標準」共 **{len(sop_df)}** 檔。")
                if not sop_df.empty:
                    disp_cols = [c for c in ['code','name','price','stock_price_real','trend_status','conv_rate','score'] if c in sop_df.columns]
                    st.dataframe(sop_df[disp_cols].head(20), use_container_width=True)
        else:
            st.info("請上傳 CB 清單以啟動自動獵殺掃描。")

    # ─────────────────────────────────────────────────────────────
    # 2.2 核心策略檢核 (5 子分頁)
    # ─────────────────────────────────────────────────────────────
    with st.expander("2.2 🎯 核心策略檢核 (The War Room)", expanded=False):
        if 'full_census_data' not in st.session_state:
            st.warning("⚠️ 請先至本頁上方執行「SOP 全市場普查」。")
        else:
            full_data = pd.DataFrame(st.session_state['full_census_data'])
            if 'issue_date' in full_data.columns:
                full_data['issue_date'] = pd.to_datetime(full_data['issue_date'], errors='coerce')
            if 'put_date' in full_data.columns:
                full_data['put_date'] = pd.to_datetime(full_data['put_date'], errors='coerce')

            sub1, sub2, sub3, sub4, sub5 = st.tabs([
                "🏆 SOP 菁英榜", "👶 新券蜜月", "💤 滿年沈澱", "🛡️ 賣回保衛", "🔥 產業風口地圖"
            ])

            # ── Tab 2.2-1: SOP 菁英榜 ────────────────────────────
            with sub1:
                if 'scan_results' in st.session_state and not st.session_state['scan_results'].empty:
                    df_t1 = st.session_state['scan_results'].head(20)
                else:
                    mask = (full_data['price'] < 120) & (full_data['trend_status'].str.contains("多頭", na=False))
                    df_t1 = full_data[mask].sort_values('score', ascending=False).head(20)

                if df_t1.empty:
                    st.info("無符合標準標的。")
                else:
                    st.caption(f"共 {len(df_t1)} 檔通過 SOP 黃金標準")
                    for _, row in df_t1.iterrows():
                        _render_cb_card(row, badge="👑", report_title="📄 查看詳細分析報告 (Detailed Report)")

            # ── Tab 2.2-2: 新券蜜月 ──────────────────────────────
            with sub2:
                mask_t2 = (
                    full_data['issue_date'].notna() &
                    ((now - full_data['issue_date']).dt.days < 90) &
                    (full_data['price'] < 130) &
                    (full_data['conv_rate'] < 30)
                )
                df_t2 = full_data[mask_t2].sort_values('issue_date', ascending=False)

                if df_t2.empty:
                    st.info("目前無符合「新券蜜月」標準的標的 (上市<90天, 價格<130, 轉換率<30%)。")
                else:
                    st.caption(f"共 {len(df_t2)} 檔蜜月期新券")
                    for _, row in df_t2.iterrows():
                        days = (now - row['issue_date']).days
                        price = pd.to_numeric(row.get('price'), errors='coerce') or 0.0
                        ma87  = pd.to_numeric(row.get('ma87'),  errors='coerce') or 0.0
                        ma284 = pd.to_numeric(row.get('ma284'), errors='coerce') or 0.0
                        conv_pct = _safe_conv(row)
                        cb_code = str(row.get('code', row.get('stock_code','0000'))).strip()
                        cb_name = row.get('name', '未知')

                        title = f"👶 {cb_name} ({cb_code}) | 上市 {days} 天 | CB價: {price:.1f}"
                        with st.expander(title):
                            st.markdown(
                                f"### 🛡️ 新券檢核: "
                                f"`✅ 上市 {days} 天` | "
                                f"`✅ 價格 < 130` | "
                                f"`✅ 已轉換 {conv_pct:.2f}%`"
                            )
                            st.divider()
                            with st.expander("📄 查看蜜月期深度分析 (Honeymoon Report)", expanded=False):
                                st.markdown(f"## 📊 {cb_name} ({cb_code}) 蜜月期戰略")
                                st.info("### 1. 核心策略檢核 (The 4 Commandments)")
                                st.markdown(f"1. 蜜月期價格: {'✅ 通過' if price < 115 else '⚠️ 監控'} (新券甜蜜區 105-115，目前 **{price:.1f}**)")
                                is_bullish = ma87 > ma284
                                trend_txt = "✅ 多頭排列" if is_bullish else ("⚠️ 資料不足" if ma87 == 0 else "❌ 偏弱")
                                st.markdown(f"2. 中期多頭排列: {trend_txt}")
                                if ma87 > 0:
                                    st.markdown(f"> 87MA **{ma87:.2f}** {' > ' if is_bullish else ' < '} 284MA **{ma284:.2f}**")
                                else:
                                    st.caption("(新券上市天數較短，均線指標僅供參考)")
                                st.markdown("3. 身分認證 (Identity): ☐ 領頭羊 / ☐ 風口豬")
                                st.markdown("4. 發債故事 (Story): ☐ 從無到有 / ☐ 擴產 / ☐ 政策事件")
                                st.success("### 2. 決策輔助 (Decision Support)")
                                conv_price  = pd.to_numeric(row.get('conv_price_val', 0.01), errors='coerce')
                                stock_price = pd.to_numeric(row.get('stock_price_real', 0.0), errors='coerce')
                                parity  = (stock_price / conv_price * 100) if conv_price > 0 else 0.0
                                conv_val = pd.to_numeric(row.get('conv_value_val', 0.0), errors='coerce')
                                premium = ((price - conv_val) / conv_val * 100) if conv_val > 0 else 0.0
                                c1, c2, c3 = st.columns(3)
                                c1.metric("理論價 (Parity)", f"{parity:.2f}")
                                c2.metric("溢價率 (Premium)", f"{premium:.2f}%")
                                c3.metric("已轉換比例", f"{conv_pct:.2f}%")
                                st.markdown("### 4. 交易計畫")
                                st.markdown("* 🎯 蜜月期佈局: 新券上市初期若價格在 110 元以下為極佳安全邊際。")
                                st.markdown("* 🚀 加碼時機: 股價帶量突破 87MA 或 284MA。")
                                st.markdown("* 🛑 停損: CB 跌破 100 元 (保本天條，新券下檔有限)。")
                                st.divider()
                                _plot_candle_chart(cb_code)

            # ── Tab 2.2-3: 滿年沈澱 ──────────────────────────────
            with sub3:
                fd_t3 = full_data.copy()
                fd_t3 = fd_t3.dropna(subset=['issue_date'])
                fd_t3['days_old'] = (now - fd_t3['issue_date']).dt.days

                def _mask_t3(row):
                    try:
                        if not (350 <= row['days_old'] <= 420): return False
                        p = pd.to_numeric(row.get('price'), errors='coerce') or 0.0
                        if p >= 115 or p <= 0: return False
                        actual = _safe_conv(row)
                        return actual < 30
                    except Exception:
                        return False

                df_t3 = fd_t3[fd_t3.apply(_mask_t3, axis=1)].sort_values('days_old')

                if df_t3.empty:
                    st.info("💡 目前無符合「滿年沈澱」標準的標的 (上市滿一年, 價格<115, 轉換率<30%)。")
                else:
                    st.caption(f"共 {len(df_t3)} 檔滿年沈澱標的")
                    for _, row in df_t3.iterrows():
                        days   = int(row['days_old'])
                        price  = pd.to_numeric(row.get('price'), errors='coerce') or 0.0
                        ma87   = pd.to_numeric(row.get('ma87'),  errors='coerce') or 0.0
                        sp     = pd.to_numeric(row.get('stock_price_real'), errors='coerce') or 0.0
                        c_pct  = _safe_conv(row)
                        cb_code = str(row.get('code', row.get('stock_code','0000'))).strip()
                        cb_name = row.get('name', '未知')
                        above87 = sp > ma87 if ma87 > 0 else False

                        title = f"💤 {cb_name} ({cb_code}) | 沈澱 {days} 天 | CB價: {price:.1f}"
                        with st.expander(title):
                            st.markdown(
                                f"### 🛡️ 沈澱檢核: `✅ 上市 {days} 天` | "
                                f"`✅ 價格 < 115` | "
                                f"`{'✅ 已站上 87MA' if above87 else '⚠️ 均線下方'}`"
                            )
                            st.divider()
                            with st.expander("📄 查看滿年沈澱深度分析 (Consolidation Report)", expanded=False):
                                st.markdown(f"## 📊 {cb_name} ({cb_code}) 滿年甦醒評估")
                                st.info("### 1. 核心策略檢核")
                                st.markdown(f"1. 價格天條 (<115): ✅ 通過 (目前 **{price:.1f}**)")
                                st.markdown(f"2. {'✅ 站上87MA' if above87 else '⚠️ 均線整理中'}")
                                if ma87 > 0:
                                    st.markdown(f"> 現價 **{sp:.2f}** {' > ' if above87 else ' < '} 87MA **{ma87:.2f}**")
                                st.markdown("3. 身分認證: ☐ 領頭羊 / ☐ 風口豬")
                                st.markdown("4. 發債故事: ☐ 從無到有 / ☐ 擴產 / ☐ 政策事件")
                                st.success("### 2. 決策輔助")
                                cp  = pd.to_numeric(row.get('conv_price_val', 0.01), errors='coerce')
                                par = (sp / cp * 100) if cp > 0 else 0.0
                                cv  = pd.to_numeric(row.get('conv_value_val', 0.0), errors='coerce')
                                prm = ((price - cv) / cv * 100) if cv > 0 else 0.0
                                c1, c2, c3 = st.columns(3)
                                c1.metric("理論價 (Parity)", f"{par:.2f}")
                                c2.metric("溢價率 (Premium)", f"{prm:.2f}%")
                                c3.metric("已轉換比例", f"{c_pct:.2f}%")
                                st.markdown("* 🎯 滿一年後，股價「站穩87MA」即為首波進場點。")
                                st.markdown("* 🚀 當87MA由平轉上揚，且股價帶量突破橫盤區間。")
                                st.markdown("* 🛑 停損: CB 跌破 100 元。 💰 停利: 152 元以上。")
                                st.divider()
                                _plot_candle_chart(cb_code)

            # ── Tab 2.2-4: 賣回保衛 ──────────────────────────────
            with sub4:
                fd_t4 = full_data.copy()
                fd_t4['days_to_put'] = (fd_t4['put_date'] - now).dt.days

                def _mask_t4(row):
                    try:
                        dtp = row['days_to_put']
                        if pd.isna(dtp) or not (0 < dtp < 180): return False
                        p = pd.to_numeric(row.get('price'), errors='coerce') or 0.0
                        if not (95 <= p <= 105): return False
                        return _safe_conv(row) < 30
                    except Exception:
                        return False

                df_t4 = fd_t4[fd_t4.apply(_mask_t4, axis=1)].sort_values('days_to_put')

                if df_t4.empty:
                    st.info("💡 目前無符合「賣回保衛」標準的標的 (距賣回<180天, 價格 95~105, 轉換率<30%)。")
                else:
                    st.caption(f"共 {len(df_t4)} 檔賣回套利機會")
                    for _, row in df_t4.iterrows():
                        left   = int(row['days_to_put'])
                        price  = pd.to_numeric(row.get('price'), errors='coerce') or 0.0
                        c_pct  = _safe_conv(row)
                        pd_str = row['put_date'].strftime('%Y-%m-%d')
                        cb_code = str(row.get('code', row.get('stock_code','0000'))).strip()
                        cb_name = row.get('name', '未知')
                        ma87   = pd.to_numeric(row.get('ma87'),  errors='coerce') or 0.0
                        ma284  = pd.to_numeric(row.get('ma284'), errors='coerce') or 0.0

                        title = f"🛡️ {cb_name} ({cb_code}) | 賣回倒數 {left} 天 | CB價: {price:.1f}"
                        with st.expander(title):
                            st.markdown(
                                f"### 🚨 保衛警告: `📅 賣回日: {pd_str}` | "
                                f"`✅ 價格甜甜圈 95-105` | "
                                f"`✅ 已轉換 {c_pct:.2f}%`"
                            )
                            st.divider()
                            with st.expander("📄 查看賣回保衛戰術報告 (Put Protection Report)", expanded=False):
                                st.markdown(f"## 📊 {cb_name} ({cb_code}) 賣回壓力測試")
                                is_bullish = ma87 > ma284
                                st.error("### 1. 核心策略檢核")
                                st.markdown(f"1. 價格天條 (95-105): ✅ 通過 (目前 **{price:.1f}**)")
                                st.markdown(f"2. 中期多頭: {'✅ 通過' if is_bullish else '⚠️ 整理中'}")
                                st.markdown("3. 身分認證: ☐ 領頭羊 / ☐ 風口豬")
                                st.markdown("4. 發債故事: ☐ 從無到有 / ☐ 擴產")
                                st.success("### 2. 決策輔助")
                                sp = pd.to_numeric(row.get('stock_price_real', 0.0), errors='coerce')
                                cp = pd.to_numeric(row.get('conv_price_val', 0.01), errors='coerce')
                                cv = pd.to_numeric(row.get('conv_value_val', 0.0), errors='coerce')
                                par = (sp / cp * 100) if cp > 0 else 0.0
                                prm = ((price - cv) / cv * 100) if cv > 0 else 0.0
                                c1, c2, c3 = st.columns(3)
                                c1.metric("距離賣回", f"{left} 天")
                                c2.metric("溢價率 (Premium)", f"{prm:.2f}%")
                                c3.metric("目標價", "152+", delta="保本套利")
                                st.markdown("* 🎯 此區間 (95-105) 買入，下檔風險極低。")
                                st.markdown("* 🚀 觀察賣回日前 2-3 月，股價站上87MA且量增。")
                                st.markdown("* 🛑 原則上不需停損。 💰 目標價 152 元以上。")
                                st.divider()
                                _plot_candle_chart(cb_code)

            # ── Tab 2.2-5: 產業風口地圖 ──────────────────────────
            with sub5:
                st.subheader("🌌 IC.TPEX 官方產業價值矩陣")

                full_json = pd.DataFrame(st.session_state['full_census_data']).to_json()
                df_galaxy = _get_tpex_data(full_json)

                if df_galaxy.empty:
                    st.info("無資料，請先執行普查。")
                else:
                    # Treemap
                    fig = px.treemap(
                        df_galaxy,
                        path=['L1','L2','L3','name'],
                        values='size_metric',
                        color='bias_clean',
                        color_continuous_scale=['#00FF00','#262730','#FF0000'],
                        color_continuous_midpoint=0,
                        hover_data={'name':True,'bias_label':True,'L3':True,'size_metric':False,'bias_clean':False},
                        title='<b>🎯 資金流向熱力圖 (IC.TPEX 官方分類版)</b>'
                    )
                    fig.update_layout(
                        margin=dict(t=30, l=10, r=10, b=10),
                        height=500,
                        font=dict(size=14),
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)'
                    )
                    fig.update_traces(
                        textinfo="label+text",
                        texttemplate="%{label}<br>%{customdata[1]}",
                        textposition="middle center"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    st.divider()

                    # 戰力排行榜
                    st.subheader("🏆 全產業戰力排行榜 (Sector Roster)")
                    st.info("💡 點擊下方官方產業板塊，展開查看「上中下游」兵力部署")

                    sector_stats = df_galaxy.groupby('L1')['bias'].mean().sort_values(ascending=False)
                    for sector, avg_bias in sector_stats.items():
                        sector_df = df_galaxy[df_galaxy['L1'] == sector]
                        if len(sector_df) == 0: continue
                        bulls = len(sector_df[sector_df['bias'] > 0])
                        flag  = "🔴" if avg_bias > 0 else "🟢"
                        header = f"{flag} **{sector}** (均 {avg_bias:+.1f}%) | 強勢 {bulls}/{len(sector_df)} 檔"
                        with st.expander(header):
                            l2_groups  = sector_df.groupby('L2')
                            sorted_l2  = sorted(l2_groups.groups.keys(),
                                                key=lambda x: 0 if '上' in str(x) else (1 if '中' in str(x) else 2))
                            for l2 in sorted_l2:
                                sub_df = l2_groups.get_group(l2).sort_values('bias', ascending=False)
                                st.markdown(f"**{l2}**")
                                for _, r in sub_df.iterrows():
                                    color = "red" if r['bias'] > 0 else "#26A69A"
                                    st.markdown(
                                        f"<span style='color:{color};font-weight:bold;'>{r.get('code','')} {r['name']}</span> "
                                        f"<span style='color:#aaa;font-size:0.9em;'>({r['bias_label']})</span>",
                                        unsafe_allow_html=True
                                    )
                                st.markdown("---")

    # ─────────────────────────────────────────────────────────────
    # 2.3 潛在風險雷達 (Risk Radar)
    # ─────────────────────────────────────────────────────────────
    with st.expander("2.3 ☠️ 潛在風險雷達 (Risk Radar)", expanded=False):
        if 'scan_results' in st.session_state and not st.session_state['scan_results'].empty:
            scan_results = st.session_state['scan_results']
            st.info("此區塊為「負面表列」清單，旨在警示符合特定風險條件的標的，提醒您「避開誰」。")

            risk1, risk2, risk3 = st.tabs([
                "☠️ 籌碼鬆動 (主力落跑)",
                "⚠️ 高溢價 (肉少湯喝)",
                "🧊 流動性陷阱 (殭屍債)"
            ])

            with risk1:
                if 'conv_rate' in scan_results.columns:
                    loose = scan_results[scan_results['conv_rate'] > 30].sort_values('conv_rate', ascending=False)
                    if not loose.empty:
                        st.warning(f"發現 {len(loose)} 檔標的「已轉換比例」> 30%，特定人可能已在下車。")
                        cols = [c for c in ['name','code','conv_rate','price'] if c in loose.columns]
                        st.dataframe(loose[cols].head(20), use_container_width=True)
                    else:
                        st.success("✅ 目前無標的觸發「籌碼鬆動」警示。")
                else:
                    st.warning("掃描結果無 conv_rate 欄位。")

            with risk2:
                if 'premium' in scan_results.columns:
                    overp = scan_results[scan_results['premium'] > 20].sort_values('premium', ascending=False)
                    if not overp.empty:
                        st.warning(f"發現 {len(overp)} 檔「溢價率」> 20%，潛在報酬空間受壓縮。")
                        cols = [c for c in ['name','code','premium','price','parity'] if c in overp.columns]
                        st.dataframe(overp[cols].head(20), use_container_width=True)
                    else:
                        st.success("✅ 目前無標的觸發「高溢價」警示。")
                else:
                    st.info("掃描結果無 premium 欄位，跳過此警示。")

            with risk3:
                if 'avg_volume' in scan_results.columns:
                    illiq = scan_results[scan_results['avg_volume'] < 10].sort_values('avg_volume')
                    if not illiq.empty:
                        st.error(f"發現 {len(illiq)} 檔平均成交量 < 10 張，存在嚴峻流動性風險！")
                        cols = [c for c in ['name','code','avg_volume','price'] if c in illiq.columns]
                        st.dataframe(illiq[cols].head(20), use_container_width=True)
                    else:
                        st.success("✅ 目前無標的觸發「流動性陷阱」警示。")
                else:
                    st.info("掃描結果無 avg_volume 欄位，跳過此警示。")
        else:
            st.info("請先執行本頁上方的掃描以啟動風險雷達。")

    # ─────────────────────────────────────────────────────────────
    # 2.4 資金配置試算 (Position Sizing)
    # ─────────────────────────────────────────────────────────────
    with st.expander("2.4 💰 資金配置試算 (Position Sizing)", expanded=False):
        if 'scan_results' in st.session_state and not st.session_state['scan_results'].empty:
            buys = st.session_state['scan_results']
            st.success(f"已同步獵殺結果：共 **{len(buys)}** 檔可配置標的")

            total_capital = st.number_input(
                "輸入您的總操作資金 (元)", min_value=100_000, value=2_000_000, step=100_000
            )

            if not buys.empty:
                st.subheader("建議投資組合 (Top 5，每檔 20%)")
                sort_col = 'score' if 'score' in buys.columns else 'price'
                top5 = buys.sort_values(sort_col, ascending=False).head(5)

                portfolio_lines = []
                for _, row in top5.iterrows():
                    cb_price = row.get('price', 0)
                    name     = row.get('name', '未知')
                    code     = row.get('code', '0000')
                    if cb_price > 0:
                        invest = total_capital * 0.20
                        mkt_per_unit = cb_price * 1000
                        num_lots = int(invest / mkt_per_unit)
                        portfolio_lines.append(
                            f"- **{name} ({code})** | 市價 `{cb_price}` | "
                            f"建議配置 `{num_lots}` 張 (約 {int(invest):,} 元)"
                        )
                st.markdown("\n".join(portfolio_lines))

                # 視覺化配置圓餅圖
                if portfolio_lines:
                    pie_data = pd.DataFrame({
                        '標的': [r.get('name','') for _, r in top5.iterrows()],
                        '配置': [20.0] * len(top5)
                    })
                    remaining = 100 - len(top5) * 20
                    if remaining > 0:
                        pie_data = pd.concat([
                            pie_data,
                            pd.DataFrame([{'標的': '現金', '配置': remaining}])
                        ], ignore_index=True)
                    fig = px.pie(pie_data, names='標的', values='配置',
                                 title='建議資金配置', hole=0.4)
                    fig.update_layout(template='plotly_dark',
                                      paper_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("請先執行本頁上方的掃描以獲取買進建議。")
