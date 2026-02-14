# main.py
# Titan SOP V100.0 — App Entry Point

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(
    page_title="🏛️ Titan SOP V100.0",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="auto",
)

_defaults = {
    'df':               pd.DataFrame(),
    'api_key':          '',
    'intel_files':      [],
    'selected_ticker':  None,
    'mobile_page':      'macro',
    'page':             'home',
    'device_mode':      None,
    'choice_confirmed': False,
    'last_active_time': datetime.now(),
    'portfolio_df': pd.DataFrame([
        {'資產代號': '2330.TW', '持有數量 (股)': 1000, '買入均價': 550.0,    '資產類別': 'Stock'},
        {'資產代號': 'NVDA',    '持有數量 (股)': 10,   '買入均價': 400.0,    '資產類別': 'US_Stock'},
        {'資產代號': 'TLT',     '持有數量 (股)': 20,   '買入均價': 95.0,     '資產類別': 'US_Bond'},
        {'資產代號': 'CASH',    '持有數量 (股)': 1,    '買入均價': 500000.0, '資產類別': 'Cash'},
    ]),
}

for _k, _v in _defaults.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

_now  = datetime.now()
_diff = _now - st.session_state.last_active_time
if _diff > timedelta(minutes=120):
    st.session_state.portfolio_df = _defaults['portfolio_df']
st.session_state.last_active_time = _now


def _show_device_selector():
    st.markdown("""
    <h1 style="text-align:center; color:#00FF00;
               text-shadow:0 0 10px #00FF00, 0 0 20px #00FF00;">
        🏛️ Titan SOP V100.0
    </h1>
    <p style="text-align:center; color:#aaa; font-size:1.1em;">
        全自動戰情室 | 元趨勢創世紀版
    </p>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.subheader("請選擇介面模式")
    col1, col2 = st.columns(2, gap="large")
    with col1:
        st.markdown("""
        <div style="background:#1a1a1a; border:2px solid #00FF00;
                    border-radius:12px; padding:30px; text-align:center;">
            <h2>🖥️ 桌面版</h2>
            <p>Bloomberg Terminal 風格<br>完整功能 | 6大分析模組</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("進入桌面版", type="primary", use_container_width=True, key="choose_desktop"):
            st.session_state.device_mode     = "desktop"
            st.session_state.choice_confirmed = True
            st.rerun()
    with col2:
        st.markdown("""
        <div style="background:#1a1a1a; border:2px solid #FFD700;
                    border-radius:12px; padding:30px; text-align:center;">
            <h2>📱 手機版</h2>
            <p>觸控優化 | 底部導航<br>完整功能重新設計</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("進入手機版", type="secondary", use_container_width=True, key="choose_mobile"):
            st.session_state.device_mode     = "mobile"
            st.session_state.choice_confirmed = True
            st.rerun()
    st.markdown("---")
    st.caption("💡 桌面版：電腦寬螢幕最佳；手機版：觸控完全重設計")


mode      = st.session_state.device_mode
confirmed = st.session_state.choice_confirmed

if not confirmed or mode is None:
    _show_device_selector()

elif mode == "desktop":
    try:
        from ui_desktop.layout import render as desktop_render
        desktop_render()
    except ImportError:
        try:
            from layout import render as desktop_render
            desktop_render()
        except Exception as e:
            st.error(f"桌面版載入失敗: {e}")
            if st.button("🔄 重新選擇", key="retry_desktop"):
                st.session_state.choice_confirmed = False
                st.rerun()

elif mode == "mobile":
    try:
        from ui_mobile.layout_mobile import render as mobile_render
        mobile_render()
    except ImportError:
        try:
            from layout_mobile import render as mobile_render
            mobile_render()
        except Exception as e:
            st.error(f"手機版載入失敗: {e}")
            if st.button("🔄 重新選擇", key="retry_mobile"):
                st.session_state.choice_confirmed = False
                st.rerun()