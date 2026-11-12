import streamlit as st
import requests
import urllib.parse
import plotly.express as px
import time
import pandas as pd
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="Command Center", page_icon="🚨", layout="wide")

# ==========================================
# 1. التصميم السايبر (CSS)
# ==========================================
st.markdown("""
    <style>
    .stApp { background-color: #0a0a0a; color: #e0e0e0; }
    div[data-testid="metric-container"] {
        background: rgba(20, 25, 35, 0.8); border: 1px solid #00f3ff;
        padding: 15px; border-radius: 10px; box-shadow: 0 0 15px rgba(0, 243, 255, 0.2);
    }
    [data-testid="stMetricValue"] { color: #ffffff !important; }
    [data-testid="stMetricLabel"] { color: #00f3ff !important; font-weight: bold; }
    @keyframes pulse-red {
        0% { box-shadow: 0 0 0 0 rgba(255, 0, 0, 0.7); }
        70% { box-shadow: 0 0 0 15px rgba(255, 0, 0, 0); }
        100% { box-shadow: 0 0 0 0 rgba(255, 0, 0, 0); }
    }
    .danger-box {
        background-color: #330000; border: 2px solid #ff0000; padding: 15px; border-radius: 10px;
        animation: pulse-red 1.5s infinite; color: #ff4b4b !important; text-align: center;
        font-weight: 900; font-size: 20px; margin-bottom: 20px;
    }
    .safe-box {
        background-color: #003311; border: 2px solid #00ff00; padding: 15px; border-radius: 10px;
        color: #00ff00 !important; text-align: center; font-weight: bold; font-size: 18px; margin-bottom: 20px;
    }
    .ai-terminal {
        background-color: #000000; border-left: 5px solid #00f3ff; padding: 20px;
        font-family: 'Courier New', Courier, monospace; color: #00f3ff !important;
        box-shadow: 0 0 20px rgba(0, 243, 255, 0.1); white-space: pre-wrap;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #00f3ff; text-shadow: 0 0 10px #00f3ff;'>🚨 COMMAND CENTER 🚨</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #888;'>Live Telemetry & AI Diagnostics</p>", unsafe_allow_html=True)

# ==========================================
# 2. قراءة الداتا من ThingSpeak
# ==========================================
THINGSPEAK_LAST_URL = "https://api.thingspeak.com/channels/3566946/feeds/last.json?api_key=INOALOP5AO7TBQ59"
THINGSPEAK_HISTORY_URL = "https://api.thingspeak.com/channels/3566946/feeds.json?api_key=INOALOP5AO7TBQ59&results=20"

@st.cache_data(ttl=5)
def get_data():
    try:
        response = requests.get(THINGSPEAK_LAST_URL)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def get_history():
    try:
        response = requests.get(THINGSPEAK_HISTORY_URL)
        if response.status_code == 200:
            return response.json().get('feeds', [])
        return []
    except:
        return []

# ==========================================
# 3. الواجهة
# ==========================================
@st.fragment(run_every="5s") 
def show_live_data():
    data = get_data()
    if not data:
        st.error("⏳ Waiting for Wokwi to send data...")
        return

    try:
        temp = float(data.get('field1') or 0)
        hum = float(data.get('field2') or 0)
        gas = float(data.get('field3') or 0)
        hr = float(data.get('field4') or 0)
        alarm = int(float(data.get('field5') or 0))
        
        # اللوكيشن
        gps_data = data.get('field8') or "0.0,0.0"
        lat_str, lng_str = gps_data.split(',')
        lat = float(lat_str)
        lng = float(lng_str)
    except ValueError:
        st.error("Data format error from ThingSpeak.")
        return

    # التحذير
    if alarm == 1:
        st.markdown('<div class="danger-box">⚠️ CRITICAL WARNING: HAZARDOUS ENVIRONMENT ⚠️</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="safe-box">✅ SYSTEM NORMAL: ALL PARAMETERS STABLE</div>', unsafe_allow_html=True)

    # المربعات
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(label="🌡️ TEMPERATURE", value=f"{temp:.1f} °C")
    col2.metric(label="💧 HUMIDITY", value=f"{hum:.1f} %")
    col3.metric(label="💨 GAS LEVEL", value=f"{gas:.0f} PPM", delta="DANGER" if alarm == 1 else "Normal", delta_color="inverse")
    col4.metric(label="❤️ HEART RATE", value=f"{hr:.0f} BPM")

    st.markdown("<br>", unsafe_allow_html=True)
    
    # الخريطة والرسم
    col_map, col_chart = st.columns(2)
    with col_map:
        st.markdown("<h4 style='color:#00f3ff;'>📍 Live Location</h4>", unsafe_allow_html=True)
        if lat != 0.0 and lng != 0.0:
            m = folium.Map(location=[lat, lng], zoom_start=15)
            folium.Marker([lat, lng], popup="Helmet", icon=folium.Icon(color="red", icon="info-sign")).add_to(m)
            st_folium(m, height=350, use_container_width=True, key="stable_map")
        else:
            st.warning("⏳ Waiting for GPS Signal...")

    with col_chart:
        st.markdown("<h4 style='color:#00f3ff;'>📊 Live Telemetry</h4>", unsafe_allow_html=True)
        history_data = get_history()
        if history_data:
            df = pd.DataFrame(history_data)
            df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%H:%M:%S')
            for col in ['field1', 'field3', 'field4']:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            fig = px.line(df, x='created_at', y=['field3', 'field1', 'field4'], 
                          color_discrete_sequence=["#ff4b4b", "#00f3ff", "#ffaa00"],
                          labels={'value': 'Value', 'created_at': 'Time', 'variable': 'Metric'})
            fig.update_layout(
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="white"), margin=dict(l=0, r=0, t=0, b=0),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig, use_container_width=True, key="stable_chart")

    # ==========================================
    # 4. الجزء السفلي (AI والواتساب)
    # ==========================================
    st.markdown("---")
    col_btn, col_wa = st.columns([1, 1])

    with col_btn:
        if st.button("🧠 RUN AI DIAGNOSTICS", use_container_width=True):
            with st.spinner("AI is analyzing..."):
                try:
                    from groq import Groq
                    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                    prompt = f"أنت خبير سلامة. قراءات: حرارة {temp}C، غاز {gas} PPM، نبض {hr} BPM. إنذار: {'مفعل' if alarm == 1 else 'غير مفعل'}. اكتب تحليل وتوصيات سريعة بالعربي."
                    chat = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="openai/gpt-oss-120b")
                    st.session_state.ai_response = chat.choices[0].message.content
                except Exception as e:
                    st.session_state.ai_response = f"❌ Error: {e}"

    with col_wa:
        map_link = f"https://www.google.com/maps?q={lat},{lng}"
        msg = f"🚨 تنبيه الخوذة:\n🌡️ حرارة: {temp}C\n💨 غاز: {gas}\n📍 الموقع: {map_link}"
        wa_url = f"https://wa.me/201283605279?text={urllib.parse.quote(msg)}"
        
        if alarm == 1:
            st.markdown(f'''
                <a href="{wa_url}" target="_blank">
                    <button style="background:linear-gradient(90deg, #25D366, #128C7E); color:white; border:none; padding:12px; border-radius:5px; cursor:pointer; font-weight:bold; width:100%; font-size:16px;">
                        📲 SEND WHATSAPP SOS ALERT
                    </button>
                </a>
            ''', unsafe_allow_html=True)
        else:
            st.markdown(f'''
                <a href="{wa_url}" target="_blank">
                    <button style="background-color:#444; color:white; border:none; padding:12px; border-radius:5px; cursor:pointer; font-weight:bold; width:100%; font-size:16px;">
                        📲 SEND WHATSAPP STATUS (SAFE)
                    </button>
                </a>
            ''', unsafe_allow_html=True)

    if 'ai_response' in st.session_state:
        if "❌" in st.session_state.ai_response:
            st.error(st.session_state.ai_response)
        else:
            st.markdown(f'<div class="ai-terminal">> {st.session_state.ai_response}</div>', unsafe_allow_html=True)

show_live_data()
