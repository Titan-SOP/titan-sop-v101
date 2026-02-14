# main.py
# Titan SOP V100.0 - Main Entry Point
# 功能：日出動畫 → The Matrix Choice → 雙模式路由

import streamlit as st
import time

try:
    from utils_ui import load_lottie_url, inject_css, get_lottie_animation
except ImportError:
    st.error("❌ 無法導入 utils_ui 模組，請確保 utils_ui.py 在同一目錄下。")
    st.stop()


def import_ui_modules():
    import importlib

    desktop_layout = None
    for path in ["ui_desktop.layout", "layout"]:
        try:
            desktop_layout = importlib.import_module(path)
            break
        except Exception:
            continue

    mobile_layout = None
    for path in ["ui_mobile.layout_mobile", "ui_mobile.layout", "layout_mobile"]:
        try:
            mobile_layout = importlib.import_module(path)
            break
        except Exception:
            continue

    return desktop_layout, mobile_layout


# ==========================================
# [1] 頁面配置
#   initial_sidebar_state = "auto" 保持側邊欄切換按鈕可見
# ==========================================

st.set_page_config(
    page_title="Titan SOP V100.0 - Ray of Hope",
    layout="wide",
    page_icon="🌅",
    initial_sidebar_state="auto"   # ← 改為 auto，收縮後按鈕仍可見
)

import pandas as pd
from datetime import datetime, timedelta

# ==========================================
# [2] Session State 初始化
# ==========================================

