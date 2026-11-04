import streamlit as st
import requests
import time
import pandas as pd
import folium
from streamlit_folium import st_folium
from groq import Groq
import urllib.parse

# ==========================================
# 1. إعدادات النظام والـ AI
# ==========================================
# بنقرا المفتاح من إعدادات Streamlit (مش مكتوب في الكود عشان الأمان)
GROQ_API_KEY=st.secrets["GROQ_API_KEY"]
client = Groq(api_key=GROQ_API_KEY)

FIREBASE_URL = "https://smart-helmet-project-23822-default-rtdb.firebaseio.com/helmet_data.json"

# ⚠️ غير الرقم ده برقم الواتساب بتاعك (بصيغة دولية وبدون + أو أصفار في البداية)
WHATSAPP_NUMBER = "201283605279" 

st.set_page_config(page_title="Humanity & Environmental Command Center", page_icon="🏢", layout="wide")

st.title("🏢 Humanity & Environmental Command Center")
st.markdown("### Live System Telemetry & AI Diagnostics")

# ==========================================
# 2. الدوال المساعدة
# ==========================================
def get_data():
    try:
        response = requests.get(FIREBASE_URL)
        if response.status_code == 200:
            data = response.json()
            if data:
                return dict(data)
        return None
    except Exception as e:
        return None

def generate_whatsapp_alert(lat, lng, message="🚨 تنبيه طوارئ من محطة المراقبة: بيئة العمل خطرة!"):
    map_url = f"https://www.google.com/maps?q={lat},{lng}"
    full_message = f"{message}\n📍 الموقع: {map_url}"
    encoded_text = urllib.parse.quote(full_message)
    return f"https://wa.me/{WHATSAPP_NUMBER}?text={encoded_text}"

# ==========================================
# 3. الجزء العلوي (البيانات الحية)
# ==========================================
@st.fragment(run_every="1s")
def show_live_data():
    data = get_data()
    if data:
        # الأرقام الأساسية
        col1, col2, col3, col4 = st.columns(4)
        col1.metric(label="🌡️ Room Temp", value=f"{data.get('temperature', 0)} °C")
        col2.metric(label="💧 Humidity", value=f"{data.get('humidity', 0)} %")
        
        gas_val = float(data.get('gas', 0))
        col3.metric(label="💨 Air Quality (Gas)", value=f"{gas_val} PPM", delta="DANGER" if gas_val > 300 else "Normal", delta_color="inverse")
        
        col4.metric(label="❤️ Heart Rate", value=f"{data.get('heart_rate', 0)} BPM")
        
        st.markdown("---")
        
        # الخريطة والرسم البياني
        col_map, col_chart = st.columns(2)
        
        with col_map:
            st.markdown("#### 📍 Live Location Tracker")
            lat = data.get('latitude', 0.0)
            lng = data.get('longitude', 0.0)
            
            if lat != 0.0 and lng != 0.0:
                m = folium.Map(location=[lat, lng], zoom_start=15)
                folium.Marker(
                    [lat, lng], 
                    popup="Worker Location", 
                    icon=folium.Icon(color="red", icon="info-sign")
                ).add_to(m)
                st_folium(m, height=400, use_container_width=True, key="map")
            else:
                st.warning("⏳ Waiting for GPS Signal...")

        with col_chart:
            st.markdown("#### 📊 Live Telemetry Trends")
            if 'history' not in st.session_state:
                st.session_state.history = pd.DataFrame(columns=["Time", "Temp", "Gas", "HR"])
            
            new_row = {
                "Time": time.strftime("%H:%M:%S"),
                "Temp": float(data.get('temperature', 0)),
                "Gas": float(data.get('gas', 0)),
                "HR": float(data.get('heart_rate', 0))
            }
            st.session_state.history = pd.concat([st.session_state.history, pd.DataFrame([new_row])], ignore_index=True).tail(15)
            st.line_chart(st.session_state.history.set_index("Time"), height=400, color=["#ff4b4b", "#1f77b4", "#ffaa00"])
    else:
        st.error("⚠️ Failed to fetch data. Waiting for ESP32...")

show_live_data()

# ==========================================
# 4. الجزء السفلي (تحليل الـ AI والتنبيهات)
# ==========================================
st.markdown("---")
st.markdown("### 🤖 AI Safety Diagnostics")

if 'ai_response' not in st.session_state:
    st.session_state.ai_response = "System standby. Awaiting manual diagnostic trigger..."

col_btn, col_status = st.columns([1, 2])

with col_btn:
    if st.button("🔄 Run AI Diagnostics", key="analyze_btn_groq"):
        with st.spinner("Analyzing telemetry data..."):
            current_data = get_data() 
            if current_data:
                try:
                    prompt = f"""
                    أنت خبير سلامة وصحة مهنية (Occupational Health and Safety Expert).
                    لديك قراءات حية:
                    - حرارة الغرفة: {current_data.get('temperature')} C
                    - الرطوبة: {current_data.get('humidity')}%
                    - الغاز: {current_data.get('gas')} PPM
                    - النبضات: {current_data.get('heart_rate')} BPM
                    - اهتزاز: {'نعم' if current_data.get('vibration_detected') else 'لا'}
                    - العامل موجود: {'نعم' if current_data.get('user_present') else 'لا'}

                    المطلوب:
                    1. نسبة أمان (Safety Score) من 100%.
                    2. تحليل مختصر.
                    3. توصيات فورية بالعربي.
                    """
                    chat_completion = client.chat.completions.create(
                        messages=[{"role": "user", "content": prompt}],
                        model="openai/gpt-oss-120b", # الموديل الشغال
                    )
                    st.session_state.ai_response = chat_completion.choices[0].message.content
                except Exception as e:
                    st.session_state.ai_response = f"❌ SYSTEM ERROR: {e}"
            else:
                st.session_state.ai_response = "❌ NO DATA FOUND."

with col_status:
    current_data = get_data()
    if current_data:
        gas = float(current_data.get('gas', 0))
        temp = float(current_data.get('temperature', 0))
        lat = current_data.get('latitude', 0.0)
        lng = current_data.get('longitude', 0.0)

        if gas > 300 or temp > 40:
            st.error("⚠️ CRITICAL WARNING: HAZARDOUS ENVIRONMENT DETECTED")
            
            # توليد لينك الواتساب وإظهاره كزرار
            wa_url = generate_whatsapp_alert(lat, lng)
            st.markdown(
                f'''
                <a href="{wa_url}" target="_blank">
                    <button style="background-color:#25D366; color:white; border:none; padding:10px 20px; border-radius:5px; cursor:pointer; font-weight:bold; font-size:16px;">
                        📲 إرسال تنبيه طوارئ للواتساب
                    </button>
                </a>
                ''', 
                unsafe_allow_html=True
            )
        else:
            st.success("✅ SYSTEM STATUS: ALL PARAMETERS NORMAL")

# عرض رد الـ AI
if "❌" in st.session_state.ai_response:
    st.error(st.session_state.ai_response)
else:
    st.info(st.session_state.ai_response)
