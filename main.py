# main.py
# Titan SOP V100.0 - Main Entry Point
# 功能：日出動畫 → The Matrix Choice → 雙模式路由
# 作者：Streamlit Full-Stack Developer
# 狀態：PRODUCTION READY

import streamlit as st
from streamlit_lottie import st_lottie
import time

# 導入工具函數
try:
    from utils_ui import load_lottie_url, inject_css, get_lottie_animation
except ImportError:
    st.error("❌ 無法導入 utils_ui 模組。請確保 utils_ui.py 在同一目錄下。")
    st.stop()

# 導入 UI 模組（延遲導入以避免循環依賴）
def import_ui_modules():
    """延遲導入 UI 模組"""
    try:
        from ui_desktop import layout as desktop_layout
        from ui_mobile import layout as mobile_layout
        return desktop_layout, mobile_layout
    except ImportError as e:
        st.warning(f"⚠️ UI 模組尚未完成: {e}")
        st.info("📝 當前處於開發模式。請確保 ui_desktop/layout.py 和 ui_mobile/layout.py 已創建。")
        return None, None

# ==========================================
# [1] 頁面配置
# ==========================================

st.set_page_config(
    page_title="Titan SOP V100.0 - Ray of Hope",
    layout="wide",
    page_icon="🌅",
    initial_sidebar_state="expanded"  # [PHASE 1 FIX] Changed from collapsed
)

# ==========================================
# [2] Session State 初始化
# ==========================================

if 'animation_shown' not in st.session_state:
    st.session_state.animation_shown = False

if 'device_mode' not in st.session_state:
    st.session_state.device_mode = None

if 'choice_confirmed' not in st.session_state:
    st.session_state.choice_confirmed = False

# ==========================================
# [3] CSS 樣式 (精美動畫效果)
# ==========================================

MAIN_CSS = """
<style>
    /* 全局設定 */
    .stApp {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%);
        color: #FFFFFF;
    }
    
    /* 隱藏 Streamlit 雜項，但保留側邊欄按鈕 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* 關鍵修復：讓 Header 透明但可見，這樣按鈕才按得到 */
    header {
        visibility: visible !important;
        background-color: transparent !important;
    }
    
    /* 強制隱藏 Header 裡面的裝飾線條，只留按鈕 */
    header[data-testid="stHeader"] > div:first-child {
        background: transparent !important;
    }

    /* 讓側邊欄展開按鈕 (>) 變成金色並強制顯示 */
    [data-testid="collapsedControl"] {
        visibility: visible !important;
        display: block !important;
        color: #FFD700 !important;
        z-index: 99999 !important;
    }
    
    /* 動畫容器 */
    .animation-container {
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        min-height: 80vh;
        padding: 40px;
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
    
    /* 確認按鈕 */
    .stButton > button {
        background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
        color: #000000;
        font-size: 24px;
        font-weight: bold;
        padding: 20px 60px;
        border-radius: 50px;
        border: none;
        box-shadow: 0 8px 24px rgba(255, 215, 0, 0.4);
        transition: all 0.3s ease;
        margin-top: 40px;
    }
    
    .stButton > button:hover {
        transform: scale(1.05);
        box-shadow: 0 12px 32px rgba(255, 215, 0, 0.6);
    }
    
    /* The Matrix Choice - 設備選擇 */
    .choice-container {
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 80vh;
        gap: 60px;
        padding: 40px;
    }
    
    .choice-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #2a2a3e 100%);
        border: 2px solid #444;
        border-radius: 24px;
        padding: 60px 40px;
        width: 400px;
        text-align: center;
        transition: all 0.4s ease;
        cursor: pointer;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
    }
    
    .choice-card:hover {
        transform: translateY(-10px) scale(1.02);
        border-color: #00FF00;
        box-shadow: 0 16px 48px rgba(0, 255, 0, 0.3);
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
    
    .choice-button {
        background: linear-gradient(135deg, #00FF00 0%, #00CC00 100%);
        color: #000000;
        font-size: 20px;
        font-weight: bold;
        padding: 16px 40px;
        border-radius: 12px;
        border: none;
        box-shadow: 0 4px 16px rgba(0, 255, 0, 0.3);
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .choice-button:hover {
        transform: scale(1.05);
        box-shadow: 0 8px 24px rgba(0, 255, 0, 0.5);
    }
    
    /* 動畫效果 */
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes pulse {
        0%, 100% {
            transform: scale(1);
        }
        50% {
            transform: scale(1.05);
        }
    }
    
    /* Matrix 背景效果 */
    .matrix-bg {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: 
            linear-gradient(0deg, transparent 24%, rgba(0, 255, 0, 0.05) 25%, rgba(0, 255, 0, 0.05) 26%, transparent 27%, transparent 74%, rgba(0, 255, 0, 0.05) 75%, rgba(0, 255, 0, 0.05) 76%, transparent 77%, transparent),
            linear-gradient(90deg, transparent 24%, rgba(0, 255, 0, 0.05) 25%, rgba(0, 255, 0, 0.05) 26%, transparent 27%, transparent 74%, rgba(0, 255, 0, 0.05) 75%, rgba(0, 255, 0, 0.05) 76%, transparent 77%, transparent);
        background-size: 50px 50px;
        pointer-events: none;
        z-index: -1;
        opacity: 0.3;
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
</style>
"""

