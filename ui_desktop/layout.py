# ui_desktop/layout.py
# Titan SOP V100.0 - Desktop UI Layout (PHASE 1 OVERHAUL)
# CRITICAL: UNLOCK Tabs 3, 4, 5, 6

import streamlit as st
import pandas as pd
from utils_ui import inject_css, create_glowing_title, render_sidebar_utilities
from data_engine import load_cb_data_from_upload

# [PHASE 1] Import with error handling
try:
    from ui_desktop import tab1_macro
except:
    tab1_macro = None

try:
    from ui_desktop import tab2_radar
except:
    tab2_radar = None

try:
    from ui_desktop import tab3_sniper
except:
    tab3_sniper = None

try:
    from ui_desktop import tab4_decision
except:
    tab4_decision = None

try:
    from ui_desktop import tab6_metatrend
except:
    tab6_metatrend = None


def render():
    """渲染桌面版 UI - [PHASE 1 OVERHAUL] UNLOCK Tabs 3-6"""
    
    inject_css("desktop")
    
    # ==========================================
    # 側邊欄設定
    # ==========================================
    
    with st.sidebar:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%); 
                    padding: 10px 15px; border-radius: 10px; text-align: center; margin-bottom: 15px;">
            <div style="color: #000000; font-weight: bold; font-size: 14px;">⚡ 側邊欄控制中心 ⚡</div>
            <div style="color: #333333; font-size: 12px; margin-top: 5px;">上傳數據 | 設定 API | 快速操作</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(create_glowing_title("⚙️ 系統設定"), unsafe_allow_html=True)
        
        if st.button("🔄 切換模式", use_container_width=True):
            st.session_state.device_mode = None
            st.session_state.choice_confirmed = False
            st.rerun()
        
        st.divider()
        st.header("📂 CB 資料上傳")
        
        uploaded_file = st.file_uploader(
            "上傳 CB 清單 (Excel/CSV)",
            type=['csv', 'xlsx'],
            help="需包含：代號、名稱、標的股票代號、可轉債市價"
        )
        
        if uploaded_file:
            with st.spinner("正在載入數據..."):
                df = load_cb_data_from_upload(uploaded_file)
                
                if df is not None and not df.empty:
                    st.session_state.df = df
                    st.success(f"✅ 載入 {len(df)} 筆 CB")
                    st.metric("總數量", len(df))
                    if 'close' in df.columns:
                        avg_price = df['close'].mean()
                        st.metric("平均市價", f"{avg_price:.2f}")
        
        st.divider()
        st.header("🔑 AI 功能")
        
        api_key = st.text_input(
            "Gemini API Key (選填)",
            type="password",
            value=st.session_state.api_key,
            help="啟用 AI 辯論功能需要 API Key"
        )
        
        if api_key:
            st.session_state.api_key = api_key
            st.success("✅ API Key 已設定")
        
        # [PHASE 1] Use utility function
        render_sidebar_utilities()
    
    # ==========================================
    # 主標題
    # ==========================================
    
    st.markdown(create_glowing_title("🏛️ Titan SOP V100.0 - Desktop War Room"), unsafe_allow_html=True)
    st.caption("Bloomberg Terminal Style | 專業級可轉債獵殺系統")
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, #2a2a2a 0%, #1a1a2a 100%); 
                padding: 15px 20px; border-radius: 10px; border-left: 4px solid #FFD700; margin-bottom: 20px;">
        <div style="display: flex; align-items: center; gap: 15px;">
            <div style="font-size: 32px;">👈</div>
            <div>
                <div style="color: #FFD700; font-size: 16px; font-weight: bold; margin-bottom: 5px;">
                    💡 找不到上傳按鈕？
                </div>
                <div style="color: #AAAAAA; font-size: 14px;">
                    請點擊左上角的 <strong style="color: #FFFFFF;">「>」符號</strong> 展開側邊欄
                </div>
                <div style="color: #00FF00; font-size: 13px; margin-top: 5px;">
                    📂 CB 資料上傳 | 🔑 API Key 設定 | 🧹 快速操作
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ==========================================
    # [PHASE 1 CRITICAL] 6 個 Tab - UNLOCK Strategy
    # ==========================================
    
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🛡️ 宏觀風控",
        "🏹 獵殺雷達",
        "🎯 單兵狙擊",
        "🚀 全球決策",
        "📚 戰略百科",
        "🧠 元趨勢戰法"
    ])
    
    # Tab 1 & 2: LOCK (需要數據)
    with tab1:
        if st.session_state.df.empty:
            st.info("📂 請先在側邊欄上傳 CB 清單以使用宏觀風控功能")
        else:
            if tab1_macro:
                try:
                    tab1_macro.render()
                except Exception as e:
                    st.error(f"Tab 1 渲染失敗: {e}")
            else:
                st.warning("Tab 1 模組未找到")
    
    with tab2:
        if st.session_state.df.empty:
            st.info("📂 請先在側邊欄上傳 CB 清單以使用獵殺雷達功能")
        else:
            if tab2_radar:
                try:
                    tab2_radar.render()
                except Exception as e:
                    st.error(f"Tab 2 渲染失敗: {e}")
            else:
                st.warning("Tab 2 模組未找到")
    
    # Tab 3, 4, 5, 6: UNLOCK (無需數據)
    with tab3:
        if tab3_sniper:
            try:
                tab3_sniper.render()
            except Exception as e:
                st.error(f"Tab 3 渲染失敗: {e}")
        else:
            render_tab3_placeholder()
    
    with tab4:
        if tab4_decision:
            try:
                tab4_decision.render()
            except Exception as e:
                st.error(f"Tab 4 渲染失敗: {e}")
        else:
            render_tab4_placeholder()
    
    with tab5:
        render_tab5_placeholder()
    
    with tab6:
        if tab6_metatrend:
            try:
                tab6_metatrend.render()
            except Exception as e:
                st.error(f"Tab 6 渲染失敗: {e}")
        else:
            render_tab6_placeholder()


