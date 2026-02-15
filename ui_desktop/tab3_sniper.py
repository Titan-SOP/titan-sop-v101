# ui_desktop/tab3_sniper.py
# Titan SOP V100 — Tab 3: 單兵狙擊
# ══════════════════════════════════════════════════════════════
#  校正紀錄 (vs 原始 tab3單兵狙擊.py):
#    [F1] @st.fragment 裝飾器恢復
#    [F2] expander 標題 "3.1 萬用個股狙擊雷達" 恢復
#    [F3] t1 tab 標籤改回 "🔮 雙軌扣抵預演"
#    [F4] sdf['Volume'] = 0 引號修正 (原版 bug 已修)
#    [F5] slope_10 / path_inertia 計算恢復 (原版存在)
#  功能強化:
#    [E1] T3 日K 下方掛 RSI(14) 子圖
#    [E2] Poster Rail 上方加「技術概覽」徽章列
#    [E3] T1 加「扣抵方向預測」箭頭指示卡
#    [E4] T7 加「波浪完成度」進度條
# ══════════════════════════════════════════════════════════════
import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import yfinance as yf
from datetime import datetime
from macro_risk import MacroRiskEngine

@st.cache_resource
def _get_macro():
    return MacroRiskEngine()

# ── HELPERS (verbatim from original V82) ──────────────────────
def safe_clamp(val, min_v, max_v):
    if val is None or pd.isna(val): return min_v
    return max(min_v, min(max_v, float(val)))

def get_advanced_granville(cp, op, ma87_curr, ma87_prev5):
    slope=ma87_curr-ma87_prev5; bias=((cp-ma87_curr)/ma87_curr)*100 if ma87_curr>0 else 0
    is_rising=slope>0.3; is_falling=slope<-0.3
    if bias>25:  return "🔴 正乖離過大","乖離>25%，過熱"
    if bias<-25: return "🟢 負乖離過大","乖離<-25%，超跌"
    if cp>ma87_curr and op<ma87_curr and not is_falling: return "🚀 G1 突破買點","突破生命線且均線未下彎"
    if cp<ma87_curr and is_rising:                       return "🛡️ G2 假跌破(買)","跌破上揚均線"
    if cp>ma87_curr and bias<3 and is_rising:            return "🧱 G3 回測支撐","回測生命線有守"
    if cp>ma87_curr and op<ma87_curr and not is_rising:  return "💀 G4 跌破賣點","跌破生命線且均線未上揚"
    if cp>ma87_curr and is_falling:                      return "🎣 G5 假突破(賣)","突破下彎均線"
    if cp<ma87_curr and bias>-3 and is_falling:          return "🚧 G6 反彈遇壓","反彈生命線不過"
    return "盤整(無訊號)","均線走平，區間震盪"

def calculate_zigzag(df, deviation=0.03):
    df=df.reset_index()
    dc=next((c for c in df.columns if str(c).lower() in ['date','index']),None)
    if dc: df.rename(columns={dc:'Date'},inplace=True)
    if 'Close' not in df.columns or 'Date' not in df.columns: return pd.DataFrame()
    closes=df['Close'].values; dates=df['Date'].values
    if len(closes)==0: return pd.DataFrame()
    pivots=[{'idx':0,'Price':closes[0],'Type':'Start','Date':dates[0]}]
    trend=0; lp=closes[0]; li=0
    for i in range(1,len(closes)):
        diff=(closes[i]-lp)/lp
        if trend==0:
            if diff>deviation:    trend=1;  lp=closes[i]; li=i
            elif diff<-deviation: trend=-1; lp=closes[i]; li=i
        elif trend==1:
            if closes[i]>lp: lp=closes[i]; li=i
            elif diff<-deviation:
                pivots.append({'idx':li,'Price':lp,'Type':'High','Date':dates[li]})
                trend=-1; lp=closes[i]; li=i
        elif trend==-1:
            if closes[i]<lp: lp=closes[i]; li=i
            elif diff>deviation:
                pivots.append({'idx':li,'Price':lp,'Type':'Low','Date':dates[li]})
                trend=1; lp=closes[i]; li=i
    pivots.append({'idx':len(closes)-1,'Price':closes[-1],'Type':'Current','Date':dates[-1]})
    return pd.DataFrame(pivots)

def calculate_5_waves(zigzag_df):
    if len(zigzag_df)<2: return pd.DataFrame()
    last=zigzag_df.iloc[-1]; prev=zigzag_df.iloc[-2]
    direction=1 if last['Price']>prev['Price'] else -1
    wl=abs(last['Price']-prev['Price']); sp=last['Price']; sd=last['Date']
    pts=[]
    if direction==1:
        p1=sp-wl*0.382; d1=sd+pd.Timedelta(days=10); pts.append({'Date':d1,'Price':p1,'Label':'W2(回)'})
        p2=p1+wl*1.618; d2=d1+pd.Timedelta(days=20); pts.append({'Date':d2,'Price':p2,'Label':'W3(推)'})
        p3=p2-(p2-p1)*0.382; d3=d2+pd.Timedelta(days=15); pts.append({'Date':d3,'Price':p3,'Label':'W4(回)'})
        p4=p3+wl; d4=d3+pd.Timedelta(days=15); pts.append({'Date':d4,'Price':p4,'Label':'W5(末)'})
    else:
        p1=sp+wl*0.5; d1=sd+pd.Timedelta(days=10); pts.append({'Date':d1,'Price':p1,'Label':'B波(彈)'})
        p2=p1-wl;     d2=d1+pd.Timedelta(days=20); pts.append({'Date':d2,'Price':p2,'Label':'C波(殺)'})
    return pd.concat([pd.DataFrame([{'Date':sd,'Price':sp,'Label':'Origin'}]),pd.DataFrame(pts)],ignore_index=True)

def calculate_ark_scenarios(rev_ttm,shares,cp,g,m,pe,years=5):
    if not rev_ttm or not shares or shares==0: return None
    cases={'Bear':{'g_m':0.8,'pe_m':0.8,'m_adj':-0.05},'Base':{'g_m':1.0,'pe_m':1.0,'m_adj':0.0},'Bull':{'g_m':1.2,'pe_m':1.2,'m_adj':0.05}}
    out={}
    for c,mults in cases.items():
        tg=g*mults['g_m']; tpe=pe*mults['pe_m']; tm=max(0.01,m+mults['m_adj'])
        target=(rev_ttm*((1+tg)**years)*tm*tpe)/shares
        out[c]={'Target':target,'CAGR':(target/cp)**(1/years)-1 if cp>0 else 0}
    return out

