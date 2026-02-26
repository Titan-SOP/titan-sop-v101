# ui_mobile/layout_mobile.py
# Titan OS V100.0 — Mobile Command Post
# 設計哲學：Netflix × Robinhood × 戰情室
# ─────────────────────────────────────────────────────────────
#  底部導航列 (Bottom Tab Bar) + 手勢友善大按鈕
#  每個 Tab 直接呼叫對應模組的 render()
#  完全觸控重設計 — 手機 / iPad 最佳化
# ─────────────────────────────────────────────────────────────

import streamlit as st
import importlib
import sys
import os
import traceback
from datetime import datetime

# ── sys.path 設定：根目錄 + ui_desktop 都加入 ─────────────────
# layout_mobile.py 在 ui_mobile/ 裡，往上兩層才是專案根目錄
_root        = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_ui_desktop  = os.path.join(_root, "ui_desktop")

for _p in [_root, _ui_desktop]:
    if os.path.isdir(_p) and _p not in sys.path:
        sys.path.insert(0, _p)


# ══════════════════════════════════════════════════════════════
#  六大戰區定義
# ══════════════════════════════════════════════════════════════
TABS = [
    {
        "id":      "tab1_macro",
        "icon":    "🛡️",
        "label":   "宏觀",
        "label_en":"Macro",
        "color":   "#FF4B4B",
        "desc":    "宏觀風控指揮中心",
    },
    {
        "id":      "tab2_radar",
        "icon":    "📡",
        "label":   "雷達",
        "label_en":"Radar",
        "color":   "#00C9FF",
        "desc":    "CB 獵殺雷達",
    },
    {
        "id":      "tab3_sniper",
        "icon":    "🎯",
        "label":   "狙擊",
        "label_en":"Sniper",
        "color":   "#00FF7F",
        "desc":    "個股狙擊手",
    },
    {
        "id":      "tab4_decision",
        "icon":    "⚖️",
        "label":   "決策",
        "label_en":"Decision",
        "color":   "#FFD700",
        "desc":    "全球資產決策",
    },
    {
        "id":      "tab5_wiki",
        "icon":    "🔍",
        "label":   "分析",
        "label_en":"Analyze",
        "color":   "#00F5FF",
        "desc":    "通用市場分析儀",
    },
    {
        "id":      "tab6_metatrend",
        "icon":    "🌌",
        "label":   "元趨勢",
        "label_en":"MetaTrend",
        "color":   "#B77DFF",
        "desc":    "全球元趨勢",
    },
]


