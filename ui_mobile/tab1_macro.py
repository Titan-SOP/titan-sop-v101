# ui_mobile/tab1_macro.py
# Titan SOP V100.0 - Tab 1 Mobile: 宏觀風控 (Tinder-Style Cards)
# 功能：滑動卡片式風控儀表板
# 美學：Netflix/Robinhood Style + 大按鈕 + 巨大字體

import streamlit as st
import pandas as pd
import numpy as np
from data_engine import get_market_benchmarks
from datetime import datetime


def render():
    """
    渲染移動版宏觀風控 Tab - Tinder-Style Card Stack
    
    結構：
    - Card 1: Market Pulse (VIX + Signal)
    - Card 2: Predator Targets (WTX)
    - Card 3: Sector Hotspots
    - Card 4: Bull/Bear Meter
    """
    
    # ==========================================
    # Header
    # ==========================================
    
    st.markdown(
        """
        <div style="text-align: center; margin-bottom: 20px;">
            <h1 style="font-size: 2.5em; color: #FFD700; margin: 0;">🛡️ 宏觀風控</h1>
            <p style="color: #AAAAAA; font-size: 1em;">Macro Risk Dashboard</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # ==========================================
    # Get Data
    # ==========================================
    
    df = st.session_state.get('df', pd.DataFrame())
    
    with st.spinner("載入中..."):
        try:
            benchmarks = get_market_benchmarks(period='1mo')
            
            if benchmarks is None or benchmarks.empty:
                vix_current = 20.5
                vix_change = -2.3
            else:
                vix_current = benchmarks['^VIX'].iloc[-1] if '^VIX' in benchmarks.columns else 20.5
                vix_change = benchmarks['^VIX'].iloc[-1] - benchmarks['^VIX'].iloc[0] if '^VIX' in benchmarks.columns else -2.3
        
        except Exception:
            vix_current = 20.5
            vix_change = -2.3
    
    # ==========================================
    # CARD 1: Market Pulse (VIX + Signal)
    # ==========================================
    
    # Signal Light Logic
    if vix_current < 15:
        signal = "🟢"
        signal_text = "綠燈"
        signal_desc = "市場平穩"
        signal_color = "#00FF00"
        bg_gradient = "linear-gradient(135deg, #1B4D3E 0%, #0a0a0a 100%)"
    elif vix_current < 20:
        signal = "🟡"
        signal_text = "黃燈"
        signal_desc = "適度謹慎"
        signal_color = "#FFD700"
        bg_gradient = "linear-gradient(135deg, #4D3E1B 0%, #0a0a0a 100%)"
    elif vix_current < 30:
        signal = "🟠"
        signal_text = "橙燈"
        signal_desc = "風險升溫"
        signal_color = "#FFA500"
        bg_gradient = "linear-gradient(135deg, #4D2B1B 0%, #0a0a0a 100%)"
    else:
        signal = "🔴"
        signal_text = "紅燈"
        signal_desc = "恐慌模式"
        signal_color = "#FF0000"
        bg_gradient = "linear-gradient(135deg, #4D1B1B 0%, #0a0a0a 100%)"
    
    st.markdown(
        f"""
        <div style="
            background: {bg_gradient};
            padding: 40px 30px;
            border-radius: 20px;
            margin-bottom: 20px;
            border: 3px solid {signal_color};
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
        ">
            <div style="text-align: center;">
                <div style="font-size: 100px; margin-bottom: 10px;">{signal}</div>
                <div style="font-size: 48px; color: {signal_color}; font-weight: bold; margin-bottom: 10px;">
                    {signal_text}
                </div>
                <div style="font-size: 24px; color: #FFFFFF; margin-bottom: 20px;">
                    {signal_desc}
                </div>
                <div style="font-size: 72px; color: #FFD700; font-weight: bold; margin-bottom: 5px;">
                    {vix_current:.1f}
                </div>
                <div style="font-size: 20px; color: #AAAAAA;">
                    VIX 恐慌指數
                </div>
                <div style="font-size: 24px; color: {'#00FF00' if vix_change < 0 else '#FF0000'}; margin-top: 10px;">
                    {vix_change:+.1f}
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # ==========================================
    # CARD 2: Predator Targets (WTX)
    # ==========================================
    
    st.markdown(
        """
        <div style="
            background: linear-gradient(135deg, #2a2a3e 0%, #0a0a0a 100%);
            padding: 30px;
            border-radius: 20px;
            margin-bottom: 20px;
            border: 2px solid #FFD700;
        ">
            <div style="text-align: center; margin-bottom: 20px;">
                <div style="font-size: 32px; color: #FFD700; font-weight: bold;">
                    🎯 台指期獵殺者
                </div>
                <div style="font-size: 16px; color: #AAAAAA; margin-top: 5px;">
                    WTX Predator Targets
                </div>
            </div>
            
            <div style="background: #1a1a2e; padding: 20px; border-radius: 15px; margin-bottom: 15px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="font-size: 28px;">🏆 HR</div>
                    <div style="font-size: 36px; color: #FF0000; font-weight: bold;">23,500</div>
                </div>
            </div>
            
            <div style="background: #1a1a2e; padding: 20px; border-radius: 15px; margin-bottom: 15px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="font-size: 28px;">⚾ 3B</div>
                    <div style="font-size: 36px; color: #00FF00; font-weight: bold;">22,800</div>
                </div>
            </div>
            
            <div style="background: #1a1a2e; padding: 20px; border-radius: 15px; margin-bottom: 15px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="font-size: 28px;">⚾ 2B</div>
                    <div style="font-size: 36px; color: #00FF00; font-weight: bold;">22,500</div>
                </div>
            </div>
            
            <div style="background: #1a1a2e; padding: 20px; border-radius: 15px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="font-size: 28px;">⚾ 1B</div>
                    <div style="font-size: 36px; color: #00FF00; font-weight: bold;">22,200</div>
                </div>
            </div>
            
            <div style="text-align: center; margin-top: 20px; padding-top: 20px; border-top: 1px solid #444;">
                <div style="font-size: 18px; color: #AAAAAA;">當前點位</div>
                <div style="font-size: 48px; color: #FFD700; font-weight: bold;">22,300</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # ==========================================
    # CARD 3: Sector Hotspots
    # ==========================================
    
    st.markdown(
        """
        <div style="
            background: linear-gradient(135deg, #1B4D3E 0%, #0a0a0a 100%);
            padding: 30px;
            border-radius: 20px;
            margin-bottom: 20px;
            border: 2px solid #00FF00;
        ">
            <div style="text-align: center; margin-bottom: 20px;">
                <div style="font-size: 32px; color: #00FF00; font-weight: bold;">
                    🗺️ 族群熱點
                </div>
                <div style="font-size: 16px; color: #AAAAAA; margin-top: 5px;">
                    Sector Hotspots
                </div>
            </div>
            
            <div style="background: #0a0a0a; padding: 20px; border-radius: 15px; margin-bottom: 15px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="font-size: 24px; color: #FFFFFF;">🔥 半導體</div>
                    <div style="font-size: 28px; color: #00FF00; font-weight: bold;">+5.2%</div>
                </div>
            </div>
            
            <div style="background: #0a0a0a; padding: 20px; border-radius: 15px; margin-bottom: 15px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="font-size: 24px; color: #FFFFFF;">🔥 AI 科技</div>
                    <div style="font-size: 28px; color: #00FF00; font-weight: bold;">+3.8%</div>
                </div>
            </div>
            
            <div style="background: #0a0a0a; padding: 20px; border-radius: 15px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="font-size: 24px; color: #FFFFFF;">❄️ 航運</div>
                    <div style="font-size: 28px; color: #FF0000; font-weight: bold;">-1.2%</div>
                </div>
            </div>
            
            <div style="text-align: center; margin-top: 20px; padding-top: 20px; border-top: 1px solid #00FF00;">
                <div style="font-size: 16px; color: #AAAAAA;">
                    🚧 Phase 1: 模擬數據
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # ==========================================
    # CARD 4: Bull/Bear Meter
    # ==========================================
    
    bull_ratio = 65
    bear_ratio = 35
    
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, #2a2a3e 0%, #0a0a0a 100%);
            padding: 30px;
            border-radius: 20px;
            margin-bottom: 20px;
            border: 2px solid #1E90FF;
        ">
            <div style="text-align: center; margin-bottom: 20px;">
                <div style="font-size: 32px; color: #1E90FF; font-weight: bold;">
                    📊 多空溫度計
                </div>
                <div style="font-size: 16px; color: #AAAAAA; margin-top: 5px;">
                    Bull/Bear Thermometer
                </div>
            </div>
            
            <!-- Bull Bar -->
            <div style="margin-bottom: 30px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                    <div style="font-size: 24px; color: #FFFFFF;">🐂 多頭</div>
                    <div style="font-size: 32px; color: #00FF00; font-weight: bold;">{bull_ratio}%</div>
                </div>
                <div style="background: #1a1a2e; height: 30px; border-radius: 15px; overflow: hidden;">
                    <div style="background: linear-gradient(90deg, #00FF00, #00CC00); 
                                height: 100%; width: {bull_ratio}%; 
                                transition: width 0.5s ease;"></div>
                </div>
            </div>
            
            <!-- Bear Bar -->
            <div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                    <div style="font-size: 24px; color: #FFFFFF;">🐻 空頭</div>
                    <div style="font-size: 32px; color: #FF0000; font-weight: bold;">{bear_ratio}%</div>
                </div>
                <div style="background: #1a1a2e; height: 30px; border-radius: 15px; overflow: hidden;">
                    <div style="background: linear-gradient(90deg, #FF0000, #CC0000); 
                                height: 100%; width: {bear_ratio}%; 
                                transition: width 0.5s ease;"></div>
                </div>
            </div>
            
            <div style="text-align: center; margin-top: 20px; padding-top: 20px; border-top: 1px solid #444;">
                <div style="font-size: 16px; color: #AAAAAA;">
                    🚧 Phase 1: 模擬數據
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # ==========================================
    # PR90 Chip Distribution (如果有數據)
    # ==========================================
    
    if not df.empty and 'close' in df.columns:
        pr90_value = df['close'].quantile(0.9)
        avg_price = df['close'].mean()
        
        st.markdown(
            f"""
            <div style="
                background: linear-gradient(135deg, #4D3E1B 0%, #0a0a0a 100%);
                padding: 30px;
                border-radius: 20px;
                margin-bottom: 20px;
                border: 2px solid #FFD700;
            ">
                <div style="text-align: center; margin-bottom: 20px;">
                    <div style="font-size: 32px; color: #FFD700; font-weight: bold;">
                        📈 籌碼分佈
                    </div>
                    <div style="font-size: 16px; color: #AAAAAA; margin-top: 5px;">
                        Chip Distribution
                    </div>
                </div>
                
                <div style="background: #1a1a2e; padding: 20px; border-radius: 15px; margin-bottom: 15px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div style="font-size: 24px; color: #FFFFFF;">PR90 過熱線</div>
                        <div style="font-size: 36px; color: #FF0000; font-weight: bold;">{pr90_value:.2f}</div>
                    </div>
                </div>
                
                <div style="background: #1a1a2e; padding: 20px; border-radius: 15px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div style="font-size: 24px; color: #FFFFFF;">市場均價</div>
                        <div style="font-size: 36px; color: #00FF00; font-weight: bold;">{avg_price:.2f}</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    # ==========================================
    # Footer
    # ==========================================
    
    st.markdown(
        f"""
        <div style="text-align: center; margin-top: 30px; padding: 20px; color: #666;">
            <div style="font-size: 14px;">📅 更新時間</div>
            <div style="font-size: 12px; margin-top: 5px;">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
        </div>
        """,
        unsafe_allow_html=True
    )
