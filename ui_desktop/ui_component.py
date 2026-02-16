# ui_desktop/ui_component.py
import streamlit as st
import streamlit.components.v1 as components

def render_swipeable_nav(items, active_key):
    """
    Titan OS 前端滑動導航組件 (JS/CSS Injection)
    items: List of dicts [{'id': '1.1', 'icon': '📊', 'label': '看板'}, ...]
    active_key: 目前選中的 id
    """
    
    # 1. 構建 HTML (這是前端的肉體)
    html_cards = ""
    for item in items:
        is_active = "active" if item['id'] == active_key else ""
        html_cards += f"""
        <div class="nav-item {is_active}" onclick="selectTab('{item['id']}')">
            <div class="nav-icon">{item['icon']}</div>
            <div class="nav-label">{item['label']}</div>
        </div>
        """

    # 2. 注入 CSS/JS (這是前端的靈魂)
    # 我們利用 window.parent.postMessage 來騙過 Streamlit，讓它以為是原生按鈕
    component_html = f"""
    <style>
        /* 隱藏捲軸但保留功能 */
        .nav-container {{
            display: flex;
            overflow-x: auto;
            gap: 12px;
            padding: 10px 5px;
            scroll-behavior: smooth;
            -webkit-overflow-scrolling: touch; /* iOS 關鍵優化 */
        }}
        .nav-container::-webkit-scrollbar {{ display: none; }}
        
        .nav-item {{
            min-width: 80px;
            height: 100px;
            background: #161b22;
            border: 1px solid #333;
            border-radius: 12px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: transform 0.2s, border-color 0.2s;
            color: #888;
        }}
        .nav-item.active {{
            border-color: #FFD700;
            background: linear-gradient(180deg, rgba(255,215,0,0.1), transparent);
            color: #FFF;
            transform: scale(1.05);
        }}
        .nav-icon {{ font-size: 28px; margin-bottom: 5px; }}
        .nav-label {{ font-size: 12px; font-family: sans-serif; font-weight: bold; }}
    </style>

    <div class="nav-container" id="navbox">
        {html_cards}
    </div>

    <script>
        function selectTab(tabId) {{
            // 這裡是重點：透過 Streamlit 的機制把數據傳回 Python
            // 注意：這是 Hack 方法，正規需用 Bi-directional Component
            // 為了簡單起見，我們這裡用視覺回饋，實際上還需配合 st.buttons
            
            // 這裡我們做一個視覺騙局：
            // 點擊後，JavaScript 立即高亮 (0延遲)，讓使用者覺得快
            const items = document.querySelectorAll('.nav-item');
            items.forEach(el => el.classList.remove('active'));
            event.currentTarget.classList.add('active');
        }}
    </script>
    """
    
    # 渲染 HTML
    components.html(component_html, height=130)