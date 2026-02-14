# ui_desktop/layout.py
import streamlit as st
import pandas as pd
import sys, os
from datetime import datetime

# 確保根目錄在 sys.path（讓 tab 模組能被找到）
_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _root not in sys.path:
    sys.path.insert(0, _root)

from utils_ui import inject_css, create_glowing_title

try:
    from data_engine import load_cb_data_from_upload
except ImportError:
    load_cb_data_from_upload = None


def _import_tab(name):
    import importlib
    for attempt in [f"ui_desktop.{name}", name]:
        try:
            return importlib.import_module(attempt)
        except ImportError:
            continue
    return None


_tab1 = _import_tab("tab1_macro")
_tab2 = _import_tab("tab2_radar")
_tab3 = _import_tab("tab3_sniper")
_tab4 = _import_tab("tab4_decision")
_tab5 = _import_tab("tab5_wiki")
_tab6 = _import_tab("tab6_metatrend")


def _render_sidebar():
    with st.sidebar:
        st.markdown(create_glowing_title("⚙️ Titan V100"), unsafe_allow_html=True)

        if st.button("📱 切換至手機版", use_container_width=True, key="layout_switch_mobile"):
            st.session_state.device_mode     = "mobile"
            st.session_state.choice_confirmed = True
            st.rerun()

        st.divider()
        st.header("📂 CB 資料上傳")
        f = st.file_uploader("CB 清單 (Excel/CSV)", type=['csv','xlsx'], key="layout_cb_upload")
        if f and load_cb_data_from_upload:
            with st.spinner("載入…"):
                df = load_cb_data_from_upload(f)
                if df is not None and not df.empty:
                    st.session_state.df = df
                    st.success(f"✅ {len(df)} 筆 CB")
        df_cur = st.session_state.get('df', pd.DataFrame())
        if not df_cur.empty:
            st.caption(f"📊 {len(df_cur)} 筆 CB")

        st.divider()
        st.header("🔑 AI 功能")
        api_key = st.text_input("Gemini API Key (選填)", type="password",
                                value=st.session_state.get('api_key',''), key="layout_api_key")
        st.session_state.api_key = api_key

        st.divider()
        st.header("🕵️ 情報上傳")
        intel = st.file_uploader("情報文件 (PDF/TXT)", type=['pdf','txt'],
                                  accept_multiple_files=True, key="layout_intel")
        st.session_state.intel_files = intel or []

        st.divider()
        if st.button("🗑️ 清除快取", use_container_width=True, key="layout_clear_cache"):
            st.cache_data.clear(); st.cache_resource.clear()
            st.toast("快取已清除 ✅")
        st.caption(f"V100.0 | {datetime.now().strftime('%Y-%m-%d %H:%M')}")


def render():
    inject_css("desktop")
    _render_sidebar()
    st.markdown(create_glowing_title("🏛️ Titan SOP V100.0 — 全自動戰情室"), unsafe_allow_html=True)
    st.markdown("---")

    t1, t2, t3, t4, t5, t6 = st.tabs([
        "🛡️ 宏觀大盤", "🏹 獵殺雷達", "🎯 單兵狙擊",
        "🚀 全球決策", "📚 戰略百科", "🧠 元趨勢戰法",
    ])

    def _safe(mod, num):
        if mod is None:
            st.warning(f"⚠️ Tab {num} 模組未找到，請確認檔案已上傳至根目錄")
            return
        try:
            mod.render()
        except Exception as e:
            st.error(f"Tab {num} 錯誤: {e}")
            with st.expander("錯誤詳情"):
                import traceback; st.code(traceback.format_exc())

    with t1: _safe(_tab1, 1)
    with t2: _safe(_tab2, 2)
    with t3: _safe(_tab3, 3)
    with t4: _safe(_tab4, 4)
    with t5: _safe(_tab5, 5)
    with t6: _safe(_tab6, 6)