# ==========================================
# Placeholder Functions
# ==========================================

def render_tab3_placeholder():
    """Tab 3 佔位符"""
    st.subheader("🎯 單兵狙擊 (Phase 1 Skeleton)")
    
    ticker_input = st.text_input("輸入股票代號", placeholder="例如：2330, NVDA")
    
    if ticker_input and st.button("🔍 查詢"):
        st.info(f"🚧 Phase 1: K 線圖與回測功能尚未完整移植 (標的: {ticker_input})")


def render_tab4_placeholder():
    """Tab 4 佔位符"""
    st.subheader("🚀 全球決策 (Phase 1 Skeleton)")
    
    ticker_input = st.text_input("輸入分析標的", placeholder="例如：2330", key="tab4_ticker")
    
    if ticker_input and st.button("🤖 啟動 AI 辯論"):
        st.info(f"🚧 Phase 1: AI 參謀本部尚未完整移植 (標的: {ticker_input})")


def render_tab5_placeholder():
    """Tab 5 佔位符"""
    st.subheader("📚 戰略百科 (Phase 1 Skeleton)")
    
    st.info("""
### 🚧 功能規劃

**知識庫內容**:
- SOP 核心策略
- 20 條第一性原則
- 時間套利事件
- 發債故事關鍵字

**未來功能**:
- 知識庫搜索
- 策略案例庫
- 歷史回測資料庫
""")


def render_tab6_placeholder():
    """Tab 6 佔位符"""
    st.subheader("🧠 元趨勢戰法 (Phase 1 Skeleton)")
    
    ticker_input = st.text_input("輸入掃描標的", placeholder="例如：2330", key="tab6_ticker")
    
    if ticker_input and st.button("📐 計算 7D 幾何"):
        from core_logic import compute_7d_geometry, titan_rating_system
        
        geo_data = compute_7d_geometry(ticker_input)
        rating = titan_rating_system(geo_data)
        
        st.write(f"**評級**: {rating[0]} - {rating[1]}")
        st.caption(rating[2])