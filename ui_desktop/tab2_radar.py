# ui_desktop/tab2_radar.py
# Titan SOP V100 — 獵殺雷達
# ╔══════════════════════════════════════════════════════╗
# ║  GOD-TIER BUILD  —  Bloomberg × Palantir × Titan OS  ║
# ╚══════════════════════════════════════════════════════╝
# Design language identical to tab1_macro_cinematic.py
# Logic:  V82.0 fully preserved  (TitanStrategyEngine / Census / Kelly)
# UI:     4 Fire-Control Buttons · 6 Strategy Pills · Sniper Cards · Warning Cards

import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import yfinance as yf

from strategy import TitanStrategyEngine
from knowledge_base import TitanKnowledgeBase


# ══════════════════════════════════════════════════════════════════════════════
#  ENGINES  (unchanged from V82)
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_resource
def _load_engines():
    kb    = TitanKnowledgeBase()
    strat = TitanStrategyEngine()
    strat.kb = kb
    return strat, kb


@st.cache_data(ttl=600)
def _get_scan_result(_strat_id, df_json):
    strat, _ = _load_engines()
    df = pd.read_json(df_json)
    return strat.scan_entire_portfolio(df)


# ══════════════════════════════════════════════════════════════════════════════
#  CSS — shared vocabulary with tab1 for seamless OS feel
# ══════════════════════════════════════════════════════════════════════════════
def _inject_css():
    st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Rajdhani:wght@400;600;700&family=JetBrains+Mono:wght@300;400;600;700&display=swap" rel="stylesheet">
<style>
/* ══ CSS VARIABLES ══════════════════════════════════════════ */
:root {
    --c-gold:   #FFD700; --c-cyan:  #00F5FF;
    --c-red:    #FF3131; --c-green: #00FF7F;
    --c-orange: #FF9A3C;
    --f-display:'Bebas Neue',sans-serif;
    --f-body:   'Rajdhani',sans-serif;
    --f-mono:   'JetBrains Mono',monospace;
}

