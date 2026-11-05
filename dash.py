import streamlit as st
import requests
import time
import pandas as pd
from groq import Groq
import urllib.parse
import folium
from streamlit_folium import st_folium
import plotly.express as px

# ==========================================
# 1. الإعدادات الأساسية
# ==========================================
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except:
    GROQ_API_KEY = "YOUR_GROQ_API_KEY_HERE"
client = Groq(api_key=GROQ_API_KEY)

# ⚠️ إعدادات ThingSpeak
CHANNEL_ID = "3566946"  # <--- ضع Channel ID هنا
READ_API_KEY = "INOALOP5AO7TBQ59" # <--- ضع Read API Key هنا
THINGSPEAK_URL = f"https://api.thingspeak.com/channels/{CHANNEL_ID}/feeds/last.json?api_key={READ_API_KEY}"

WHATSAPP_NUMBER = "2010283605279"

st.set_page_config(page_title="Command Center", page_icon="🚨", layout="wide")

# ... (نفس كود CSS بتاع التصميم السايبر اللي فات) ...
st.markdown("""<style> ... </style>""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #00f3ff;'>🚨 COMMAND CENTER 🚨</h1>", unsafe_allow_html=True)

# ==========================================
# 2. دالة قراءة البيانات من ThingSpeak
# ==========================================
@st.cache_data(ttl=5) # هنخلي الكاش 5 ثواني عشان منضغطش على السيرفر
def get_data():
    try:
        response = requests.get(THINGSPEAK_URL)
        if response.status_code == 200:
            data = response.json()
            if 'field1' in data: # التأكد من وجود بيانات
                return data
        return None
    except:
        return None

# ==========================================
# 3. دالة الواتساب
# ==========================================
def generate_whatsapp_alert(lat, lng):
    map_url = f"https://www.google.com/maps?q={lat},{lng}"
    encoded_text = urllib.parse.quote(f"🚨 تنبيه طوارئ: بيئة العمل خطرة!\n📍 الموقع: {map_url}")
    return f"https://wa.me/{WHATSAPP_NUMBER}?text={encoded_text}"

# ==========================================
# 4. عرض البيانات الحية
# ==========================================
@st.fragment(run_every="5s") # التحديث كل 5 ثواني (عشان ThingSpeak)
def show_live_data():
    data = get_data()
    if data:
        # استخراج القيم من حقول ThingSpeak
        temp_val = float(data.get('field1') or 0)
        hum_val = float(data.get('field2') or 0)
        gas_val = float(data.get('field3') or 0)
        hr_val = float(data.get('field4') or 0)
        lat = float(data.get('field5') or 0.0)
        lng = float(data.get('field6') or 0.0)

        # التحذيرات
        if gas_val > 300 or temp_val > 40:
            st.markdown('<div class="danger-box">⚠️ CRITICAL WARNING ⚠️</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="safe-box">✅ SYSTEM NORMAL</div>', unsafe_allow_html=True)

        # المربعات
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("🌡️ TEMPERATURE", f"{temp_val} °C")
        col2.metric("💧 HUMIDITY", f"{hum_val} %")
        col3.metric("💨 GAS LEVEL", f"{gas_val} PPM")
        col4.metric("❤️ HEART RATE", f"{hr_val} BPM")

        # الخريطة والرسم البياني
        col_map, col_chart = st.columns(2)
        with col_map:
            st.markdown("#### 📍 Live Location")
            if lat != 0.0 and lng != 0.0:
                m = folium.Map(location=[lat, lng], zoom_start=15)
                folium.Marker([lat, lng], popup="Worker").add_to(m)
                st_folium(m, height=350, use_container_width=True, key="map")
            else:
                st.warning("Waiting for GPS...")

        with col_chart:
            st.markdown("#### 📊 Live Telemetry")
            # الرسم البياني (بنجيب آخر 20 قراءة)
            history_url = f"https://api.thingspeak.com/channels/{CHANNEL_ID}/feeds.json?api_key={READ_API_KEY}&results=20"
            res = requests.get(history_url).json()
            if 'feeds' in res:
                df = pd.DataFrame(res['feeds'])
                df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%H:%M:%S')
                # تحويل القيم لأرقام
                for col in ['field1', 'field3', 'field4']:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                
                fig = px.line(df, x='created_at', y=['field3', 'field1', 'field4'],
                              labels={'value': 'Value', 'created_at': 'Time'},
                              color_discrete_sequence=["#ff4b4b", "#00f3ff", "#ffaa00"])
                fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font=dict(color="white"))
                st.plotly_chart(fig, use_container_width=True, key="chart")
    else:
        st.error("No data received from ThingSpeak yet...")

show_live_data()

# ... (باقي كود الـ AI والواتساب كما هو) ...