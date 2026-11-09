import streamlit as st
import requests
import time
import urllib.parse # ضفنا المكتبة دي عشان الواتساب

st.set_page_config(page_title="Smart Helmet Dashboard", page_icon="🪖", layout="wide")

# ==========================================
# 1. التصميم (CSS) - ستايل أبيض زي التطبيق
# ==========================================
st.markdown("""
    <style>
    /* الخلفية العامة */
    .stApp {
        background-color: #f4f6f9;
        color: #333;
    }
    
    /* كروت الأرقام العلوية */
    .top-card {
        background-color: white;
        padding: 15px;
        border-radius: 15px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        text-align: center;
        border: 1px solid #e0e0e0;
    }
    .top-number { font-size: 32px; font-weight: 900; color: #111; margin: 0; }
    .top-label { font-size: 14px; color: #777; margin: 0; }

    /* كارت الجهاز الرئيسي */
    .main-card {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin-top: 20px;
        border: 1px solid #e0e0e0;
    }
    .device-name { font-size: 20px; font-weight: bold; color: #111; margin: 0; }
    .device-sub { font-size: 13px; color: #777; }
    .badge-online { 
        background-color: #e8f5e9; color: #2e7d32; 
        padding: 5px 12px; border-radius: 20px; font-weight: bold; font-size: 12px;
    }

    /* كروت الحساسات */
    .sensor-card {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #eee;
        margin-bottom: 10px;
    }
    .sensor-title { font-size: 14px; color: #777; margin-bottom: 5px; }
    .sensor-value { font-size: 22px; font-weight: bold; color: #111; margin: 0; }
    .sensor-unit { font-size: 14px; font-weight: normal; color: #888; }

    /* شريط الإنذار */
    .alarm-safe {
        background-color: #e8f5e9; border: 1px solid #c8e6c9;
        color: #2e7d32; text-align: center; padding: 15px;
        border-radius: 12px; font-weight: bold; font-size: 16px;
        margin-top: 15px;
    }
    .alarm-danger {
        background-color: #ffebee; border: 1px solid #ffcdd2;
        color: #c62828; text-align: center; padding: 15px;
        border-radius: 12px; font-weight: bold; font-size: 16px;
        margin-top: 15px; animation: pulse 1s infinite;
    }
    @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.6; } 100% { opacity: 1; } }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h2 style='text-align: left; color: #0b3b60; font-weight: 900;'>Smart Helmet</h2>", unsafe_allow_html=True)

# ==========================================
# 2. دالة قراءة البيانات من ThingSpeak
# ==========================================
THINGSPEAK_URL = "https://api.thingspeak.com/channels/3566946/feeds/last.json?api_key=INOALOP5AO7TBQ59"

@st.cache_data(ttl=5)
def get_data():
    try:
        response = requests.get(THINGSPEAK_URL)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

# ==========================================
# 3. بناء الواجهة
# ==========================================
@st.fragment(run_every="5s") 
def show_dashboard():
    data = get_data()
    
    if not data:
        st.warning("⏳ Waiting for Helmet to send data...")
        return

    # استخراج القيم (مع تحويلها لأرقام)
    temp = float(data.get('field1') or 0)
    hum = float(data.get('field2') or 0)
    gas = float(data.get('field3') or 0)
    vib = float(data.get('field4') or 0)
    alarm = int(data.get('field5') or 0)
    gyro = float(data.get('field6') or 0)
    mpu_stat = int(data.get('field7') or 0)

    # --- الصف الأول (عدد العمال) ---
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        st.markdown(f'''
            <div class="top-card">
                <p class="top-number">01</p>
                <p class="top-label">Workers Safe</p>
            </div>
        ''', unsafe_allow_html=True)
    with col2:
        st.markdown(f'''
            <div class="top-card">
                <p class="top-number">00</p>
                <p class="top-label">Offline Helmets</p>
            </div>
        ''', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<h4 style='color: #333;'>Helmets Overview</h4>", unsafe_allow_html=True)

    # --- الكارت الرئيسي للجهاز ---
    st.markdown(f'''
        <div class="main-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div style="display: flex; align-items: center; gap: 15px;">
                    <div style="background-color: #e3f2fd; padding: 10px; border-radius: 50%; font-size: 24px;">🛡️</div>
                    <div>
                        <p class="device-name">HELMET_001</p>
                        <p class="device-sub">Smart Helmet Device</p>
                    </div>
                </div>
                <div class="badge-online">ONLINE</div>
            </div>
            <hr style="margin: 15px 0; border: 0; border-top: 1px solid #eee;">
            <p style="font-weight: bold; margin-bottom: 15px;">Sensor Readings</p>
    ''', unsafe_allow_html=True)

    # --- شبكة الحساسات (2 أعمدة) ---
    row1_col1, row1_col2 = st.columns(2)
    with row1_col1:
        st.markdown(f'''
            <div class="sensor-card">
                <div class="sensor-title">🌡️ Temperature</div>
                <p class="sensor-value">{temp:.2f} <span class="sensor-unit">°C</span></p>
            </div>
        ''', unsafe_allow_html=True)
    with row1_col2:
        st.markdown(f'''
            <div class="sensor-card">
                <div class="sensor-title">💧 Humidity</div>
                <p class="sensor-value">{hum:.2f} <span class="sensor-unit">%</span></p>
            </div>
        ''', unsafe_allow_html=True)

    row2_col1, row2_col2 = st.columns(2)
    with row2_col1:
        st.markdown(f'''
            <div class="sensor-card">
                <div class="sensor-title">💨 Gas Raw</div>
                <p class="sensor-value">{gas:.0f} <span class="sensor-unit"></span></p>
            </div>
        ''', unsafe_allow_html=True)
    with row2_col2:
        st.markdown(f'''
            <div class="sensor-card">
                <div class="sensor-title">📳 Vibration</div>
                <p class="sensor-value">{vib:.2f} <span class="sensor-unit"></span></p>
            </div>
        ''', unsafe_allow_html=True)

    row3_col1, row3_col2 = st.columns(2)
    with row3_col1:
        st.markdown(f'''
            <div class="sensor-card">
                <div class="sensor-title">🔄 Gyro Magnitude</div>
                <p class="sensor-value">{gyro:.2f} <span class="sensor-unit"></span></p>
            </div>
        ''', unsafe_allow_html=True)
    with row3_col2:
        mpu_color = "#2e7d32" if mpu_stat == 1 else "#c62828"
        mpu_text = "READY" if mpu_stat == 1 else "ERROR"
        st.markdown(f'''
            <div class="sensor-card">
                <div class="sensor-title">⚙️ MPU6050</div>
                <p class="sensor-value" style="color: {mpu_color};">{mpu_text}</p>
            </div>
        ''', unsafe_allow_html=True)

    # --- شريط الإنذار وزرار الواتساب ---
    if alarm == 1:
        st.markdown('''
            <div class="alarm-danger">
                🚨 ACTIVE ALARM: HAZARDOUS ENVIRONMENT DETECTED!
            </div>
        ''', unsafe_allow_html=True)
        
        # زرار الواتساب بيظهر بس لما يكون فيه خطر
        phone_num = "201283605279" # <--- حط رقمك هنا
        msg = f"🚨 EMERGENCY! Hazardous environment. Temp: {temp}C, Gas: {gas}, Vib: {vib}"
        wa_url = f"https://wa.me/{phone_num}?text={urllib.parse.quote(msg)}"
        
        st.markdown(f'''
            <a href="{wa_url}" target="_blank" style="text-decoration: none;">
                <button style="background-color: #25D366; color: white; border: none; padding: 15px 30px; border-radius: 10px; width: 100%; font-size: 18px; font-weight: bold; cursor: pointer; margin-top: 10px; box-shadow: 0 4px 10px rgba(37,211,102,0.3);">
                    📲 SEND WHATSAPP SOS ALERT
                </button>
            </a>
        ''', unsafe_allow_html=True)
        
    else:
        st.markdown('''
            <div class="alarm-safe">
                ✅ NO ACTIVE ALARM
            </div>
        ''', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True) # قفل الكارت الرئيسي

# تشغيل الواجهة
show_dashboard()

# ==========================================
# 4. قسم الذكاء الاصطناعي (تحت خالص)
# ==========================================
st.markdown("<br><hr><br>", unsafe_allow_html=True)
st.markdown("<h3 style='color:#0b3b60;'>🧠 AI Safety Diagnostics</h3>", unsafe_allow_html=True)

if st.button("🔄 Run AI Diagnostics"):
    data = get_data()
    if data:
        try:
            from groq import Groq
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            
            prompt = f"""
            أنت خبير سلامة مهنية. لديك قراءات حية من خوذة ذكية:
            - حرارة: {data.get('field1')} C
            - رطوبة: {data.get('field2')}%
            - غاز: {data.get('field3')}
            - اهتزاز: {data.get('field4')}
            - إنذار: {'مفعل' if data.get('field5') == '1' else 'غير مفعل'}
            المطلوب: تحليل سريع وتوصيات فورية بالعربي.
            """
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="openai/gpt-oss-120b",
            )
            st.info(chat_completion.choices[0].message.content)
        except Exception as e:
            st.error(f"AI Error: {e} (تأكد من إضافة GROQ_API_KEY في الـ Secrets)")
