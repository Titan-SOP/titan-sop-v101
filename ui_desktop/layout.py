# ui_desktop/layout.py
# Titan SOP V100.0 — Desktop UI Layout

import streamlit as st
import pandas as pd
import importlib
import sys, os
from datetime import datetime

# 確保根目錄在 sys.path
_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _root not in sys.path:
    sys.path.insert(0, _root)

try:
    from data_engine import load_cb_data_from_upload
except ImportError:
    load_cb_data_from_upload = None

try:
    from utils_ui import inject_css, create_glowing_title
except ImportError:
    def inject_css(mode="desktop"): pass
    def create_glowing_title(t, c="#FFD700"): return f"<h2>{t}</h2>"


# ═══════════════════════════════════════════════════════════════
#  每個 Tab 獨立 import（不互相影響）
#  優先 ui_desktop 子包，失敗才找根目錄
# ═══════════════════════════════════════════════════════════════
def _load_tab(name):
    """優先從 ui_desktop 載入，找不到才試根目錄"""
    for path in [f"ui_desktop.{name}", name]:
        try:
            return importlib.import_module(path)
        except ImportError:
            continue
    return None

tab1 = _load_tab("tab1_macro")
tab2 = _load_tab("tab2_radar")
tab3 = _load_tab("tab3_sniper")
tab4 = _load_tab("tab4_decision")
tab5 = _load_tab("tab5_wiki")
tab6 = _load_tab("tab6_metatrend")


# ═══════════════════════════════════════════════════════════════
#  側邊欄
# ═══════════════════════════════════════════════════════════════
def _render_sidebar():
    with st.sidebar:
        st.markdown(create_glowing_title("⚙️ Titan V100"), unsafe_allow_html=True)

        if st.button("📱 切換至手機版", use_container_width=True, key="sidebar_switch_mobile"):
            st.session_state.device_mode     = "mobile"
            st.session_state.choice_confirmed = True
            st.rerun()

        st.divider()

        # ── CB 資料上傳 ──────────────────────────────────────────
        st.header("📂 CB 資料上傳")
        uploaded_file = st.file_uploader(
            "上傳 CB 清單 (Excel/CSV)",
            type=['csv', 'xlsx'],
            help="需含：代號、名稱、標的股票代號、可轉債市價",
            key="sidebar_cb_upload"
        )
        if uploaded_file and load_cb_data_from_upload:
            with st.spinner("載入數據…"):
                df = load_cb_data_from_upload(uploaded_file)
                if df is not None and not df.empty:
                    st.session_state.df = df
                    st.success(f"✅ 載入 {len(df)} 筆 CB")
                    c1, c2 = st.columns(2)
                    c1.metric("總數量", len(df))
                    if 'close' in df.columns:
                        c2.metric("均價", f"{df['close'].mean():.2f}")

        df_cur = st.session_state.get('df', pd.DataFrame())
        if not df_cur.empty:
            st.caption(f"📊 目前：{len(df_cur)} 筆 CB")

        st.divider()

        # ── AI 功能 ──────────────────────────────────────────────
        st.header("🔑 AI 功能")
        api_key = st.text_input(
            "Gemini API Key (選填)", type="password",
            value=st.session_state.get('api_key', ''),
            key="sidebar_api_key"
        )
        st.session_state.api_key = api_key
        st.caption("✅ AI 已啟用" if api_key else "ℹ️ 未設定 API Key")

        st.divider()

        # ── 情報文件 ─────────────────────────────────────────────
        st.header("🕵️ 情報上傳")
        intel_files = st.file_uploader(
            "拖曳情報文件 (PDF/TXT)",
            type=['pdf', 'txt'],
            accept_multiple_files=True,
            key="sidebar_intel"
        )
        st.session_state.intel_files = intel_files or []
        if intel_files:
            st.caption(f"📎 已上傳 {len(intel_files)} 份")

        st.divider()

        # ── 系統工具 ─────────────────────────────────────────────
        st.header("🔧 系統工具")
        if st.button("🗑️ 清除快取", use_container_width=True, key="sidebar_clear"):
            st.cache_data.clear()
            st.cache_resource.clear()
            st.toast("快取已清除", icon="✅")

        st.caption(f"V100.0 | {datetime.now().strftime('%Y-%m-%d %H:%M')}")


# ═══════════════════════════════════════════════════════════════
#  安全渲染
# ═══════════════════════════════════════════════════════════════
def _safe_render(mod, num, name):
    if mod is None:
        st.warning(f"⚠️ {name} 模組未找到（嘗試路徑：ui_desktop/{name.lower().replace(' ','_')}.py 及根目錄）")
        return
    try:
        mod.render()
    except Exception as e:
        st.error(f"❌ {name} 載入失敗: {e}")
        with st.expander("錯誤詳情"):
            import traceback
            st.code(traceback.format_exc())


# ═══════════════════════════════════════════════════════════════
#  主渲染入口
# ═══════════════════════════════════════════════════════════════
def render():
    inject_css("desktop")
    _render_sidebar()

    st.markdown(create_glowing_title("🏛️ Titan SOP V100.0 — 全自動戰情室"), unsafe_allow_html=True)
    st.markdown("---")

    t1, t2, t3, t4, t5, t6 = st.tabs([
        "🛡️ 宏觀大盤", "🏹 獵殺雷達", "🎯 單兵狙擊",
        "🚀 全球決策", "📚 戰略百科", "🧠 元趨勢戰法",
    ])

    with t1: _safe_render(tab1, 1, "tab1_macro")
    with t2: _safe_render(tab2, 2, "tab2_radar")
    with t3: _safe_render(tab3, 3, "tab3_sniper")
    with t4: _safe_render(tab4, 4, "tab4_decision")
    with t5: _safe_render(tab5, 5, "tab5_wiki")
    with t6: _safe_render(tab6, 6, "tab6_metatrend")