for k, v in {
    'animation_shown':  False,
    'device_mode':      None,
    'choice_confirmed': False,
    'api_key':          '',
    'intel_files':      [],
    'df':               pd.DataFrame(),
    'mobile_page':      'macro',
    'last_active_time': datetime.now(),
    'portfolio_df': pd.DataFrame([
        {'資產代號': '2330.TW', '持有數量 (股)': 1000, '買入均價': 550.0,    '資產類別': 'Stock'},
        {'資產代號': 'NVDA',    '持有數量 (股)': 10,   '買入均價': 400.0,    '資產類別': 'US_Stock'},
        {'資產代號': 'TLT',     '持有數量 (股)': 20,   '買入均價': 95.0,     '資產類別': 'US_Bond'},
        {'資產代號': 'CASH',    '持有數量 (股)': 1,    '買入均價': 500000.0, '資產類別': 'Cash'},
    ]),
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

_now = datetime.now()
if (_now - st.session_state.last_active_time) > timedelta(minutes=120):
    pass
st.session_state.last_active_time = _now


# ==========================================
# [3] CSS 樣式
#   - header 不整體隱藏（保留側邊欄切換按鈕）
#   - 只隱藏 Streamlit 裝飾元素
#   - 所有 CTA 按鈕改為金色 #FFD700
# ==========================================

MAIN_CSS = """
<style>
    /* 全局 */
    .stApp {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%);
        color: #FFFFFF;
    }

    /* 隱藏 Streamlit 品牌，但保留 header（讓側邊欄按鈕可見）*/
    #MainMenu        { visibility: hidden; }
    footer           { visibility: hidden; }
    [data-testid="stDecoration"]   { display: none; }
    [data-testid="stStatusWidget"] { display: none; }

    /* Header 只透明化，不隱藏 */
    [data-testid="stHeader"] {
        background: transparent !important;
        border-bottom: none !important;
    }

    /* 宣言文字 */
    .manifesto {
        font-size: 32px;
        font-weight: 300;
        text-align: center;
        color: #FFD700;
        text-shadow: 0 0 20px rgba(255, 215, 0, 0.5);
        margin: 40px 0;
        line-height: 1.6;
        animation: fadeIn 2s ease-in;
    }
    .manifesto-cn {
        font-size: 28px;
        color: #FFF;
        margin-top: 20px;
        opacity: 0.9;
    }

    /* 選擇卡片 */
    .choice-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #2a2a3e 100%);
        border: 2px solid #444;
        border-radius: 24px;
        padding: 60px 40px;
        text-align: center;
        transition: all 0.4s ease;
        cursor: pointer;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
    }
    .choice-card:hover {
        transform: translateY(-10px) scale(1.02);
        border-color: #FFD700;
        box-shadow: 0 16px 48px rgba(255, 215, 0, 0.3);
    }
    .choice-icon {
        font-size: 120px;
        margin-bottom: 30px;
        filter: drop-shadow(0 0 20px rgba(255, 255, 255, 0.3));
    }
    .choice-title {
        font-size: 36px;
        font-weight: bold;
        color: #FFD700;
        margin-bottom: 20px;
        text-shadow: 0 0 10px rgba(255, 215, 0, 0.5);
    }
    .choice-subtitle {
        font-size: 18px;
        color: #AAAAAA;
        line-height: 1.6;
        margin-bottom: 30px;
    }

    /* ★ 所有按鈕改金色 ★ */
    div.stButton > button {
        background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
        color: #000000;
        font-size: 20px;
        font-weight: bold;
        padding: 16px 40px;
        border-radius: 12px;
        border: none;
        box-shadow: 0 4px 16px rgba(255, 215, 0, 0.4);
        transition: all 0.3s ease;
        width: 100%;
    }
    div.stButton > button:hover {
        transform: scale(1.05);
        box-shadow: 0 8px 24px rgba(255, 215, 0, 0.6);
    }

    /* Matrix 格線背景 */
    .matrix-bg {
        position: fixed;
        top: 0; left: 0; width: 100%; height: 100%;
        background:
            linear-gradient(0deg,
                transparent 24%,
                rgba(255,215,0,0.03) 25%, rgba(255,215,0,0.03) 26%,
                transparent 27%, transparent 74%,
                rgba(255,215,0,0.03) 75%, rgba(255,215,0,0.03) 76%,
                transparent 77%, transparent),
            linear-gradient(90deg,
                transparent 24%,
                rgba(255,215,0,0.03) 25%, rgba(255,215,0,0.03) 26%,
                transparent 27%, transparent 74%,
                rgba(255,215,0,0.03) 75%, rgba(255,215,0,0.03) 76%,
                transparent 77%, transparent);
        background-size: 50px 50px;
        pointer-events: none;
        z-index: -1;
        opacity: 0.5;
    }

    /* 頁面標題 */
    .page-title {
        font-size: 48px;
        font-weight: bold;
        text-align: center;
        color: #FFD700;
        text-shadow: 0 0 20px rgba(255, 215, 0, 0.5);
        margin-bottom: 20px;
        animation: fadeIn 1s ease-in;
    }
    .page-subtitle {
        font-size: 20px;
        text-align: center;
        color: #AAAAAA;
        margin-bottom: 60px;
        animation: fadeIn 1.5s ease-in;
    }

    /* 動畫 */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50%       { transform: scale(1.05); }
    }
</style>
"""

st.markdown(MAIN_CSS, unsafe_allow_html=True)


# ==========================================
# [4] Ray of Hope 動畫
# ==========================================

def render_sunrise_animation():
    lottie_sunrise = load_lottie_url(get_lottie_animation("sunrise"))

    if lottie_sunrise:
        try:
            from streamlit_lottie import st_lottie
            st_lottie(lottie_sunrise, speed=1.0, height=300, key="sunrise")
        except Exception:
            st.markdown(
                '<h1 style="text-align:center; font-size:80px; animation:pulse 2s infinite;">🌅</h1>',
                unsafe_allow_html=True)
    else:
        st.markdown(
            '<h1 style="text-align:center; font-size:80px; animation:pulse 2s infinite;">🌅</h1>',
            unsafe_allow_html=True)

    st.markdown("""
        <div class="manifesto">
            Titan SOP V100.0
            <div class="manifesto-cn">在混亂的股海中，這是你的希望之光。</div>
        </div>
    """, unsafe_allow_html=True)

    # ★ 確認進入按鈕 → 金色（繼承全局 CSS）
    if st.button("🚀 確認進入戰情室", use_container_width=True):
        st.session_state.animation_shown = True
        st.rerun()


# ==========================================
# [5] The Matrix Choice（設備選擇）
# ==========================================

def render_device_selection():
    st.markdown('<div class="matrix-bg"></div>', unsafe_allow_html=True)

    st.markdown('<div class="page-title">🏛️ Titan SOP V100.0</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-subtitle">Choose Your Battle Station | 選擇你的戰鬥模式</div>',
        unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown("""
        <div class="choice-card">
            <div class="choice-icon">🖥️</div>
            <div class="choice-title">Desktop War Room</div>
            <div class="choice-subtitle">
                Bloomberg Terminal 風格<br>
                高密度資訊顯示<br>
                專業級數據分析<br>
                適合：深度研究、多螢幕操作
            </div>
        </div>""", unsafe_allow_html=True)
        # ★ 金色按鈕
        if st.button("⚔️ Enter Desktop Mode", key="desktop_btn", use_container_width=True):
            st.session_state.device_mode     = "desktop"
            st.session_state.choice_confirmed = True
            st.rerun()

    with col2:
        st.markdown("""
        <div class="choice-card">
            <div class="choice-icon">📱</div>
            <div class="choice-title">Mobile Command Post</div>
            <div class="choice-subtitle">
                Netflix / Robinhood 風格<br>
                大按鈕 + 底部導航列<br>
                觸控完全重設計<br>
                適合：快速決策、移動狙擊
            </div>
        </div>""", unsafe_allow_html=True)
        # ★ 金色按鈕
        if st.button("🎯 Enter Mobile Mode", key="mobile_btn", use_container_width=True):
            st.session_state.device_mode     = "mobile"
            st.session_state.choice_confirmed = True
            st.rerun()

    st.markdown("---")
    st.markdown(
        '<div style="text-align:center; color:#666; font-size:14px; margin-top:20px;">'
        '💡 提示：選擇後可隨時在側邊欄切換模式</div>',
        unsafe_allow_html=True)


# ==========================================
# [6] UI 路由
# ==========================================

def render_ui():
    desktop_layout, mobile_layout = import_ui_modules()

    if st.session_state.device_mode == "desktop":
        if desktop_layout is None:
            st.error("❌ 桌面版模組載入失敗，請確認 ui_desktop/layout.py 存在")
            if st.button("🔄 重新選擇", key="retry_d"):
                st.session_state.choice_confirmed = False
                st.rerun()
            return
        try:
            desktop_layout.render()
        except Exception as e:
            st.error(f"❌ 桌面版渲染失敗: {e}")
            import traceback
            st.code(traceback.format_exc())

    elif st.session_state.device_mode == "mobile":
        if mobile_layout is None:
            st.error("❌ 手機版模組載入失敗，請確認 ui_mobile/layout_mobile.py 存在")
            if st.button("🔄 重新選擇", key="retry_m"):
                st.session_state.choice_confirmed = False
                st.rerun()
            return
        try:
            mobile_layout.render()
        except Exception as e:
            st.error(f"❌ 手機版渲染失敗: {e}")
            import traceback
            st.code(traceback.format_exc())


# ==========================================
# [7] 主流程
# ==========================================

def main():
    if not st.session_state.animation_shown:
        render_sunrise_animation()
        return
    if st.session_state.device_mode is None or not st.session_state.choice_confirmed:
        render_device_selection()
        return
    render_ui()


if __name__ == "__main__":
    main()