/* ══ FIRE CONTROL DECK (4 top buttons) ═══════════════════════ */
.t2-fire-card {
    height:110px; border-radius:16px;
    display:flex; flex-direction:column; align-items:center;
    justify-content:center; gap:6px;
    transition:all .24s cubic-bezier(.4,0,.2,1);
    position:relative; overflow:hidden;
}
.t2-fire-card::after {
    content:''; position:absolute; bottom:0; left:12%; right:12%; height:2px;
    background:var(--fa,#00F5FF); opacity:0; border-radius:2px;
    transition:opacity .24s ease;
}
.t2-fire-card.active::after { opacity:1; }
.t2-fire-card.active { transform:translateY(-3px); }
.t2-fire-icon  { font-size:30px; line-height:1; }
.t2-fire-label { font-family:var(--f-body);  font-size:14px; font-weight:700; color:#CDD; }
.t2-fire-tag   { font-family:var(--f-mono);  font-size:7.5px; color:#334; letter-spacing:2px; text-transform:uppercase; }
.t2-fire-card.active .t2-fire-label { color:var(--fa,#00F5FF); }

/* ══ STRATEGY PILL RAIL (6 sub-strategy pills inside 2.1) ═══ */
.t2-pill-rail {
    display:flex; gap:8px; flex-wrap:wrap;
    padding:13px 15px; margin-bottom:18px;
    background:rgba(0,0,0,0.20);
    border:1px solid rgba(255,255,255,0.052);
    border-radius:13px;
}
.t2-pill {
    font-family:var(--f-mono); font-size:11px; font-weight:700;
    color:rgba(150,168,195,0.48); letter-spacing:1.5px;
    padding:7px 16px; border-radius:30px;
    border:1px solid rgba(255,255,255,0.065);
    background:rgba(255,255,255,0.022);
    text-transform:uppercase; white-space:nowrap;
    transition:all .2s ease; cursor:pointer;
}
.t2-pill:hover { border-color:rgba(0,245,255,0.42); color:rgba(0,245,255,0.82); }
.t2-pill.active {
    border-color:rgba(255,215,0,0.55);
    background:rgba(255,215,0,0.07); color:#FFD700;
    box-shadow:0 0 12px rgba(255,215,0,0.12);
}

/* ══ SCANNER STATUS HUD (above result table) ═════════════════ */
.t2-hud-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:10px; margin-bottom:18px; }
.t2-hud-card {
    background:rgba(255,255,255,0.022);
    border:1px solid rgba(255,255,255,0.062);
    border-top:2px solid var(--hc,#00F5FF);
    border-radius:14px; padding:13px 14px 11px;
    position:relative; overflow:hidden;
}
.t2-hud-card::after {
    content:''; position:absolute; top:0; right:0;
    width:72px; height:72px;
    background:radial-gradient(circle at top right, var(--hc,#00F5FF), transparent 68%);
    opacity:0.04; pointer-events:none;
}
.t2-hud-lbl { font-family:var(--f-mono); font-size:8px; color:rgba(140,155,178,0.55); text-transform:uppercase; letter-spacing:2px; margin-bottom:8px; }
.t2-hud-val { font-family:var(--f-display); font-size:44px; color:#FFF; line-height:.95; margin-bottom:5px; letter-spacing:1px; }
.t2-hud-sub { font-family:var(--f-body); font-size:12px; color:var(--hc,#00F5FF); opacity:.85; font-weight:600; }

/* ══ RESULT TABLE ════════════════════════════════════════════ */
.t2-tbl { width:100%; border-collapse:collapse; font-family:var(--f-body); }
.t2-tbl th {
    font-family:var(--f-mono); font-size:8.5px; font-weight:700;
    letter-spacing:2px; text-transform:uppercase;
    color:rgba(0,245,255,0.62); background:rgba(0,245,255,0.04);
    padding:9px 12px; border-bottom:1px solid rgba(0,245,255,0.09);
}
.t2-tbl td { padding:8px 12px; border-bottom:1px solid rgba(255,255,255,0.028); color:rgba(210,222,238,0.82); font-size:14px; }
.t2-tbl tr:hover td { background:rgba(0,245,255,0.023); }

/* ══ SNIPER CHECKLIST CARDS (4 commandments) ═════════════════ */
.t2-rule-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:10px; margin-bottom:20px; }
.t2-rule-card {
    background:rgba(255,255,255,0.022); border:1px solid rgba(255,255,255,0.062);
    border-radius:14px; padding:16px 12px 13px; text-align:center;
    position:relative; overflow:hidden; transition:transform .18s ease;
}
.t2-rule-card:hover { transform:translateY(-2px); }
.t2-rule-card.pass { border-color:rgba(0,255,127,0.32); background:rgba(0,255,127,0.03); }
.t2-rule-card.fail { border-color:rgba(255,49,49,0.32);  background:rgba(255,49,49,0.03); }
.t2-rule-card.warn { border-color:rgba(255,215,0,0.30);  background:rgba(255,215,0,0.025); }
.t2-rule-icon  { font-size:28px; margin-bottom:9px; }
.t2-rule-title { font-family:var(--f-mono); font-size:8.5px; color:rgba(145,162,185,0.55); text-transform:uppercase; letter-spacing:1.5px; margin-bottom:7px; }
.t2-rule-val   { font-family:var(--f-display); font-size:24px; color:#FFF; margin-bottom:6px; }
.t2-rule-badge { font-family:var(--f-body); font-size:12px; font-weight:700; display:inline-block; padding:3px 10px; border-radius:20px; }
.pass .t2-rule-badge { background:rgba(0,255,127,0.14); color:#00FF7F; }
.fail .t2-rule-badge { background:rgba(255,49,49,0.14);  color:#FF6B6B; }
.warn .t2-rule-badge { background:rgba(255,215,0,0.12);  color:#FFD700; }

/* ══ WARNING CARDS (2.3 Risk red glow) ══════════════════════ */
.t2-warn-card {
    border:1px solid rgba(255,49,49,0.28);
    background:rgba(255,49,49,0.03);
    border-left:3px solid #FF3131;
    border-radius:14px; padding:14px 18px 12px;
    margin-bottom:10px;
    box-shadow:0 0 16px rgba(255,49,49,0.07);
    transition:transform .18s ease;
    position:relative;
}
.t2-warn-card:hover { transform:translateX(4px); }
.t2-warn-header { font-family:var(--f-body); font-size:16px; font-weight:700; color:#FF6B6B; margin-bottom:5px; }
.t2-warn-meta   { font-family:var(--f-mono); font-size:9.5px; color:#445566; letter-spacing:1px; }
.t2-warn-value  { font-family:var(--f-display); font-size:30px; color:#FF3131; position:absolute; right:18px; top:12px; }
.t2-warn-ok     { font-family:var(--f-mono); font-size:10px; color:#00FF7F; border:1px solid rgba(0,255,127,0.2); background:rgba(0,255,127,0.04); border-radius:9px; padding:10px 14px; letter-spacing:2px; text-align:center; text-transform:uppercase; }

/* ══ KELLY BIG NUMBER (2.4) ══════════════════════════════════ */
.t2-kelly-box {
    text-align:center; padding:28px 20px 22px;
    background:rgba(0,0,0,0.30); border:1px solid rgba(255,215,0,0.14);
    border-radius:20px; margin-bottom:18px; position:relative; overflow:hidden;
}
.t2-kelly-box::before {
    content:''; position:absolute; top:-40px; left:50%; transform:translateX(-50%);
    width:220px; height:220px; border-radius:50%;
    background:radial-gradient(circle,rgba(255,215,0,0.07) 0%,transparent 70%);
    pointer-events:none;
}
.t2-kelly-lbl { font-family:var(--f-mono); font-size:8.5px; color:rgba(255,215,0,0.38); letter-spacing:3px; text-transform:uppercase; margin-bottom:12px; }
.t2-kelly-num { font-family:var(--f-display); font-size:96px; color:#FFD700; line-height:1; text-shadow:0 0 38px rgba(255,215,0,0.32); letter-spacing:4px; }
.t2-kelly-pct { font-family:var(--f-display); font-size:38px; color:rgba(255,215,0,0.5); }
.t2-kelly-sub { font-family:var(--f-body); font-size:13px; color:#445566; margin-top:10px; }

/* ══ SHARED COMPONENTS ══════════════════════════════════════ */
.t2-sec-title {
    font-family:var(--f-display); font-size:22px; letter-spacing:2px;
    color:var(--c-cyan); text-shadow:0 0 16px rgba(0,245,255,0.22);
    margin-bottom:18px; padding-bottom:12px;
    border-bottom:1px solid rgba(255,255,255,0.052);
}
.t2-chart-wrap {
    background:rgba(0,0,0,0.32); border:1px solid rgba(255,255,255,0.055);
    border-radius:16px; padding:14px 8px 5px; margin:14px 0; overflow:hidden;
}
.t2-action div.stButton > button {
    background:rgba(0,245,255,0.05) !important;
    border:1px solid rgba(0,245,255,0.28) !important;
    color:rgba(0,245,255,0.85) !important;
    font-family:var(--f-mono) !important; font-size:11px !important;
    letter-spacing:2px !important; min-height:46px !important;
    border-radius:12px !important; text-transform:uppercase !important;
}
.t2-action div.stButton > button:hover {
    background:rgba(0,245,255,0.10) !important;
    box-shadow:0 0 20px rgba(0,245,255,0.2) !important;
}
.t2-content {
    background:linear-gradient(175deg,#06090e 0%,#090c14 100%);
    border:1px solid rgba(255,255,255,0.05);
    border-radius:20px; padding:24px 22px 30px; min-height:420px;
    position:relative;
}
.t2-content::after {
    content:''; position:absolute; bottom:0; left:8%; right:8%; height:1px;
    background:linear-gradient(90deg,transparent,rgba(0,245,255,0.10) 50%,transparent);
}
.t2-empty {
    border:1px dashed rgba(255,255,255,0.07); border-radius:16px;
    padding:58px 30px; text-align:center;
}
.t2-empty-icon { font-size:42px; opacity:.22; margin-bottom:14px; }
.t2-empty-text { font-family:var(--f-mono); font-size:11px; color:#2a3844; letter-spacing:2.5px; text-transform:uppercase; }
.t2-foot { font-family:var(--f-mono); font-size:9px; color:rgba(70,90,110,0.28); letter-spacing:2px; text-align:right; margin-top:18px; text-transform:uppercase; }
</style>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  HELPERS — math unchanged from V82
# ══════════════════════════════════════════════════════════════════════════════
def _safe_conv(row) -> float:
    raw = pd.to_numeric(row.get('conv_rate', 100), errors='coerce') or 100.0
    converted = (100.0 - raw) if raw > 50 else raw
    return max(0.0, converted)


# ── K-LINE CHART (dark theme wrapper) ────────────────────────────────────────
def _plot_candle_chart(cb_code: str):
    target_code = str(cb_code).strip()
    if len(target_code) == 5 and target_code.isdigit():
        target_code = target_code[:4]
    try:
        chart_df = yf.download(f"{target_code}.TW", period="2y", progress=False)
        if chart_df.empty:
            chart_df = yf.download(f"{target_code}.TWO", period="2y", progress=False)
        if chart_df.empty:
            st.error(f"❌ Yahoo Finance 查無 K 線資料: {target_code}"); return

        if isinstance(chart_df.columns, pd.MultiIndex):
            chart_df.columns = chart_df.columns.get_level_values(0)
        chart_df = chart_df.reset_index()
        chart_df['MA87']  = chart_df['Close'].rolling(87).mean()
        chart_df['MA284'] = chart_df['Close'].rolling(284).mean()

        base  = alt.Chart(chart_df).encode(
            x=alt.X('Date:T', axis=alt.Axis(format='%Y-%m', labelColor='#445566', titleColor='#334455', title=''))
        )
        color_cond = alt.condition("datum.Open <= datum.Close", alt.value("#FF4B4B"), alt.value("#26A69A"))
        candles = (
            base.mark_rule(color='#445566').encode(
                y=alt.Y('Low', title='股價', scale=alt.Scale(zero=False),
                        axis=alt.Axis(labelColor='#445566', titleColor='#334455')),
                y2='High')
            + base.mark_bar(size=3).encode(y='Open', y2='Close', color=color_cond,
                                           tooltip=['Date:T', 'Open:Q', 'Close:Q', 'High:Q', 'Low:Q'])
        )
        l87  = base.mark_line(color='#FFD700', strokeWidth=2).encode(y='MA87')
        l284 = base.mark_line(color='#00F5FF', strokeWidth=1.5, strokeDash=[4, 2]).encode(y='MA284')

        st.markdown('<div class="t2-chart-wrap">', unsafe_allow_html=True)
        st.altair_chart(
            (candles + l87 + l284).interactive()
            .configure_view(strokeOpacity=0, fill='rgba(0,0,0,0)')
            .configure_axis(gridColor='rgba(255,255,255,0.04)'),
            use_container_width=True
        )
        st.markdown('</div>', unsafe_allow_html=True)
        st.caption(f"📈 {target_code}  ·  🟡 87MA  ·  🔵 284MA")
    except Exception as e:
        st.warning(f"K 線圖生成失敗: {e}")


# ── TPEX TREEMAP DATA (chain map unchanged) ───────────────────────────────────
@st.cache_data(ttl=3600)
def _get_tpex_data(df_json: str) -> pd.DataFrame:
    full_data = pd.read_json(df_json)
    chain_map = {
        '世芯':('半導體','⬆️上游-IC設計','IP/ASIC'),'創意':('半導體','⬆️上游-IC設計','IP/ASIC'),
        '聯發科':('半導體','⬆️上游-IC設計','手機SoC'),'瑞昱':('半導體','⬆️上游-IC設計','網通IC'),
        '台積':('半導體','↔️中游-製造','晶圓代工'),'聯電':('半導體','↔️中游-製造','晶圓代工'),
        '弘塑':('半導體','↔️中游-設備','濕製程'),'辛耘':('半導體','↔️中游-設備','CoWoS'),
        '萬潤':('半導體','↔️中游-設備','封測設備'),'日月光':('半導體','⬇️下游-封測','封裝'),
        '智邦':('通信網路','⬇️下游-網通設備','交換器'),'啟碁':('通信網路','⬇️下游-網通設備','衛星/車用'),
        '中磊':('通信網路','⬇️下游-網通設備','寬頻'),'全新':('通信網路','⬆️上游-元件','PA砷化鎵'),
        '穩懋':('通信網路','⬆️上游-元件','PA代工'),'華星光':('通信網路','↔️中游-光通訊','CPO模組'),
        '波若威':('通信網路','↔️中游-光通訊','光纖元件'),'聯亞':('通信網路','↔️中游-光通訊','雷射二極體'),
        '廣達':('電腦週邊','⬇️下游-組裝','AI伺服器'),'緯創':('電腦週邊','⬇️下游-組裝','AI伺服器'),
        '技嘉':('電腦週邊','⬇️下游-品牌','板卡/Server'),'微星':('電腦週邊','⬇️下游-品牌','電競'),
        '奇鋐':('電腦週邊','↔️中游-散熱','3D VC'),'雙鴻':('電腦週邊','↔️中游-散熱','水冷板'),
        '勤誠':('電腦週邊','↔️中游-機殼','伺服器機殼'),'川湖':('電腦週邊','↔️中游-機構','導軌'),
        '樺漢':('電腦週邊','⬇️下游-工業電腦','IPC'),'研華':('電腦週邊','⬇️下游-工業電腦','IPC'),
        '台光電':('電子零組件','⬆️上游-材料','CCL銅箔基板'),'台燿':('電子零組件','⬆️上游-材料','CCL高頻'),
        '金像電':('電子零組件','↔️中游-PCB','伺服器板'),'健鼎':('電子零組件','↔️中游-PCB','HDI'),
        '欣興':('電子零組件','↔️中游-PCB','ABF載板'),'南電':('電子零組件','↔️中游-PCB','ABF載板'),
        '國巨':('電子零組件','↔️中游-被動元件','MLCC'),'華新科':('電子零組件','↔️中游-被動元件','MLCC'),
        '凡甲':('電子零組件','↔️中游-連接器','車用/Server'),'嘉澤':('電子零組件','↔️中游-連接器','CPU Socket'),
        '大立光':('光電','⬆️上游-光學','鏡頭'),'玉晶光':('光電','⬆️上游-光學','鏡頭'),
        '亞光':('光電','⬆️上游-光學','車載鏡頭'),'群創':('光電','↔️中游-面板','LCD'),
        '友達':('光電','↔️中游-面板','LCD'),'中光電':('光電','⬇️下游-背光','背光模組'),
        '藥華藥':('生技醫療','⬆️上游-新藥','新藥研發'),'合一':('生技醫療','⬆️上游-新藥','新藥研發'),
        '保瑞':('生技醫療','↔️中游-製造','CDMO'),'美時':('生技醫療','↔️中游-製造','學名藥'),
        '晶碩':('生技醫療','⬇️下游-醫材','隱形眼鏡'),'視陽':('生技醫療','⬇️下游-醫材','隱形眼鏡'),
        '上銀':('電機機械','⬆️上游-傳動','滾珠螺桿'),'亞德客':('電機機械','⬆️上游-氣動','氣動元件'),
        '東元':('電機機械','↔️中游-馬達','工業馬達'),
        '華固':('建材營造','⬇️下游-建設','住宅商辦'),'長虹':('建材營造','⬇️下游-建設','住宅商辦'),
        '興富發':('建材營造','⬇️下游-建設','住宅'),'遠雄':('建材營造','⬇️下游-建設','廠辦'),
        '長榮':('航運業','↔️中游-海運','貨櫃'),'陽明':('航運業','↔️中游-海運','貨櫃'),
        '萬海':('航運業','↔️中游-海運','貨櫃'),'長榮航':('航運業','↔️中游-空運','航空'),
        '華航':('航運業','↔️中游-空運','航空'),'星宇':('航運業','↔️中游-空運','航空'),
        '華城':('綠能環保','↔️中游-重電','變壓器'),'士電':('綠能環保','↔️中游-重電','配電盤'),
        '中興電':('綠能環保','↔️中游-重電','GIS開關'),'亞力':('綠能環保','↔️中游-重電','輸配電'),
        '世紀鋼':('綠能環保','⬆️上游-風電','水下基礎'),'森崴':('綠能環保','⬇️下游-能源','綠電開發'),
        '東陽':('汽車工業','↔️中游-零組件','AM保險桿'),'帝寶':('汽車工業','↔️中游-零組件','AM車燈'),
        '裕隆':('汽車工業','⬇️下游-整車','品牌製造'),'和泰車':('汽車工業','⬇️下游-代理','TOYOTA'),
    }

    def classify(name):
        for k, v in chain_map.items():
            if k in name: return v
        if any(x in name for x in ['電','科','矽','晶','半']):
            return ('光電','一般光電','光電') if '光' in name else ('半導體','其他半導體','半導體')
        for kws, cat in [(['網','通','訊'],('通信網路','網通設備','通信')),
                         (['腦','機','資'],('電腦週邊','系統','電腦')),
                         (['板','線','器','零'],('電子零組件','被動/連接','零組件')),
                         (['生','醫','藥'],('生技醫療','生技','醫療')),
                         (['綠','能','源'],('綠能環保','能源','綠能')),
                         (['航','運','船'],('航運業','運輸','航運')),
                         (['營','建','地'],('建材營造','建設','營造')),
                         (['金','銀','保'],('金融業','金融','金控')),
                         (['車','汽'],('汽車工業','零組件','汽車'))]:
            if any(x in name for x in kws): return cat
        return ('其他','未分類','其他')

    d = full_data.copy()
    d[['L1','L2','L3']] = d['name'].apply(lambda x: pd.Series(classify(x)))
    d['ma87']       = pd.to_numeric(d.get('ma87', pd.Series(dtype=float)), errors='coerce')
    d['price']      = pd.to_numeric(d.get('stock_price_real', pd.Series(dtype=float)), errors='coerce')
    d['bias']       = (d['price'] - d['ma87']) / d['ma87'] * 100
    d['bias_clean'] = d['bias'].fillna(0).clip(-25, 25)
    d['bias_label'] = d['bias'].apply(lambda x: f"{x:+.1f}%" if pd.notnull(x) else "N/A")
    d['size_metric']= d['price'].fillna(10)
    return d


# ══════════════════════════════════════════════════════════════════════════════
#  CENSUS ENGINE  (V82 — fully unchanged)
# ══════════════════════════════════════════════════════════════════════════════
def _run_census(df: pd.DataFrame, min_score: int) -> tuple:
    strat, _ = _load_engines()
    work_df  = df.copy()
    rename_map = {
        '代號':'code','名稱':'name','可轉債市價':'price',
        '轉換價格':'conv_price','轉換標的':'stock_code',
        '已轉換比例':'conv_rate','轉換價值':'conv_value',
        '發行日':'issue_date','賣回日':'put_date','餘額比例':'balance_ratio'
    }
    work_df.rename(columns=lambda c: rename_map.get(c.strip(), c.strip()), inplace=True)
    if 'balance_ratio' in work_df.columns:
        bal = pd.to_numeric(work_df['balance_ratio'], errors='coerce').fillna(100.0)
        work_df['conv_rate'] = 100.0 - bal
    for col in ['price','conv_rate','conv_price','conv_value']:
        work_df[col] = pd.to_numeric(work_df.get(col, pd.Series(dtype=float)), errors='coerce').fillna(0.0)
    for dcol in ['issue_date','put_date','list_date']:
        if dcol in work_df.columns:
            work_df[dcol] = pd.to_datetime(work_df[dcol], errors='coerce')
    if 'issue_date' not in work_df.columns and 'list_date' in work_df.columns:
        work_df['issue_date'] = work_df['list_date']

    try:
        scan_df = strat.scan_entire_portfolio(work_df)
        records = scan_df.to_dict('records')
    except Exception as e:
        st.error(f"策略掃描失敗: {e}"); return pd.DataFrame(), pd.DataFrame()

    total = len(records)
    pbar  = st.progress(0)
    stxt  = st.empty()
    enriched = []

    for i, row in enumerate(records):
        stxt.text(f"普查進行中 ({i+1}/{total}): {row.get('name','')}…")
        code = str(row.get('stock_code','')).strip()
        row.update({'stock_price_real':0.0,'ma87':0.0,'ma284':0.0,
                    'trend_status':'⚠️ 資料不足','cb_price':row.get('price',0.0),
                    'conv_price_val':row.get('conv_price',0.0),
                    'conv_value_val':row.get('conv_value',0.0)})
        if code:
            try:
                hist = yf.Ticker(f"{code}.TW").history(period="2y")
                if hist.empty: hist = yf.Ticker(f"{code}.TWO").history(period="2y")
                if not hist.empty and len(hist) > 284:
                    curr  = float(hist['Close'].iloc[-1])
                    ma87  = float(hist['Close'].rolling(87).mean().iloc[-1])
                    ma284 = float(hist['Close'].rolling(284).mean().iloc[-1])
                    row.update({'stock_price_real':curr,'ma87':ma87,'ma284':ma284})
                    if ma87 > ma284:
                        row['trend_status'] = '✅ 中期多頭'
                        row['score']        = min(100, row.get('score',0) + 20)
                    else:
                        row['trend_status'] = '整理/空頭'
            except Exception: pass
        enriched.append(row)
        pbar.progress((i+1)/total)

    stxt.text("✅ 普查完成！")
    full_df = pd.DataFrame(enriched)
    for col in ['price','conv_rate']:
        if col not in full_df.columns: full_df[col] = 0.0

    sop_mask = (
        (full_df['price'] < 120) &
        (full_df['trend_status'].str.contains('多頭', na=False)) &
        (full_df['conv_rate'] < 30)
    )
    sop_df = full_df[sop_mask].sort_values('score', ascending=False)
    if 'score' in sop_df.columns:
        sop_df = sop_df[sop_df['score'] >= min_score]
    return sop_df, full_df


# ══════════════════════════════════════════════════════════════════════════════
#  REUSABLE PRIMITIVES
# ══════════════════════════════════════════════════════════════════════════════

def _scanner_hud(total: int, sop: int, bull: int, avg_score: float):
    st.markdown(f"""
<div class="t2-hud-grid">
  <div class="t2-hud-card" style="--hc:#00F5FF">
    <div class="t2-hud-lbl">Total Scanned</div>
    <div class="t2-hud-val">{total}</div>
    <div class="t2-hud-sub">CB 標的數量</div>
  </div>
  <div class="t2-hud-card" style="--hc:#00FF7F">
    <div class="t2-hud-lbl">SOP Targets Found</div>
    <div class="t2-hud-val">{sop}</div>
    <div class="t2-hud-sub">通過黃金標準</div>
  </div>
  <div class="t2-hud-card" style="--hc:#FF9A3C">
    <div class="t2-hud-lbl">Bull Trend</div>
    <div class="t2-hud-val">{bull}</div>
    <div class="t2-hud-sub">87MA &gt; 284MA</div>
  </div>
  <div class="t2-hud-card" style="--hc:#FFD700">
    <div class="t2-hud-lbl">Avg Score</div>
    <div class="t2-hud-val">{avg_score:.0f}</div>
    <div class="t2-hud-sub">SOP 平均評分</div>
  </div>
</div>""", unsafe_allow_html=True)


def _rule_card(icon: str, title: str, value: str, badge: str, state: str) -> str:
    """state = 'pass' | 'fail' | 'warn'"""
    return (
        f'<div class="t2-rule-card {state}">'
        f'<div class="t2-rule-icon">{icon}</div>'
        f'<div class="t2-rule-title">{title}</div>'
        f'<div class="t2-rule-val">{value}</div>'
        f'<div class="t2-rule-badge">{badge}</div>'
        f'</div>'
    )


def _four_commandments(row):
    """Render the 4 Sniper Checklist Cards for a given CB row."""
    price    = pd.to_numeric(row.get('price'),  errors='coerce') or 0.0
    ma87     = pd.to_numeric(row.get('ma87'),   errors='coerce') or 0.0
    ma284    = pd.to_numeric(row.get('ma284'),  errors='coerce') or 0.0
    conv_pct = _safe_conv(row)
    score    = pd.to_numeric(row.get('score'),  errors='coerce') or 0
    is_bull  = ma87 > ma284

    cards = "".join([
        _rule_card(
            "✅" if price < 120 else "❌",
            "1. 價格天條",
            f"{price:.1f}",
            "PASS &lt;120" if price < 120 else "FAIL ≥120",
            "pass" if price < 120 else "fail"
        ),
        _rule_card(
            "✅" if is_bull else "⚠️",
            "2. 中期多頭",
            "87MA >" if is_bull else "87MA <",
            "BULLISH" if is_bull else "BEARISH",
            "pass" if is_bull else "warn"
        ),
        _rule_card(
            "✅" if conv_pct < 30 else "❌",
            "3. 已轉換率",
            f"{conv_pct:.1f}%",
            "CLEAN" if conv_pct < 30 else "HEAVY",
            "pass" if conv_pct < 30 else "fail"
        ),
        _rule_card(
            "✅" if score >= 60 else "⚠️",
            "4. 策略評分",
            f"{int(score)}",
            "ELITE ≥60" if score >= 60 else "WATCH",
            "pass" if score >= 60 else "warn"
        ),
    ])
    st.markdown(f'<div class="t2-rule-grid">{cards}</div>', unsafe_allow_html=True)


def _cb_card(row, badge="👑", report_title="📄 查看詳細分析報告"):
    """Full CB detail expander with checklist cards, metrics, K-line."""
    cb_code  = str(row.get('code', row.get('stock_code','0000'))).strip()
    cb_name  = row.get('name','未知')
    price    = pd.to_numeric(row.get('price'),  errors='coerce') or 0.0
    ma87     = pd.to_numeric(row.get('ma87'),   errors='coerce') or 0.0
    ma284    = pd.to_numeric(row.get('ma284'),  errors='coerce') or 0.0
    score    = pd.to_numeric(row.get('score'),  errors='coerce') or 0
    conv_pct = _safe_conv(row)
    is_bull  = ma87 > ma284

    title = f"{badge} {cb_name} ({cb_code})  ·  CB {price:.1f}  ·  Score {int(score)}"
    with st.expander(title):
        _four_commandments(row)

        with st.expander(report_title, expanded=False):
            st.markdown(f"## 📊 {cb_name} ({cb_code})")
            st.info("### 1. 核心策略檢核 (The 4 Commandments)")
            st.markdown(f"1. 價格天條 (<115): {'✅ 通過' if price < 115 else '⚠️ 警戒'} (目前 **{price:.1f}**)")
            st.markdown(f"2. 中期多頭排列: {'✅ 通過' if is_bull else '⚠️ 整理中'}")
            if ma87 > 0:
                st.markdown(f"> 87MA **{ma87:.2f}** {' > ' if is_bull else ' < '} 284MA **{ma284:.2f}**")
            st.markdown("3. 身分認證: ☐ 領頭羊 / ☐ 風口豬")
            st.markdown("4. 發債故事: ☐ 從無到有 / ☐ 擴產 / ☐ 政策事件")

            st.success("### 2. 決策輔助")
            cp  = pd.to_numeric(row.get('conv_price_val', 0.01), errors='coerce')
            sp  = pd.to_numeric(row.get('stock_price_real', 0.0), errors='coerce')
            cv  = pd.to_numeric(row.get('conv_value_val', 0.0), errors='coerce')
            par = (sp / cp * 100) if cp > 0 else 0.0
            prm = ((price - cv) / cv * 100) if cv > 0 else 0.0
            c1, c2, c3 = st.columns(3)
            c1.metric("理論價 (Parity)", f"{par:.2f}")
            c2.metric("溢價率 (Premium)", f"{prm:.2f}%")
            c3.metric("已轉換比例", f"{conv_pct:.2f}%")

            st.markdown("### 4. 交易計畫")
            st.warning("🕒 09:00 開盤後30分鐘 · 13:25 收盤前25分鐘")
            st.markdown(
                "* 🎯 佈局: 105~115 區間  "
                "· 🚀 加碼: 帶量突破87MA  "
                "· 🛑 停損: 跌破100元  "
                "· 💰 停利: 152元以上"
            )
            st.divider()
            _plot_candle_chart(cb_code)


def _styled_table(df: pd.DataFrame, cols: list):
    """Render a dark-themed HTML table from a DataFrame subset."""
    tbl = df[cols].to_html(escape=False, index=False)
    tbl = tbl.replace('<table', '<table class="t2-tbl"')
    st.markdown(tbl, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 2.1  —  AUTO SCAN  (Strategy Matrix)
# ══════════════════════════════════════════════════════════════════════════════
def render_2_1(df: pd.DataFrame):
    st.markdown('<div class="t2-sec-title">📡 2.1 自動獵殺推薦 — Strategy Matrix</div>',
                unsafe_allow_html=True)

    if df.empty:
        st.markdown('<div class="t2-empty"><div class="t2-empty-icon">📂</div>'
                    '<div class="t2-empty-text">Upload CB List to Activate Census</div></div>',
                    unsafe_allow_html=True)
        return

    # ── Scan control ──────────────────────────────────────────────────────────
    ctrl_l, ctrl_r = st.columns([3, 1])
    with ctrl_l:
        min_score = st.slider("最低評分門檻", 0, 100, 50, key="t21_minscore")
    with ctrl_r:
        st.markdown('<div class="t2-action" style="margin-top:24px;">', unsafe_allow_html=True)
        if st.button("🚀  LAUNCH CENSUS", key="btn_census"):
            with st.spinner("執行全市場雙軌普查 (.TW / .TWO)…"):
                sop_df, full_df = _run_census(df, min_score)
                st.session_state['t2_scan']  = sop_df
                st.session_state['t2_full']  = full_df.to_dict('records')
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Scanner HUD ───────────────────────────────────────────────────────────
    full_data = pd.DataFrame(st.session_state.get('t2_full', []))
    sop_df    = st.session_state.get('t2_scan', pd.DataFrame())

    if not full_data.empty:
        bull_n  = len(full_data[full_data.get('trend_status', pd.Series('', index=full_data.index)).str.contains('多頭', na=False)]) if 'trend_status' in full_data.columns else 0
        avg_sc  = float(sop_df['score'].mean()) if (not sop_df.empty and 'score' in sop_df.columns) else 0.0
        _scanner_hud(len(full_data), len(sop_df), bull_n, avg_sc)
        for dcol in ['issue_date','put_date']:
            if dcol in full_data.columns:
                full_data[dcol] = pd.to_datetime(full_data[dcol], errors='coerce')
    else:
        st.markdown(
            '<div style="font-family:var(--f-mono);font-size:11px;color:#2a3a4a;'
            'letter-spacing:1.5px;padding:10px 2px;text-transform:uppercase;">'
            '↑  Click LAUNCH CENSUS to populate scanner HUD</div>',
            unsafe_allow_html=True
        )

    # ── Strategy Pill Rail ────────────────────────────────────────────────────
    PILLS = [
        ("global",    "🌍", "全市場"),
        ("sop",       "🏆", "SOP菁英"),
        ("honeymoon", "👶", "新債蜜月"),
        ("sediment",  "⚓", "滿年沈澱"),
        ("put",       "🛡️", "賣回保衛"),
        ("sector",    "🌪️", "產業風口"),
    ]
    if 't21_pill' not in st.session_state:
        st.session_state.t21_pill = "global"
    active_pill = st.session_state.t21_pill

    # Build pill buttons inside columns (visible pill cosmetics via markdown offset)
    btn_cols = st.columns(len(PILLS))
    pill_mds = []
    for col, (key, icon, label) in zip(btn_cols, PILLS):
        is_a   = (key == active_pill)
        brd    = "1.5px solid rgba(255,215,0,0.55)" if is_a else "1px solid rgba(255,255,255,0.065)"
        bg_c   = "rgba(255,215,0,0.07)" if is_a else "rgba(255,255,255,0.022)"
        txt_c  = "#FFD700" if is_a else "rgba(148,168,196,0.48)"
        shd    = "0 0 12px rgba(255,215,0,0.12)" if is_a else "none"
        pill_mds.append(
            f'<div style="background:{bg_c};border:{brd};border-radius:30px;'
            f'text-align:center;padding:7px 2px;font-family:JetBrains Mono,monospace;'
            f'font-size:11px;letter-spacing:1.5px;color:{txt_c};box-shadow:{shd};'
            f'text-transform:uppercase;margin-bottom:-54px;pointer-events:none;'
            f'position:relative;z-index:0;">'
            f'{icon} {label}</div>'
        )
        with col:
            st.markdown(pill_mds[-1], unsafe_allow_html=True)
            if st.button(f"{icon} {label}", key=f"pill_{key}", use_container_width=True):
                st.session_state.t21_pill = key
                st.rerun()

    st.markdown('<div style="height:6px"></div>', unsafe_allow_html=True)

    if full_data.empty:
        return

    now  = datetime.now()
    pill = st.session_state.t21_pill

    # ──────────────────────────────────────────────────────────────────────────
    # 🌍 全市場 — Full results table
    # ──────────────────────────────────────────────────────────────────────────
    if pill == "global":
        if not sop_df.empty:
            st.markdown(
                f'<div style="font-family:var(--f-mono);font-size:10px;color:#00FF7F;'
                f'letter-spacing:1.5px;margin:12px 0 10px;text-transform:uppercase;">'
                f'✅  {len(sop_df)} 檔通過 SOP 黃金標準</div>',
                unsafe_allow_html=True
            )
            disp_cols = [c for c in ['code','name','price','stock_price_real','trend_status','conv_rate','score'] if c in sop_df.columns]
            _styled_table(sop_df.head(30), disp_cols)
        else:
            st.info("執行普查後，全市場 SOP 標的將顯示於此。")

    # ──────────────────────────────────────────────────────────────────────────
    # 🏆 SOP菁英
    # ──────────────────────────────────────────────────────────────────────────
    elif pill == "sop":
        df_t = sop_df.head(20) if not sop_df.empty else pd.DataFrame()
        if df_t.empty and not full_data.empty:
            mask = (full_data.get('price', pd.Series(0)) < 120) & \
                   (full_data.get('trend_status', pd.Series('')).str.contains('多頭', na=False))
            df_t = full_data[mask].sort_values('score', ascending=False).head(20) if 'score' in full_data.columns else full_data[mask].head(20)
        if df_t.empty:
            st.info("無符合 SOP 黃金標準的標的。")
        else:
            st.caption(f"共 {len(df_t)} 檔通過 SOP 黃金標準")
            for _, row in df_t.iterrows():
                _cb_card(row, badge="👑")

    # ──────────────────────────────────────────────────────────────────────────
    # 👶 新債蜜月
    # ──────────────────────────────────────────────────────────────────────────
    elif pill == "honeymoon":
        if 'issue_date' not in full_data.columns:
            st.warning("普查資料無 issue_date 欄位。"); return
        mask = (
            full_data['issue_date'].notna() &
            ((now - full_data['issue_date']).dt.days < 90) &
            (full_data.get('price', pd.Series(999)) < 130) &
            (full_data.get('conv_rate', pd.Series(100)) < 30)
        )
        df_t = full_data[mask].sort_values('issue_date', ascending=False)
        if df_t.empty:
            st.info("目前無符合「新券蜜月」標準 (上市<90天 · 價格<130 · 轉換率<30%)。")
        else:
            st.caption(f"共 {len(df_t)} 檔蜜月期新券")
            for _, row in df_t.iterrows():
                days = int((now - row['issue_date']).days)
                price = pd.to_numeric(row.get('price'), errors='coerce') or 0.0
                name  = row.get('name','未知'); code = str(row.get('code','')).strip()
                ma87  = pd.to_numeric(row.get('ma87'),  errors='coerce') or 0.0
                ma284 = pd.to_numeric(row.get('ma284'), errors='coerce') or 0.0
                c_pct = _safe_conv(row)

                with st.expander(f"👶 {name} ({code})  ·  上市 {days} 天  ·  CB {price:.1f}"):
                    _four_commandments(row)
                    with st.expander("📄 蜜月期深度分析", expanded=False):
                        is_bull = ma87 > ma284
                        st.info("### 1. 核心策略檢核")
                        st.markdown(f"1. 蜜月期價格: {'✅ 通過' if price < 115 else '⚠️ 監控'} (新券甜蜜區 105-115，目前 **{price:.1f}**)")
                        st.markdown(f"2. 中期多頭: {'✅' if is_bull else '⚠️ 偏弱'}")
                        if ma87 > 0: st.markdown(f"> 87MA {ma87:.2f} {' > ' if is_bull else ' < '} 284MA {ma284:.2f}")
                        st.markdown("3. 身分認證: ☐ 領頭羊 / ☐ 風口豬")
                        st.markdown("4. 發債故事: ☐ 從無到有 / ☐ 擴產 / ☐ 政策事件")
                        cp = pd.to_numeric(row.get('conv_price_val',0.01), errors='coerce')
                        sp = pd.to_numeric(row.get('stock_price_real',0.0), errors='coerce')
                        cv = pd.to_numeric(row.get('conv_value_val',0.0), errors='coerce')
                        par = (sp/cp*100) if cp > 0 else 0.0
                        prm = ((price-cv)/cv*100) if cv > 0 else 0.0
                        c1,c2,c3 = st.columns(3)
                        c1.metric("理論價", f"{par:.2f}")
                        c2.metric("溢價率", f"{prm:.2f}%")
                        c3.metric("已轉換", f"{c_pct:.2f}%")
                        st.markdown("* 🎯 新券上市初期若 ≤110 為極佳安全邊際  · 🛑 停損: 跌破100  · 💰 停利: 152+")
                        st.divider()
                        _plot_candle_chart(code)

    # ──────────────────────────────────────────────────────────────────────────
    # ⚓ 滿年沈澱
    # ──────────────────────────────────────────────────────────────────────────
    elif pill == "sediment":
        if 'issue_date' not in full_data.columns:
            st.warning("普查資料無 issue_date 欄位。"); return
        fd = full_data.copy().dropna(subset=['issue_date'])
        fd['days_old'] = (now - fd['issue_date']).dt.days

        def _mask_s(r):
            try:
                if not (350 <= r['days_old'] <= 420): return False
                p = pd.to_numeric(r.get('price'), errors='coerce') or 0.0
                return 0 < p < 115 and _safe_conv(r) < 30
            except: return False

        df_t = fd[fd.apply(_mask_s, axis=1)].sort_values('days_old')
        if df_t.empty:
            st.info("目前無符合「滿年沈澱」標準 (上市滿一年 · 價格<115 · 轉換率<30%)。")
        else:
            st.caption(f"共 {len(df_t)} 檔滿年沈澱標的")
            for _, row in df_t.iterrows():
                days  = int(row['days_old'])
                price = pd.to_numeric(row.get('price'), errors='coerce') or 0.0
                ma87  = pd.to_numeric(row.get('ma87'),  errors='coerce') or 0.0
                sp    = pd.to_numeric(row.get('stock_price_real'), errors='coerce') or 0.0
                c_pct = _safe_conv(row)
                name  = row.get('name','未知'); code = str(row.get('code','')).strip()
                above = sp > ma87 if ma87 > 0 else False

                with st.expander(f"⚓ {name} ({code})  ·  沈澱 {days} 天  ·  CB {price:.1f}"):
                    _four_commandments(row)
                    with st.expander("📄 滿年沈澱深度分析", expanded=False):
                        st.info("### 1. 核心策略檢核")
                        st.markdown(f"1. 價格天條 (<115): ✅ 通過 (目前 **{price:.1f}**)")
                        st.markdown(f"2. {'✅ 站上87MA' if above else '⚠️ 均線整理中'}")
                        if ma87 > 0: st.markdown(f"> 現價 {sp:.2f} {' > ' if above else ' < '} 87MA {ma87:.2f}")
                        st.markdown("3. 身分認證: ☐ 領頭羊 / ☐ 風口豬")
                        st.markdown("4. 發債故事: ☐ 從無到有 / ☐ 擴產")
                        cp = pd.to_numeric(row.get('conv_price_val',0.01), errors='coerce')
                        cv = pd.to_numeric(row.get('conv_value_val',0.0),  errors='coerce')
                        par = (sp/cp*100) if cp > 0 else 0.0
                        prm = ((price-cv)/cv*100) if cv > 0 else 0.0
                        c1,c2,c3 = st.columns(3)
                        c1.metric("理論價", f"{par:.2f}")
                        c2.metric("溢價率", f"{prm:.2f}%")
                        c3.metric("已轉換", f"{c_pct:.2f}%")
                        st.markdown("* 🎯 站穩87MA即為首波進場點  · 87MA由平轉揚時加碼  · 🛑 停損: 100  · 💰 停利: 152+")
                        st.divider()
                        _plot_candle_chart(code)

    # ──────────────────────────────────────────────────────────────────────────
    # 🛡️ 賣回保衛
    # ──────────────────────────────────────────────────────────────────────────
    elif pill == "put":
        if 'put_date' not in full_data.columns:
            st.warning("普查資料無 put_date 欄位。"); return
        fd = full_data.copy()
        fd['days_to_put'] = (fd['put_date'] - now).dt.days

        def _mask_p(r):
            try:
                dtp = r['days_to_put']
                if pd.isna(dtp) or not (0 < dtp < 180): return False
                p = pd.to_numeric(r.get('price'), errors='coerce') or 0.0
                return 95 <= p <= 105 and _safe_conv(r) < 30
            except: return False

        df_t = fd[fd.apply(_mask_p, axis=1)].sort_values('days_to_put')
        if df_t.empty:
            st.info("目前無符合「賣回保衛」標準 (距賣回<180天 · 價格 95~105 · 轉換率<30%)。")
        else:
            st.caption(f"共 {len(df_t)} 檔賣回套利機會")
            for _, row in df_t.iterrows():
                left  = int(row['days_to_put'])
                price = pd.to_numeric(row.get('price'), errors='coerce') or 0.0
                pd_s  = row['put_date'].strftime('%Y-%m-%d') if pd.notnull(row['put_date']) else 'N/A'
                c_pct = _safe_conv(row)
                name  = row.get('name','未知'); code = str(row.get('code','')).strip()
                ma87  = pd.to_numeric(row.get('ma87'),  errors='coerce') or 0.0
                ma284 = pd.to_numeric(row.get('ma284'), errors='coerce') or 0.0

                with st.expander(f"🛡️ {name} ({code})  ·  賣回倒數 {left} 天  ·  CB {price:.1f}"):
                    _four_commandments(row)
                    with st.expander("📄 賣回保衛戰術報告", expanded=False):
                        is_bull = ma87 > ma284
                        st.error("### 1. 核心策略檢核")
                        st.markdown(f"1. 甜甜圈區間 (95~105): ✅ 通過 (目前 **{price:.1f}**)")
                        st.markdown(f"2. 中期多頭: {'✅ 通過' if is_bull else '⚠️ 整理中'}")
                        st.markdown("3. 身分認證: ☐ 領頭羊 / ☐ 風口豬")
                        st.markdown("4. 發債故事: ☐ 從無到有 / ☐ 擴產")
                        sp = pd.to_numeric(row.get('stock_price_real',0.0), errors='coerce')
                        cp = pd.to_numeric(row.get('conv_price_val',0.01), errors='coerce')
                        cv = pd.to_numeric(row.get('conv_value_val',0.0), errors='coerce')
                        par = (sp/cp*100) if cp > 0 else 0.0
                        prm = ((price-cv)/cv*100) if cv > 0 else 0.0
                        c1,c2,c3 = st.columns(3)
                        c1.metric("距離賣回", f"{left} 天")
                        c2.metric("溢價率", f"{prm:.2f}%")
                        c3.metric("賣回日", pd_s)
                        st.markdown(f"* 🎯 {pd_s} 前買入，下檔風險極低  · 🛑 原則上不停損  · 💰 停利: 152+")
                        st.divider()
                        _plot_candle_chart(code)

    # ──────────────────────────────────────────────────────────────────────────
    # 🌪️ 產業風口地圖
    # ──────────────────────────────────────────────────────────────────────────
    elif pill == "sector":
        if 't2_full' not in st.session_state:
            st.warning("請先執行普查。"); return
        full_json = pd.DataFrame(st.session_state['t2_full']).to_json()
        df_gal    = _get_tpex_data(full_json)
        if df_gal.empty:
            st.info("無資料，請先執行普查。"); return

        fig = px.treemap(
            df_gal, path=['L1','L2','L3','name'], values='size_metric',
            color='bias_clean',
            color_continuous_scale=['#00FF00','#0e1117','#FF0000'],
            color_continuous_midpoint=0,
            hover_data={'name':True,'bias_label':True,'L3':True,'size_metric':False,'bias_clean':False},
            title='<b>🎯 IC.TPEX 官方分類 — 資金流向熱力圖</b>'
        )
        fig.update_layout(
            margin=dict(t=34,l=8,r=8,b=8), height=500,
            font=dict(size=13,family='Rajdhani'),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            title_font_color='#FFD700', title_font_size=14
        )
        fig.update_traces(
            textinfo="label+text",
            texttemplate="%{label}<br>%{customdata[1]}",
            textposition="middle center"
        )
        st.markdown('<div class="t2-chart-wrap">', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.divider()

        st.markdown(
            '<div style="font-family:var(--f-display);font-size:20px;color:#00F5FF;'
            'letter-spacing:2px;margin-bottom:14px;">🏆 全產業戰力排行榜</div>',
            unsafe_allow_html=True
        )
        ss = df_gal.groupby('L1')['bias'].mean().sort_values(ascending=False)
        for sector, avg_bias in ss.items():
            sd   = df_gal[df_gal['L1'] == sector]
            if not len(sd): continue
            bulls = len(sd[sd['bias'] > 0])
            flag  = "🔴" if avg_bias > 0 else "🟢"
            with st.expander(f"{flag} **{sector}** (均 {avg_bias:+.1f}%)  ·  強勢 {bulls}/{len(sd)} 檔"):
                l2g  = sd.groupby('L2')
                sl2  = sorted(l2g.groups.keys(), key=lambda x: 0 if '上' in str(x) else (1 if '中' in str(x) else 2))
                for l2 in sl2:
                    sub = l2g.get_group(l2).sort_values('bias', ascending=False)
                    st.markdown(f"**{l2}**")
                    for _, r in sub.iterrows():
                        c = "red" if r['bias'] > 0 else "#26A69A"
                        st.markdown(
                            f"<span style='color:{c};font-weight:bold'>{r.get('code','')} {r['name']}</span>"
                            f" <span style='color:#445566;font-size:.9em'>({r['bias_label']})</span>",
                            unsafe_allow_html=True
                        )
                    st.markdown("---")


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 2.2  —  STRATEGY CHECK  (Sniper Scope)
# ══════════════════════════════════════════════════════════════════════════════
def render_2_2(df: pd.DataFrame):
    st.markdown('<div class="t2-sec-title">📈 2.2 核心策略檢核 — Sniper Scope</div>',
                unsafe_allow_html=True)

    full_data = pd.DataFrame(st.session_state.get('t2_full', []))
    if full_data.empty:
        st.markdown('<div class="t2-empty"><div class="t2-empty-icon">🎯</div>'
                    '<div class="t2-empty-text">Run Census in 2.1 First</div></div>',
                    unsafe_allow_html=True)
        return

    st.markdown(
        '<div style="font-family:var(--f-mono);font-size:10px;color:#2a3a4a;'
        'letter-spacing:2px;margin-bottom:10px;text-transform:uppercase;">'
        '↓  Enter CB code to pull live K-line + 4 Commandment check</div>',
        unsafe_allow_html=True
    )

    cb_input = st.text_input("CB 代號 (5碼)", value="", placeholder="e.g. 12345",
                              label_visibility="collapsed", key="t22_input")

    if cb_input.strip():
        _plot_candle_chart(cb_input.strip())
        # Try to match from census data
        code_col = 'code' if 'code' in full_data.columns else None
        matched  = full_data[full_data[code_col] == cb_input.strip()] if code_col else pd.DataFrame()
        if not matched.empty:
            st.markdown(
                '<div style="font-family:var(--f-mono);font-size:10px;color:#334455;'
                'letter-spacing:2px;margin:16px 0 10px;text-transform:uppercase;">'
                'Commandment Status — from Census Data</div>',
                unsafe_allow_html=True
            )
            _four_commandments(matched.iloc[0])
            _cb_card(matched.iloc[0], badge="🎯", report_title="📄 Detailed Strategy Report")
        else:
            st.caption("⚠️ 此代號不在普查資料中，顯示 K 線圖但無法顯示檢核卡。請先執行 2.1 普查。")
    else:
        # Browse SOP candidates
        sop = st.session_state.get('t2_scan', pd.DataFrame())
        if not sop.empty:
            st.markdown(
                '<div style="font-family:var(--f-mono);font-size:10px;color:#2a3a4a;'
                'letter-spacing:2px;margin:10px 0 8px;text-transform:uppercase;">'
                'Or select from SOP candidates</div>',
                unsafe_allow_html=True
            )
            opts = [f"{r.get('code','')} — {r.get('name','')}" for _, r in sop.head(20).iterrows()]
            sel  = st.selectbox("選擇標的", ["— 請選擇 —"] + opts, key="t22_sel")
            if sel != "— 請選擇 —":
                code = sel.split("—")[0].strip()
                _plot_candle_chart(code)
                m = sop[sop.get('code', pd.Series()) == code]
                if not m.empty:
                    _four_commandments(m.iloc[0])
                    _cb_card(m.iloc[0], badge="🎯")
        else:
            st.markdown('<div class="t2-empty"><div class="t2-empty-icon">🔍</div>'
                        '<div class="t2-empty-text">Run Census or enter a CB code above</div></div>',
                        unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 2.3  —  RISK RADAR
# ══════════════════════════════════════════════════════════════════════════════
def render_2_3():
    st.markdown('<div class="t2-sec-title">⚠️ 2.3 潛在風險雷達 — Negative Screener</div>',
                unsafe_allow_html=True)

    scan = st.session_state.get('t2_scan', pd.DataFrame())
    if scan.empty:
        st.markdown('<div class="t2-empty"><div class="t2-empty-icon">⚠️</div>'
                    '<div class="t2-empty-text">Run Census in 2.1 First</div></div>',
                    unsafe_allow_html=True)
        return

    st.markdown(
        '<div style="font-family:var(--f-mono);font-size:10px;color:#FF4B4B;'
        'letter-spacing:1.5px;border-left:2px solid rgba(255,49,49,0.28);'
        'padding:8px 14px;margin-bottom:18px;text-transform:uppercase;">'
        '負面表列 — 警示特定風險標的 · 提醒您「避開誰」</div>',
        unsafe_allow_html=True
    )

    tab1, tab2, tab3 = st.tabs(["☠️ 籌碼鬆動", "⚠️ 高溢價", "🧊 流動性陷阱"])

    # ── 籌碼鬆動 ─────────────────────────────────────────────────────────────
    with tab1:
        if 'conv_rate' in scan.columns:
            loose = scan[scan['conv_rate'] > 30].sort_values('conv_rate', ascending=False)
            if not loose.empty:
                st.markdown(
                    f'<div style="font-family:var(--f-mono);font-size:11px;color:#FF3131;'
                    f'margin-bottom:14px;letter-spacing:1px;text-transform:uppercase;">'
                    f'⚠️  {len(loose)} 檔  已轉換比例 &gt;30%  — 主力可能正在下車</div>',
                    unsafe_allow_html=True
                )
                for _, row in loose.head(15).iterrows():
                    cr    = pd.to_numeric(row.get('conv_rate',0), errors='coerce')
                    price = pd.to_numeric(row.get('price',0),     errors='coerce')
                    name  = row.get('name',''); code = row.get('code','')
                    st.markdown(f"""
<div class="t2-warn-card">
  <div class="t2-warn-value">{cr:.1f}%</div>
  <div class="t2-warn-header">{name}  ({code})</div>
  <div class="t2-warn-meta">CB市價 {price:.1f} &nbsp;·&nbsp; 已轉換 {cr:.1f}% &nbsp;·&nbsp; 籌碼鬆動風險</div>
</div>""", unsafe_allow_html=True)
            else:
                st.markdown('<div class="t2-warn-ok">✅  NO LOOSE CHIP ALERTS</div>',
                            unsafe_allow_html=True)
        else:
            st.warning("掃描結果無 conv_rate 欄位。")

    # ── 高溢價 ───────────────────────────────────────────────────────────────
    with tab2:
        if 'premium' in scan.columns:
            overp = scan[scan['premium'] > 20].sort_values('premium', ascending=False)
            if not overp.empty:
                st.markdown(
                    f'<div style="font-family:var(--f-mono);font-size:11px;color:#FFD700;'
                    f'margin-bottom:14px;letter-spacing:1px;text-transform:uppercase;">'
                    f'⚠️  {len(overp)} 檔  溢價率 &gt;20%  — 上漲空間受壓縮</div>',
                    unsafe_allow_html=True
                )
                for _, row in overp.head(15).iterrows():
                    prm   = pd.to_numeric(row.get('premium',0), errors='coerce')
                    price = pd.to_numeric(row.get('price',0),   errors='coerce')
                    name  = row.get('name',''); code = row.get('code','')
                    st.markdown(f"""
<div class="t2-warn-card" style="border-color:rgba(255,215,0,0.28);background:rgba(255,215,0,0.025);
     border-left-color:#FFD700;box-shadow:0 0 14px rgba(255,215,0,0.06);">
  <div class="t2-warn-value" style="color:#FFD700">{prm:.1f}%</div>
  <div class="t2-warn-header" style="color:#E8C400">{name}  ({code})</div>
  <div class="t2-warn-meta">CB市價 {price:.1f} &nbsp;·&nbsp; 溢價率 {prm:.1f}% &nbsp;·&nbsp; 肉少湯喝</div>
</div>""", unsafe_allow_html=True)
            else:
                st.markdown('<div class="t2-warn-ok">✅  NO HIGH PREMIUM ALERTS</div>',
                            unsafe_allow_html=True)
        else:
            st.info("掃描結果無 premium 欄位，跳過。")

    # ── 流動性陷阱 ───────────────────────────────────────────────────────────
    with tab3:
        if 'avg_volume' in scan.columns:
            illiq = scan[scan['avg_volume'] < 10].sort_values('avg_volume')
            if not illiq.empty:
                st.markdown(
                    f'<div style="font-family:var(--f-mono);font-size:11px;color:#FF3131;'
                    f'margin-bottom:14px;letter-spacing:1px;text-transform:uppercase;">'
                    f'🧊  {len(illiq)} 檔  日均量 &lt;10張  — 殭屍債陷阱！</div>',
                    unsafe_allow_html=True
                )
                for _, row in illiq.head(15).iterrows():
                    vol   = pd.to_numeric(row.get('avg_volume',0), errors='coerce')
                    price = pd.to_numeric(row.get('price',0),      errors='coerce')
                    name  = row.get('name',''); code = row.get('code','')
                    st.markdown(f"""
<div class="t2-warn-card">
  <div class="t2-warn-value">{vol:.0f}張</div>
  <div class="t2-warn-header">{name}  ({code})</div>
  <div class="t2-warn-meta">CB市價 {price:.1f} &nbsp;·&nbsp; 日均量 {vol:.0f} 張 &nbsp;·&nbsp; 出場困難</div>
</div>""", unsafe_allow_html=True)
            else:
                st.markdown('<div class="t2-warn-ok">✅  NO LIQUIDITY TRAP ALERTS</div>',
                            unsafe_allow_html=True)
        else:
            st.info("掃描結果無 avg_volume 欄位，跳過。")


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 2.4  —  PORTFOLIO  (Kelly Criterion)
# ══════════════════════════════════════════════════════════════════════════════
def render_2_4():
    st.markdown('<div class="t2-sec-title">💰 2.4 資金配置試算 — Kelly Position Sizing</div>',
                unsafe_allow_html=True)

    scan = st.session_state.get('t2_scan', pd.DataFrame())
    if scan.empty:
        st.markdown('<div class="t2-empty"><div class="t2-empty-icon">💰</div>'
                    '<div class="t2-empty-text">Run Census in 2.1 First</div></div>',
                    unsafe_allow_html=True)
        return

    n_tgts = len(scan)
    st.markdown(
        f'<div style="font-family:var(--f-mono);font-size:10px;color:#00FF7F;'
        f'letter-spacing:1.5px;margin-bottom:18px;text-transform:uppercase;">'
        f'✅  已同步獵殺結果：{n_tgts} 檔可配置標的</div>',
        unsafe_allow_html=True
    )

    left_col, right_col = st.columns([1, 1])

    with left_col:
        total_cap = st.number_input(
            "總操作資金 (元)", min_value=100_000, value=2_000_000, step=100_000, key="t24_cap"
        )

        n_display  = min(n_tgts, 5)
        kelly_pct  = round(100.0 / n_display) if n_display > 0 else 0

        # ── BIG KELLY NUMBER ─────────────────────────────────────────────────
        st.markdown(f"""
<div class="t2-kelly-box">
  <div class="t2-kelly-lbl">Kelly Criterion — Recommended Position Per Target</div>
  <div class="t2-kelly-num">{kelly_pct}<span class="t2-kelly-pct">%</span></div>
  <div class="t2-kelly-sub">每檔建議配置 &nbsp;·&nbsp; Top {n_display} 等權重分散</div>
</div>""", unsafe_allow_html=True)

        # ── Position detail lines ─────────────────────────────────────────────
        sort_col = 'score' if 'score' in scan.columns else 'price'
        top5     = scan.sort_values(sort_col, ascending=False).head(5)
        invest   = total_cap * (kelly_pct / 100.0)

        lines_html = ""
        for _, row in top5.iterrows():
            cb_price = row.get('price', 0) or 0
            name     = row.get('name','未知')
            code     = row.get('code','0000')
            if cb_price > 0:
                num_lots  = int(invest / (cb_price * 1000))
                lines_html += (
                    f'<div style="font-family:var(--f-body);font-size:14px;color:#8BAABB;'
                    f'padding:8px 0;border-bottom:1px solid rgba(255,255,255,0.04);">'
                    f'<span style="color:#CDD;font-weight:700">{name} ({code})</span>'
                    f'  <span style="color:#445566">·  {cb_price:.1f} 元  ·  '
                    f'建議 <span style="color:#FFD700;font-weight:700">{num_lots} 張</span>'
                    f'  ≈ {int(invest):,} 元</span></div>'
                )
        st.markdown(lines_html, unsafe_allow_html=True)

    with right_col:
        # ── Pie chart next to Kelly number ────────────────────────────────────
        sort_col = 'score' if 'score' in scan.columns else 'price'
        top5     = scan.sort_values(sort_col, ascending=False).head(5)
        alloc    = [kelly_pct] * len(top5)
        remain   = 100 - sum(alloc)

        pie_df   = pd.DataFrame({
            '標的': [r.get('name','') for _, r in top5.iterrows()],
            '配置': alloc
        })
        if remain > 0:
            pie_df = pd.concat([pie_df, pd.DataFrame([{'標的':'現金保留','配置':remain}])],
                               ignore_index=True)

        fig = go.Figure(go.Pie(
            labels=pie_df['標的'], values=pie_df['配置'], hole=0.52,
            marker=dict(
                colors=['#FF3131','#FFD700','#00F5FF','#00FF7F','#FF9A3C','#445566'],
                line=dict(color='rgba(0,0,0,0.4)', width=1)
            ),
            textfont=dict(color='#DDE', size=12, family='Rajdhani'),
        ))
        fig.update_layout(
            title=dict(text="建議資金配置",
                       font=dict(color='#FFD700', size=13, family='JetBrains Mono')),
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            height=360, margin=dict(t=44, b=0, l=0, r=0),
            legend=dict(font=dict(color='#B0C0D0', size=11, family='Rajdhani'))
        )
        st.markdown('<div class="t2-chart-wrap">', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  FIRE CONTROL DECK CONFIG
# ══════════════════════════════════════════════════════════════════════════════
FIRE_BTNS = [
    ("2.1", "📡", "自動獵殺",  "AUTO SCAN",    "#00F5FF", "0,245,255"),
    ("2.2", "📈", "核心檢核",  "SNIPER SCOPE", "#00FF7F", "0,255,127"),
    ("2.3", "⚠️", "風險雷達",  "RISK RADAR",   "#FF3131", "255,49,49"),
    ("2.4", "💰", "資金配置",  "PORTFOLIO",    "#FFD700", "255,215,0"),
]

RENDER_MAP = {
    "2.1": render_2_1,
    "2.2": render_2_2,
    "2.3": render_2_3,
    "2.4": render_2_4,
}


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN ENTRY
# ══════════════════════════════════════════════════════════════════════════════
def render():
    """Tab 2 — 獵殺雷達  God-Tier Build"""
    _inject_css()

    df = st.session_state.get('df', pd.DataFrame())

    if 't2_active' not in st.session_state:
        st.session_state.t2_active = "2.1"
    active = st.session_state.t2_active

    # ── SYSTEM BAR ────────────────────────────────────────────────────────────
    st.markdown(f"""
<div style="display:flex;align-items:baseline;justify-content:space-between;
            padding-bottom:16px;border-bottom:1px solid rgba(255,255,255,0.052);
            margin-bottom:18px;">
  <div>
    <span style="font-family:'Bebas Neue',sans-serif;font-size:26px;
                 color:#00F5FF;letter-spacing:3px;
                 text-shadow:0 0 22px rgba(0,245,255,0.32);">
      🎯 獵殺雷達
    </span>
    <span style="font-family:'JetBrains Mono',monospace;font-size:9px;
                 color:rgba(0,245,255,0.26);letter-spacing:3px;
                 border:1px solid rgba(0,245,255,0.10);border-radius:20px;
                 padding:3px 13px;margin-left:14px;background:rgba(0,245,255,0.022);">
      KILL RADAR V100
    </span>
  </div>
  <div style="font-family:'JetBrains Mono',monospace;font-size:10px;
              color:rgba(200,215,230,0.20);letter-spacing:2px;text-align:right;line-height:1.7;">
    {datetime.now().strftime('%H:%M:%S')}<br>{datetime.now().strftime('%Y · %m · %d')}
  </div>
</div>""", unsafe_allow_html=True)

    # ── FIRE CONTROL DECK ─────────────────────────────────────────────────────
    st.markdown(
        '<div style="background:linear-gradient(165deg,#07080f,#0b0c16);'
        'border:1px solid rgba(255,255,255,0.055);border-radius:18px;'
        'padding:16px 14px 13px;margin-bottom:16px;position:relative;overflow:hidden;">'
        '<div style="font-family:JetBrains Mono,monospace;font-size:8px;letter-spacing:4px;'
        'color:rgba(0,245,255,0.18);text-transform:uppercase;margin-bottom:12px;padding-left:2px;">'
        '⬡ fire control deck — select module</div>',
        unsafe_allow_html=True
    )

    fire_cols = st.columns(4)
    for col, (code, icon, label_zh, label_en, accent, rgb) in zip(fire_cols, FIRE_BTNS):
        is_a   = (active == code)
        brd    = f"2px solid {accent}" if is_a else "1px solid #1b2030"
        bg_c   = f"rgba({rgb},0.08)"   if is_a else "#090c14"
        lbl_c  = accent                 if is_a else "#AABB"
        glow   = f"0 0 20px rgba({rgb},0.14), 0 8px 26px rgba(0,0,0,0.4)" if is_a else "none"

        with col:
            # Visual card (pointer-events:none, rendered behind button)
            st.markdown(
                f'<div style="height:108px;background:{bg_c};border:{brd};border-radius:16px;'
                f'display:flex;flex-direction:column;align-items:center;justify-content:center;'
                f'gap:6px;box-shadow:{glow};margin-bottom:-56px;pointer-events:none;'
                f'position:relative;z-index:0;">'
                f'<div style="font-size:28px">{icon}</div>'
                f'<div style="font-family:Rajdhani,sans-serif;font-size:14px;font-weight:700;color:{lbl_c}">{label_zh}</div>'
                f'<div style="font-family:JetBrains Mono,monospace;font-size:7px;color:#223;letter-spacing:2px">{label_en}</div>'
                f'</div>',
                unsafe_allow_html=True
            )
            if st.button(f"{icon} {label_zh}", key=f"fire_{code}", use_container_width=True):
                st.session_state.t2_active = code
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)  # fire deck frame

    # ── CONTENT FRAME ─────────────────────────────────────────────────────────
    st.markdown('<div class="t2-content">', unsafe_allow_html=True)

    fn = RENDER_MAP.get(active)
    if fn:
        try:
            if active in ("2.1", "2.2"):
                fn(df)
            else:
                fn()
        except Exception as exc:
            import traceback
            st.error(f"❌ 子模組 {active} 渲染失敗: {exc}")
            with st.expander("🔍 Debug Trace"):
                st.code(traceback.format_exc())

    st.markdown(
        f'<div class="t2-foot">Titan Kill Radar V100 &nbsp;·&nbsp; '
        f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>',
        unsafe_allow_html=True
    )
    st.markdown('</div>', unsafe_allow_html=True)  # t2-content
