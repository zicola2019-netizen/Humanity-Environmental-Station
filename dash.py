import streamlit as st
import requests
import time
import pandas as pd
import folium
from streamlit_folium import st_folium
from groq import Groq
import urllib.parse
import plotly.express as px

# ==========================================
# 1. إعدادات النظام والـ AI
# ==========================================
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except:
    GROQ_API_KEY = "YOUR_GROQ_API_KEY_HERE"

client = Groq(api_key=GROQ_API_KEY)

# ⚠️ إعدادات ThingSpeak (حط أرقامك هنا)
CHANNEL_ID = "3566946"  # <--- ضع Channel ID هنا (بين علامات تنصيص)
READ_API_KEY = "INOALOP5AO7TBQ59" # <--- ضع Read API Key هنا

THINGSPEAK_LAST_URL = f"https://api.thingspeak.com/channels/{CHANNEL_ID}/feeds/last.json?api_key={READ_API_KEY}"
THINGSPEAK_HISTORY_URL = f"https://api.thingspeak.com/channels/{CHANNEL_ID}/feeds.json?api_key={READ_API_KEY}&results=20"

WHATSAPP_NUMBER = "201283605279" 

st.set_page_config(page_title="Command Center", page_icon="🚨", layout="wide")

# ==========================================
# 2. التصميم السايبر (Custom CSS)
# ==========================================
st.markdown("""
    <style>
    .stApp { background-color: #0a0a0a; color: #e0e0e0; }
    div[data-testid="metric-container"] {
        background: rgba(20, 25, 35, 0.8); border: 1px solid #00f3ff;
        padding: 15px; border-radius: 10px; box-shadow: 0 0 15px rgba(0, 243, 255, 0.2);
    }
    div[data-testid="metric-container"] label { color: #00f3ff !important; font-weight: bold; }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] { color: #ffffff !important; }
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
        box-shadow: 0 0 20px rgba(0, 243, 255, 0.1);
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #00f3ff; text-shadow: 0 0 10px #00f3ff;'>🚨 COMMAND CENTER 🚨</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #888;'>Humanity & Environmental Telemetry</p>", unsafe_allow_html=True)

# ==========================================
# 3. دوال مساعدة
# ==========================================
@st.cache_data(ttl=5) # كاش 5 ثواني عشان منضغطش على ThingSpeak
def get_data():
    try:
        response = requests.get(THINGSPEAK_LAST_URL)
        if response.status_code == 200:
            data = response.json()
            if 'field1' in data: 
                return data
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

def generate_whatsapp_alert(lat, lng):
    map_url = f"https://www.google.com/maps?q={lat},{lng}"
    encoded_text = urllib.parse.quote(f"🚨 تنبيه طوارئ: بيئة العمل خطرة!\n📍 الموقع: {map_url}")
    return f"https://wa.me/{WHATSAPP_NUMBER}?text={encoded_text}"

# ==========================================
# 4. الجزء العلوي (البيانات الحية)
# ==========================================
@st.fragment(run_every="5s") 
def show_live_data():
    data = get_data()
    if data:
        # استخراج القيم من الحقول
        temp_val = float(data.get('field1') or 0)
        hum_val = float(data.get('field2') or 0)
        gas_val = float(data.get('field3') or 0)
        hr_val = float(data.get('field4') or 0)
        lat = float(data.get('field5') or 0.0)
        lng = float(data.get('field6') or 0.0)

        if gas_val > 300 or temp_val > 40:
            st.markdown('<div class="danger-box">⚠️ CRITICAL WARNING: HAZARDOUS ENVIRONMENT DETECTED ⚠️</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="safe-box">✅ SYSTEM NORMAL: ALL PARAMETERS STABLE</div>', unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns(4)
        col1.metric(label="🌡️ TEMPERATURE", value=f"{temp_val} °C")
        col2.metric(label="💧 HUMIDITY", value=f"{hum_val} %")
        col3.metric(label="💨 GAS LEVEL", value=f"{gas_val} PPM", delta="DANGER" if gas_val > 300 else "Normal", delta_color="inverse")
        col4.metric(label="❤️ HEART RATE", value=f"{hr_val} BPM")

        st.markdown("<br>", unsafe_allow_html=True)
        
        col_map, col_chart = st.columns(2)
        
        with col_map:
            st.markdown("<h4 style='color:#00f3ff;'>📍 Live Location</h4>", unsafe_allow_html=True)
            if lat != 0.0 and lng != 0.0:
                m = folium.Map(location=[lat, lng], zoom_start=15)
                folium.Marker([lat, lng], popup="Worker", icon=folium.Icon(color="red", icon="info-sign")).add_to(m)
                st_folium(m, height=350, use_container_width=True, key="stable_map")
            else:
                st.warning("⏳ Waiting for GPS Signal...")

        with col_chart:
            st.markdown("<h4 style='color:#00f3ff;'>📊 Live Telemetry</h4>", unsafe_allow_html=True)
            history_data = get_history()
            if history_data:
                df = pd.DataFrame(history_data)
                # تنظيف البيانات
                df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%H:%M:%S')
                for col in ['field1', 'field3', 'field4']:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                
                # رسم بياني تفاعلي
                fig = px.line(df, x='created_at', y=['field3', 'field1', 'field4'], 
                              color_discrete_sequence=["#ff4b4b", "#00f3ff", "#ffaa00"],
                              labels={'value': 'Value', 'created_at': 'Time', 'variable': 'Metric'})
                fig.update_layout(
                    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="white"), margin=dict(l=0, r=0, t=0, b=0),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                st.plotly_chart(fig, use_container_width=True, key="stable_chart")
            else:
                st.info("Waiting for history data...")
    else:
        st.error("Connection to ThingSpeak lost...")

show_live_data()

# ==========================================
# 5. الجزء السفلي (تحليل الـ AI والواتساب)
# ==========================================
st.markdown("---")
col_btn, col_wa = st.columns([1, 1])

with col_btn:
    if st.button("🧠 RUN AI DIAGNOSTICS", use_container_width=True):
        with st.spinner("AI is analyzing..."):
            current_data = get_data() 
            if current_data:
                try:
                    prompt = f"""
                    أنت خبير سلامة وصحة مهنية.
                    قراءات حية: حرارة {current_data.get('field1')}C، رطوبة {current_data.get('field2')}%، غاز {current_data.get('field3')} PPM، نبضات {current_data.get('field4')} BPM.
                    
                    المطلوب: 1. نسبة أمان (0-100%). 2. تحليل مختصر. 3. توصيات فورية.
                    """
                    chat_completion = client.chat.completions.create(
                        messages=[{"role": "user", "content": prompt}],
                        model="openai/gpt-oss-120b",
                    )
                    st.session_state.ai_response = chat_completion.choices[0].message.content
                except Exception as e:
                    st.session_state.ai_response = f"❌ ERROR: {e}"

with col_wa:
    current_data = get_data()
    if current_data and (float(current_data.get('field3') or 0) > 300 or float(current_data.get('field1') or 0) > 40):
        wa_url = generate_whatsapp_alert(float(current_data.get('field5') or 0.0), float(current_data.get('field6') or 0.0))
        st.markdown(f'''
            <a href="{wa_url}" target="_blank">
                <button style="background:linear-gradient(90deg, #25D366, #128C7E); color:white; border:none; padding:10px; border-radius:5px; cursor:pointer; font-weight:bold; width:100%; height:100%; font-size:16px;">
                    📲 SEND WHATSAPP SOS ALERT
                </button>
            </a>
            ''', unsafe_allow_html=True)

if 'ai_response' in st.session_state:
    if "❌" in st.session_state.ai_response:
        st.error(st.session_state.ai_response)
    else:
        st.markdown(f'<div class="ai-terminal">> {st.session_state.ai_response}</div>', unsafe_allow_html=True)
