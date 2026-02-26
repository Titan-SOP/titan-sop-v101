# ui_desktop/layout.py
# Titan SOP V100.0 — Titan OS Launcher
# 功能：六大戰區啟動器 + 側邊欄模式切換

import streamlit as st
import importlib
import sys
import os
import traceback
from datetime import datetime

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _root not in sys.path:
    sys.path.insert(0, _root)

try:
    from utils_ui import inject_css, create_glowing_title, render_sidebar_utilities
except ImportError:
    def inject_css(mode): pass
    def create_glowing_title(t): return f"<h1>{t}</h1>"
    def render_sidebar_utilities(): pass


def _load_and_run_module(module_name):
    inject_css("desktop")
    c1, c2 = st.columns([1, 6])
    with c1:
        if st.button("🏠 返回總部", type="primary", use_container_width=True):
            st.session_state.active_tab = None
            st.rerun()
    with c2:
        st.markdown(f"### 正在執行: {module_name}")
    st.divider()
    try:
        full_module_name = f"ui_desktop.{module_name}"
        if full_module_name in sys.modules:
            mod = importlib.reload(sys.modules[full_module_name])
        else:
            mod = importlib.import_module(full_module_name)
        if hasattr(mod, 'render'):
            mod.render()
        else:
            st.error(f"❌ 模組 {module_name} 找不到 render() 函數！")
    except ImportError as e:
        st.error(f"❌ 模組載入失敗 (Import Error)")
        st.error(f"原因: {str(e)}")
        with st.expander("🔍 查看詳細錯誤堆疊"):
            st.code(traceback.format_exc())
    except Exception as e:
        st.error(f"❌ 模組執行時發生錯誤: {e}")
        with st.expander("🔍 查看詳細錯誤堆疊"):
            st.code(traceback.format_exc())


def render_launcher():
    inject_css("desktop")
    st.markdown(create_glowing_title("🏛️ Titan OS 戰情指揮中心"), unsafe_allow_html=True)
    st.caption(f"系統就緒 | {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("### 🛡️ 宏觀風控")
        if st.button("進入 Tab 1", key="btn_t1", use_container_width=True):
            st.session_state.active_tab = "tab1_macro"; st.rerun()
    with c2:
        st.markdown("### 📡 CB雷達")
        if st.button("進入 Tab 2", key="btn_t2", use_container_width=True):
            st.session_state.active_tab = "tab2_radar"; st.rerun()
    with c3:
        st.markdown("### 🎯 個股狙擊")
        if st.button("進入 Tab 3", key="btn_t3", use_container_width=True):
            st.session_state.active_tab = "tab3_sniper"; st.rerun()
    st.markdown("---")
    c4, c5, c6 = st.columns(3)
    with c4:
        st.markdown("### ⚖️ 部位回測")
        if st.button("進入 Tab 4", key="btn_t4", use_container_width=True):
            st.session_state.active_tab = "tab4_decision"; st.rerun()
    with c5:
        st.markdown("### 🔍 通用分析")
        if st.button("進入 Tab 5", key="btn_t5", use_container_width=True):
            st.session_state.active_tab = "tab5_wiki"; st.rerun()
    with c6:
        st.markdown("### 🌌 元趨勢")
        if st.button("進入 Tab 6", key="btn_t6", use_container_width=True):
            st.session_state.active_tab = "tab6_metatrend"; st.rerun()


def render():
    if 'active_tab' not in st.session_state:
        st.session_state.active_tab = None

    render_sidebar_utilities()

    # ── 側邊欄：全局控制中心 ──────────────────────────────────
    with st.sidebar:
        # ── 1. 數據引擎切換開關 (桌面版) ──
        st.markdown(
            '<div style="font-size:11px;color:rgba(160,180,220,0.4);' 
            'letter-spacing:2px;text-transform:uppercase;margin-bottom:8px;">' 
            '⬡ 數據連線引擎</div>',
            unsafe_allow_html=True
        )
        current_mode = st.session_state.get("DATA_MODE", "Guest")
        is_quantum = st.toggle("⚡ 啟動 Quantum API", value=(current_mode == "Quantum"), key="desktop_api_toggle")
        
        if is_quantum and current_mode != "Quantum":
            st.session_state["DATA_MODE"] = "Quantum"
            st.rerun()
        elif not is_quantum and current_mode == "Quantum":
            st.session_state["DATA_MODE"] = "Guest"
            st.rerun()
            
        st.markdown("---")

        # ── 2. 切換到手機版 ──
        st.markdown(
            '<div style="font-size:11px;color:rgba(160,180,220,0.4);' 
            'letter-spacing:2px;text-transform:uppercase;margin-bottom:8px;">' 
            '⬡ 介面模式</div>',
            unsafe_allow_html=True
        )
        if st.button("📱  切換到手機版", use_container_width=True, key="desk_switch_mobile"):
            st.session_state.device_mode      = "mobile"
            st.session_state.choice_confirmed  = True
            st.session_state.active_tab        = None
            st.rerun()
        st.markdown(
            '<div style="font-size:9px;color:rgba(160,180,220,0.2);' 
            'margin-top:6px;letter-spacing:1px;">目前：🖥️ Desktop Mode</div>',
            unsafe_allow_html=True
        )

    if st.session_state.active_tab is None:
        render_launcher()
    else:
        _load_and_run_module(st.session_state.active_tab)