st.markdown(MAIN_CSS, unsafe_allow_html=True)

# ==========================================
# [4] Ray of Hope 動畫 (首次載入)
# ==========================================

def render_sunrise_animation():
    """渲染日出動畫與標題"""
    lottie_url = get_lottie_animation("sunrise")
    lottie_sunrise = load_lottie_url(lottie_url)
    
    st.markdown('<div class="sunrise-container">', unsafe_allow_html=True)
    
    # --- 防護邏輯：如果動畫載入失敗，顯示替代文字而不是報錯 ---
    if lottie_sunrise:
        try:
            st_lottie(lottie_sunrise, speed=1.0, height=300, key="sunrise")
        except Exception:
            st.warning("🌅 [動畫載入中，請稍候...]") 
    else:
        st.title("🌅 Titan V100.0") # 備援標題
        
    st.markdown("""
        <h1 style='text-align: center; color: #FFD700;'>Titan SOP V100.0</h1>
        <p style='text-align: center; font-size: 1.5rem;'>在混亂的股海中，這是你的希望之光。</p>
    """, unsafe_allow_html=True)
    
    if st.button("🚀 確認進入戰情室", use_container_width=True):
        st.session_state.animation_shown = True
        st.rerun()


# ==========================================
# [5] The Matrix Choice (設備選擇)
# ==========================================