# ══════════════════════════════════════════════════════════════
#  CSS — 全域 Mobile 樣式
# ══════════════════════════════════════════════════════════════
MOBILE_CSS = """
<style>
/* ── 全域基礎 ─────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Rajdhani:wght@600;700&family=JetBrains+Mono:wght@400;700&display=swap');

html, body, .stApp {
    background: #090d14 !important;
    color: #E8EDF5 !important;
    font-family: 'Rajdhani', sans-serif;
    overflow-x: hidden;
}

/* ── 隱藏 Streamlit 裝飾 ───────────────────── */
#MainMenu, footer, [data-testid="stDecoration"],
[data-testid="stStatusWidget"] { visibility: hidden; }

[data-testid="stHeader"] {
    background: transparent !important;
    border-bottom: none !important;
}

/* ── 頁面主體留底部空間給 nav bar ─────────── */
[data-testid="stAppViewContainer"] > section:first-child {
    padding-bottom: 90px !important;
}

/* ── 頂部狀態列 ───────────────────────────── */
.mob-statusbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 10px 16px 8px;
    background: rgba(9,13,20,0.95);
    border-bottom: 1px solid rgba(255,255,255,0.05);
    position: sticky;
    top: 0;
    z-index: 999;
    backdrop-filter: blur(12px);
}
.mob-statusbar-logo {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 20px;
    color: #FFD700;
    letter-spacing: 3px;
    text-shadow: 0 0 14px rgba(255,215,0,0.5);
}
.mob-statusbar-time {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    color: rgba(160,180,220,0.45);
    letter-spacing: 1px;
}
.mob-statusbar-badge {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    color: #00FF7F;
    background: rgba(0,255,127,0.1);
    border: 1px solid rgba(0,255,127,0.25);
    border-radius: 6px;
    padding: 2px 8px;
    letter-spacing: 1px;
}

/* ── 底部導航列 ───────────────────────────── */
.mob-navbar {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    z-index: 9999;
    display: flex;
    background: rgba(10,14,22,0.97);
    border-top: 1px solid rgba(255,255,255,0.06);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    padding: 0;
    height: 72px;
}
.mob-nav-item {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 3px;
    cursor: pointer;
    border: none;
    background: transparent;
    padding: 8px 4px 12px;
    transition: background 0.2s;
    text-decoration: none;
    -webkit-tap-highlight-color: transparent;
}
.mob-nav-item:hover {
    background: rgba(255,255,255,0.04);
}
.mob-nav-icon {
    font-size: 22px;
    line-height: 1;
    transition: transform 0.15s;
}
.mob-nav-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 9px;
    letter-spacing: 0.5px;
    opacity: 0.5;
    text-transform: uppercase;
    transition: opacity 0.15s;
}
.mob-nav-item.active .mob-nav-icon {
    transform: scale(1.15) translateY(-2px);
    filter: drop-shadow(0 0 6px currentColor);
}
.mob-nav-item.active .mob-nav-label {
    opacity: 1;
    font-weight: 700;
}
.mob-nav-dot {
    width: 4px;
    height: 4px;
    border-radius: 50%;
    margin-top: -1px;
    opacity: 0;
    transition: opacity 0.15s;
}
.mob-nav-item.active .mob-nav-dot {
    opacity: 1;
}

/* ── 首頁卡片 Grid ────────────────────────── */
.mob-home-hero {
    text-align: center;
    padding: 40px 20px 24px;
}
.mob-home-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 42px;
    color: #FFD700;
    letter-spacing: 4px;
    text-shadow: 0 0 30px rgba(255,215,0,0.4);
    line-height: 1;
    margin-bottom: 8px;
}
.mob-home-sub {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    color: rgba(160,180,220,0.4);
    letter-spacing: 3px;
    text-transform: uppercase;
}

.mob-card-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
    padding: 8px 14px 100px;
}
.mob-card {
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 18px;
    padding: 20px 14px 18px;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
    cursor: pointer;
    transition: all 0.2s;
    text-decoration: none;
    position: relative;
    overflow: hidden;
    min-height: 130px;
    justify-content: center;
}
.mob-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    border-radius: 18px 18px 0 0;
}
.mob-card:active {
    transform: scale(0.97);
    background: rgba(255,255,255,0.05);
}
.mob-card-icon {
    font-size: 36px;
    line-height: 1;
}
.mob-card-title {
    font-family: 'Rajdhani', sans-serif;
    font-size: 18px;
    font-weight: 700;
    text-align: center;
    line-height: 1.1;
}
.mob-card-sub {
    font-family: 'JetBrains Mono', monospace;
    font-size: 9px;
    color: rgba(160,180,220,0.4);
    letter-spacing: 1px;
    text-transform: uppercase;
    text-align: center;
}

/* ── 模組頂部返回列 ────────────────────────── */
.mob-topbar {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 14px 12px;
    background: rgba(9,13,20,0.92);
    border-bottom: 1px solid rgba(255,255,255,0.05);
    backdrop-filter: blur(12px);
    position: sticky;
    top: 0;
    z-index: 998;
}
.mob-topbar-back {
    font-size: 22px;
    cursor: pointer;
    opacity: 0.7;
    transition: opacity 0.15s;
    padding: 4px 8px;
    border-radius: 8px;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.06);
}
.mob-topbar-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 20px;
    letter-spacing: 2px;
    color: #FFD700;
}
.mob-topbar-sub {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    color: rgba(160,180,220,0.35);
    margin-left: auto;
    letter-spacing: 1px;
}

/* ── 所有 Streamlit 按鈕 → 金色（覆蓋 primary / secondary / tertiary）── */
div.stButton > button,
div.stButton > button[kind="primary"],
div.stButton > button[kind="secondary"],
[data-testid="baseButton-primary"],
[data-testid="baseButton-secondary"],
[data-testid="baseButton-secondaryFormSubmit"] {
    background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%) !important;
    color: #000 !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-weight: 700 !important;
    font-size: 16px !important;
    border-radius: 10px !important;
    border: none !important;
    padding: 12px 20px !important;
    box-shadow: 0 4px 14px rgba(255,215,0,0.25) !important;
    transition: all 0.2s !important;
    min-height: 48px !important;
}
div.stButton > button:hover,
[data-testid="baseButton-primary"]:hover,
[data-testid="baseButton-secondary"]:hover {
    transform: scale(1.03) !important;
    box-shadow: 0 6px 20px rgba(255,215,0,0.4) !important;
    color: #000 !important;
}

/* ── 返回按鈕：小一點，深色背景 ─────────── */
.mob-back-wrap div.stButton > button {
    background: rgba(255,255,255,0.07) !important;
    color: #FFD700 !important;
    border: 1px solid rgba(255,215,0,0.3) !important;
    font-size: 20px !important;
    padding: 10px 14px !important;
    box-shadow: none !important;
    min-height: 44px !important;
}
.mob-back-wrap div.stButton > button:hover {
    background: rgba(255,215,0,0.12) !important;
    transform: none !important;
    box-shadow: none !important;
}

/* ── 底部導航列容器 ──────────────────────── */
[data-testid="stBottom"] {
    background: rgba(10,14,22,0.97) !important;
    border-top: 1px solid rgba(255,255,255,0.06) !important;
    backdrop-filter: blur(20px) !important;
    -webkit-backdrop-filter: blur(20px) !important;
}

/* ── 底部 nav 按鈕：圖示導航樣式 ─────────── */
.mob-bottom-nav div.stButton > button {
    background: transparent !important;
    color: rgba(160,180,220,0.45) !important;
    border: none !important;
    box-shadow: none !important;
    padding: 6px 4px 10px !important;
    min-height: 64px !important;
    font-size: 22px !important;
    font-family: 'JetBrains Mono', monospace !important;
    line-height: 1.3 !important;
    border-radius: 0 !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    gap: 2px !important;
    width: 100% !important;
    letter-spacing: 0 !important;
}
.mob-bottom-nav div.stButton > button:hover {
    background: rgba(255,255,255,0.04) !important;
    transform: none !important;
    box-shadow: none !important;
    color: rgba(220,230,245,0.7) !important;
}

/* ── 讓 Streamlit 容器寬度最大化 ─────────── */
.block-container {
    padding: 0 !important;
    max-width: 100% !important;
}
.element-container { padding: 0 4px !important; }

/* ── 滾動條隱藏 ───────────────────────────── */
::-webkit-scrollbar { display: none; }
* { scrollbar-width: none; }
</style>
"""


