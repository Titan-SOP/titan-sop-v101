# ui_desktop/layout.py
# Titan SOP V100.0 — Titan OS Launcher (Final Debug Edition)
# 功能：六大戰區啟動器 (Grid Launcher) + 真實錯誤揭露
# 風格：戰情室大按鈕 (Big Buttons)

import streamlit as st
import importlib
import sys
import os
import traceback
from datetime import datetime

# 確保根目錄在 sys.path，這樣才能 import 根目錄的引擎檔案
_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _root not in sys.path:
    sys.path.insert(0, _root)

# 嘗試載入 UI 工具
try:
    from utils_ui import inject_css, create_glowing_title, render_sidebar_utilities
except ImportError:
    # Fallback if utils_ui is broken
    def inject_css(mode): pass
    def create_glowing_title(t): return f"<h1>{t}</h1>"
    def render_sidebar_utilities(): pass

# ═══════════════════════════════════════════════════════════════
#  核心：模組動態載入器 (不再隱藏錯誤！)
# ═══════════════════════════════════════════════════════════════
def _load_and_run_module(module_name):
    """
    嘗試載入並執行模組。
    如果失敗，會顯示詳細錯誤，而不是說找不到檔案。
    """
    # 注入桌面版 CSS
    inject_css("desktop")
    
    # 頂部導航列
    c1, c2 = st.columns([1, 6])
    with c1:
        if st.button("🏠 返回總部", type="primary", use_container_width=True):
            st.session_state.active_tab = None
            st.rerun()
    with c2:
        st.markdown(f"### 正在執行: {module_name}")
    
    st.divider()

    # 嘗試 Import
    try:
        # 優先嘗試從 ui_desktop 載入
        full_module_name = f"ui_desktop.{module_name}"
        
        if full_module_name in sys.modules:
            mod = importlib.reload(sys.modules[full_module_name])
        else:
            mod = importlib.import_module(full_module_name)
            
        # 執行 render()
        if hasattr(mod, 'render'):
            mod.render()
        else:
            st.error(f"❌ 模組 {module_name} 載入成功，但找不到 render() 函數！")
            
    except ImportError as e:
        # 這邊會顯示真正的 ImportError (例如: No module named 'strategy')
        st.error(f"❌ 模組載入失敗 (Import Error)")
        st.error(f"原因: {str(e)}")
        st.info("💡 提示：這通常是因為該模組依賴的檔案 (如 strategy.py, macro_risk.py) 不在根目錄中。")
        with st.expander("🔍 查看詳細錯誤堆疊"):
            st.code(traceback.format_exc())
            
    except Exception as e:
        st.error(f"❌ 模組執行時發生錯誤: {e}")
        with st.expander("🔍 查看詳細錯誤堆疊"):
            st.code(traceback.format_exc())

# ═══════════════════════════════════════════════════════════════
#  頁面：戰情室首頁 (Launcher)
# ═══════════════════════════════════════════════════════════════
def render_launcher():
    """顯示 6 大戰區啟動按鈕"""
    inject_css("desktop")  # 使用桌面樣式
    
    st.markdown(create_glowing_title("🏛️ Titan OS 戰情指揮中心"), unsafe_allow_html=True)
    st.caption(f"系統就緒 | {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    st.markdown("---")

    # 建立 2x3 的按鈕矩陣 (CSS 會讓按鈕變大)
    # 這裡我們使用 columns 來排版
    
    # Row 1
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("### 🛡️ 宏觀風控")
        if st.button("進入 Tab 1", key="btn_t1", use_container_width=True):
            st.session_state.active_tab = "tab1_macro"
            st.rerun()
    with c2:
        st.markdown("### 📡 獵殺雷達")
        if st.button("進入 Tab 2", key="btn_t2", use_container_width=True):
            st.session_state.active_tab = "tab2_radar"
            st.rerun()
    with c3:
        st.markdown("### 🎯 單兵狙擊")
        if st.button("進入 Tab 3", key="btn_t3", use_container_width=True):
            st.session_state.active_tab = "tab3_sniper"
            st.rerun()

    st.markdown("---") # 分隔線

    # Row 2
    c4, c5, c6 = st.columns(3)
    with c4:
        st.markdown("### ⚖️ 全球決策")
        if st.button("進入 Tab 4", key="btn_t4", use_container_width=True):
            st.session_state.active_tab = "tab4_decision"
            st.rerun()
    with c5:
        st.markdown("### 📚 戰略百科")
        if st.button("進入 Tab 5", key="btn_t5", use_container_width=True):
            st.session_state.active_tab = "tab5_wiki"
            st.rerun()
    with c6:
        st.markdown("### 🌌 元趨勢")
        if st.button("進入 Tab 6", key="btn_t6", use_container_width=True):
            st.session_state.active_tab = "tab6_metatrend"
            st.rerun()

# ═══════════════════════════════════════════════════════════════
#  主程式入口
# ═══════════════════════════════════════════════════════════════
def render():
    # 初始化狀態
    if 'active_tab' not in st.session_state:
        st.session_state.active_tab = None  # None 代表在首頁 (Launcher)

    # 側邊欄
    render_sidebar_utilities()

    # 路由判斷
    if st.session_state.active_tab is None:
        render_launcher()
    else:
        _load_and_run_module(st.session_state.active_tab)