def calculate_smart_valuation(eps,rev,shares,g,m,pe,dr=0.1,y=10):
    if not rev or shares==0: return 0
    return (rev*((1+g)**y)*m*pe/((1+dr)**y))/shares

# ── CSS ────────────────────────────────────────────────────────
def _inject_css():
    st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Rajdhani:wght@300;400;600;700&family=JetBrains+Mono:wght@300;400;700&display=swap" rel="stylesheet">
<style>
:root{--c-gold:#FFD700;--c-cyan:#00F5FF;--c-red:#FF3131;--c-green:#00FF7F;--c-orange:#FF9A3C;
  --f-d:'Bebas Neue',sans-serif;--f-b:'Rajdhani',sans-serif;--f-m:'JetBrains Mono',monospace;}
/* KPI */
.t3-kpi-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin:12px 0;}
.t3-kpi-card{background:rgba(255,255,255,.022);border:1px solid rgba(255,255,255,.062);
  border-top:2px solid var(--kc,#00F5FF);border-radius:14px;padding:13px 14px 10px;position:relative;overflow:hidden;}
.t3-kpi-card::after{content:'';position:absolute;top:0;right:0;width:70px;height:70px;
  background:radial-gradient(circle at top right,var(--kc,#00F5FF),transparent 68%);opacity:.04;pointer-events:none;}
.t3-kpi-lbl{font-family:var(--f-m);font-size:8px;color:rgba(140,155,178,.55);text-transform:uppercase;letter-spacing:2px;margin-bottom:7px;}
.t3-kpi-val{font-family:var(--f-d);font-size:48px;color:#FFF;line-height:.9;margin-bottom:4px;}
.t3-kpi-sub{font-family:var(--f-b);font-size:12px;color:var(--kc,#00F5FF);font-weight:600;}
/* BADGES */
.t3-badge-row{display:flex;gap:8px;flex-wrap:wrap;margin:8px 0 12px;}
.t3-badge{font-family:var(--f-m);font-size:10px;letter-spacing:1px;
  border:1px solid var(--bc,rgba(255,255,255,.10));background:rgba(0,0,0,.01);
  color:var(--bc,#778899);border-radius:20px;padding:4px 12px;}
/* RAIL */
.t3-rail{background:linear-gradient(165deg,#07080f,#0b0c16);border:1px solid rgba(255,255,255,.055);
  border-radius:18px;padding:14px 12px 11px;margin-bottom:13px;}
.t3-rail-lbl{font-family:var(--f-m);font-size:8px;letter-spacing:4px;color:rgba(255,154,60,.18);text-transform:uppercase;margin-bottom:10px;}
/* CONTENT */
.t3-content{background:linear-gradient(175deg,#06090e,#090c14);border:1px solid rgba(255,255,255,.05);
  border-radius:20px;padding:20px 18px 26px;min-height:460px;}
.t3-sec-title{font-family:var(--f-d);font-size:21px;letter-spacing:2px;color:#FF9A3C;
  text-shadow:0 0 16px rgba(255,154,60,.22);margin-bottom:13px;padding-bottom:9px;border-bottom:1px solid rgba(255,255,255,.05);}
/* GSCORE */
.t3-gscore{background:#0d1018;border:1px solid rgba(255,165,0,.22);border-radius:16px;padding:17px 19px;margin-bottom:13px;}
.t3-gscore-num{font-family:var(--f-d);font-size:66px;line-height:1;letter-spacing:2px;}
.t3-scene-row{font-family:var(--f-m);font-size:12px;color:#ccc;line-height:2.0;}
/* DED CARDS */
.t3-ded-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:11px 0;}
.t3-ded-card{background:rgba(255,255,255,.018);border:1px solid rgba(255,255,255,.06);border-radius:12px;padding:12px 13px;}
.t3-ded-lbl{font-family:var(--f-m);font-size:8px;color:rgba(140,155,178,.5);letter-spacing:2px;text-transform:uppercase;margin-bottom:5px;}
.t3-ded-val{font-family:var(--f-d);font-size:36px;color:#FFF;line-height:1;}
/* ARK */
.t3-ark-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:13px;margin-top:15px;}
.t3-ark-card{border-radius:16px;padding:18px 15px;text-align:center;border:1px solid var(--ac,rgba(255,255,255,.1));background:var(--ab,rgba(255,255,255,.02));}
.t3-ark-card.bear{--ac:rgba(255,49,49,.28);--ab:rgba(255,49,49,.04);}
.t3-ark-card.base{--ac:rgba(0,245,255,.22);--ab:rgba(0,245,255,.03);}
.t3-ark-card.bull{--ac:rgba(0,255,127,.28);--ab:rgba(0,255,127,.04);}
.t3-ark-lbl{font-family:var(--f-m);font-size:10px;color:rgba(180,195,215,.48);letter-spacing:2px;text-transform:uppercase;margin-bottom:9px;}
.t3-ark-val{font-family:var(--f-d);font-size:48px;color:#FFF;line-height:1;}
.t3-ark-cagr{font-family:var(--f-b);font-size:14px;margin-top:7px;}
/* VALUATION */
.t3-val-grid{display:grid;grid-template-columns:1fr 1fr;gap:13px;margin-top:13px;}
.t3-val-card{background:rgba(255,255,255,.022);border:1px solid rgba(255,255,255,.062);border-radius:16px;padding:17px 13px;text-align:center;}
.t3-val-lbl{font-family:var(--f-m);font-size:9px;color:rgba(140,155,178,.5);letter-spacing:2px;text-transform:uppercase;margin-bottom:7px;}
.t3-val-num{font-family:var(--f-d);font-size:50px;color:#FFF;line-height:1;}
/* WAVE PROGRESS */
.t3-wave-track{height:8px;background:rgba(255,255,255,.06);border-radius:4px;overflow:hidden;margin-top:4px;}
.t3-wave-fill{height:100%;border-radius:4px;background:linear-gradient(90deg,var(--wc,#00F5FF),transparent);}
/* CHART */
.t3-chart{background:rgba(0,0,0,.32);border:1px solid rgba(255,255,255,.055);border-radius:16px;padding:12px 7px 4px;margin:10px 0;overflow:hidden;}
/* BTN */
.t3-action div.stButton>button{background:rgba(255,154,60,.05)!important;border:1px solid rgba(255,154,60,.28)!important;
  color:rgba(255,154,60,.85)!important;font-family:var(--f-m)!important;font-size:11px!important;
  letter-spacing:2px!important;min-height:42px!important;border-radius:12px!important;text-transform:uppercase!important;}
.t3-action div.stButton>button:hover{background:rgba(255,154,60,.10)!important;box-shadow:0 0 20px rgba(255,154,60,.2)!important;}
.t3-foot{font-family:var(--f-m);font-size:9px;color:rgba(70,90,110,.28);letter-spacing:2px;text-align:right;margin-top:16px;text-transform:uppercase;}
</style>""", unsafe_allow_html=True)

# ── CHART THEME ────────────────────────────────────────────────
def _cfg(chart):
    return (chart.configure_view(fill='rgba(0,0,0,0)',strokeOpacity=0)
                 .configure_axis(gridColor='rgba(255,255,255,0.04)',labelColor='#445566',titleColor='#334455'))

# ── [E2] BADGE ROW ─────────────────────────────────────────────
def _render_badges(sdf, cp, m87, m284, bias):
    try:
        delta=sdf['Close'].diff()
        gain=delta.clip(lower=0).rolling(14).mean()
        loss=(-delta.clip(upper=0)).rolling(14).mean()
        rsi=100-(100/(1+(gain/loss.replace(0,np.nan))))
        rsi_v=float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else 50
        rsi_lbl="RSI 超買" if rsi_v>70 else ("RSI 超賣" if rsi_v<30 else "RSI 中性")
        rsi_c="#FF3131" if rsi_v>70 else ("#00FF7F" if rsi_v<30 else "#778899")
        ema12=sdf['Close'].ewm(span=12).mean(); ema26=sdf['Close'].ewm(span=26).mean()
        macd_line=ema12-ema26; macd_sig=macd_line.ewm(span=9).mean()
        macd_up=float(macd_line.iloc[-1])>float(macd_sig.iloc[-1])
        macd_lbl="MACD 金叉" if macd_up else "MACD 死叉"; macd_c="#00FF7F" if macd_up else "#FF3131"
        tstr=abs(m87-m284)/m284*100 if m284>0 else 0
        tstr_lbl=f"趨勢強度 {tstr:.1f}%"; tstr_c="#00FF7F" if tstr>3 else ("#FFD700" if tstr>1 else "#778899")
        hvol=sdf['Close'].pct_change().std()*100*np.sqrt(252)
        vol_lbl=f"年化波動 {hvol:.0f}%"; vol_c="#FF3131" if hvol>60 else ("#FFD700" if hvol>30 else "#00FF7F")
        bias_lbl=f"乖離 {bias:+.1f}%"; bias_c="#FF3131" if abs(bias)>15 else ("#FFD700" if abs(bias)>7 else "#00FF7F")
        badges=[(f"{rsi_lbl} {rsi_v:.0f}",rsi_c),(macd_lbl,macd_c),(tstr_lbl,tstr_c),(vol_lbl,vol_c),(bias_lbl,bias_c)]
        html='<div class="t3-badge-row">'
        for lbl,c in badges:
            html+=f'<div class="t3-badge" style="--bc:{c}">{lbl}</div>'
        html+='</div>'
        st.markdown(html,unsafe_allow_html=True)
    except Exception: pass

# ── T1: 雙軌扣抵預演 [F3 label restored + F5 slope_10 + E3] ────
def _t1(sdf,v_ticker,cp,m87,m87p5,m284):
    st.markdown('<div class="t3-sec-title">🔮 雙軌扣抵預演 (Holographic Strategy)</div>',unsafe_allow_html=True)
    hist_vol=sdf['Close'].pct_change().std()*100; cur_vol=max(1.5,hist_vol)
    with st.expander("⚙️ 戰略參數設定 (點擊展開)",expanded=False):
        c1,c2=st.columns(2)
        sim_days=c1.slider("預演天數",10,60,20,key="t1_days")
        momentum_input=c2.number_input("假設動能 (%)",-10.0,10.0,0.0,step=0.5,key="t1_mom")
        c2.caption(f"目前波動率: {cur_vol:.1f}%")
    last_date=sdf.index[-1]; future_days=sim_days
    future_dates=[last_date+pd.Timedelta(days=i+1) for i in range(future_days)]
    # [F5] slope_10 / path_inertia 原版邏輯
    slope_10=(sdf['Close'].iloc[-1]-sdf['Close'].iloc[-10])/10
    path_inertia=[cp+slope_10*(i+1) for i in range(future_days)]
    path_bull=[cp*(1+(cur_vol/100)*np.sqrt(i+1)) for i in range(future_days)]
    path_bear=[cp*(1-(cur_vol/100)*np.sqrt(i+1)) for i in range(future_days)]
    sim_prices=[]; curr_s=cp
    for _ in range(future_days):
        curr_s*=(1+momentum_input/100); sim_prices.append(curr_s)
    future_series=pd.Series(sim_prices,index=future_dates)
    combined=pd.concat([sdf['Close'],future_series])
    comb_ma87=combined.rolling(87).mean(); comb_ma284=combined.rolling(284).mean()
    si=len(sdf); ac=combined.values
    deduct_87=[float(ac[si+i-87]) if (si+i-87)>=0 else np.nan for i in range(future_days)]
    deduct_284=[float(ac[si+i-284]) if (si+i-284)>=0 else np.nan for i in range(future_days)]
    f_df=pd.DataFrame({'Date':future_dates,'Sim_Price':sim_prices,'Bull_Bound':path_bull,'Bear_Bound':path_bear,
                       'MA87':comb_ma87.loc[future_dates].values,'MA284':comb_ma284.loc[future_dates].values,
                       'Deduct_87':deduct_87,'Deduct_284':deduct_284})
    score=0; ma87c=comb_ma87.iloc[-future_days-1]; ma284c=comb_ma284.iloc[-future_days-1]
    if cp>ma87c: score+=15
    if cp>ma284c: score+=15
    if cp>sdf['Close'].iloc[-20:].mean(): score+=20
    bd=abs(ma87c-ma284c)/ma284c if ma284c>0 else 0; is_sq=bd<0.015
    if ma87c>ma284c: score+=30
    if np.nanmean(deduct_87[:20])<cp: score+=20
    if score>=80:   g_status="🔥 多頭坦途 (Clear Sky)"
    elif score>=50: g_status="⚠️ 區間震盪 (Range Bound)"
    else:           g_status="🐻 空頭承壓 (Bearish Pressure)"
    cmd='積極操作' if score>70 else ('觀望/區間' if score>40 else '保守防禦')
    sq_msg=(f"🌪️ <b>螺旋絞殺 (Squeeze)</b>：87/284MA 乖離僅 <b>{bd*100:.2f}%</b>。兩線打結，預計 <b>3-5天</b> 大變盤。"
            if is_sq else ("🚀 <b>發散攻擊</b>：均線呈多頭排列，開口擴大，趨勢明確。" if ma87c>ma284c
                           else "📉 <b>空頭壓制</b>：均線呈空頭排列，上方層層賣壓。"))
    fib_high=max(path_bull); fib_low=min(path_bear); fib_0618=fib_low+(fib_high-fib_low)*0.618
    var_date=(last_date+pd.Timedelta(days=13)).strftime('%m/%d')
    d87_0=deduct_87[0] if deduct_87 and not np.isnan(deduct_87[0]) else 0
    d284_0=deduct_284[0] if deduct_284 and not np.isnan(deduct_284[0]) else 0
    sc_c="#00FF7F" if score>=80 else ("#FFD700" if score>=50 else "#FF3131")
    st.markdown(f"""
<div class="t3-gscore">
  <div style="display:flex;align-items:baseline;gap:18px;margin-bottom:10px;">
    <div class="t3-gscore-num" style="color:{sc_c}">{score}</div>
    <div>
      <div style="font-family:var(--f-m);font-size:9px;color:rgba(255,165,0,.4);letter-spacing:3px;text-transform:uppercase;">G-SCORE RATING</div>
      <div style="font-family:var(--f-b);font-size:16px;color:#ddd;font-weight:600;">{g_status}</div>
      <div style="font-family:var(--f-m);font-size:10px;color:{sc_c};margin-top:2px;">指令：{cmd}</div>
    </div>
  </div>
  <hr style="border:none;border-top:1px solid #1e2530;margin:10px 0;">
  <div style="font-family:var(--f-b);font-size:14px;color:#4db8ff;font-weight:700;margin-bottom:6px;">⚔️ 雙線糾纏場 (Interaction)</div>
  <div style="font-family:var(--f-b);font-size:14px;color:#ccc;margin-bottom:10px;">{sq_msg}</div>
  <div class="t3-scene-row">
    • <b>87MA (季)</b>：{ma87c:.1f} | 扣抵：{d87_0:.1f} ({'扣低助漲' if d87_0<cp else '扣高壓力'})<br>
    • <b>284MA (年)</b>：{ma284c:.1f} | 扣抵：{d284_0:.1f}
  </div>
  <hr style="border:none;border-top:1px solid #1e2530;margin:10px 0;">
  <div style="font-family:var(--f-b);font-size:14px;color:#98FB98;font-weight:700;margin-bottom:6px;">🔮 五維全息劇本</div>
  <div class="t3-scene-row">
    關鍵變盤窗：<b style="color:#FFD700">{var_date} (費氏轉折)</b><br>
    • <b>劇本 A (慣性 50%)</b>：在 <b>{fib_low:.1f} ~ {fib_high:.1f}</b> 區間震盪，以盤代跌。<br>
    • <b>劇本 B (破底翻 30%)</b>：回測 <b>{fib_0618:.1f}</b> (Fib 0.618) 不破，V型反轉。<br>
    • <b>劇本 C (風險 20%)</b>：若跌破 <b>{min(deduct_87[:5]) if deduct_87 else 0:.1f}</b>，確認均線蓋頭，向下尋求支撐。
  </div>
</div>""",unsafe_allow_html=True)
    # [E3] 扣抵方向箭頭卡
    def _ded(lbl,ded,cur,ma,accent):
        is_h=ded<cur; ac="#00FF7F" if is_h else "#FF3131"
        arrow="▲ 扣低助漲" if is_h else "▼ 扣高壓力"
        pct=(ded-ma)/ma*100 if ma>0 else 0
        return f'<div class="t3-ded-card" style="border-top:2px solid {accent}"><div class="t3-ded-lbl">{lbl}</div><div style="display:flex;align-items:baseline;gap:8px;"><div class="t3-ded-val">{ded:.1f}</div><div style="font-size:20px;color:{ac}">{arrow.split()[0]}</div></div><div style="font-family:var(--f-b);font-size:11px;color:{ac}">{arrow}</div><div style="font-family:var(--f-m);font-size:9px;color:rgba(120,140,165,.5);margin-top:3px;">MA變動預估：{pct:+.2f}%</div></div>'
    st.markdown(f'<div class="t3-ded-grid">{_ded("87MA 扣抵 (下一交易日)",d87_0,cp,ma87c,"#FFD700")}{_ded("284MA 扣抵 (下一交易日)",d284_0,cp,ma284c,"#FF9A3C")}</div>',unsafe_allow_html=True)
    # Chart
    base_f=alt.Chart(f_df).encode(x='Date:T')
    cone=base_f.mark_area(opacity=0.2,color='gray').encode(y='Bear_Bound:Q',y2='Bull_Bound:Q')
    l_sim=base_f.mark_line(color='white',strokeDash=[4,2]).encode(y='Sim_Price')
    l_87=base_f.mark_line(color='orange',strokeWidth=2).encode(y='MA87')
    l_284=base_f.mark_line(color='#00bfff',strokeWidth=2).encode(y='MA284')
    g_87=base_f.mark_line(color='red',strokeDash=[1,1],opacity=0.5).encode(y='Deduct_87')
    g_284=base_f.mark_line(color='blue',strokeDash=[1,1],opacity=0.3).encode(y='Deduct_284')
    hist_d=sdf.iloc[-60:].reset_index()
    bh=alt.Chart(hist_d).encode(x='Date:T')
    candles=(bh.mark_rule().encode(y='Low',y2='High')+bh.mark_bar().encode(y='Open',y2='Close',
        color=alt.condition("datum.Open<=datum.Close",alt.value("#FF4B4B"),alt.value("#00AA00"))))
    chart=(cone+candles+l_sim+l_87+l_284+g_87+g_284).properties(height=500,title="量子路徑預演 (含波動率機率錐)")
    st.markdown('<div class="t3-chart">',unsafe_allow_html=True)
    st.altair_chart(_cfg(chart.interactive()),use_container_width=True)
    st.markdown('</div>',unsafe_allow_html=True)
    st.caption("🟠 87MA | 🔵 284MA | ⬜ 模擬路徑 | 🔴虛線 87扣抵 | 🔵虛線 284扣抵 | 灰色錐體 機率錐")

# ── T2 ──────────────────────────────────────────────────────────
def _t2(sdf,v_ticker):
    st.markdown('<div class="t3-sec-title">📐 亞當理論二次反射路徑</div>',unsafe_allow_html=True)
    try:
        adf=_get_macro().calculate_adam_projection(sdf,20)
        if not adf.empty:
            h=sdf.iloc[-60:].reset_index(); h['T']='History'
            p=adf.reset_index(); p['T']='Project'; p.rename(columns={'Projected_Price':'Close'},inplace=True)
            chart=(alt.Chart(pd.concat([h,p])).mark_line()
                   .encode(x='Date:T',y=alt.Y('Close',scale=alt.Scale(zero=False)),color='T:N',strokeDash='T:N')
                   .properties(title="亞當理論二次反射路徑圖",height=420).interactive())
            st.markdown('<div class="t3-chart">',unsafe_allow_html=True)
            st.altair_chart(_cfg(chart),use_container_width=True)
            st.markdown('</div>',unsafe_allow_html=True)
        else: st.warning("資料不足。")
    except Exception as e: st.warning(f"亞當理論計算失敗: {e}")

# ── T3: 日K + RSI [E1] ──────────────────────────────────────────
def _t3(sdf,v_ticker):
    st.markdown('<div class="t3-sec-title">🕯️ 日K線 (含黃金/死亡交叉 + RSI)</div>',unsafe_allow_html=True)
    kd=sdf.tail(252).copy()
    delta=kd['Close'].diff(); gain=delta.clip(lower=0).rolling(14).mean()
    loss=(-delta.clip(upper=0)).rolling(14).mean()
    kd['RSI']=100-(100/(1+(gain/loss.replace(0,np.nan)))); kd=kd.reset_index()
    col_c=alt.condition("datum.Open<=datum.Close",alt.value("#FF4B4B"),alt.value("#00AA00"))
    bk=alt.Chart(kd).encode(x=alt.X('Date:T',axis=alt.Axis(format='%m/%d',title='Date')))
    candle=(bk.mark_rule().encode(y=alt.Y('Low',scale=alt.Scale(zero=False)),y2='High',color=col_c)+
            bk.mark_bar().encode(y='Open',y2='Close',color=col_c))
    l87=bk.mark_line(color='blue',strokeWidth=2).encode(y='MA87',tooltip=['MA87'])
    l284=bk.mark_line(color='purple',strokeWidth=2).encode(y='MA284',tooltip=['MA284'])
    chart_p=candle+l87+l284
    cross_d=kd[kd['Cross_Signal']!=0]
    if not cross_d.empty:
        chart_p+=(alt.Chart(cross_d).mark_point(size=150,filled=True,opacity=1)
                  .encode(x='Date:T',y='Close',
                          shape=alt.condition("datum.Cross_Signal > 0",alt.value("triangle-up"),alt.value("triangle-down")),
                          color=alt.condition("datum.Cross_Signal > 0",alt.value("gold"),alt.value("black")),
                          tooltip=['Date','Close','Cross_Signal']))
    chart_p=chart_p.properties(height=310,title=f"{v_ticker} 日K線圖")
    chart_vol=bk.mark_bar().encode(y='Volume',color=col_c).properties(height=75)
    chart_rsi=(
        bk.mark_line(color='#B77DFF',strokeWidth=1.5).encode(y=alt.Y('RSI:Q',scale=alt.Scale(domain=[0,100]),title='RSI'))
        +alt.Chart(pd.DataFrame({'y':[70,30]})).mark_rule(strokeDash=[3,2],opacity=0.4).encode(y='y:Q',color=alt.value('#FF3131'))
    ).properties(height=85,title="RSI (14)")
    final=alt.vconcat(chart_p,chart_vol,chart_rsi).resolve_scale(x='shared').interactive()
    st.markdown('<div class="t3-chart">',unsafe_allow_html=True)
    st.altair_chart(_cfg(final),use_container_width=True)
    st.markdown('</div>',unsafe_allow_html=True)
    st.caption("指標：🔵 87MA | 🟣 284MA | ▲ 黃金交叉 | ▼ 死亡交叉 | 🟣 RSI(14)  虛線=超買/超賣")

# ── T4 ──────────────────────────────────────────────────────────
def _t4(sdf,v_ticker):
    st.markdown('<div class="t3-sec-title">🗓️ 月K線 (43/87/284MA)</div>',unsafe_allow_html=True)
    try:
        freq='ME'
        try: sdf.resample('ME').last()
        except Exception: freq='M'
        md=sdf.resample(freq).agg({'Open':'first','High':'max','Low':'min','Close':'last'}).dropna()
        if len(md)>=43:
            md['MA43']=md['Close'].rolling(43).mean(); md['MA87']=md['Close'].rolling(87).mean(); md['MA284']=md['Close'].rolling(284).mean()
            pm=md.tail(120).reset_index()
            bm=alt.Chart(pm).encode(x=alt.X('Date:T',axis=alt.Axis(format='%Y-%m')))
            col_m=alt.condition("datum.Open<=datum.Close",alt.value("#FF4B4B"),alt.value("#00AA00"))
            mc=(bm.mark_rule().encode(y='Low',y2='High',color=col_m)+bm.mark_bar().encode(y='Open',y2='Close',color=col_m))
            final=(mc+bm.mark_line(color='orange').encode(y='MA43')+bm.mark_line(color='blue').encode(y='MA87')+bm.mark_line(color='purple').encode(y='MA284')).interactive()
            st.markdown('<div class="t3-chart">',unsafe_allow_html=True)
            st.altair_chart(_cfg(final),use_container_width=True)
            st.markdown('</div>',unsafe_allow_html=True)
            st.caption("月線指標：🟠 43MA | 🔵 87MA | 🟣 284MA")
        else: st.warning("月線資料不足。")
    except Exception as e: st.error(f"月線失敗: {e}")

# ── T5 ──────────────────────────────────────────────────────────
def _t5(v_ticker,cp):
    st.markdown('<div class="t3-sec-title">🧠 ARK 戰情室 (三情境 DCF)</div>',unsafe_allow_html=True)
    try:
        info=yf.Ticker(v_ticker).info; rev_ttm=info.get('totalRevenue',0); shares_out=info.get('sharesOutstanding',0)
        ag=info.get('revenueGrowth',info.get('earningsGrowth',0.15)) or 0.15
        is_us=not v_ticker.endswith(('.TW','.TWO'))
        region_tag="🇺🇸 美股" if is_us else "🇹🇼 台股"
        region_hint="美股通常享有較高估值溢價" if is_us else "台股估值相對保守"
    except Exception: rev_ttm=0;shares_out=0;ag=0.15;is_us=False;region_tag="未知";region_hint=""
    st.info(f"💡 基於期望值的三情境推演。{region_hint}");st.markdown(f'<div style="font-family:var(--f-m);font-size:10px;color:rgba(0,245,255,.4);letter-spacing:2px;margin-bottom:10px;">{region_tag}</div>',unsafe_allow_html=True)
    if rev_ttm>0 and shares_out>0:
        a1,a2,a3=st.columns(3)
        base_g=a1.number_input("基本成長率",-10.0,50.0,safe_clamp(ag,-10.0,50.0),0.01,key="t5_g")
        base_m=a2.number_input("基本淨利率",-5.0,5.0,0.20,0.01,key="t5_m")
        base_pe=a3.number_input("基本 PE",0.0,9999.0,30.0 if is_us else 20.0,1.0,key="t5_pe")
        sc=calculate_ark_scenarios(rev_ttm,shares_out,cp,base_g,base_m,base_pe)
        if sc:
            colors={"Bear":"#FF6B6B","Base":"#00F5FF","Bull":"#00FF7F"}
            css_map={"Bear":"bear","Base":"base","Bull":"bull"}
            icons={"Bear":"🐻 熊市","Base":"⚖️ 基本","Bull":"🐮 牛市"}
            html='<div class="t3-ark-grid">'
            for k in ["Bear","Base","Bull"]:
                html+=f'<div class="t3-ark-card {css_map[k]}"><div class="t3-ark-lbl">{icons[k]}</div><div class="t3-ark-val" style="color:{colors[k]}">${sc[k]["Target"]:.1f}</div><div class="t3-ark-cagr" style="color:{colors[k]}">CAGR: {sc[k]["CAGR"]:.1%}</div></div>'
            html+='</div>'
            st.markdown(html,unsafe_allow_html=True)
    else: st.warning("財務數據不足。")

# ── T6 ──────────────────────────────────────────────────────────
def _t6(v_ticker,cp):
    st.markdown('<div class="t3-sec-title">💎 智能估值引擎</div>',unsafe_allow_html=True)
    try:
        info=yf.Ticker(v_ticker).info; rev_ttm=info.get('totalRevenue',0); shares_out=info.get('sharesOutstanding',0)
        eps_ttm=info.get('trailingEps',0); ag=info.get('revenueGrowth',info.get('earningsGrowth',0.15)) or 0.15
        is_us=not v_ticker.endswith(('.TW','.TWO')); region_tag="🇺🇸 美股" if is_us else "🇹🇼 台股"
    except Exception: rev_ttm=0;shares_out=0;eps_ttm=0;ag=0.15;is_us=False;region_tag="未知"
    st.markdown(f'<div style="font-family:var(--f-m);font-size:10px;color:rgba(0,245,255,.4);letter-spacing:2px;margin-bottom:10px;">{region_tag}</div>',unsafe_allow_html=True)
    if rev_ttm>0:
        ind_sel=st.selectbox("產業模板：",["🚀 軟體/SaaS","💊 生技","⚙️ 硬體","🏭 傳統"],key="t6_ind")
        if "軟體" in ind_sel:   def_m=0.25;def_pe=50.0
        elif "生技" in ind_sel: def_m=0.30;def_pe=40.0
        elif "硬體" in ind_sel: def_m=0.15;def_pe=25.0
        else:                    def_m=0.08;def_pe=15.0
        if is_us: def_pe*=1.2
        s1,s2,s3=st.columns(3)
        u_g=s1.number_input("成長率",min_value=-10.0,max_value=None,value=safe_clamp(ag,-10.0,50.0),step=0.01,key="t6_g")
        u_m=s2.number_input("淨利率",min_value=-5.0,max_value=None,value=float(def_m),step=0.01,key="t6_m")
        u_pe=s3.number_input("終端 PE",min_value=0.0,max_value=None,value=float(def_pe),step=1.0,key="t6_pe")
        fair=calculate_smart_valuation(eps_ttm,rev_ttm,shares_out,u_g,u_m,u_pe)
        st.divider()
        v1,v2=st.columns(2)
        v1.metric("目前股價",f"{cp:.2f}")
        v2.metric("合理估值",f"{fair:.2f}",f"{cp-fair:.2f}",delta_color="inverse")
        is_under=fair>cp; clr="#00FF7F" if is_under else "#FF6B6B"; brd="rgba(0,255,127,.28)" if is_under else "rgba(255,49,49,.28)"
        st.markdown(f'<div class="t3-val-grid"><div class="t3-val-card"><div class="t3-val-lbl">Current Price</div><div class="t3-val-num">{cp:.1f}</div></div><div class="t3-val-card" style="border-color:{brd}"><div class="t3-val-lbl">Fair Value (10yr DCF)</div><div class="t3-val-num" style="color:{clr}">{fair:.1f}</div><div style="font-family:var(--f-m);font-size:10px;color:{clr};margin-top:5px;">{"低估 ▲" if is_under else "高估 ▼"} {abs(fair-cp):.1f}</div></div></div>',unsafe_allow_html=True)
    else: st.warning("數據不足。")

# ── T7: 5波 + 完成度 [E4] ───────────────────────────────────────
def _t7(sdf):
    st.markdown('<div class="t3-sec-title">🌊 艾略特5波模擬 (Elliott Wave Sim)</div>',unsafe_allow_html=True)
    st.info("💡 虛線為 AI 模擬路徑。文字已優化，提高辨識度。")
    zz=calculate_zigzag(sdf.tail(300),0.03)
    if not zz.empty:
        n_p=len(zz); wave_pct=min(100,int((n_p/9)*100))
        wave_phase="推進中" if wave_pct<50 else ("接近頂部" if wave_pct<80 else "末升段/末跌段")
        wave_c="#00FF7F" if wave_pct<50 else ("#FFD700" if wave_pct<80 else "#FF3131")
        st.markdown(f"""
<div style="margin:10px 0;">
  <div style="display:flex;justify-content:space-between;align-items:center;">
    <div style="font-family:var(--f-m);font-size:10px;color:rgba(150,165,180,.6);letter-spacing:2px;text-transform:uppercase;">Wave Completion</div>
    <div style="font-family:var(--f-d);font-size:26px;color:{wave_c}">{wave_pct}%</div>
  </div>
  <div class="t3-wave-track"><div class="t3-wave-fill" style="width:{wave_pct}%;--wc:{wave_c}"></div></div>
  <div style="font-family:var(--f-m);font-size:9px;color:rgba(150,165,180,.5);letter-spacing:1.5px;margin-top:3px;">轉折點數：{n_p} &nbsp;·&nbsp; 階段：<span style="color:{wave_c}">{wave_phase}</span></div>
</div>""",unsafe_allow_html=True)
        bz=alt.Chart(zz).encode(x='Date:T')
        real_l=bz.mark_line(point=True,color='black').encode(y=alt.Y('Price',scale=alt.Scale(zero=False)),tooltip=['Date','Price','Type'])
        text_p=bz.mark_text(dy=-15,color='blue',fontSize=14,fontWeight='bold').encode(y='Price',text=alt.Text('Price',format='.1f'))
        chart_w=real_l+text_p
        sim=calculate_5_waves(zz)
        if not sim.empty:
            sl=alt.Chart(sim).mark_line(strokeDash=[5,5],color='red').encode(x='Date:T',y='Price',tooltip=['Date','Price','Label'])
            sp=alt.Chart(sim[sim['Label']!='Origin']).mark_circle(color='red',size=60).encode(x='Date:T',y='Price')
            sl_l=alt.Chart(sim[sim['Label']!='Origin']).mark_text(dy=-30,color='blue',fontSize=14,fontWeight='bold').encode(x='Date:T',y='Price',text='Label')
            sl_v=alt.Chart(sim[sim['Label']!='Origin']).mark_text(dy=30,color='blue',fontSize=14,fontWeight='bold').encode(x='Date:T',y='Price',text=alt.Text('Price',format='.1f'))
            chart_w=chart_w+sl+sp+sl_l+sl_v
        st.markdown('<div class="t3-chart">',unsafe_allow_html=True)
        st.altair_chart(_cfg(chart_w.interactive()),use_container_width=True)
        st.markdown('</div>',unsafe_allow_html=True)
    else: st.warning("波動過小，無法計算。")

# ── POSTER CONFIG ──────────────────────────────────────────────
POSTERS=[("t1","🔮","雙軌扣抵","DEDUCTION","#00F5FF"),("t2","📐","亞當理論","ADAM","#FFD700"),
         ("t3","🕯️","日K+RSI","DAILY K","#FF9A3C"),("t4","🗓️","月K線","MONTHLY","#FF3131"),
         ("t5","🧠","ARK戰情","ARK DESK","#00FF7F"),("t6","💎","智能估值","VALUATION","#B77DFF"),
         ("t7","🌊","5波模擬","ELLIOTT","#FF6BFF")]
RENDER={"t1":_t1,"t2":_t2,"t3":_t3,"t4":_t4,"t5":_t5,"t6":_t6,"t7":_t7}

# ── MAIN [F1] ──────────────────────────────────────────────────
@st.fragment
def render():
    _inject_css()
    if 't3_active' not in st.session_state: st.session_state.t3_active="t1"
    st.markdown(f"""<div style="display:flex;align-items:baseline;justify-content:space-between;
  padding-bottom:14px;border-bottom:1px solid rgba(255,255,255,.052);margin-bottom:16px;">
  <div><span style="font-family:'Bebas Neue',sans-serif;font-size:26px;color:#FF9A3C;letter-spacing:3px;text-shadow:0 0 22px rgba(255,154,60,.32);">🎯 單兵狙擊</span>
    <span style="font-family:'JetBrains Mono',monospace;font-size:9px;color:rgba(255,154,60,.26);letter-spacing:3px;border:1px solid rgba(255,154,60,.10);border-radius:20px;padding:3px 13px;margin-left:14px;">SOLO SNIPER V100</span></div>
  <div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:rgba(200,215,230,.20);letter-spacing:2px;text-align:right;line-height:1.7;">{datetime.now().strftime('%H:%M:%S')}<br>{datetime.now().strftime('%Y·%m·%d')}</div>
</div>""",unsafe_allow_html=True)
    # [F2] 原版 expander 標題
    with st.expander("3.1 萬用個股狙擊雷達 (Universal Sniper)",expanded=True):
        st.info("🌍 全球戰情模式：支援台股 (2330)、美股 (TSLA, PLTR)、加密貨幣BTC-USD。已啟動雙軌扣抵預演系統。")
        ic,bc=st.columns([5,1])
        with ic:
            w17_in=st.text_input("輸入代號或股名",value=st.session_state.get('t3_ticker','2330'),
                                  placeholder="2330 / TSLA / BTC-USD",key="w17_final_v102").strip()
        with bc:
            st.markdown('<div style="margin-top:22px;"><div class="t3-action">',unsafe_allow_html=True)
            if st.button("🔍 搜尋",key="t3_search",use_container_width=True):
                st.session_state.t3_ticker=w17_in
            st.markdown('</div></div>',unsafe_allow_html=True)
        ticker_in=st.session_state.get('t3_ticker','2330').strip()
        if not ticker_in: st.info("請輸入標的代號"); return
        try:
            from macro_risk import STOCK_METADATA
            N2T={v['name'].strip():k for k,v in STOCK_METADATA.items()}
            if ticker_in in N2T: ticker_in=N2T[ticker_in]
        except Exception: pass
        cands=[ticker_in]
        if ticker_in.isdigit(): cands=[f"{ticker_in}.TW",f"{ticker_in}.TWO"]
        elif not ticker_in.endswith((".TW",".TWO")): cands=[ticker_in.upper(),f"{ticker_in.upper()}.TW"]
        macro=_get_macro(); sdf=pd.DataFrame(); v_ticker=None
        with st.spinner("掃描全球資料庫..."):
            for c in cands:
                temp=macro.get_single_stock_data(c,period="max")
                if not temp.empty and len(temp)>=300: sdf=temp; v_ticker=c; break
        if sdf.empty: st.error("❌ 查無數據，或歷史數據不足 300 天無法計算年線扣抵。"); return
        try:
            if isinstance(sdf.columns,pd.MultiIndex): sdf.columns=sdf.columns.get_level_values(0)
            sdf.columns=[str(c).strip().capitalize() for c in sdf.columns]
            sdf=sdf.reset_index()
            dc=next((c for c in sdf.columns if str(c).lower() in ['date','datetime','index']),None)
            if dc:
                sdf.rename(columns={dc:'Date'},inplace=True); sdf['Date']=pd.to_datetime(sdf['Date'])
                sdf.set_index('Date',inplace=True); sdf.sort_index(inplace=True)
            col_map={}
            for c in sdf.columns:
                if c.lower() in ['close','price']: col_map[c]='Close'
                elif c.lower() in ['volume','vol']: col_map[c]='Volume'
            sdf.rename(columns=col_map,inplace=True)
            for req in ['Open','High','Low']:
                if req not in sdf.columns: sdf[req]=sdf['Close']
            if 'Volume' not in sdf.columns: sdf['Volume']=0  # [F4] 引號修正
            for c in ['Close','Open','High','Low','Volume']: sdf[c]=pd.to_numeric(sdf[c],errors='coerce')
            sdf=sdf.dropna(subset=['Close'])
        except Exception as e: st.error(f"資料格式錯誤: {e}"); return
        sdf['MA87']=sdf['Close'].rolling(87).mean(); sdf['MA284']=sdf['Close'].rolling(284).mean()
        sdf['Prev_MA87']=sdf['MA87'].shift(1); sdf['Prev_MA284']=sdf['MA284'].shift(1); sdf['Cross_Signal']=0
        sdf.loc[(sdf['Prev_MA87']<=sdf['Prev_MA284'])&(sdf['MA87']>sdf['MA284']),'Cross_Signal']=1
        sdf.loc[(sdf['Prev_MA87']>=sdf['Prev_MA284'])&(sdf['MA87']<sdf['MA284']),'Cross_Signal']=-1
        cp=float(sdf['Close'].iloc[-1]); op=float(sdf['Open'].iloc[-1])
        m87=float(sdf['MA87'].iloc[-1]) if not pd.isna(sdf['MA87'].iloc[-1]) else 0
        m87p5=float(sdf['MA87'].iloc[-6]) if len(sdf)>6 and not pd.isna(sdf['MA87'].iloc[-6]) else m87
        m284=float(sdf['MA284'].iloc[-1]) if not pd.isna(sdf['MA284'].iloc[-1]) else 0
        bias=((cp-m87)/m87)*100 if m87>0 else 0
        trend_days=0; trend_str="整理中"; trend_c="#FFD700"
        if m87>0 and m284>0:
            is_bull=m87>m284; trend_str="🔥 中期多頭 (87>284)" if is_bull else "❄️ 中期空頭 (87<284)"
            trend_c="#00FF7F" if is_bull else "#FF6B6B"
            bs=sdf['MA87']>sdf['MA284']; cs=bs.iloc[-1]
            for i in range(len(bs)-1,-1,-1):
                if bs.iloc[i]==cs: trend_days+=1
                else: break
        g_title,g_desc=get_advanced_granville(cp,op,m87,m87p5)
        bias_c="#FF3131" if abs(bias)>15 else ("#FFD700" if abs(bias)>7 else "#00FF7F")
        st.subheader(f"🎯 {v_ticker} 戰情報告")
        c1,c2,c3,c4=st.columns(4)
        c1.metric("目前股價",f"{cp:.2f}"); c2.metric("87MA (季線)",f"{m87:.2f}",f"{cp-m87:.2f}")
        c3.metric("284MA (年線)",f"{m284:.2f}",f"{cp-m284:.2f}"); c4.metric("乖離率 (Bias)",f"{bias:.1f}%")
        st.markdown(f'<div style="font-family:Rajdhani,sans-serif;font-size:14px;color:rgba(200,215,230,.6);margin:6px 0 4px;"><span style="color:{trend_c};font-weight:700;">{trend_str}</span> &nbsp;·&nbsp; 持續 <span style="color:#FFD700;font-weight:700;">{trend_days}</span> 天 &nbsp;·&nbsp; 格蘭碧：<span style="color:#00F5FF;font-weight:700;">{g_title}</span> — {g_desc}</div>',unsafe_allow_html=True)
        _render_badges(sdf,cp,m87,m284,bias)  # [E2]
        st.markdown("---")
        # Poster Rail
        active=st.session_state.t3_active
        st.markdown('<div class="t3-rail"><div class="t3-rail-lbl">⬡ analysis modules — click to select</div>',unsafe_allow_html=True)
        p_cols=st.columns(7)
        for col,(key,icon,label,tag,accent) in zip(p_cols,POSTERS):
            is_a=(active==key)
            brd=f"2px solid {accent}" if is_a else "1px solid #1b2030"
            bg_c="rgba(255,154,60,.08)" if is_a else "#090c14"
            lbl_c=accent if is_a else "rgba(200,215,230,.7)"
            glow=f"0 0 18px rgba(255,154,60,.10)" if is_a else "none"
            with col:
                st.markdown(f'<div style="height:128px;background:{bg_c};border:{brd};border-radius:14px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:5px;box-shadow:{glow};margin-bottom:-51px;pointer-events:none;z-index:0;position:relative;"><div style="font-size:23px">{icon}</div><div style="font-family:Rajdhani,sans-serif;font-size:11px;font-weight:700;color:{lbl_c};text-align:center;padding:0 2px;">{label}</div><div style="font-family:JetBrains Mono,monospace;font-size:6px;color:#223;letter-spacing:1.5px;">{tag}</div></div>',unsafe_allow_html=True)
                if st.button(f"{icon}",key=f"p3_{key}",use_container_width=True):
                    st.session_state.t3_active=key; st.rerun()
        st.markdown('</div>',unsafe_allow_html=True)
        st.markdown('<div class="t3-content">',unsafe_allow_html=True)
        try:
            fn=RENDER[active]
            if active=="t1":               fn(sdf,v_ticker,cp,m87,m87p5,m284)
            elif active in("t2","t3","t4"): fn(sdf,v_ticker)
            elif active in("t5","t6"):      fn(v_ticker,cp)
            elif active=="t7":              fn(sdf)
        except Exception as exc:
            import traceback
            st.error(f"❌ 子模組 {active} 渲染失敗: {exc}")
            with st.expander("🔍 Debug"): st.code(traceback.format_exc())
        st.markdown(f'<div class="t3-foot">Titan Solo Sniper V100 · {datetime.now().strftime("%Y-%m-%d %H:%M")}</div>',unsafe_allow_html=True)
        st.markdown('</div>',unsafe_allow_html=True)