# ══════════════════════════════════════════════════════════════
#  模組載入器
# ══════════════════════════════════════════════════════════════
def _load_module(module_id: str):
    """
    動態載入 tab 模組。
    嘗試順序：
      1. tab1_macro          （ui_desktop/ 已加入 sys.path，直接 import）
      2. ui_desktop.tab1_macro（有 __init__.py 時的 package 方式）
    """
    for path in [module_id, f"ui_desktop.{module_id}"]:
        try:
            if path in sys.modules:
                return importlib.reload(sys.modules[path])
            return importlib.import_module(path)
        except ImportError:
            continue
        except Exception as _e:
            # import 成功但模組本身有錯 → 不繼續嘗試，直接回傳 None 讓外層報錯
            raise _e
    return None


def _run_tab(tab_id: str):
    """載入並執行指定 tab 的 render()"""
    mod = _load_module(tab_id)
    if mod is None:
        st.error(f"❌ 模組 `{tab_id}` 無法載入，請確認檔案存在。")
        return
    if not hasattr(mod, 'render'):
        st.error(f"❌ 模組 `{tab_id}` 沒有 render() 函式。")
        return
    try:
        mod.render()
    except Exception as e:
        st.error(f"❌ {tab_id} 執行失敗: {e}")
        with st.expander("🔍 Debug Trace"):
            st.code(traceback.format_exc())


