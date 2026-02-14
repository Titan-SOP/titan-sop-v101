# ui_desktop/tab5_wiki.py
# Titan SOP V100.0 — Tab 5: 戰略百科
# [靈魂注入 V82.0 → V100.0]
# 完整移植：
#   5.1 SOP 戰略百科 (5子分頁: 四大時間套利/進出場紀律/產業族群/特殊心法/OTC神奇均線)
#   5.2 情報獵殺分析結果
#   5.3 CBAS 槓桿試算儀
#   5.4 時間套利行事曆

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

from knowledge_base import TitanKnowledgeBase
from execution import CalendarAgent

@st.cache_resource
def _load_kb():
    return TitanKnowledgeBase()

@st.cache_resource
def _load_calendar():
    return CalendarAgent()


def render():
    """Tab 5: 戰略百科 — 全功能復原版 (V82 靈魂 + V100 外殼)"""
    kb       = _load_kb()
    calendar = _load_calendar()
    df       = st.session_state.get('df', pd.DataFrame())

    # ─────────────────────────────────────────────────────────────
    # 5.1 SOP 戰略百科
    # ─────────────────────────────────────────────────────────────
    with st.expander("5.1 📖 SOP 戰略百科 (SOP Strategy Encyclopedia)", expanded=True):
        with st.expander("點此展開，查核系統內建的完整 SOP 規則庫", expanded=False):
            if 'all_rules' not in st.session_state:
                st.session_state.all_rules = kb.get_all_rules_for_ui()
            all_rules = st.session_state.all_rules

            w1, w2, w3, w4, w5 = st.tabs([
                "⏰ 四大時間套利",
                "📋 進出場紀律",
                "🏭 產業族群庫",
                "🧠 特殊心法",
                "📈 OTC 神奇均線"
            ])

            with w1:
                st.subheader("SOP 時間套利總覽")
                events = all_rules.get("time_arbitrage", [])
                if events:
                    for rule in events:
                        st.markdown(f"- {rule}")
                else:
                    st.info("""
**四大黃金時間套利窗口**

1. **新券蜜月期 (0-90天)**：上市初期追蹤，大戶定調，股性未定。進場甜蜜點：105-115元。

2. **滿年沈澱 (350-420天)**：沈澱洗牌結束，底部有支撐。觸發點：CB站上87MA且帶量。

3. **賣回保衛 (距賣回<180天)**：下檔保護最強，CB價95-105甜甜圈。最佳風報比窗口。

4. **百日轉換窗口 (距到期<100天)**：最後一搏。股價需站上轉換價 × 1.05 才有轉換意義。
                    """)

            with w2:
                st.subheader("SOP 進出場規則原文 (摘錄)")
                ee = all_rules.get("entry_exit", {})
                if isinstance(ee, dict):
                    st.text_area("📥 進場條件 (Entry)", value=ee.get('entry', '無紀錄'), height=300)
                    st.text_area("📤 出場條件 (Exit)",  value=ee.get('exit',  '無紀錄'), height=300)
                else:
                    st.markdown("""
**📥 核心進場條件 (The 4 Commandments)**

1. **價格天條**：CB市價 < 120 元（理想 105~115）
2. **均線天條**：87MA > 284MA（中期多頭排列）
3. **身分認證**：領頭羊（族群指標股）或風口豬（主流題材二軍）
4. **發債故事**：從無到有 / 擴產 / 政策事件三選一

**📤 核心出場條件**

- 🛑 **停損**：CB跌破100元（保本天條不妥協）
- 💰 **停利**：目標152元以上，留魚尾策略
- ⏰ **時間停損**：持有超過90天仍未動，重新評估
                    """)

            with w3:
                st.subheader("SOP 核心產業與故事")
                ind = all_rules.get("industry_story", {})
                stories = ind.get("general_issuance_stories", []) if isinstance(ind, dict) else []
                if stories:
                    st.markdown("#### **發債故事總覽**")
                    st.text_area("General Issuance Stories", "\n\n".join(stories), height=200)
                sector_map = ind.get("sector_map", {}) if isinstance(ind, dict) else {}
                st.markdown("---")
                st.markdown("#### **族群與領頭羊對照**")
                if sector_map:
                    rows = [{"族群 (Sector)": s, "關聯標的 (Stocks)": ", ".join(sorted(list(stks)))}
                            for s, stks in sorted(sector_map.items())]
                    st.dataframe(pd.DataFrame(rows), use_container_width=True)
                else:
                    st.markdown("""
| 族群 | 關聯標的 |
|------|---------|
| AI伺服器 | 廣達、緯創、英業達、技嘉 |
| 散熱 | 奇鋐、雙鴻、建準 |
| CoWoS封測 | 日月光、矽品 |
| 重電/電網 | 華城、士電、中興電 |
| 半導體設備 | 弘塑、辛耘、漢微科 |
| 航運 | 長榮、陽明、萬海 |
| 生技新藥 | 藥華藥、合一 |
                    """)

            with w4:
                st.subheader("隱藏心法與特殊策略")
                tactics = all_rules.get("special_tactics", [])
                if tactics:
                    st.text_area("Tactics & Mindset", "\n\n---\n\n".join(tactics), height=500)
                else:
                    st.markdown("""
**🧠 Titan 核心心法 (Top 10)**

1. **賣出是種藝術**：目標區間到達後，分批出場，絕不一次梭哈。「留魚尾」策略讓下一次持倉更安心。

2. **跌破100是天條**：不管故事多美，CB跌破100元立刻離場，沒有例外，沒有感情。

3. **族群共振才是主力**：單兵突破假象居多。觀察是否有2~3檔同族群CB同步上攻，才是真正主力進場訊號。

4. **87MA是生命線**：股價站上87MA且均線向上，才是安全進場時機。跌破87MA視為第一警戒。

5. **溢價率的陷阱**：溢價率 > 20% 的CB，上漲空間有限。避開高溢價，選擇低溢價（5~15%）的標的。

6. **籌碼鬆動就跑**：已轉換比例超過 30%，代表大量轉換股票，股東結構改變，籌碼不乾淨，警惕。

7. **尾盤定勝負**：13:25後的最後25分鐘，是當天多空最誠實的表態。收盤站穩才是真突破。

8. **消息面最後出現**：有基本面、技術面支撐，消息面是最後確認彈，不是買入理由。

9. **跟隨資金流向**：先看哪個產業有錢進來，再找該產業中CB價格最低、溢價最小的標的。

10. **做錯立刻認錯**：沒有人能100%準確，做錯了立刻認錯出場，留下現金才能把握下一次機會。
                    """)

            with w5:
                st.subheader("OTC 神奇均線法則 (OTC Magic MA Rules)")
                try:
                    otc = kb.get_otc_magic_rules()
                    for name, desc in otc.items():
                        st.markdown(f"**{name.replace('_',' ').title()}**: {desc}")
                except Exception:
                    st.markdown("""
**OTC 上櫃市場神奇均線觀察**

- **87日均線 (季線)**：OTC市場的核心生命線。多頭時支撐強，空頭時壓力大。
- **284日均線 (年線)**：長線多空分界。287MA翻揚 = 機構開始佈局訊號。
- **雙線黃金交叉**：87MA由下往上穿越284MA，啟動中期多頭，歷史勝率 >70%。
- **上櫃特性**：OTC成交量較小，主力更容易控盤。單日異常量能（>3倍均量）需特別警覺。
                    """)

    # ─────────────────────────────────────────────────────────────
    # 5.2 情報獵殺分析結果
    # ─────────────────────────────────────────────────────────────
    with st.expander("5.2 🕵️ 情報獵殺分析結果", expanded=False):
        intel_files = st.session_state.get('intel_files', [])
        if intel_files:
            for file in intel_files:
                with st.expander(f"📄 分析報告: {file.name}"):
                    try:
                        from intelligence import IntelligenceEngine
                        intel = IntelligenceEngine()
                        result = intel.analyze_file(file, kb, df)
                        if "error" in result:
                            st.error(result["error"])
                        else:
                            st.markdown(result.get("local_analysis_md", "本地分析失敗。"))
                            st.divider()
                            api_key = st.session_state.get('api_key', '')
                            if api_key:
                                with st.spinner(f"執行 Gemini AI 深度分析: {file.name}…"):
                                    try:
                                        import google.generativeai as genai
                                        genai.configure(api_key=api_key)
                                        report = intel.analyze_with_gemini(result["full_text"])
                                        st.markdown("### 💎 **Gemini AI 深度解析**")
                                        st.markdown(report)
                                    except Exception as e:
                                        st.error(f"Gemini 失敗: {e}")
                            else:
                                st.info("未輸入 Gemini API Key，跳過 AI 深度解析。")
                    except ImportError:
                        st.info(f"📄 已上傳: **{file.name}**（情報引擎尚未掛載，請確認 intelligence.py）")
        else:
            st.info("請於左側上傳情報文件 (PDF/TXT) 以進行分析。")

    # ─────────────────────────────────────────────────────────────
    # 5.3 CBAS 槓桿試算儀
    # ─────────────────────────────────────────────────────────────
    with st.expander("5.3 ⚖️ CBAS 槓桿試算儀", expanded=False):
        c1, c2 = st.columns(2)
        cb_price = c1.number_input("輸入 CB 市價", min_value=100.0, value=110.0, step=0.5, format="%.2f")
        premium_cost = cb_price - 100

        if premium_cost > 0:
            leverage = cb_price / premium_cost
            c1.metric("💰 理論權利金 (百元)", f"{premium_cost:.2f} 元")
            c2.metric("⚖️ 槓桿倍數", f"{leverage:.2f} 倍")

            if leverage > 3:
                st.success("🔥 高槓桿甜蜜點：目前槓桿效益佳，適合以小博大。")
                st.info(f"""
**槓桿解讀**：CB 市價 {cb_price} 元，等同以 {premium_cost:.2f} 元的「時間價值」控制 100 元的股票轉換價值。
若標的股票上漲 10%，CB 理論增值幅度約 {10 * leverage:.1f}%（{leverage:.2f} 倍槓桿）。
                """)
            else:
                st.warning("⚠️ 肉少湯多：槓桿效益較低，風險報酬比可能不佳，建議直接買進 CB 現股。")
        else:
            st.info("CB 市價需高於 100 元才能計算 CBAS 權利金。")

    # ─────────────────────────────────────────────────────────────
    # 5.4 時間套利行事曆
    # ─────────────────────────────────────────────────────────────
    with st.expander("5.4 📅 時間套利行事曆 (Event Calendar)", expanded=False):
        if not df.empty:
            days_ahead = st.slider("選擇要掃描的未來天數", 7, 90, 30)
            today = datetime.now().date()
            future_date = today + timedelta(days=days_ahead)
            upcoming_events = []

            code_col     = next((c for c in df.columns if 'code' in c.lower()), None)
            name_col     = next((c for c in df.columns if 'name' in c.lower()), None)
            list_col     = next((c for c in df.columns if 'list' in c.lower() or 'issue' in c.lower()), None)
            put_col      = next((c for c in df.columns if 'put' in c.lower() or '賣回' in c.lower()), None)

            if code_col and name_col:
                for _, row in df.iterrows():
                    try:
                        events = calendar.calculate_time_traps(
                            str(row.get(code_col, '')),
                            str(row.get(list_col, '')) if list_col else '',
                            str(row.get(put_col,  '')) if put_col  else ''
                        )
                        for ev in events:
                            ev_date = pd.to_datetime(ev['date']).date()
                            if today <= ev_date <= future_date:
                                upcoming_events.append({
                                    "name":  row.get(name_col, ''),
                                    "date":  ev_date,
                                    "event": ev['event'],
                                    "desc":  ev.get('desc','')
                                })
                    except Exception:
                        pass

            if upcoming_events:
                upcoming_events.sort(key=lambda x: x['date'])
                st.subheader(f"未來 {days_ahead} 天的關鍵事件")
                for ev in upcoming_events:
                    days_left = (ev['date'] - today).days
                    st.markdown(
                        f"📅 **{days_left}天後 ({ev['date'].strftime('%Y-%m-%d')})**: "
                        f"`{ev['name']}` - **{ev['event']}**"
                    )
                    if ev['desc']:
                        st.caption(ev['desc'])
            else:
                st.info(f"未來 {days_ahead} 天內無觸發任何時間套利事件。")
        else:
            st.info("請上傳 CB 清單以掃描時間套利事件。")
