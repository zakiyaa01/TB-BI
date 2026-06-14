# ============================================================================
# PROYEK TUGAS BESAR BUSINESS INTELLIGENCE
# DASHBOARD VISUALISASI INTERAKTIF (app.py) - DASHBOARD STUDLYTICS (DARK MODE)
# Deskripsi: Dashboard BI lengkap dengan 5 halaman analisis dan modul prediksi ML.
# ============================================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine, text
from sklearn.tree import DecisionTreeClassifier
import os

# --- KONFIGURASI HALAMAN STREAMLIT ---
st.set_page_config(
    page_title="Studlytics - Dashboard BI Kinerja Akademik",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CONFIG KONEKSI DATABASE ---
DB_USER = "root"
DB_PASSWORD = ""  # Sesuaikan dengan password MySQL lokal Anda
DB_HOST = "localhost"
DB_PORT = "3306"
DB_NAME = "student_performance_db"

# --- CUSTOM CSS: PREMIUM DARK THEME ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    /* Global Styles */
    html, body, [class*="css"], .stApp {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        background-color: #080b11 !important;
    }
    
    /* Main container background override */
    .stApp, div[data-testid="stAppViewContainer"] {
        background: radial-gradient(circle at 50% 0%, #101626 0%, #080b11 100%) !important;
    }
    
    /* Sidebar Styles */
    [data-testid="stSidebar"] {
        background-color: #0a0d16 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
    }
    
    /* Typography Colors */
    h1, h2, h3, h4, h5, h6, p, label, .stMarkdown, .stText {
        color: #f1f5f9 !important;
    }
    
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] span {
        color: #cbd5e1 !important;
    }
    
    /* Custom Headings with Left Border Accent */
    h3 {
        font-size: 17px !important;
        font-weight: 700 !important;
        color: #e2e8f0 !important;
        border-left: 4px solid #38bdf8;
        padding-left: 10px;
        margin-top: 25px !important;
        margin-bottom: 15px !important;
    }
    
    /* Glassmorphic Plotly Chart Cards */
    div[data-testid="stPlotlyChart"] {
        background: rgba(15, 22, 38, 0.5) !important;
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 16px;
        padding: 18px;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.2);
        margin-bottom: 24px;
        transition: border-color 0.3s, box-shadow 0.3s;
    }
    div[data-testid="stPlotlyChart"]:hover {
        border-color: rgba(255, 255, 255, 0.12);
        box-shadow: 0 12px 35px rgba(0, 0, 0, 0.3);
    }
    
    /* Hide Plotly mode bar buttons globally */
    .modebar-container {
        display: none !important;
    }
    
    /* Alert / Error Containers */
    div[data-testid="stAlert"] {
        background-color: rgba(30, 41, 59, 0.5) !important;
        backdrop-filter: blur(8px);
        color: #f1f5f9 !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 12px;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.25) !important;
    }
    
    /* KPI Card Style */
    .kpi-card {
        display: flex;
        align-items: center;
        background: rgba(15, 22, 38, 0.55) !important;
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 16px;
        padding: 18px 20px;
        margin-bottom: 15px;
        transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.3s cubic-bezier(0.4, 0, 0.2, 1), border-color 0.3s;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.25);
    }
    .kpi-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 30px rgba(0, 0, 0, 0.4);
        border-color: rgba(255, 255, 255, 0.15) !important;
    }
    .kpi-icon-container {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 48px;
        height: 48px;
        border-radius: 12px;
        margin-right: 16px;
        flex-shrink: 0;
    }
    .kpi-content-container {
        display: flex;
        flex-direction: column;
        text-align: left;
    }
    .kpi-val {
        font-size: 24px;
        font-weight: 800;
        margin: 2px 0 0 0;
        line-height: 1.15;
    }
    .kpi-title {
        font-size: 11px;
        font-weight: 700;
        color: #94a3b8 !important;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin: 0;
    }
    
    /* Main Page Header Gradient */
    .main-header {
        font-size: 34px;
        font-weight: 850;
        background: linear-gradient(135deg, #38bdf8 0%, #818cf8 50%, #c084fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 25px;
        text-align: center;
        letter-spacing: -0.02em;
    }
    
    /* Sidebar Title */
    .sidebar-title {
        font-size: 22px;
        font-weight: 800;
        color: #38bdf8;
        margin-bottom: 20px;
        text-align: center;
        letter-spacing: -0.01em;
        background: linear-gradient(135deg, #38bdf8 0%, #818cf8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* DB Status LED display */
    .db-status-container {
        display: flex;
        align-items: center;
        background: rgba(15, 22, 38, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 10px 14px;
        margin-bottom: 20px;
    }
    .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        margin-right: 10px;
        display: inline-block;
    }
    @keyframes pulse {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 6px rgba(16, 185, 129, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
    }
    .status-online {
        background-color: #10b981;
        animation: pulse 2s infinite;
    }
    @keyframes pulse-offline {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(245, 158, 11, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 6px rgba(245, 158, 11, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(245, 158, 11, 0); }
    }
    .status-offline {
        background-color: #f59e0b;
        animation: pulse-offline 2s infinite;
    }
    .status-text {
        font-size: 12.5px;
        color: #cbd5e1;
    }
    
    /* Radio Button Segmented Control in Sidebar */
    div[data-testid="stSidebar"] div[role="radiogroup"] label {
        background: rgba(30, 41, 59, 0.25) !important;
        border: 1px solid rgba(255, 255, 255, 0.04) !important;
        border-radius: 10px !important;
        padding: 8px 12px !important;
        margin-bottom: 6px !important;
        transition: all 0.25s ease !important;
        width: 100% !important;
    }
    div[data-testid="stSidebar"] div[role="radiogroup"] label > div:nth-child(2) div {
        color: #ffffff !important;
    }
    div[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
        background: rgba(30, 41, 59, 0.5) !important;
        border-color: rgba(56, 189, 248, 0.2) !important;
    }
    div[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
        background: rgba(56, 189, 248, 0.12) !important;
        border-color: rgba(56, 189, 248, 0.45) !important;
    }
    div[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) > div:nth-child(2) div {
        color: #38bdf8 !important;
        font-weight: 700 !important;
    }
    
    /* Profile Analyst Card */
    .analyst-card {
        display: flex;
        align-items: center;
        background: rgba(15, 22, 38, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 14px;
        padding: 12px 14px;
        margin-top: 25px;
    }
    .analyst-avatar {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        background: rgba(56, 189, 248, 0.1);
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 12px;
        border: 1px solid rgba(56, 189, 248, 0.2);
        flex-shrink: 0;
    }
    .analyst-info {
        display: flex;
        flex-direction: column;
    }
    .analyst-name {
        font-size: 12.5px;
        font-weight: 700;
        color: #f1f5f9;
    }
    .analyst-role {
        font-size: 10.5px;
        color: #94a3b8;
    }
    
    /* Tab Navigation Styles */
    button[data-baseweb="tab"] {
        color: #94a3b8 !important;
        font-weight: 600 !important;
        border-bottom: 2px solid transparent !important;
        transition: all 0.3s !important;
        background-color: transparent !important;
        padding-bottom: 8px !important;
    }
    button[data-baseweb="tab"]:hover {
        color: #38bdf8 !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #38bdf8 !important;
        border-bottom-color: #38bdf8 !important;
        font-weight: 700 !important;
    }
    div[data-testid="stTabContent"] {
        background: rgba(15, 22, 38, 0.3) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 14px;
        padding: 20px;
        margin-top: 12px;
    }
    
    /* Native Widget Tuning */
    div[data-testid="stSlider"] div[aria-valuenow] {
        background-color: #38bdf8 !important;
    }
    div[data-testid="stSlider"] div[role="slider"] {
        border: 2px solid #38bdf8 !important;
        background-color: #0c101b !important;
    }
    div[data-baseweb="select"] {
        background-color: rgba(15, 22, 38, 0.4) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 10px !important;
    }
    div[data-baseweb="select"] > div {
        background-color: transparent !important;
        color: #f1f5f9 !important;
    }
    div[role="listbox"] {
        background-color: #0a0d16 !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    div[role="option"] {
        color: #f1f5f9 !important;
    }
    div[role="option"]:hover {
        background-color: rgba(56, 189, 248, 0.15) !important;
    }
    
    /* Form Button */
    div.stButton > button {
        background: linear-gradient(135deg, #38bdf8 0%, #6366f1 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 10px 24px !important;
        font-weight: 700 !important;
        letter-spacing: 0.02em !important;
        box-shadow: 0 4px 15px rgba(56, 189, 248, 0.25) !important;
        transition: all 0.25s ease !important;
        width: 100% !important;
    }
    div.stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 22px rgba(56, 189, 248, 0.45) !important;
        border: none !important;
        color: #ffffff !important;
    }
    div.stButton > button:active {
        transform: translateY(1px) !important;
    }
    
    /* Prediction ML Result Cards */
    .result-card {
        background: rgba(15, 22, 38, 0.6) !important;
        backdrop-filter: blur(8px);
        border-radius: 16px;
        padding: 24px;
        margin-top: 24px;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.35);
        border: 1px solid rgba(255, 255, 255, 0.07);
    }
    .result-high-risk {
        border-left: 6px solid #ef4444 !important;
    }
    .result-low-risk {
        border-left: 6px solid #10b981 !important;
    }
    .result-header {
        display: flex;
        align-items: center;
        margin-bottom: 16px;
    }
    .result-icon {
        width: 30px;
        height: 30px;
        margin-right: 12px;
        flex-shrink: 0;
    }
    .result-header h2 {
        font-size: 19px !important;
        font-weight: 800 !important;
        margin: 0 !important;
        padding: 0 !important;
        background: none !important;
        -webkit-text-fill-color: initial !important;
    }
    .result-high-risk .result-header h2 {
        color: #ef4444 !important;
    }
    .result-low-risk .result-header h2 {
        color: #10b981 !important;
    }
    .result-card p {
        font-size: 13.5px;
        color: #cbd5e1 !important;
        line-height: 1.6;
        margin-bottom: 16px;
    }
    .recommendation-list {
        margin: 0;
        padding-left: 20px;
    }
    .recommendation-list li {
        font-size: 13px;
        color: #e2e8f0 !important;
        margin-bottom: 8px;
        line-height: 1.55;
    }
    .recommendation-list li strong {
        color: #38bdf8 !important;
    }
</style>
""", unsafe_allow_html=True)


def preprocess_data(df):
    """Menambahkan kolom kategorisasi binned secara dinamis pada aplikasi."""
    if df is None:
        return None
        
    df['study_hours_category'] = pd.cut(
        df['study_hours_per_day'], 
        bins=[0, 2, 5, 24], 
        labels=["Rendah", "Sedang", "Tinggi"], 
        include_lowest=True
    ).astype(str)
    
    df['sleep_category'] = pd.cut(
        df['sleep_hours'], 
        bins=[0, 6, 8, 24], 
        labels=["Kurang", "Cukup", "Sangat Cukup"], 
        include_lowest=True
    ).astype(str)
    
    df['stress_category'] = pd.cut(
        df['stress_level'], 
        bins=[0, 3, 7, 10], 
        labels=["Rendah", "Sedang", "Tinggi"], 
        include_lowest=True
    ).astype(str)
    
    df['attendance_category'] = pd.cut(
        df['attendance_percentage'], 
        bins=[0, 75, 90, 100], 
        labels=["Rendah", "Sedang", "Tinggi"], 
        include_lowest=True
    ).astype(str)
    
    df['exercise_category'] = pd.cut(
        df['exercise_frequency'], 
        bins=[-1, 1, 3, 7], 
        labels=["Jarang", "Sedang", "Sering"], 
        include_lowest=True
    ).astype(str)
    
    df['exam_anxiety_category'] = pd.cut(
        df['exam_anxiety_score'], 
        bins=[0, 3, 7, 10], 
        labels=["Rendah", "Sedang", "Tinggi"], 
        include_lowest=True
    ).astype(str)
    
    df['mental_health_category'] = pd.cut(
        df['mental_health_rating'], 
        bins=[0, 4, 7, 10], 
        labels=["Buruk", "Sedang", "Baik"], 
        include_lowest=True
    ).astype(str)
    
    df['dropout_risk_flag'] = df['dropout_risk'].apply(lambda x: 1 if x == 'Yes' else 0)
    return df


# ============================================================================
# DATA ACCESS LAYER (PENGAMBILAN DATA DENGAN FALLBACK)
# ============================================================================
@st.cache_data(show_spinner=False)
def load_data_from_db_or_csv():
    """Membaca data mart dari MySQL. Jika gagal, otomatis fall back ke CSV lokal."""
    db_success = False
    df = None
    connection_url = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    try:
        engine = create_engine(connection_url)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        query = """
        SELECT 
            f.previous_gpa, f.exam_score, f.dropout_risk, f.semester,
            m.age, m.gender, m.major,
            h.study_hours_per_day, h.time_management_score, h.learning_style,
            l.sleep_hours, l.screen_time, l.exercise_frequency, l.diet_quality, l.social_activity,
            p.stress_level, p.mental_health_rating, p.exam_anxiety_score, p.motivation_level,
            e.attendance_percentage, e.extracurricular_participation, e.part_time_job
        FROM fact_academic_performance f
        JOIN dim_student m ON f.student_key = m.student_id
        JOIN dim_study_habit h ON f.study_habit_key = h.study_habit_key
        JOIN dim_lifestyle l ON f.lifestyle_key = l.lifestyle_key
        JOIN dim_psychology p ON f.psychology_key = p.psychology_key
        JOIN dim_engagement e ON f.engagement_key = e.engagement_key
        """
        df = pd.read_sql(query, con=engine)
        db_success = True
        
    except Exception as e:
        csv_filename = "enhanced_student_habits_performance_dataset.csv"
        csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), csv_filename)
        
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
        else:
            df = None
            
    if df is not None:
        df = preprocess_data(df)
        
    return df, db_success


with st.spinner("Memuat Data Mart..."):
    df_raw, is_db_connected = load_data_from_db_or_csv()

if df_raw is None:
    st.error("❌ Data tidak ditemukan! Harap jalankan file 'etl_process.py' terlebih dahulu.")
    st.stop()

# --- FUNGSI MEMBUAT KARTU KPI ---
def create_kpi_card(title, value, column, icon_type="gpa"):
    """Menampilkan KPI card dengan gaya premium dark theme & ikon SVG kustom."""
    icons = {
        "gpa": ('#38bdf8', 'rgba(56, 189, 248, 0.1)', """<svg viewBox="0 0 24 24" width="22" height="22" stroke="#38bdf8" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="M22 10v6M2 10l10-5 10 5-10 5z"></path><path d="M6 12v5c0 2 2 3 6 3s6-1 6-3v-5"></path></svg>"""),
        "exam": ('#fb7185', 'rgba(251, 113, 133, 0.1)', """<svg viewBox="0 0 24 24" width="22" height="22" stroke="#fb7185" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"></path><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"></path></svg>"""),
        "dropout": ('#fbbf24', 'rgba(251, 191, 36, 0.1)', """<svg viewBox="0 0 24 24" width="22" height="22" stroke="#fbbf24" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>"""),
        "attendance": ('#34d399', 'rgba(52, 211, 153, 0.1)', """<svg viewBox="0 0 24 24" width="22" height="22" stroke="#34d399" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>"""),
        "study": ('#c084fc', 'rgba(192, 132, 252, 0.1)', """<svg viewBox="0 0 24 24" width="22" height="22" stroke="#c084fc" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>"""),
    }
    
    color, bg, svg = icons.get(icon_type, icons['gpa'])
    
    column.markdown(
        f"""
        <div class="kpi-card" style="border-left: 4px solid {color};">
            <div class="kpi-icon-container" style="background-color: {bg}; color: {color};">
                {svg}
            </div>
            <div class="kpi-content-container">
                <div class="kpi-title">{title}</div>
                <div class="kpi-val" style="color: {color} !important;">{value}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# --- FUNGSI FORMATTING DIAGRAM UNTUK VISUALISASI TRANSPARAN (MENYATU) ---
def apply_plotly_theme(fig):
    """Mengatur diagram agar memiliki latar belakang transparan dan menyatu dengan halaman."""
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',  
        plot_bgcolor='rgba(0,0,0,0)',   
        font=dict(family="'Plus Jakarta Sans', sans-serif", color='#cbd5e1', size=11),  
        margin=dict(l=40, r=40, t=30, b=40),
        hoverlabel=dict(
            bgcolor='#1c2333',
            font_size=12,
            font_family="'Plus Jakarta Sans', sans-serif",
            bordercolor='rgba(255,255,255,0.1)'
        )
    )
    
    if hasattr(fig, 'layout') and fig.layout:
        if 'xaxis' in fig.layout or any(t.type in ['scatter', 'bar', 'histogram', 'box'] for t in fig.data):
            fig.update_layout(
                xaxis=dict(
                    gridcolor='rgba(255, 255, 255, 0.05)',        
                    linecolor='rgba(255, 255, 255, 0.1)',        
                    zerolinecolor='rgba(255, 255, 255, 0.1)',
                    title=dict(font=dict(size=11, color='#94a3b8'))
                ),
                yaxis=dict(
                    gridcolor='rgba(255, 255, 255, 0.05)',        
                    linecolor='rgba(255, 255, 255, 0.1)',        
                    zerolinecolor='rgba(255, 255, 255, 0.1)',
                    title=dict(font=dict(size=11, color='#94a3b8'))
                )
            )
    return fig

# Palet warna bervariasi sesuai gambar kanan
MIXED_PALETTE = ['#38bdf8', '#fb7185', '#34d399', '#fbbf24', '#c084fc'] 


# --- MODUL MODEL PREDIKSI ML (DECISION TREE CLASSIFIER) ---
@st.cache_resource
def train_prediction_model(df):
    """Melatih model Decision Tree untuk prediksi risiko dropout."""
    features = [
        'study_hours_per_day', 'time_management_score', 'sleep_hours', 'screen_time',
        'exercise_frequency', 'stress_level', 'mental_health_rating', 'exam_anxiety_score',
        'attendance_percentage', 'extracurricular_participation_encoded'
    ]
    df_train = df.copy()
    df_train['extracurricular_participation_encoded'] = df_train['extracurricular_participation'].apply(lambda x: 1 if x == 'Yes' else 0)
    
    X = df_train[features]
    y = df_train['dropout_risk_flag']
    
    # Train
    model = DecisionTreeClassifier(max_depth=5, random_state=42)
    model.fit(X, y)
    return model

# Train model
ml_model = train_prediction_model(df_raw)


# ============================================================================
# SIDEBAR: NAVIGASI & FILTER GLOBAL
# ============================================================================
with st.sidebar:
    st.markdown('<div class="sidebar-title">Studlytics BI</div>', unsafe_allow_html=True)
    
    # DB connection status indicator
    if is_db_connected:
        status_html = """
        <div class="db-status-container">
            <span class="status-dot status-online"></span>
            <span class="status-text">Database MySQL: <strong>Aktif</strong></span>
        </div>
        """
    else:
        status_html = """
        <div class="db-status-container">
            <span class="status-dot status-offline"></span>
            <span class="status-text">Database MySQL: <strong>Offline (CSV)</strong></span>
        </div>
        """
    st.markdown(status_html, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.subheader("Navigasi Analisis")
    page = st.radio(
        "Pilih Halaman Analisis:",
        [
            "1. Executive Summary",
            "2. Study Habits Analysis",
            "3. Lifestyle & Psychology Analysis",
            "4. Engagement & Risk Analysis",
            "5. Prediction (ML)"
        ]
    )
    
    st.markdown("---")
    
    # Filter Global dinonaktifkan khusus untuk Halaman Prediksi ML agar input fleksibel
    if page != "5. Prediction (ML)":
        st.subheader("Filter Global")
        
        # Filter Program Studi
        all_majors = sorted(df_raw['major'].unique().tolist())
        selected_majors = st.multiselect("Program Studi (Major):", options=all_majors, default=all_majors)
        
        # Filter Jenis Kelamin
        all_genders = sorted(df_raw['gender'].unique().tolist())
        selected_genders = st.multiselect("Jenis Kelamin:", options=all_genders, default=all_genders)
        
        # Filter Semester
        all_semesters = sorted(df_raw['semester'].unique().tolist())
        selected_semesters = st.multiselect("Semester:", options=all_semesters, default=all_semesters)

    # Analyst profile card at the bottom of sidebar
    analyst_card_html = """
    <div class="analyst-card">
        <div class="analyst-avatar">
            <svg viewBox="0 0 24 24" width="20" height="20" stroke="#38bdf8" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
        </div>
        <div class="analyst-info">
            <div class="analyst-role">Suci Nurhaliza</div>
            <div class="analyst-role">Zakiya Aulia</div>
        </div>
    </div>
    """
    st.markdown(analyst_card_html, unsafe_allow_html=True)


# ============================================================================
# PROSES FILTERING DATA GLOBAL
# ============================================================================
if page != "5. Prediction (ML)":
    df_filtered = df_raw.copy()

    if selected_majors:
        df_filtered = df_filtered[df_filtered['major'].isin(selected_majors)]
    else:
        df_filtered = df_filtered.head(0)

    if selected_genders:
        df_filtered = df_filtered[df_filtered['gender'].isin(selected_genders)]
    else:
        df_filtered = df_filtered.head(0)

    if selected_semesters:
        df_filtered = df_filtered[df_filtered['semester'].isin(selected_semesters)]
    else:
        df_filtered = df_filtered.head(0)

    if df_filtered.empty:
        st.warning("⚠️ Tidak ada data yang cocok dengan kriteria filter global Anda. Harap ubah filter di sidebar.")
        st.stop()


# ============================================================================
# HALAMAN 1: EXECUTIVE SUMMARY
# ============================================================================
if page == "1. Executive Summary":
    st.markdown('<div class="main-header">Dashboard Studlytics - Executive Summary</div>', unsafe_allow_html=True)
    
    # KPI Row (5 Cards)
    kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5 = st.columns(5)
    
    avg_gpa = df_filtered['previous_gpa'].mean()
    avg_exam = df_filtered['exam_score'].mean()
    dropout_risk_pct = (df_filtered['dropout_risk_flag'].mean()) * 100
    avg_attend = df_filtered['attendance_percentage'].mean()
    avg_study = df_filtered['study_hours_per_day'].mean()
    
    create_kpi_card("Rata-Rata GPA", f"{avg_gpa:.2f} / 4.00", kpi_col1, "gpa")
    create_kpi_card("Rata-Rata Exam Score", f"{avg_exam:.1f}", kpi_col2, "exam")
    create_kpi_card("Tingkat Dropout Risk", f"{dropout_risk_pct:.2f}%", kpi_col3, "dropout")
    create_kpi_card("Rata-Rata Attendance", f"{avg_attend:.1f}%", kpi_col4, "attendance")
    create_kpi_card("Rata-Rata Study Hours", f"{avg_study:.1f} Jam", kpi_col5, "study")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("GPA Distribution (Histogram)")
        fig_gpa_dist = px.histogram(
            df_filtered, 
            x='previous_gpa', 
            nbins=30, 
            color_discrete_sequence=['#38bdf8'],
            labels={'previous_gpa': 'IPK (GPA)', 'count': 'Jumlah Mahasiswa'}
        )
        apply_plotly_theme(fig_gpa_dist)
        st.plotly_chart(fig_gpa_dist, use_container_width=True, theme=None)
        
    with col2:
        st.subheader("Exam Score Distribution (Histogram)")
        fig_exam_dist = px.histogram(
            df_filtered, 
            x='exam_score', 
            nbins=30, 
            color_discrete_sequence=['#fb7185'],
            labels={'exam_score': 'Nilai Ujian', 'count': 'Jumlah Mahasiswa'}
        )
        apply_plotly_theme(fig_exam_dist)
        st.plotly_chart(fig_exam_dist, use_container_width=True, theme=None)
        
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("Dropout Risk Composition")
        risk_comp = df_filtered['dropout_risk'].value_counts().reset_index()
        risk_comp.columns = ['dropout_risk', 'count']
        # Map ke labels baru
        risk_comp['Label'] = risk_comp['dropout_risk'].map({'Yes': 'High Risk', 'No': 'Low Risk'})
        fig_risk_pie = px.pie(
            risk_comp, 
            values='count', 
            names='Label',
            hole=0.4,
            color_discrete_sequence=['#34d399', '#f87171'] # Low Risk (Hijau), High Risk (Merah)
        )
        apply_plotly_theme(fig_risk_pie)
        st.plotly_chart(fig_risk_pie, use_container_width=True, theme=None)
        
    with col4:
        st.subheader("Top Major Performance (Major vs Average GPA)")
        major_perf = df_filtered.groupby('major')['previous_gpa'].mean().reset_index().sort_values(by='previous_gpa', ascending=False)
        fig_major_perf = px.bar(
            major_perf,
            x='previous_gpa',
            y='major',
            orientation='h',
            color='major',
            color_discrete_sequence=MIXED_PALETTE,
            text_auto='.2f',
            labels={'previous_gpa': 'Rata-Rata GPA', 'major': 'Program Studi'}
        )
        apply_plotly_theme(fig_major_perf)
        fig_major_perf.update_layout(showlegend=False)
        st.plotly_chart(fig_major_perf, use_container_width=True, theme=None)


# ============================================================================
# HALAMAN 2: STUDY HABITS & ACADEMIC PERFORMANCE
# ============================================================================
elif page == "2. Study Habits Analysis":
    st.markdown('<div class="main-header">Study Habits & Academic Performance Analysis</div>', unsafe_allow_html=True)
    
    # Ambil sampel 2000 data agar scatter plot responsif
    df_sample = df_filtered.sample(n=min(2000, len(df_filtered)), random_state=42)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Study Hours vs GPA")
        fig_sh_gpa = px.scatter(
            df_sample,
            x='study_hours_per_day',
            y='previous_gpa',
            color='study_hours_category',
            trendline='ols',
            color_discrete_sequence=['#34d399', '#fbbf24', '#f87171'],
            labels={'study_hours_per_day': 'Jam Belajar / Hari', 'previous_gpa': 'GPA (IPK)'}
        )
        apply_plotly_theme(fig_sh_gpa)
        st.plotly_chart(fig_sh_gpa, use_container_width=True, theme=None)
        
    with col2:
        st.subheader("Time Management vs GPA")
        fig_tm_gpa = px.scatter(
            df_sample,
            x='time_management_score',
            y='previous_gpa',
            color='study_hours_category',
            trendline='ols',
            color_discrete_sequence=['#34d399', '#fbbf24', '#f87171'],
            labels={'time_management_score': 'Skor Manajemen Waktu', 'previous_gpa': 'GPA (IPK)'}
        )
        apply_plotly_theme(fig_tm_gpa)
        st.plotly_chart(fig_tm_gpa, use_container_width=True, theme=None)
        
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("Study Hours Category vs Average GPA")
        gpa_by_cat = df_filtered.groupby('study_hours_category')['previous_gpa'].mean().reset_index()
        fig_sh_cat = px.bar(
            gpa_by_cat,
            x='study_hours_category',
            y='previous_gpa',
            color='study_hours_category',
            color_discrete_sequence=['#f87171', '#fbbf24', '#34d399'],
            text_auto='.2f',
            labels={'study_hours_category': 'Kategori Jam Belajar', 'previous_gpa': 'Rata-Rata GPA'}
        )
        apply_plotly_theme(fig_sh_cat)
        fig_sh_cat.update_layout(showlegend=False)
        st.plotly_chart(fig_sh_cat, use_container_width=True, theme=None)
        
    with col4:
        st.subheader("Correlation Heatmap (Study Habits & Academic)")
        corr_cols = ['study_hours_per_day', 'time_management_score', 'previous_gpa', 'exam_score']
        friendly_labels = ['Study Hours', 'Time Management', 'GPA', 'Exam Score']
        corr_matrix = df_filtered[corr_cols].corr()
        
        fig_corr = px.imshow(
            corr_matrix,
            x=friendly_labels,
            y=friendly_labels,
            color_continuous_scale='RdBu_r',
            text_auto='.2f'
        )
        apply_plotly_theme(fig_corr)
        st.plotly_chart(fig_corr, use_container_width=True, theme=None)
        
    st.markdown("---")
    st.markdown("### 💡 Insight Kebiasaan Belajar")
    # Hitung data riil untuk insight
    high_study_gpa = df_filtered[df_filtered['study_hours_per_day'] > 5]['previous_gpa'].mean()
    low_study_gpa = df_filtered[df_filtered['study_hours_per_day'] <= 2]['previous_gpa'].mean()
    diff_pct = ((high_study_gpa - low_study_gpa) / low_study_gpa) * 100
    
    st.info(f"**Hasil Analisis Data**: Mahasiswa dengan jam belajar >5 jam per hari memiliki rata-rata GPA **{high_study_gpa:.2f}**, yaitu sekitar **{diff_pct:.1f}% lebih tinggi** dibandingkan mahasiswa dengan jam belajar rendah ≤2 jam per hari (**{low_study_gpa:.2f}**). Hal ini menunjukkan adanya korelasi positif yang kuat antara alokasi waktu belajar dengan pencapaian prestasi akademik.")


# ============================================================================
# HALAMAN 3: LIFESTYLE & PSYCHOLOGY ANALYSIS
# ============================================================================
elif page == "3. Lifestyle & Psychology Analysis":
    st.markdown('<div class="main-header">Lifestyle & Psychology Analysis</div>', unsafe_allow_html=True)
    
    df_sample = df_filtered.sample(n=min(2000, len(df_filtered)), random_state=42)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Sleep Hours vs GPA")
        fig_sleep_gpa = px.scatter(
            df_sample, 
            x='sleep_hours', 
            y='previous_gpa', 
            trendline='ols',
            color_discrete_sequence=['#38bdf8'],
            labels={'sleep_hours': 'Jam Tidur', 'previous_gpa': 'GPA (IPK)'}
        )
        apply_plotly_theme(fig_sleep_gpa)
        st.plotly_chart(fig_sleep_gpa, use_container_width=True, theme=None)
        
    with col2:
        st.subheader("Screen Time vs Exam Score")
        fig_screen_exam = px.scatter(
            df_sample, 
            x='screen_time', 
            y='exam_score', 
            trendline='ols',
            color_discrete_sequence=['#fb7185'],
            labels={'screen_time': 'Screen Time (Jam)', 'exam_score': 'Nilai Ujian'}
        )
        apply_plotly_theme(fig_screen_exam)
        st.plotly_chart(fig_screen_exam, use_container_width=True, theme=None)

    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("Exercise Frequency vs GPA")
        exercise_gpa = df_filtered.groupby('exercise_frequency')['previous_gpa'].mean().reset_index()
        fig_exercise = px.bar(
            exercise_gpa, 
            x='exercise_frequency', 
            y='previous_gpa',
            color='exercise_frequency',
            color_continuous_scale='Teal',
            text_auto='.2f',
            labels={'exercise_frequency': 'Frekuensi Olahraga / Minggu', 'previous_gpa': 'Rata-Rata GPA'}
        )
        apply_plotly_theme(fig_exercise)
        fig_exercise.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig_exercise, use_container_width=True, theme=None)
        
    with col4:
        st.subheader("Stress Level vs GPA (Boxplot)")
        fig_stress_box = px.box(
            df_sample, 
            x='stress_level', 
            y='previous_gpa',
            color='stress_category',
            color_discrete_sequence=['#34d399', '#fbbf24', '#f87171'],
            labels={'stress_level': 'Tingkat Stres', 'previous_gpa': 'GPA (IPK)'}
        )
        apply_plotly_theme(fig_stress_box)
        st.plotly_chart(fig_stress_box, use_container_width=True, theme=None)

    col5, col6 = st.columns(2)
    
    with col5:
        st.subheader("Mental Health vs Exam Score")
        mental_exam = df_filtered.groupby('mental_health_category')['exam_score'].mean().reset_index()
        fig_mental = px.bar(
            mental_exam, 
            x='mental_health_category', 
            y='exam_score',
            color='mental_health_category',
            color_discrete_sequence=['#f87171', '#fbbf24', '#34d399'], # Buruk (Merah), Sedang (Kuning), Baik (Hijau)
            text_auto='.1f',
            labels={'mental_health_category': 'Rating Kesehatan Mental', 'exam_score': 'Rata-Rata Ujian'}
        )
        apply_plotly_theme(fig_mental)
        fig_mental.update_layout(showlegend=False)
        st.plotly_chart(fig_mental, use_container_width=True, theme=None)
        
    with col6:
        st.subheader("Exam Anxiety vs GPA")
        fig_anxiety = px.scatter(
            df_sample, 
            x='exam_anxiety_score', 
            y='previous_gpa', 
            trendline='ols',
            color_discrete_sequence=['#c084fc'],
            labels={'exam_anxiety_score': 'Skor Kecemasan Ujian', 'previous_gpa': 'GPA (IPK)'}
        )
        apply_plotly_theme(fig_anxiety)
        st.plotly_chart(fig_anxiety, use_container_width=True, theme=None)

    st.subheader("Correlation Matrix (Lifestyle & Psychology)")
    corr_cols_lp = ['sleep_hours', 'screen_time', 'exercise_frequency', 'stress_level', 'mental_health_rating', 'exam_anxiety_score', 'previous_gpa', 'exam_score']
    friendly_labels_lp = ['Sleep', 'Screen Time', 'Exercise', 'Stress', 'Mental Health', 'Anxiety', 'GPA', 'Exam Score']
    corr_matrix_lp = df_filtered[corr_cols_lp].corr()
    
    fig_corr_lp = px.imshow(
        corr_matrix_lp,
        x=friendly_labels_lp,
        y=friendly_labels_lp,
        color_continuous_scale='RdBu_r',
        text_auto='.2f'
    )
    apply_plotly_theme(fig_corr_lp)
    st.plotly_chart(fig_corr_lp, use_container_width=True, theme=None)

    st.markdown("---")
    st.markdown("### 💡 Insight Gaya Hidup & Psikologis")
    # Hitung korelasi stres vs GPA
    stress_gpa_corr = df_filtered['stress_level'].corr(df_filtered['previous_gpa'])
    st.info(f"**Hasil Analisis Data**: Koefisien korelasi antara Tingkat Stres dan GPA mahasiswa adalah **{stress_gpa_corr:.2f}**. Hal ini membuktikan adanya hubungan korelasi negatif yang nyata di mana semakin tinggi tingkat stres dan kecemasan ujian yang dirasakan mahasiswa, maka semakin cenderung menurun capaian GPA akademik mereka. Pemeliharaan kesehatan mental yang baik berkontribusi nyata pada stabilitas nilai ujian.")


# ============================================================================
# HALAMAN 4: ACADEMIC ENGAGEMENT & RISK ANALYSIS
# ============================================================================
elif page == "4. Engagement & Risk Analysis":
    st.markdown('<div class="main-header">Academic Engagement & Risk Analysis</div>', unsafe_allow_html=True)
    
    df_sample = df_filtered.sample(n=min(2000, len(df_filtered)), random_state=42)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Attendance vs GPA")
        fig_attend_gpa = px.scatter(
            df_sample, 
            x='attendance_percentage', 
            y='previous_gpa', 
            trendline='ols',
            color_discrete_sequence=['#38bdf8'],
            labels={'attendance_percentage': 'Kehadiran (%)', 'previous_gpa': 'GPA (IPK)'}
        )
        apply_plotly_theme(fig_attend_gpa)
        st.plotly_chart(fig_attend_gpa, use_container_width=True, theme=None)
        
    with col2:
        st.subheader("Attendance Category vs Exam Score")
        attend_exam = df_filtered.groupby('attendance_category')['exam_score'].mean().reset_index()
        fig_attend_bar = px.bar(
            attend_exam,
            x='attendance_category',
            y='exam_score',
            color='attendance_category',
            color_discrete_sequence=['#f87171', '#fbbf24', '#34d399'], # Rendah, Sedang, Tinggi
            text_auto='.1f',
            labels={'attendance_category': 'Kategori Kehadiran', 'exam_score': 'Rata-Rata Ujian'}
        )
        apply_plotly_theme(fig_attend_bar)
        fig_attend_bar.update_layout(showlegend=False)
        st.plotly_chart(fig_attend_bar, use_container_width=True, theme=None)

    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("Extracurricular Participation vs Average GPA")
        extra_gpa = df_filtered.groupby('extracurricular_participation')['previous_gpa'].mean().reset_index()
        fig_extra_gpa = px.bar(
            extra_gpa,
            x='extracurricular_participation',
            y='previous_gpa',
            color='extracurricular_participation',
            color_discrete_sequence=['#f97316', '#3b82f6'], # Orange, Biru
            text_auto='.2f',
            labels={'extracurricular_participation': 'Partisipasi Ekstrakurikuler', 'previous_gpa': 'Rata-Rata GPA'}
        )
        apply_plotly_theme(fig_extra_gpa)
        fig_extra_gpa.update_layout(showlegend=False)
        st.plotly_chart(fig_extra_gpa, use_container_width=True, theme=None)
        
    with col4:
        st.subheader("Dropout Risk Distribution")
        risk_dist = df_filtered['dropout_risk'].value_counts().reset_index()
        risk_dist.columns = ['dropout_risk', 'count']
        fig_risk_pie2 = px.pie(
            risk_dist,
            values='count',
            names='dropout_risk',
            hole=0.4,
            color_discrete_sequence=['#34d399', '#f87171'] # No (Hijau), Yes (Merah)
        )
        apply_plotly_theme(fig_risk_pie2)
        st.plotly_chart(fig_risk_pie2, use_container_width=True, theme=None)

    col5, col6 = st.columns(2)
    
    with col5:
        st.subheader("Dropout Risk by Attendance")
        risk_by_attend = df_filtered.groupby('attendance_category')['dropout_risk_flag'].mean().reset_index()
        risk_by_attend['dropout_risk_rate'] = risk_by_attend['dropout_risk_flag'] * 100
        fig_risk_attend = px.bar(
            risk_by_attend,
            x='attendance_category',
            y='dropout_risk_rate',
            color='attendance_category',
            color_discrete_sequence=['#f87171', '#fbbf24', '#34d399'],
            text_auto='.2f',
            labels={'attendance_category': 'Kategori Kehadiran', 'dropout_risk_rate': 'Tingkat Risiko Dropout (%)'}
        )
        apply_plotly_theme(fig_risk_attend)
        fig_risk_attend.update_layout(showlegend=False)
        st.plotly_chart(fig_risk_attend, use_container_width=True, theme=None)
        
    with col6:
        st.subheader("Dropout Risk by Stress Level")
        risk_by_stress = df_filtered.groupby('stress_category')['dropout_risk_flag'].mean().reset_index()
        risk_by_stress['dropout_risk_rate'] = risk_by_stress['dropout_risk_flag'] * 100
        fig_risk_stress = px.bar(
            risk_by_stress,
            x='stress_category',
            y='dropout_risk_rate',
            color='stress_category',
            color_discrete_sequence=['#34d399', '#fbbf24', '#f87171'], # Rendah, Sedang, Tinggi
            text_auto='.2f',
            labels={'stress_category': 'Kategori Stress', 'dropout_risk_rate': 'Tingkat Risiko Dropout (%)'}
        )
        apply_plotly_theme(fig_risk_stress)
        fig_risk_stress.update_layout(showlegend=False)
        st.plotly_chart(fig_risk_stress, use_container_width=True, theme=None)

    # Tambahan visualisasi ke-3 (Dropout Risk by Study Hours)
    st.subheader("Dropout Risk by Study Hours")
    risk_by_study = df_filtered.groupby('study_hours_category')['dropout_risk_flag'].mean().reset_index()
    risk_by_study['dropout_risk_rate'] = risk_by_study['dropout_risk_flag'] * 100
    fig_risk_study = px.bar(
        risk_by_study,
        x='study_hours_category',
        y='dropout_risk_rate',
        color='study_hours_category',
        color_discrete_sequence=['#f87171', '#fbbf24', '#34d399'],
        text_auto='.2f',
        labels={'study_hours_category': 'Kategori Jam Belajar', 'dropout_risk_rate': 'Tingkat Risiko Dropout (%)'}
    )
    apply_plotly_theme(fig_risk_study)
    fig_risk_study.update_layout(showlegend=False, height=350)
    st.plotly_chart(fig_risk_study, use_container_width=True, theme=None)

    st.markdown("---")
    st.markdown("### 💡 Insight Keterlibatan & Risiko Akademik")
    # Hitung tingkat risiko dropout
    risk_low_attend = df_filtered[df_filtered['attendance_percentage'] < 75]['dropout_risk_flag'].mean()
    risk_high_attend = df_filtered[df_filtered['attendance_percentage'] >= 75]['dropout_risk_flag'].mean()
    ratio_risk = risk_low_attend / max(0.001, risk_high_attend)
    
    st.info(f"**Hasil Analisis Data**: Mahasiswa dengan persentase kehadiran kuliah yang rendah (<75%) memiliki tingkat risiko dropout **{(risk_low_attend*100):.1f}%**, sementara mahasiswa dengan kehadiran tinggi memiliki tingkat risiko **{(risk_high_attend*100):.1f}%**. Ini menunjukkan bahwa mahasiswa dengan tingkat kehadiran rendah memiliki **risiko dropout {ratio_risk:.1f} kali lipat lebih tinggi** dibandingkan rekan mereka yang aktif mengikuti perkuliahan.")


# ============================================================================
# HALAMAN 5: PREDICTIVE ANALYTICS (ML MODEL PREDIKSI)
# ============================================================================
elif page == "5. Prediction (ML)":
    st.markdown('<div class="main-header">Predictive Analytics - Dropout Risk Prediction</div>', unsafe_allow_html=True)
    
    st.write("Gunakan form di bawah ini untuk menginput parameter profil harian mahasiswa dan memprediksi tingkat risiko dropout secara instan berdasarkan algoritma Machine Learning.")
    st.write("---")
    
    # Tabs for modern grouped parameters
    tab_academic, tab_lifestyle, tab_psychology = st.tabs([
        "📚 Akademik & Kehadiran", 
        "💤 Gaya Hidup & Aktivitas", 
        "🧠 Kondisi Psikologis"
    ])
    
    with tab_academic:
        st.markdown("<br>", unsafe_allow_html=True)
        input_study_hours = st.slider("Jam Belajar Per Hari:", min_value=0.0, max_value=24.0, value=5.0, step=0.5)
        input_time_mgmt = st.slider("Skor Manajemen Waktu (1 - 10):", min_value=1.0, max_value=10.0, value=6.5, step=0.1)
        input_attendance = st.slider("Persentase Kehadiran Kuliah (%):", min_value=0.0, max_value=100.0, value=85.0, step=1.0)
        input_extra = st.selectbox("Ikut Ekstrakurikuler?", options=["Yes", "No"], index=1)
        
    with tab_lifestyle:
        st.markdown("<br>", unsafe_allow_html=True)
        input_sleep_hours = st.slider("Jam Tidur Per Hari:", min_value=2.0, max_value=12.0, value=7.0, step=0.5)
        input_screen_time = st.slider("Penggunaan Screen Time (Jam):", min_value=0.0, max_value=18.0, value=5.5, step=0.5)
        input_exercise = st.slider("Frekuensi Olahraga (Hari / Minggu):", min_value=0, max_value=7, value=2, step=1)
        
    with tab_psychology:
        st.markdown("<br>", unsafe_allow_html=True)
        input_stress = st.slider("Tingkat Stres (Skala 1 - 10):", min_value=1, max_value=10, value=5, step=1)
        input_mental = st.slider("Rating Kesehatan Mental (Skala 1 - 10):", min_value=1, max_value=10, value=7, step=1)
        input_anxiety = st.slider("Rating Kecemasan Ujian (Skala 1 - 10):", min_value=1, max_value=10, value=4, step=1)

    st.markdown("---")
    col_pred1, col_pred2 = st.columns([2, 1])
    
    with col_pred1:
        st.markdown("### ⚙️ Jalankan Engine Prediksi")
        st.write("Model prediksi menggunakan algoritma *Decision Tree Classifier* yang dilatih langsung pada seluruh dataset mahasiswa untuk menemukan pola dropout terkini.")
    
    with col_pred2:
        st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)
        predict_button = st.button("Prediksi Risiko Sekarang", use_container_width=True)
        
    if predict_button:
        # Siapkan fitur data input
        # extracurricular di-encode
        extra_encoded = 1 if input_extra == "Yes" else 0
        
        # Format input
        input_features = np.array([[
            input_study_hours,
            input_time_mgmt,
            input_sleep_hours,
            input_screen_time,
            input_exercise,
            input_stress,
            input_mental,
            input_anxiety,
            input_attendance,
            extra_encoded
        ]])
        
        # Jalankan prediksi
        prediction = ml_model.predict(input_features)[0]
        
        if prediction == 1:
            # High Risk HTML card
            risk_html = """
            <div class="result-card result-high-risk">
                <div class="result-header">
                    <svg class="result-icon" viewBox="0 0 24 24" stroke="#ef4444" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>
                    <h2>HIGH RISK (Risiko Tinggi Putus Kuliah)</h2>
                </div>
                <p>Mahasiswa diprediksi memiliki risiko putus kuliah/dropout yang tinggi berdasarkan pola aktivitasnya. Disarankan mengambil tindakan preventif berikut:</p>
                <ul class="recommendation-list">
                    <li><strong>Konseling Akademik:</strong> Jadwalkan bimbingan khusus untuk mengevaluasi tantangan studi.</li>
                    <li><strong>Manajemen Waktu:</strong> Sarankan mahasiswa menyusun jadwal harian yang lebih realistis dan seimbang.</li>
                    <li><strong>Intervensi Kehadiran:</strong> Dorong mahasiswa untuk meningkatkan tingkat kehadiran perkuliahan di atas 80%.</li>
                    <li><strong>Dukungan Kesehatan Mental:</strong> Tawarkan layanan konseling untuk mengatasi stres dan kecemasan ujian.</li>
                </ul>
            </div>
            """
            st.markdown(risk_html, unsafe_allow_html=True)
        else:
            # Low Risk HTML card
            safe_html = """
            <div class="result-card result-low-risk">
                <div class="result-header">
                    <svg class="result-icon" viewBox="0 0 24 24" stroke="#10b981" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
                    <h2>LOW RISK (Risiko Rendah / Aman)</h2>
                </div>
                <p>Mahasiswa berada pada rentang aman dari risiko dropout. Pola aktivitas dan performa harian dinilai sehat dan konsisten. Pertahankan kondisi ini dengan rekomendasi berikut:</p>
                <ul class="recommendation-list">
                    <li><strong>Konsistensi Kebiasaan:</strong> Pertahankan alokasi jam belajar dan istirahat yang seimbang seperti saat ini.</li>
                    <li><strong>Kehadiran & Partisipasi:</strong> Tetap aktif menghadiri kelas dan pertahankan keterlibatan di kampus.</li>
                    <li><strong>Evaluasi Berkala:</strong> Lakukan peninjauan performa di akhir semester secara rutin untuk memastikan kestabilan nilai.</li>
                </ul>
            </div>
            """
            st.markdown(safe_html, unsafe_allow_html=True)
