import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import yfinance as yf

# --- 🏹 獵殺雷達 (Radar) ---
@st.fragment
def render_radar():
    if st.button("🏠 返回戰情總部"):
        st.session_state.page = 'home'
        st.rerun()
    st.title("🏹 獵殺雷達 (CB Hunter Zone)")
    
    df = st.session_state.get('df', pd.DataFrame())

    with st.expander("2.1 自動獵殺推薦 (Auto Sniper)", expanded=True):
        st.info("此模組執行「全市場雙軌普查 (.TW/.TWO)」，並同步更新全系統連動資料庫。")

        col1, col2 = st.columns(2)
        with col1: min_score = st.slider("最低評分門檻", 0, 10, 5)
        with col2: st.caption("普查將抓取即時行情，請耐心等候。")

        if not df.empty:
            if st.button("🚀 啟動 SOP 全市場普查", type="primary"):
                with st.spinner("執行全市場掃描..."):
                    # 1. 資料前處理 (Surgical Fix: Index Fallback & Type Safety)
                    work_df = df.copy()
                    
                    # [修改 1] 擴充欄位對應，加入「餘額比例」
                    rename_map = {
                        '代號': 'code', '名稱': 'name', '可轉債市價': 'price',
                        '轉換價格': 'conv_price', '轉換標的': 'stock_code',
                        '已轉換比例': 'conv_rate', '轉換價值': 'conv_value',
                        '發行日': 'issue_date', '賣回日': 'put_date',
                        '餘額比例': 'balance_ratio' # 新增對應
                    }
                    work_df.rename(columns=lambda c: rename_map.get(c.strip(), c.strip()), inplace=True)

                    # [修改 2] 主流程強制計算：已轉換率 = 100 - 餘額比例
                    # 優先使用餘額比例計算，若無則保留原值
                    if 'balance_ratio' in work_df.columns:
                        # 轉為數值，處理空值
                        bal = pd.to_numeric(work_df['balance_ratio'], errors='coerce').fillna(100.0)
                        work_df['conv_rate'] = 100.0 - bal

                    # 絕對讀取 (Index Fallback)
                    try:
                        # 檢查關鍵欄位是否存在，若不存在則觸發 Index Fallback
                        required_cols = ['conv_price', 'stock_code', 'price', 'conv_rate', 'conv_value']
                        # 注意：這裡稍微放寬檢查，如果 balance_ratio 存在且已算出 conv_rate，也算通過
                        cols_check = [c for c in required_cols if c != 'conv_rate']
                        
                        if not all(col in work_df.columns for col in cols_check) or ('conv_rate' not in work_df.columns):
                            st.warning("⚠️ 偵測到欄位名稱不符，啟用 Index Fallback 強制讀取...")
                            
                            # 確保 f_cb_list 存在才執行
                            if 'f_cb_list' in locals() or 'f_cb_list' in globals():
                                if f_cb_list is not None:
                                    # 重新讀取原始檔案，不使用 header
                                    f_cb_list.seek(0)
                                    df_by_index = pd.read_excel(f_cb_list, header=None) if f_cb_list.name.endswith('.xlsx') else pd.read_csv(f_cb_list, header=None)
                                    
                                    # 跳過標題行
                                    df_by_index = df_by_index.iloc[1:].reset_index(drop=True)

                                    # 強制賦值
                                    work_df['conv_price'] = df_by_index.iloc[:, 9]
                                    work_df['stock_code'] = df_by_index.iloc[:, 10]
                                    work_df['price'] = df_by_index.iloc[:, 13]
                                    work_df['conv_value'] = df_by_index.iloc[:, 18]
                                    
                                    # [修改 3] Fallback 流程修正：讀取 Index 6 (餘額比例) 並計算
                                    # 原始錯誤寫法: work_df['conv_rate'] = df_by_index.iloc[:, 17]
                                    # 正確寫法:
                                    balance_val = pd.to_numeric(df_by_index.iloc[:, 6], errors='coerce').fillna(100.0)
                                    work_df['conv_rate'] = 100.0 - balance_val
                                else:
                                    st.error("無法執行強制讀取：找不到上傳的檔案物件 (f_cb_list)。")
                                    st.stop()
                            else:
                                st.error("變數 f_cb_list 未定義，無法重新讀取檔案。請確認是否已上傳。")
                                st.stop()
                                
                    except Exception as e:
                        st.error(f"Index Fallback 讀取失敗: {e}")
                        st.stop()

                    # 型別安全：確保數值欄位為 float 並填補空值
                    numeric_cols = ['price', 'conv_rate', 'conv_price', 'conv_value']
                    for col in numeric_cols:
                        if col in work_df.columns:
                            work_df[col] = pd.to_numeric(work_df[col], errors='coerce').fillna(0.0) # 嚴禁填入 0 (int)
                        else:
                            work_df[col] = 0.0 # 如果欄位不存在，創建並填入 0.0

                    # 日期欄位處理
                    for date_col in ['issue_date', 'put_date', 'list_date']:
                        if date_col in work_df.columns:
                            work_df[date_col] = pd.to_datetime(work_df[date_col], errors='coerce')
                    if 'issue_date' not in work_df.columns and 'list_date' in work_df.columns:
                        work_df['issue_date'] = work_df['list_date']

                    # 2. 普查迴圈
                    # ★ 直接使用 work_df，不需要 get_scan_result
                    # 添加預設評分欄位
                    if 'score' not in work_df.columns:
                        work_df['score'] = 50  # 預設評分
                    records = work_df.to_dict('records')
                    
                    total = len(records)
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    enriched_data = []
                    
                    for i, row in enumerate(records):
                        name = row.get('name', '')
                        status_text.text(f"普查進行中 ({i+1}/{total}): {name}...")
                        
                        code = str(row.get('stock_code', '')).strip()
                        row['stock_price_real'] = 0.0
                        row['ma87'] = 0.0
                        row['ma284'] = 0.0
                        row['trend_status'] = "⚠️ 資料不足"
                        
                        # 數據傳遞：確保關鍵數據寫入
                        row['cb_price'] = row.get('price', 0.0)
                        row['conv_price_val'] = row.get('conv_price', 0.0)
                        row['conv_value_val'] = row.get('conv_value', 0.0)

                        if code:
                            try:
                                hist = pd.DataFrame()
                                try: hist = yf.Ticker(f"{code}.TW").history(period="2y")
                                except: pass
                                
                                if hist.empty:
                                    try: hist = yf.Ticker(f"{code}.TWO").history(period="2y")
                                    except: pass
                                    
                                if not hist.empty and len(hist) > 284:
                                    curr = float(hist['Close'].iloc[-1])
                                    ma87 = float(hist['Close'].rolling(87).mean().iloc[-1])
                                    ma284 = float(hist['Close'].rolling(284).mean().iloc[-1])
                                    
                                    row['stock_price_real'] = curr
                                    row['ma87'] = ma87
                                    row['ma284'] = ma284
                                    
                                    # [關鍵修正]：只要 87MA > 284MA 即判定為中期多頭 (不強制現價 > 87)
                                    if ma87 > ma284:
                                        row['trend_status'] = "✅ 中期多頭"
                                        row['score'] = min(100, row.get('score', 0) + 20)
                                    else:
                                        row['trend_status'] = "整理/空頭"
                            except: pass
                        
                        enriched_data.append(row)
                        progress_bar.progress((i + 1) / total)
                    
                    # 3. 資料分流
                    full_df_enriched = pd.DataFrame(enriched_data)
                    
                    # 確保有必要的欄位供後續篩選
                    if 'price' not in full_df_enriched.columns: full_df_enriched['price'] = 0.0
                    if 'conv_rate' not in full_df_enriched.columns: full_df_enriched['conv_rate'] = 0.0
                    
                    sop_mask = (
                        (full_df_enriched['price'] < 120) &
                        (full_df_enriched['trend_status'].str.contains("多頭", na=False)) &
                        (full_df_enriched['conv_rate'] < 30)
                    )
                    sop_results = full_df_enriched[sop_mask].sort_values('score', ascending=False)
                    
                    st.session_state['scan_results'] = sop_results
                    st.session_state['full_census_data'] = full_df_enriched.to_dict('records')
                    
                    status_text.text("✅ 普查完成！資料已同步至戰情室與全系統。")
                    st.success(f"全市場掃描結束。符合「SOP 黃金標準」共 {len(sop_results)} 檔。")
                    if not sop_results.empty:
                        st.dataframe(sop_results[['code', 'name', 'price', 'stock_price_real', 'trend_status', 'conv_rate']])

        else:
            st.info("請上傳 CB 清單以啟動自動獵殺掃描。")
        
    with st.expander("2.2 核心策略檢核 (The War Room)", expanded=False):
        # [修復 1] 互動式 K 線圖函式 (具備 5 碼代碼自動轉 4 碼邏輯)
        def plot_candle_chart(cb_code):
            """使用 Altair 繪製互動式 K 線圖 (紅漲綠跌) 並疊加 87/284MA"""
            import yfinance as yf
            import altair as alt
            
            # [關鍵修正]: 若傳入的是 5 碼 CB 代碼 (如 64145)，截取前 4 碼 (6414) 作為股票代碼
            target_code = str(cb_code).strip()
            if len(target_code) == 5 and target_code.isdigit():
                target_code = target_code[:4]
                
            try:
                chart_df = pd.DataFrame()
                # 雙軌下載 (優先試 TW，若無則試 TWO)
                ticker_tw = f"{target_code}.TW"
                ticker_two = f"{target_code}.TWO"
                
                chart_df = yf.download(ticker_tw, period="2y", progress=False)
                if chart_df.empty:
                    chart_df = yf.download(ticker_two, period="2y", progress=False)
                
                if not chart_df.empty:
                    # 解決 yfinance MultiIndex 問題
                    if isinstance(chart_df.columns, pd.MultiIndex):
                        chart_df.columns = chart_df.columns.get_level_values(0)
                    
                    chart_df = chart_df.reset_index()
                    
                    # 計算均線 (87MA 與 284MA)
                    chart_df['MA87'] = chart_df['Close'].rolling(87).mean()
                    chart_df['MA284'] = chart_df['Close'].rolling(284).mean()

                    # 定義 K 線圖基礎
                    base = alt.Chart(chart_df).encode(
                        x=alt.X('Date:T', axis=alt.Axis(title='日期', format='%Y-%m-%d'))
                    )

                    # 紅漲綠跌顏色條件
                    color_condition = alt.condition("datum.Open <= datum.Close", alt.value("#FF4B4B"), alt.value("#26A69A"))

                    # 繪製 K 線
                    candles = base.mark_rule().encode(
                        y=alt.Y('Low', title='股價', scale=alt.Scale(zero=False)),
                        y2='High'
                    ) + base.mark_bar().encode(
                        y='Open',
                        y2='Close',
                        color=color_condition,
                        tooltip=['Date', 'Open', 'Close', 'High', 'Low']
                    )
                    
                    # 繪製均線
                    line_87 = base.mark_line(color='orange', strokeWidth=2).encode(y='MA87')
                    line_284 = base.mark_line(color='#00bfff', strokeWidth=2).encode(y='MA284')
                    
                    final_chart = (candles + line_87 + line_284).interactive()
                    st.altair_chart(final_chart, use_container_width=True)
                    st.caption(f"📈 標的股票代碼: {target_code} | 🔶 橘線: 87MA | 🔷 藍線: 284MA")
                else:
                    st.error(f"❌ Yahoo Finance 查無此標的 K 線資料: {target_code}")
            except Exception as e:
                st.warning(f"K 線圖生成失敗: {e}")

        # --- 主程式邏輯 ---
        if 'full_census_data' not in st.session_state:
            st.warning("⚠️ 請先至本頁上方執行「SOP 全市場普查」。")
        else:
            # 讀取並定義基礎變數
            full_data = pd.DataFrame(st.session_state['full_census_data'])
            
            # [修復 NameError] 定義 now 供後續所有 Tab 使用
            from datetime import datetime
            now = datetime.now()
            
            # 確保日期欄位正確
            if 'issue_date' in full_data.columns:
                full_data['issue_date'] = pd.to_datetime(full_data['issue_date'], errors='coerce')

            # [需求] 修改 Tab 列表，新增 "產業風口榜"
            tab1_w9, tab2_w9, tab3_w9, tab4_w9, tab5_w9 = st.tabs([
                "🏆 SOP 菁英榜", "👶 新券蜜月", "💤 滿年沈澱", "🛡️ 賣回保衛", "🔥 產業風口榜"
            ])
            
            # --- Tab 1: SOP 菁英榜 (鄭思翰 SOP 終極美化版) ---
            with tab1_w9:
                # 篩選邏輯
                if 'scan_results' in st.session_state and not st.session_state['scan_results'].empty:
                    df_t1 = st.session_state['scan_results'].head(20)
                else:
                    mask_t1 = (full_data['price'] < 120) & (full_data['trend_status'].str.contains("多頭", na=False))
                    df_t1 = full_data[mask_t1].sort_values('score', ascending=False).head(20)

                if df_t1.empty:
                    st.info("無符合標準標的。")
                else:
                    for _, row in df_t1.iterrows():
                        cb_name = row.get('name', '未知')
                        cb_code = str(row.get('code', row.get('stock_code', '0000'))).strip()
                        
                        # [關鍵修正]: 已轉換率反轉邏輯 (修正 99.99% 錯誤)
                        raw_conv = pd.to_numeric(row.get('conv_rate', row.get('balance_rate', 100)), errors='coerce') or 100.0
                        # 若數值 > 50 視為「餘額比率」，執行反轉；否則視為已轉換率
                        converted_percentage = (100.0 - raw_conv) if raw_conv > 50 else raw_conv
                        if converted_percentage < 0: converted_percentage = 0.0
                        
                        price = pd.to_numeric(row.get('price'), errors='coerce') or 0.0
                        ma87 = pd.to_numeric(row.get('ma87'), errors='coerce') or 0.0
                        ma284 = pd.to_numeric(row.get('ma284'), errors='coerce') or 0.0
                        score = pd.to_numeric(row.get('score'), errors='coerce') or 0

                        title = f"👑 {cb_name} ({cb_code}) | CB價: {price:.1f} | 評分: {int(score)}"
                        with st.expander(title):
                            # 摘要美化
                            st.markdown(f"### 🛡️ 天條檢核: `✅ 價格<120` | `✅ 均線多頭` | `✅ 已轉換率 {converted_percentage:.2f}%`")
                            st.divider()

                            # 詳細報告
                            with st.expander("📄 查看詳細分析報告 (Detailed Report)", expanded=False):
                                st.markdown(f"## 📊 {cb_name} ({cb_code}) 策略分析")
                                
                                st.info("### 1. 核心策略檢核 (The 4 Commandments)")
                                st.markdown(f"1. 價格天條 (<115): {'✅ 通過' if price < 115 else '⚠️ 警戒'} (目前 **{price:.1f}**)")
                                
                                is_bullish = ma87 > ma284
                                st.markdown(f"2. 中期多頭排列: {'✅ 通過' if is_bullish else '⚠️ 整理中'}")
                                st.markdown(f"> 均線數據: 87MA **{ma87:.2f}** {' > ' if is_bullish else ' < '} 284MA **{ma284:.2f}**")
                                
                                st.markdown("3. 身分認證 (Identity): ☐ 領頭羊 / ☐ 風口豬")
                                st.markdown("> 💡 鄭思翰辨別準則：")
                                st.markdown("> * 領頭羊: 產業族群中率先領漲、最強勢的高價指標股(如 2025年底的群聯與PCB族群集體發債)。")
                                st.markdown("> * 風口豬: 處於主流題材風口的二軍低價股 (如 旺宏)，站在風口上連豬都會飛。")
                                
                                st.markdown("4. 發債故事 (Story): ☐ 從無到有 / ☐ 擴產 / ☐ 政策事件")
                                
                                st.success("### 2. 決策輔助 (Decision Support)")
                                conv_price = pd.to_numeric(row.get('conv_price_val', 0.01), errors='coerce')
                                stock_price = pd.to_numeric(row.get('stock_price_real', 0.0), errors='coerce')
                                conv_value = pd.to_numeric(row.get('conv_value_val', 0.0), errors='coerce')
                                # ★ 修正：理論價 = 轉換價值（S行, Index 18）
                                parity = conv_value
                                premium = ((price - conv_value) / conv_value * 100) if conv_value > 0 else 0.0
                                
                                c1, c2, c3 = st.columns(3)
                                c1.metric("理論價 (Parity)", f"{parity:.2f}")
                                c2.metric("溢價率 (Premium)", f"{premium:.2f}%")
                                c3.metric("已轉換比例", f"{converted_percentage:.2f}%")
                                
                                st.markdown("### 4. 交易計畫 (Trading Plan)")
                                st.warning("🕒 關鍵時段：09:00 開盤後30分鐘 (觀察大戶試撮) / 13:25 收盤前25分鐘 (尾盤定勝負)")
                                st.markdown(f"* 🎯 進場佈局: 建議於 105~115 元 區間佈局加碼。")
                                st.markdown(f"* 🚀 加碼時機: 股價帶量突破 87MA 或 284MA 時。")
                                
                                st.markdown("### 5. 出場/風控 (Exit/Risk)")
                                st.markdown(f"* 🛑 停損: CB 跌破 100 元 (保本天條)。")
                                st.markdown(f"* 💰 停利: 目標價 152 元以上，嚴守 「留魚尾」 策略避免過早出場。")
                                
                                st.divider()
                                # [修復] 在報告內正確渲染 K 線圖
                                plot_candle_chart(cb_code)

            # --- Tab 2: 新券蜜月 (Titan V80.18: 鄭思翰 SOP 新券專用版) ---
            with tab2_w9:
                # [篩選邏輯回歸]：上市 < 90 天、價格 < 130、溢價率 < 20、轉換率 < 30
                mask_t2 = (
                    full_data['issue_date'].notna() &
                    ((now - full_data['issue_date']).dt.days < 90) &
                    (full_data['price'] < 130) &
                    (full_data['conv_rate'] < 30) # 這裡 conv_rate 原始資料通常存的是「餘額」
                )
                df_t2 = full_data[mask_t2].sort_values('issue_date', ascending=False)
                
                if df_t2.empty: 
                    st.info("目前無符合「新券蜜月」標準的標的 (上市<90天, 價格<130, 轉換率<30%)。")
                else:
                    for _, row in df_t2.iterrows():
                        # [1. 數據獲取與型別防護]
                        name = row.get('name', '未知')
                        cb_code = str(row.get('code', row.get('stock_code', '0000'))).strip()
                        days_listed = (now - row['issue_date']).days
                        
                        # [關鍵修正]: 已轉換率智慧反轉邏輯 (修正 99.99% 錯誤)
                        # 假設資料源中的 'conv_rate' 實際存的是「餘額比率」
                        raw_balance = pd.to_numeric(row.get('conv_rate', 100), errors='coerce') or 100.0
                        converted_percentage = (100.0 - raw_balance) if raw_balance > 50 else raw_balance
                        if converted_percentage < 0: converted_percentage = 0.0

                        price = pd.to_numeric(row.get('price'), errors='coerce') or 0.0
                        ma87 = pd.to_numeric(row.get('ma87'), errors='coerce') or 0.0
                        ma284 = pd.to_numeric(row.get('ma284'), errors='coerce') or 0.0
                        
                        # 計算決策數據 (理論價與溢價率)
                        conv_price = pd.to_numeric(row.get('conv_price_val', 0.01), errors='coerce')
                        stock_price = pd.to_numeric(row.get('stock_price_real', 0.0), errors='coerce')
                        conv_value = pd.to_numeric(row.get('conv_value_val', 0.0), errors='coerce')
                        # ★ 修正：理論價 = 轉換價值（S行, Index 18）
                        parity = conv_value
                        premium = ((price - conv_value) / conv_value * 100) if conv_value > 0 else 0.0

                        # [2. UI 顯示 - 新券專用卡片]
                        title = f"👶 {name} ({cb_code}) | 上市 {days_listed} 天 | CB價: {price:.1f}"
                        with st.expander(title):
                            
                            # 摘要行: 增大字體與美化
                            st.markdown(f"### 🛡️ 新券檢核: `✅ 上市 {days_listed} 天` | `✅ 價格 < 130` | `✅ 已轉換 {converted_percentage:.2f}%`")
                            st.divider()

                            # [詳細分析報告 - 鄭思翰 SOP 蜜月版]
                            with st.expander("📄 查看蜜月期深度分析 (Honeymoon Report)", expanded=False):
                                st.markdown(f"## 📊 {name} ({cb_code}) 蜜月期戰略")
                                
                                # 區塊 1: 核心策略
                                st.info("### 1. 核心策略檢核 (The 4 Commandments)")
                                st.markdown(f"1. 蜜月期價格: {'✅ 通過' if price < 115 else '⚠️ 監控'} (新券甜蜜區 105-115, 目前 **{price:.1f}**)")
                                
                                # 技術面：新券可能資料不足
                                is_bullish = ma87 > ma284
                                trend_text = "✅ 多頭排列" if is_bullish else ("⚠️ 資料不足或整理中" if ma87 == 0 else "❌ 偏弱")
                                st.markdown(f"2. 中期多頭排列: {trend_text}")
                                if ma87 > 0:
                                    st.markdown(f"> 均線數據: 87MA **{ma87:.2f}** {' > ' if is_bullish else ' < '} 284MA **{ma284:.2f}**")
                                else:
                                    st.caption("(新券上市天數較短，均線指標僅供參考)")
                                
                                st.markdown("3. 身分認證 (Identity): ☐ 領頭羊 / ☐ 風口豬")
                                st.markdown("> 💡 鄭思翰辨別準則：")
                                st.markdown("> * 領頭羊 (Bellwether): 該族群中率先起漲、氣勢最強之標竿 (如 2025 年底群聯帶動的 PCB 族群)。")
                                st.markdown("> * 風口豬 (Wind Pig): 處於主流熱門題材風口 (如 AI、散熱、重電)，站在風口上連豬都會飛。")
                                
                                st.markdown("4. 發債故事 (Story): ☐ 從無到有 / ☐ 擴產 / ☐ 政策事件")
                                
                                # 區塊 2: 決策輔助
                                st.success("### 2. 決策輔助 (Decision Support)")
                                c1, c2, c3 = st.columns(3)
                                c1.metric("理論價 (Parity)", f"{parity:.2f}")
                                c2.metric("溢價率 (Premium)", f"{premium:.2f}%")
                                c3.metric("已轉換比例", f"{converted_percentage:.2f}%")
                                
                                # 區塊 4: 交易計畫
                                st.markdown("### 4. 交易計畫 (Trading Plan)")
                                st.warning("🕒 關鍵時段：09:00 開盤 (觀察大戶試撮氣勢) / 13:25 收盤前 (尾盤定勝負)")
                                st.markdown(f"* 🎯 蜜月期佈局: 新券上市初期若價格在 110 元以下 為極佳安全邊際。")
                                st.markdown(f"* 🚀 加碼時機: 股價帶量突破 87MA 或 284MA。")
                                
                                # 區塊 5: 出場風控
                                st.markdown("### 5. 出場/風控 (Exit/Risk)")
                                st.markdown(f"* 🛑 停損: CB 跌破 100 元 (保本天條，新券下檔有限)。")
                                st.markdown(f"* 💰 停利: 目標價 152 元以上，嚴守 「留魚尾」 策略。")
                                
                                st.divider()
                                # [修復] 呼叫 K 線圖 (自動截取 5 碼轉 4 碼)
                                plot_candle_chart(cb_code)

            # --- Tab 3: 滿年沈澱 (Titan V80.19: 鄭思翰 SOP 滿週年啟動版) ---
            with tab3_w9:
                # [修復] 數據清洗與日期計算
                full_data_t3 = full_data.copy()
                if 'issue_date' in full_data_t3.columns:
                    full_data_t3['issue_date'] = pd.to_datetime(full_data_t3['issue_date'], errors='coerce')
                
                # 計算上市天數
                full_data_t3 = full_data_t3.dropna(subset=['issue_date'])
                full_data_t3['days_old'] = (now - full_data_t3['issue_date']).dt.days
                
                # [核心篩選邏輯修正]
                def check_mask_t3(row):
                    try:
                        if not (350 <= row['days_old'] <= 420): return False
                        p = pd.to_numeric(row.get('price'), errors='coerce') or 0.0
                        if p >= 115 or p <= 0: return False
                        raw_c = pd.to_numeric(row.get('conv_rate', 100), errors='coerce') or 100.0
                        actual_conv = (100.0 - raw_c) if raw_c > 50 else raw_c
                        if actual_conv >= 30: return False
                        return True
                    except:
                        return False

                df_t3 = full_data_t3[full_data_t3.apply(check_mask_t3, axis=1)]
                df_t3 = df_t3.sort_values('days_old', ascending=True)
                
                if df_t3.empty: 
                    st.info("💡 目前無符合「滿年沈澱」標準的標的 (上市滿一年, 價格<115, 轉換率<30%)。")
                else:
                    for _, row in df_t3.iterrows():
                        name = row.get('name', '未知')
                        cb_code = str(row.get('code', row.get('stock_code', '0000'))).strip()
                        days = int(row['days_old'])
                        price = pd.to_numeric(row.get('price'), errors='coerce') or 0.0
                        ma87 = pd.to_numeric(row.get('ma87'), errors='coerce') or 0.0
                        stock_price = pd.to_numeric(row.get('stock_price_real'), errors='coerce') or 0.0
                        raw_c = pd.to_numeric(row.get('conv_rate', 100), errors='coerce') or 100.0
                        converted_percentage = (100.0 - raw_c) if raw_c > 50 else raw_c

                        title = f"💤 {name} ({cb_code}) | 沈澱 {days} 天 (滿週年) | CB價: {price:.1f}"
                        with st.expander(title):
                            is_above_ma87 = stock_price > ma87 if ma87 > 0 else False
                            st.markdown(f"### 🛡️ 沈澱檢核: `✅ 上市 {days} 天` | `✅ 價格 < 115` | `{'✅ 已站上 87MA' if is_above_ma87 else '⚠️ 均線下方'}`")
                            st.divider()

                            with st.expander("📄 查看滿年沈澱深度分析 (Consolidation Report)", expanded=False):
                                st.markdown(f"## 📊 {name} ({cb_code}) 滿年甦醒評估")
                                st.info("### 1. 核心策略檢核 (The 4 Commandments)")
                                st.markdown(f"1. 價格天條 (<115): ✅ 通過 (沈澱期最佳成本區，目前 **{price:.1f}**)")
                                check_trend = "✅ 通過 (已站上 87MA)" if is_above_ma87 else "⚠️ 均線整理中"
                                st.markdown(f"2. 中期多頭排列: {check_trend}")
                                if ma87 > 0:
                                    st.markdown(f"> 均線數據: 現價 **{stock_price:.2f}** {' > ' if is_above_ma87 else ' < '} 87MA **{ma87:.2f}**")
                                st.markdown("3. 身分認證 (Identity): ☐ 領頭羊 / ☐ 風口豬")
                                st.markdown("4. 發債故事 (Story): ☐ 從無到有 / ☐ 擴產 / ☐ 政策事件")
                                st.divider()
                                st.success("### 2. 決策輔助 (Decision Support)")
                                conv_price = pd.to_numeric(row.get('conv_price_val', 0.01), errors='coerce')
                                conv_value = pd.to_numeric(row.get('conv_value_val', 0.0), errors='coerce')
                                # ★ 修正：理論價 = 轉換價值（S行, Index 18）
                                parity = conv_value
                                premium = ((price - conv_value) / conv_value * 100) if conv_value > 0 else 0.0
                                c1, c2, c3 = st.columns(3)
                                c1.metric("理論價 (Parity)", f"{parity:.2f}")
                                c2.metric("溢價率 (Premium)", f"{premium:.2f}%")
                                c3.metric("已轉換比例", f"{converted_percentage:.2f}%")
                                st.markdown("### 4. 交易計畫 (Trading Plan)")
                                st.markdown(f"* 🎯 沈澱期佈局: 滿一年後，股價只要「站穩 87MA」即為首波觀察進場點。")
                                st.markdown(f"* 🚀 加碼時機: 當 87MA 正式由平轉上揚，且股價帶量突破橫盤區間。")
                                st.markdown("### 5. 出場/風控 (Exit/Risk)")
                                st.markdown(f"* 🛑 停損: CB 跌破 100 元 (保本天條)。")
                                st.markdown(f"* 💰 停利: 目標價 152 元以上。")
                                st.divider()
                                plot_candle_chart(cb_code)

            # --- Tab 4: 賣回保衛 (Titan V80.20: 鄭思翰 SOP 套利保衛版) ---
            with tab4_w9:
                full_data_t4 = full_data.copy()
                if 'put_date' in full_data_t4.columns:
                    full_data_t4['put_date'] = pd.to_datetime(full_data_t4['put_date'], errors='coerce')
                full_data_t4['days_to_put'] = (full_data_t4['put_date'] - now).dt.days
                
                def check_mask_t4(row):
                    try:
                        if pd.isna(row['days_to_put']) or not (0 < row['days_to_put'] < 180): return False
                        p = pd.to_numeric(row.get('price'), errors='coerce') or 0.0
                        if not (95 <= p <= 105): return False
                        raw_c = pd.to_numeric(row.get('conv_rate', 100), errors='coerce') or 100.0
                        actual_conv = (100.0 - raw_c) if raw_c > 50 else raw_c
                        if actual_conv >= 30: return False
                        return True
                    except:
                        return False

                df_t4 = full_data_t4[full_data_t4.apply(check_mask_t4, axis=1)]
                df_t4 = df_t4.sort_values('days_to_put', ascending=True)
                
                if df_t4.empty: 
                    st.info("💡 目前無符合「賣回保衛」標準的標的 (距賣回<180天, 價格 95~105, 轉換率<30%)。")
                else:
                    for _, row in df_t4.iterrows():
                        name = row.get('name', '未知')
                        cb_code = str(row.get('code', row.get('stock_code', '0000'))).strip()
                        left_days = int(row['days_to_put'])
                        price = pd.to_numeric(row.get('price'), errors='coerce') or 0.0
                        put_date_str = row['put_date'].strftime('%Y-%m-%d')
                        ma87 = pd.to_numeric(row.get('ma87'), errors='coerce') or 0.0
                        ma284 = pd.to_numeric(row.get('ma284'), errors='coerce') or 0.0
                        stock_price = pd.to_numeric(row.get('stock_price_real'), errors='coerce') or 0.0
                        raw_c = pd.to_numeric(row.get('conv_rate', 100), errors='coerce') or 100.0
                        converted_percentage = (100.0 - raw_c) if raw_c > 50 else raw_c

                        title = f"🛡️ {name} ({cb_code}) | 賣回倒數 {left_days} 天 | CB價: {price:.1f}"
                        with st.expander(title):
                            st.markdown(f"### 🚨 保衛警告: `📅 賣回日: {put_date_str}` | `✅ 價格甜甜圈區間` | `✅ 已轉換 {converted_percentage:.2f}%`")
                            st.divider()

                            with st.expander("📄 查看賣回保衛戰術報告 (Put Protection Report)", expanded=False):
                                st.markdown(f"## 📊 {name} ({cb_code}) 賣回壓力測試")
                                st.error("### 1. 核心策略檢核 (The 4 Commandments)")
                                st.markdown(f"1. 價格天條 (95-105): ✅ 通過 (目前 **{price:.1f}**)")
                                is_bullish = ma87 > ma284
                                st.markdown(f"2. 中期多頭排列: {'✅ 通過' if is_bullish else '⚠️ 整理中'}")
                                st.markdown("3. 身分認證 (Identity): ☐ 領頭羊 / ☐ 風口豬")
                                st.markdown("4. 發債故事 (Story): ☐ 從無到有 / ☐ 擴產 / ☐ 政策事件")
                                st.divider()
                                st.success("### 2. 決策輔助 (Decision Support)")
                                conv_price = pd.to_numeric(row.get('conv_price_val', 0.01), errors='coerce')
                                conv_value = pd.to_numeric(row.get('conv_value_val', 0.0), errors='coerce')
                                # ★ 修正：理論價 = 轉換價值（S行, Index 18）
                                parity = conv_value
                                premium = ((price - conv_value) / conv_value * 100) if conv_value > 0 else 0.0
                                c1, c2, c3 = st.columns(3)
                                c1.metric("距離賣回", f"{left_days} 天")
                                c2.metric("溢價率 (Premium)", f"{premium:.2f}%")
                                c3.metric("目標價", "152+", delta="保本套利")
                                st.markdown("### 4. 交易計畫 (Trading Plan)")
                                st.markdown(f"* 🎯 進場佈局: 此區間 (95-105) 買入，下檔風險極低。")
                                st.markdown(f"* 🚀 爆發點: 觀察賣回日前 2-3 個月，股價站上 87MA 且量增。")
                                st.markdown("### 5. 出場/風控 (Exit/Risk)")
                                st.markdown(f"* 🛑 停損: 原則上不需停損。")
                                st.markdown(f"* 💰 停利: 目標價 152 元以上，或賣回當天執行。")
                                st.divider()
                                plot_candle_chart(cb_code)

            # ==========================================
            # Tab 5: 產業風口地圖 (Titan V103: IC.TPEX 官方 30 大產業鏈)
            # ==========================================
            with tab5_w9:
                st.subheader("🌌 IC.TPEX 官方產業價值矩陣")
                
                # --- 1. 核心數據處理 (官方 30 大分類引擎) ---
                @st.cache_data(ttl=3600)
                def get_tpex_data(raw_df):
                    # TPEx 官方 30 大產業分類標籤 (基準)
                    # 1.半導體 2.通信網路 3.電腦週邊 4.電子零組件 5.光電 6.電子通路 7.資訊服務 8.其他電子
                    # 9.生技醫療 10.紡織纖維 11.電機機械 12.電器電纜 13.化學工業 14.建材營造 15.航運業
                    # 16.觀光事業 17.金融業 18.貿易百貨 19.油電燃氣 20.文化創意 21.鋼鐵工業 22.橡膠工業
                    # 23.塑膠工業 24.汽車工業 25.食品工業 26.造紙工業 27.綠能環保 28.運動休閒 29.居家生活 30.其他

                    # 精準對應字典 (手動定義精華版 - 擴充至 30 類)
                    chain_map = {
                        # [1. 半導體]
                        '世芯': ('半導體', '⬆️ 上游-IC設計', 'IP/ASIC'), '創意': ('半導體', '⬆️ 上游-IC設計', 'IP/ASIC'),
                        '聯發科': ('半導體', '⬆️ 上游-IC設計', '手機SoC'), '瑞昱': ('半導體', '⬆️ 上游-IC設計', '網通IC'),
                        '台積': ('半導體', '↔️ 中游-製造', '晶圓代工'), '聯電': ('半導體', '↔️ 中游-製造', '晶圓代工'),
                        '弘塑': ('半導體', '↔️ 中游-設備', '濕製程'), '辛耘': ('半導體', '↔️ 中游-設備', 'CoWoS'),
                        '萬潤': ('半導體', '↔️ 中游-設備', '封測設備'), '日月光': ('半導體', '⬇️ 下游-封測', '封裝'),
                        
                        # [2. 通信網路]
                        '智邦': ('通信網路', '⬇️ 下游-網通設備', '交換器'), '啟碁': ('通信網路', '⬇️ 下游-網通設備', '衛星/車用'),
                        '中磊': ('通信網路', '⬇️ 下游-網通設備', '寬頻'), '全新': ('通信網路', '⬆️ 上游-元件', 'PA砷化鎵'),
                        '穩懋': ('通信網路', '⬆️ 上游-元件', 'PA代工'), '華星光': ('通信網路', '↔️ 中游-光通訊', 'CPO模組'),
                        '波若威': ('通信網路', '↔️ 中游-光通訊', '光纖元件'), '聯亞': ('通信網路', '↔️ 中游-光通訊', '雷射二極體'),

                        # [3. 電腦週邊]
                        '廣達': ('電腦週邊', '⬇️ 下游-組裝', 'AI伺服器'), '緯創': ('電腦週邊', '⬇️ 下游-組裝', 'AI伺服器'),
                        '技嘉': ('電腦週邊', '⬇️ 下游-品牌', '板卡/Server'), '微星': ('電腦週邊', '⬇️ 下游-品牌', '電競'),
                        '奇鋐': ('電腦週邊', '↔️ 中游-散熱', '3D VC'), '雙鴻': ('電腦週邊', '↔️ 中游-散熱', '水冷板'),
                        '勤誠': ('電腦週邊', '↔️ 中游-機殼', '伺服器機殼'), '川湖': ('電腦週邊', '↔️ 中游-機構', '導軌'),
                        '樺漢': ('電腦週邊', '⬇️ 下游-工業電腦', 'IPC'), '研華': ('電腦週邊', '⬇️ 下游-工業電腦', 'IPC'),

                        # [4. 電子零組件]
                        '台光電': ('電子零組件', '⬆️ 上游-材料', 'CCL銅箔基板'), '台燿': ('電子零組件', '⬆️ 上游-材料', 'CCL高頻'),
                        '金像電': ('電子零組件', '↔️ 中游-PCB', '伺服器板'), '健鼎': ('電子零組件', '↔️ 中游-PCB', 'HDI'),
                        '欣興': ('電子零組件', '↔️ 中游-PCB', 'ABF載板'), '南電': ('電子零組件', '↔️ 中游-PCB', 'ABF載板'),
                        '國巨': ('電子零組件', '↔️ 中游-被動元件', 'MLCC'), '華新科': ('電子零組件', '↔️ 中游-被動元件', 'MLCC'),
                        '凡甲': ('電子零組件', '↔️ 中游-連接器', '車用/Server'), '嘉澤': ('電子零組件', '↔️ 中游-連接器', 'CPU Socket'),

                        # [5. 光電]
                        '大立光': ('光電', '⬆️ 上游-光學', '鏡頭'), '玉晶光': ('光電', '⬆️ 上游-光學', '鏡頭'),
                        '亞光': ('光電', '⬆️ 上游-光學', '車載鏡頭'), '群創': ('光電', '↔️ 中游-面板', 'LCD'),
                        '友達': ('光電', '↔️ 中游-面板', 'LCD'), '中光電': ('光電', '⬇️ 下游-背光', '背光模組'),

                        # [9. 生技醫療]
                        '藥華藥': ('生技醫療', '⬆️ 上游-新藥', '新藥研發'), '合一': ('生技醫療', '⬆️ 上游-新藥', '新藥研發'),
                        '保瑞': ('生技醫療', '↔️ 中游-製造', 'CDMO'), '美時': ('生技醫療', '↔️ 中游-製造', '學名藥'),
                        '晶碩': ('生技醫療', '⬇️ 下游-醫材', '隱形眼鏡'), '視陽': ('生技醫療', '⬇️ 下游-醫材', '隱形眼鏡'),
                        '大樹': ('生技醫療', '⬇️ 下游-通路', '藥局'), '長佳智能': ('生技醫療', '⬆️ 上游-資訊', 'AI醫療'),

                        # [11. 電機機械]
                        '上銀': ('電機機械', '⬆️ 上游-傳動', '滾珠螺桿'), '亞德客': ('電機機械', '⬆️ 上游-氣動', '氣動元件'),
                        '東元': ('電機機械', '↔️ 中游-馬達', '工業馬達'), '中砂': ('電機機械', '⬆️ 上游-耗材', '鑽石碟'),

                        # [14. 建材營造]
                        '華固': ('建材營造', '⬇️ 下游-建設', '住宅商辦'), '長虹': ('建材營造', '⬇️ 下游-建設', '住宅商辦'),
                        '興富發': ('建材營造', '⬇️ 下游-建設', '住宅'), '遠雄': ('建材營造', '⬇️ 下游-建設', '廠辦'),
                        '國產': ('建材營造', '⬆️ 上游-材料', '預拌混凝土'),

                        # [15. 航運業]
                        '長榮': ('航運業', '↔️ 中游-海運', '貨櫃'), '陽明': ('航運業', '↔️ 中游-海運', '貨櫃'),
                        '萬海': ('航運業', '↔️ 中游-海運', '貨櫃'), '長榮航': ('航運業', '↔️ 中游-空運', '航空'),
                        '華航': ('航運業', '↔️ 中游-空運', '航空'), '星宇': ('航運業', '↔️ 中游-空運', '航空'),
                        '慧洋': ('航運業', '↔️ 中游-散裝', '散裝航運'), '裕民': ('航運業', '↔️ 中游-散裝', '散裝航運'),

                        # [24. 汽車工業]
                        '東陽': ('汽車工業', '↔️ 中游-零組件', 'AM保險桿'), '堤維西': ('汽車工業', '↔️ 中游-零組件', 'AM車燈'),
                        '帝寶': ('汽車工業', '↔️ 中游-零組件', 'AM車燈'), '裕隆': ('汽車工業', '⬇️ 下游-整車', '品牌製造'),
                        '中華': ('汽車工業', '⬇️ 下游-整車', '商用車'), '和泰車': ('汽車工業', '⬇️ 下游-代理', 'TOYOTA'),

                        # [27. 綠能環保 (含重電)]
                        '華城': ('綠能環保', '↔️ 中游-重電', '變壓器'), '士電': ('綠能環保', '↔️ 中游-重電', '配電盤'),
                        '中興電': ('綠能環保', '↔️ 中游-重電', 'GIS開關'), '亞力': ('綠能環保', '↔️ 中游-重電', '輸配電'),
                        '世紀鋼': ('綠能環保', '⬆️ 上游-風電', '水下基礎'), '森崴': ('綠能環保', '⬇️ 下游-能源', '綠電開發'),
                        '雲豹': ('綠能環保', '⬇️ 下游-能源', '儲能/太陽能'),

                        # [30. 其他 (含軍工)]
                        '漢翔': ('其他', '↔️ 中游-航太', '軍工/民航'), '龍德': ('其他', '↔️ 中游-造船', '軍艦'),
                    }
                    
                    def classify(name):
                        # 1. 字典精準匹配
                        for k, v in chain_map.items():
                            if k in name: return v
                        
                        # 2. 關鍵字模糊歸類 (對標官方 30 大)
                        # 半導體
                        if any(x in name for x in ['電', '科', '矽', '晶', '半']): 
                            if '光' in name: return ('光電', '一般光電', '光電')
                            return ('半導體', '其他半導體', '半導體')
                        # 通信網路
                        if any(x in name for x in ['網', '通', '訊']): return ('通信網路', '網通設備', '通信')
                        # 電腦週邊
                        if any(x in name for x in ['腦', '機', '資']): return ('電腦週邊', '系統', '電腦')
                        # 電子零組件
                        if any(x in name for x in ['板', '線', '器', '零']): return ('電子零組件', '被動/連接', '零組件')
                        # 生技醫療
                        if any(x in name for x in ['生', '醫', '藥']): return ('生技醫療', '生技', '醫療')
                        # 綠能環保
                        if any(x in name for x in ['綠', '能', '源', '電', '華城', '重電']): return ('綠能環保', '能源', '綠能')
                        # 航運
                        if any(x in name for x in ['航', '運', '船']): return ('航運業', '運輸', '航運')
                        # 建材營造
                        if any(x in name for x in ['營', '建', '地']): return ('建材營造', '建設', '營造')
                        # 金融
                        if any(x in name for x in ['金', '銀', '保']): return ('金融業', '金融', '金控')
                        # 汽車
                        if any(x in name for x in ['車', '汽']): return ('汽車工業', '零組件', '汽車')
                        
                        return ('其他', '未分類', '其他')

                    d = raw_df.copy()
                    d[['L1', 'L2', 'L3']] = d['name'].apply(lambda x: pd.Series(classify(x)))
                    
                    # 數值清洗 (Sanitization) - 照抄原版邏輯
                    d['ma87'] = pd.to_numeric(d['ma87'], errors='coerce')
                    d['price'] = pd.to_numeric(d['stock_price_real'], errors='coerce')
                    # 若無 MA87，乖離率設為 0 (灰色)
                    d['bias'] = ((d['price'] - d['ma87']) / d['ma87'] * 100)
                    d['bias_clean'] = d['bias'].fillna(0).clip(-25, 25) # 限制顏色範圍
                    d['bias_label'] = d['bias'].apply(lambda x: f"{x:+.1f}%" if pd.notnull(x) else "N/A")
                    d['size_metric'] = d['price'].fillna(10) # 暫用股價當方塊大小
                    
                    return d

                df_galaxy = get_tpex_data(full_data)

                # --- 2. 繪製 Plotly 熱力圖 (照抄原版 UI) ---
                fig = px.treemap(
                    df_galaxy,
                    path=['L1', 'L2', 'L3', 'name'],
                    values='size_metric',
                    color='bias_clean',
                    color_continuous_scale=['#00FF00', '#262730', '#FF0000'], # 綠跌 -> 黑平 -> 紅漲
                    color_continuous_midpoint=0,
                    hover_data={'name':True, 'bias_label':True, 'L3':True, 'size_metric':False, 'bias_clean':False},
                    title='<b>🎯 資金流向熱力圖 (IC.TPEX 官方分類版)</b>'
                )
                fig.update_layout(margin=dict(t=30, l=10, r=10, b=10), height=500, font=dict(size=14))
                fig.update_traces(
                    textinfo="label+text", 
                    texttemplate="%{label}<br>%{customdata[1]}", # 顯示名稱 + 乖離率
                    textposition="middle center"
                )
                st.plotly_chart(fig, use_container_width=True)

                st.divider()

                # --- 3. 全軍戰力排行榜 (TPEx 30大戰區 結構化分組) ---
                st.subheader("🏆 全產業戰力排行榜 (Sector Roster)")
                st.info("💡 點擊下方官方產業板塊，展開查看「上中下游」兵力部署")

                # 計算各板塊平均強弱，並排序
                sector_stats = df_galaxy.groupby('L1')['bias'].mean().sort_values(ascending=False)
                
                # 遍歷排序後的板塊
                for sector, avg_bias in sector_stats.items():
                    # 找出該板塊所有股票
                    sector_df = df_galaxy[df_galaxy['L1'] == sector]
                    count = len(sector_df)
                    if count == 0: continue # 跳過無兵力的戰區

                    bulls = len(sector_df[sector_df['bias'] > 0])
                    
                    # 標題設計 (名次感)
                    header_color = "🔴" if avg_bias > 0 else "🟢"
                    header = f"{header_color} **{sector}** (均 {avg_bias:+.1f}%) | 強勢 {bulls}/{count} 檔"
                    
                    with st.expander(header):
                        # 核心：依照 L2 (上中下游) 分組顯示
                        l2_groups = sector_df.groupby('L2')
                        
                        # 簡單排序：字串排序 (上游 > 下游 > 中游... 中文排序不準，這裡直接遍歷 keys)
                        # 為了符合人類直覺，我們嘗試把 "上游" 排前面
                        sorted_l2 = sorted(l2_groups.groups.keys(), key=lambda x: 0 if '上' in str(x) else (1 if '中' in str(x) else 2))

                        for l2 in sorted_l2:
                            sub_df = l2_groups.get_group(l2).sort_values('bias', ascending=False)
                            st.markdown(f"**{l2}**") # 顯示分組標題 (如 ⬆️ 上游-IC設計)
                            
                            # 製作漂亮的表格或條列 (照抄原版)
                            cols = st.columns(3) 
                            for idx, row in sub_df.iterrows():
                                color = "red" if row['bias'] > 0 else "#00FF00"
                                label = row['bias_label']
                                # 格式： 3661 世芯 (+5.2%)
                                st.markdown(f"<span style='color:{color}; font-weight:bold;'>{row['code']} {row['name']}</span> <span style='color:#aaa; font-size:0.9em;'>({label})</span>", unsafe_allow_html=True)
                            st.markdown("---")
        
    with st.expander("2.3 潛在風險雷達 (Risk Radar)", expanded=False):
        if 'scan_results' in st.session_state and not df.empty:
            scan_results = st.session_state['scan_results']
            st.info("此區塊為「負面表列」清單，旨在警示符合特定風險條件的標的，提醒您「避開誰」。")

            required_risk_cols = ['converted_ratio', 'premium', 'avg_volume']
            if all(col in scan_results.columns for col in required_risk_cols):
                
                tab1_w13, tab2_w13, tab3_w13 = st.tabs(["**☠️ 籌碼鬆動 (主力落跑)**", "**⚠️ 高溢價 (肉少湯喝)**", "**🧊 流動性陷阱 (殭屍債)**"])

                with tab1_w13:
                    abandoned_df = scan_results[scan_results['converted_ratio'] > 30].sort_values('converted_ratio', ascending=False)
                    if not abandoned_df.empty:
                        st.warning(f"發現 {len(abandoned_df)} 檔標的「已轉換比例」 > 30%，特定人可能已在下車。")
                        st.dataframe(abandoned_df[['name', 'code', 'converted_ratio', 'price', 'action']].head(20).fillna(''))
                    else:
                        st.success("✅ 目前無標的觸發「籌碼鬆動」警示。")

                with tab2_w13:
                    overpriced_df = scan_results[scan_results['premium'] > 20].sort_values('premium', ascending=False)
                    if not overpriced_df.empty:
                        st.warning(f"發現 {len(overpriced_df)} 檔標的「溢價率」 > 20%，潛在報酬空間可能受壓縮。")
                        st.dataframe(overpriced_df[['name', 'code', 'premium', 'price', 'parity']].head(20).fillna(0))
                    else:
                        st.success("✅ 目前無標的觸發「高溢價」警示。")

                with tab3_w13:
                    illiquid_df = scan_results[scan_results['avg_volume'] < 10].sort_values('avg_volume', ascending=True)
                    if not illiquid_df.empty:
                        st.error(f"發現 {len(illiquid_df)} 檔標的平均成交量 < 10 張，存在嚴峻的流動性風險！")
                        st.dataframe(illiquid_df[['name', 'code', 'avg_volume', 'price']].head(20).fillna(0))
                    else:
                        st.success("✅ 目前無標的觸發「流動性陷阱」警示。")
            else:
                st.error("掃描結果缺少風險分析所需欄位 (converted_ratio, premium, avg_volume)，請檢查上傳的 Excel 檔案。")
        else:
            st.info("請先執行本頁上方的掃描以啟動風險雷達。")
        
    with st.expander("2.4 資金配置試算 (Position Sizing)", expanded=False):
        # [修正] 直接檢查 scan_results 是否有資料，不再依賴 'action' 欄位
        if 'scan_results' in st.session_state and not st.session_state['scan_results'].empty:
            
            # 視窗 8 篩選出來的結果，就是建議買進名單
            buy_recommendations = st.session_state['scan_results']
            
            st.success(f"已同步獵殺結果：共 {len(buy_recommendations)} 檔可配置標的")

            total_capital = st.number_input("輸入您的總操作資金 (元)", min_value=100000, value=2000000, step=100000)
            
            if not buy_recommendations.empty:
                st.subheader("建議投資組合 (Top 5)")
                portfolio_list = []
                
                # 依分數排序，若無分數則依價格
                sort_col = 'score' if 'score' in buy_recommendations.columns else 'price'
                top_picks = buy_recommendations.sort_values(sort_col, ascending=False).head(5)

                for _, row in top_picks.iterrows():
                    cb_price = row.get('price', 0)
                    name = row.get('name', '未知')
                    code = row.get('code', '0000')
                    
                    if cb_price > 0:
                        # 簡單資金模型：每檔 20%
                        investment_per_stock = total_capital * 0.20
                        # 試算張數 (一張 1000 股，價格單位為元?? 通常 CB 價格是百元報價，一張十萬)
                        # 修正：CB 報價通常為 100-120，一張面額 10 萬，市值約 10-12 萬
                        # 這裡假設 cb_price 是 106.0 這種格式 -> 一張市值 = cb_price * 1000
                        market_value_per_unit = cb_price * 1000
                        num_shares = investment_per_stock / market_value_per_unit
                        
                        portfolio_list.append(
                            f"- **{name} ({code})** | 市價 `{cb_price}` | "
                            f"建議配置 `{int(num_shares)}` 張 (約 {int(investment_per_stock):,} 元)"
                        )
                st.markdown("\n".join(portfolio_list))
            else:
                st.info("目前無符合 SOP 標準之標的。")
        else:
            st.info("請先執行本頁上方的掃描以獲取買進建議。")