# ══════════════════════════════════════════════════════════════
#  頂部狀態列
# ══════════════════════════════════════════════════════════════
def _render_statusbar(active_tab_id: str | None = None):
    now = datetime.now()
    
    # ── 新增：動態讀取連線狀態 ──
    data_mode = st.session_state.get("DATA_MODE", "Guest")
    if data_mode == "Quantum":
        status_badge = "⚡ API LIVE"
        status_color = "#00FF7F" # 螢光綠
    else:
        status_badge = "🌐 GUEST"
        status_color = "#00C9FF" # 科技藍

    if active_tab_id:
        tab_info = next((t for t in TABS if t["id"] == active_tab_id), None)
        title_text = f"TITAN OS · {tab_info['label'].upper()}" if tab_info else "TITAN OS"
    else:
        title_text = "TITAN OS V100"

    st.markdown(f"""
<div class="mob-statusbar">
  <div class="mob-statusbar-logo">{title_text}</div>
  <div class="mob-statusbar-time">{now.strftime('%H:%M')}</div>
  <div class="mob-statusbar-badge" style="color:{status_color};
       border-color:{status_color}44;background:{status_color}14;">
    {status_badge}
  </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
#  底部導航列
# ══════════════════════════════════════════════════════════════
def _render_bottom_nav(active_tab_id: str | None):
    """底部導航列 — 純 Streamlit 按鈕，CSS 做成 app 底部 tab bar 樣式"""
    st.markdown('<div class="mob-bottom-nav">', unsafe_allow_html=True)
    cols = st.columns(len(TABS))
    for col, tab in zip(cols, TABS):
        is_active = (tab["id"] == active_tab_id)
        color     = tab["color"] if is_active else "rgba(160,180,220,0.4)"
        dot       = "●" if is_active else ""
        # 按鈕文字：icon + 換行 + label（用 Unicode 空白控制間距）
        btn_label = f"{tab['icon']}\n{tab['label']}{dot}"
        # 用 markdown 注入當前 tab 的顏色
        col.markdown(
            f'<style>#mob_nav_{tab["id"]} button {{color:{color} !important;' 
            f'{"font-weight:900!important;" if is_active else ""}}}</style>',
            unsafe_allow_html=True
        )
        with col:
            if st.button(
                btn_label,
                key=f"mob_nav_{tab['id']}",
                use_container_width=True,
                help=tab["desc"],
            ):
                if is_active:
                    st.session_state.mob_active_tab = None
                else:
                    st.session_state.mob_active_tab = tab["id"]
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
#  首頁：戰區選擇 Grid
# ══════════════════════════════════════════════════════════════
def _render_home():
    """首頁 — 2×3 戰區卡片"""
    st.markdown("""
<div class="mob-home-hero">
  <div class="mob-home-title">TITAN OS</div>
  <div class="mob-home-sub">⬡ MOBILE COMMAND POST · SELECT BATTLE ZONE</div>
</div>
<div class="mob-card-grid">
""", unsafe_allow_html=True)

    # 用 HTML 渲染卡片視覺（純展示）
    cards_html = ""
    for tab in TABS:
        cards_html += f"""
<div class="mob-card" style="border-color:{tab['color']}18;">
  <div class="mob-card::before" style="background:{tab['color']};"></div>
  <div class="mob-card-icon">{tab['icon']}</div>
  <div class="mob-card-title" style="color:{tab['color']};">{tab['label']}</div>
  <div class="mob-card-sub">{tab['label_en']}</div>
</div>
"""
    st.markdown(cards_html + "</div>", unsafe_allow_html=True)

    # 實際可點擊按鈕（2列排版）
    st.markdown('<div style="margin:8px 0;"></div>', unsafe_allow_html=True)

    row1 = st.columns(3)
    row2 = st.columns(3)
    all_cols = row1 + row2

    for col, tab in zip(all_cols, TABS):
        with col:
            if st.button(
                f"{tab['icon']}  {tab['label']}",
                key=f"mob_home_{tab['id']}",
                use_container_width=True,
                type="primary",
                help=tab["desc"],
            ):
                st.session_state.mob_active_tab = tab["id"]
                st.rerun()


# ══════════════════════════════════════════════════════════════
#  模組頁面頂部返回列
# ══════════════════════════════════════════════════════════════
def _render_topbar_back(tab_info: dict):
    c1, c2 = st.columns([1, 5])
    with c1:
        st.markdown('<div class="mob-back-wrap">', unsafe_allow_html=True)
        if st.button("◀ 返回", key="mob_back_btn", use_container_width=True):
            st.session_state.mob_active_tab = None
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown(
            f'<div class="mob-topbar">'
            f'<div class="mob-topbar-title">{tab_info["icon"]} {tab_info["label"].upper()}</div>'
            f'<div class="mob-topbar-sub">{tab_info["desc"].upper()}</div>'
            f'</div>',
            unsafe_allow_html=True
        )


# ══════════════════════════════════════════════════════════════
#  主入口
# ══════════════════════════════════════════════════════════════
def _render_sidebar_switcher():
    """側邊欄：切換模式與數據源"""
    with st.sidebar:
        # ── 1. 數據源切換開關 (Data Bridge Toggle) ──
        st.markdown(
            '<div style="font-family:JetBrains Mono,monospace;font-size:10px;' 
            'color:rgba(160,180,220,0.4);letter-spacing:2px;text-transform:uppercase;' 
            'margin-bottom:8px;">⬡ 數據連線引擎</div>',
            unsafe_allow_html=True
        )
        current_mode = st.session_state.get("DATA_MODE", "Guest")
        is_quantum = st.toggle("⚡ 啟動 Quantum API", value=(current_mode == "Quantum"))
        
        if is_quantum and current_mode != "Quantum":
            st.session_state["DATA_MODE"] = "Quantum"
            st.rerun()
        elif not is_quantum and current_mode == "Quantum":
            st.session_state["DATA_MODE"] = "Guest"
            st.rerun()
            
        st.markdown("<br>", unsafe_allow_html=True)

        # ── 2. 切換到桌面版 ──
        st.markdown(
            '<div style="font-family:JetBrains Mono,monospace;font-size:10px;' 
            'color:rgba(160,180,220,0.4);letter-spacing:2px;text-transform:uppercase;' 
            'margin-bottom:8px;">⬡ 切換模式</div>',
            unsafe_allow_html=True
        )
        if st.button("🖥️  切換到桌面版", use_container_width=True, key="mob_switch_desktop"):
            st.session_state.device_mode     = "desktop"
            st.session_state.choice_confirmed = True
            st.session_state.mob_active_tab  = None
            st.rerun()
            
        st.markdown(
            '<div style="font-family:JetBrains Mono,monospace;font-size:9px;' 
            'color:rgba(160,180,220,0.2);margin-top:6px;letter-spacing:1px;">' 
            '目前：📱 Mobile Mode</div>',
            unsafe_allow_html=True
        )


def render():
    """Mobile Command Post 主入口"""

    # ── Session State 初始化 ─────────────────────────────────
    if "mob_active_tab" not in st.session_state:
        st.session_state.mob_active_tab = None

    active_id = st.session_state.mob_active_tab

    # ── CSS 注入 ─────────────────────────────────────────────
    st.markdown(MOBILE_CSS, unsafe_allow_html=True)

    # ── 側邊欄切換 ───────────────────────────────────────────
    _render_sidebar_switcher()

    # ── 頂部狀態列 ───────────────────────────────────────────
    _render_statusbar(active_id)

    # ── 主內容區 ─────────────────────────────────────────────
    if active_id is None:
        # 首頁
        _render_home()
    else:
        # 模組頁
        tab_info = next((t for t in TABS if t["id"] == active_id), None)
        if tab_info:
            _render_topbar_back(tab_info)

        # ⚡ 直接呼叫模組的 render()
        _run_tab(active_id)

    # ── 底部導航列（固定在底部）──────────────────────────────
    _render_bottom_nav(active_id)


if __name__ == "__main__":
    render()