def render_device_selection():
    """
    渲染 The Matrix 風格的設備選擇界面
    """
    # Matrix 背景效果
    st.markdown('<div class="matrix-bg"></div>', unsafe_allow_html=True)
    
    # 頁面標題
    st.markdown(
        """
        <div class="page-title">
            🏛️ Titan SOP V100.0
        </div>
        <div class="page-subtitle">
            Choose Your Battle Station | 選擇你的戰鬥模式
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # 設備選擇卡片
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        st.markdown(
            """
            <div class="choice-card">
                <div class="choice-icon">🖥️</div>
                <div class="choice-title">Desktop War Room</div>
                <div class="choice-subtitle">
                    Bloomberg Terminal 風格<br>
                    高密度資訊顯示<br>
                    專業級數據分析<br>
                    適合：深度研究、多螢幕操作
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        if st.button("⚔️ Enter Desktop Mode", key="desktop_btn", use_container_width=True):
            st.session_state.device_mode = "desktop"
            st.session_state.choice_confirmed = True
            st.success("✅ 已進入桌面戰情室模式")
            time.sleep(0.5)
            st.rerun()
    
    with col2:
        st.markdown(
            """
            <div class="choice-card">
                <div class="choice-icon">📱</div>
                <div class="choice-title">Mobile Command Post</div>
                <div class="choice-subtitle">
                    Netflix/Robinhood 風格<br>
                    大按鈕 + 巨大字體<br>
                    Tinder 滑動操作<br>
                    適合：快速決策、移動狙擊
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        if st.button("🎯 Enter Mobile Mode", key="mobile_btn", use_container_width=True):
            st.session_state.device_mode = "mobile"
            st.session_state.choice_confirmed = True
            st.success("✅ 已進入移動指揮所模式")
            time.sleep(0.5)
            st.rerun()
    
    # 底部提示
    st.markdown("---")
    st.markdown(
        """
        <div style="text-align: center; color: #666; font-size: 14px; margin-top: 40px;">
            💡 提示：選擇後可隨時在設定中切換模式
        </div>
        """,
        unsafe_allow_html=True
    )


# ==========================================
# [6] 主路由器
# ==========================================

def render_ui():
    """
    根據設備模式渲染對應的 UI
    """
    # 導入 UI 模組
    desktop_layout, mobile_layout = import_ui_modules()
    
    # 如果模組未完成，顯示開發模式提示
    if desktop_layout is None or mobile_layout is None:
        st.markdown(
            """
            <div class="page-title">🚧 開發模式</div>
            <div class="page-subtitle">UI 模組正在建構中</div>
            """,
            unsafe_allow_html=True
        )
        
        st.info(
            """
            ### 📝 待完成的模組
            
            請創建以下檔案：
            
            **桌面版 UI**:
            - `ui_desktop/__init__.py`
            - `ui_desktop/layout.py` (包含 `render()` 函數)
            
            **移動版 UI**:
            - `ui_mobile/__init__.py`
            - `ui_mobile/layout.py` (包含 `render()` 函數)
            
            ### 🎯 當前選擇的模式
            - **設備模式**: `{}`
            """.format(st.session_state.device_mode)
        )
        
        # 提供返回按鈕
        if st.button("🔄 重新選擇模式"):
            st.session_state.device_mode = None
            st.session_state.choice_confirmed = False
            st.rerun()
        
        return
    
    # 根據設備模式路由
    if st.session_state.device_mode == "desktop":
        # 注入桌面版 CSS
        try:
            inject_css("desktop")
        except:
            pass
        
        # 渲染桌面版 UI
        try:
            desktop_layout.render()
        except Exception as e:
            st.error(f"❌ 桌面版 UI 渲染失敗: {e}")
            st.code(str(e))
            
    elif st.session_state.device_mode == "mobile":
        # 注入移動版 CSS
        try:
            inject_css("mobile")
        except:
            pass
        
        # 渲染移動版 UI
        try:
            mobile_layout.render()
        except Exception as e:
            st.error(f"❌ 移動版 UI 渲染失敗: {e}")
            st.code(str(e))


# ==========================================
# [7] 主執行邏輯
# ==========================================

def main():
    """
    主執行函數
    
    流程:
    1. 首次載入 → 播放日出動畫
    2. 確認後 → 顯示設備選擇
    3. 選擇後 → 路由到對應 UI
    """
    
    # [PHASE 1 CRITICAL FIX] Strict State Initialization
    # 必須在任何渲染或邏輯之前初始化，防止 NoneType 崩潰
    import pandas as pd
    
    if 'df' not in st.session_state or st.session_state.df is None:
        st.session_state.df = pd.DataFrame()
    
    if 'api_key' not in st.session_state:
        st.session_state.api_key = ''
    
    if 'selected_ticker' not in st.session_state:
        st.session_state.selected_ticker = None
    
    if 'intel_files' not in st.session_state:
        st.session_state.intel_files = []
    
    # Step 1: 日出動畫（僅首次顯示）
    if not st.session_state.animation_shown:
        render_sunrise_animation()
        return
    
    # Step 2: 設備選擇（未選擇或取消確認時顯示）
    if st.session_state.device_mode is None or not st.session_state.choice_confirmed:
        render_device_selection()
        return
    
    # Step 3: 渲染對應的 UI
    render_ui()


# ==========================================
# [8] 應用程式入口
# ==========================================

if __name__ == "__main__":
    main()
