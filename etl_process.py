# ============================================================================
# PROYEK TUGAS BESAR BUSINESS INTELLIGENCE
# PIPELINE ETL PYTHON (etl_process.py) - NEW DATASET ALIGNED
# Deskripsi: Melakukan pembersihan data, penanganan outlier, standardisasi,
#            dan memuat data ke data mart MySQL sesuai skema baru.
# ============================================================================

import os
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
from sklearn.preprocessing import MinMaxScaler, StandardScaler, LabelEncoder

# --- KONFIGURASI KONEKSI DATABASE ---
DB_USER = "root"
DB_PASSWORD = ""  # Silakan sesuaikan password MySQL Anda di sini
DB_HOST = "localhost"
DB_PORT = "3306"
DB_NAME = "student_performance_db"

def get_db_engine():
    """Membuat koneksi ke basis data MySQL menggunakan SQLAlchemy."""
    connection_url = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    return create_engine(connection_url)

def setup_database_if_needed():
    """Membuat database jika belum ada, lalu menginisialisasi skema tabel dari data_mart.sql."""
    print("[SETUP] Memeriksa status database MySQL...")
    base_url = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}"
    temp_engine = create_engine(base_url)
    
    try:
        with temp_engine.connect() as conn:
            conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}"))
        print(f"[SETUP] Database '{DB_NAME}' dipastikan siap.")
    except Exception as e:
        print(f"[SETUP WARNING] Gagal terhubung ke MySQL Server: {str(e)}")
        print("Pastikan server MySQL Anda aktif di port 3306.")
        raise e

    # Membaca file data_mart.sql untuk inisialisasi tabel
    sql_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data_mart.sql")
    if os.path.exists(sql_path):
        print(f"[SETUP] Membaca skema tabel dari: data_mart.sql...")
        with open(sql_path, "r", encoding="utf-8") as f:
            sql_content = f.read()
        
        # Pisahkan pernyataan SQL berdasarkan semicolon (;)
        statements = []
        current_stmt = []
        for line in sql_content.split('\n'):
            clean_line = line.split('--')[0].strip()
            if not clean_line:
                continue
            current_stmt.append(clean_line)
            if clean_line.endswith(';'):
                statements.append(" ".join(current_stmt))
                current_stmt = []
        
        # Eksekusi pernyataan SQL satu per satu
        db_url = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        db_engine = create_engine(db_url)
        try:
            with db_engine.begin() as conn:
                conn.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
                for stmt in statements:
                    if stmt.strip():
                        conn.execute(text(stmt))
                conn.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))
            print("[SETUP] Seluruh tabel skema bintang berhasil diinisialisasi.")
        except Exception as e:
            print(f"[SETUP ERROR] Gagal mengeksekusi skrip SQL data_mart.sql: {str(e)}")
            raise e
    else:
        print("[SETUP WARNING] File data_mart.sql tidak ditemukan. Melewati inisialisasi skema.")

def run_etl():
    print("=== MEMULAI PROSES ETL (EXTRACT, TRANSFORM, LOAD) ===")
    
    # Setup database dan tabel terlebih dahulu
    try:
        setup_database_if_needed()
    except Exception as e:
        print("\n[ERROR] Setup database gagal. ETL akan dicoba tetapi kemungkinan akan eror.")
        raise e

    # ============================================================================
    # 1. STEP: EXTRACT (Ekstraksi Data)
    # ============================================================================
    csv_filename = "enhanced_student_habits_performance_dataset.csv"
    csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), csv_filename)
    
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Dataset tidak ditemukan di {csv_path}. Harap jalankan pembuat data terlebih dahulu.")
        
    print(f"[EXTRACT] Membaca data mentah dari: {csv_filename}...")
    df = pd.read_csv(csv_path)
    print(f"[EXTRACT] Data berhasil diekstrak. Total baris: {len(df)}, Kolom: {len(df.columns)}")

    # ============================================================================
    # 2. STEP: TRANSFORM (Transformasi & Pembersihan Data)
    # ============================================================================
    print("\n[TRANSFORM] Memulai proses transformasi data...")

    # A. Data Cleaning: Menghapus data duplikat
    initial_rows = len(df)
    df = df.drop_duplicates()
    duplicated_rows = initial_rows - len(df)
    if duplicated_rows > 0:
        print(f"   -> Menghapus {duplicated_rows} data duplikat.")
    else:
        print("   -> Tidak ditemukan data duplikat.")

    # B. Data Cleaning: Penanganan Missing Values (Imputasi)
    # Kolom numerik diimputasi menggunakan Median
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if 'student_id' in num_cols: num_cols.remove('student_id')
    if 'semester' in num_cols: num_cols.remove('semester')
    
    for col in num_cols:
        if df[col].isnull().any():
            median_val = df[col].median()
            df[col] = df[col].fillna(median_val)
            print(f"   -> Mengisi missing values pada kolom numerik '{col}' dengan Median: {median_val}")

    # Kolom kategorikal diimputasi menggunakan Modus
    cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    for col in cat_cols:
        if df[col].isnull().any():
            mode_val = df[col].mode()[0]
            df[col] = df[col].fillna(mode_val)
            print(f"   -> Mengisi missing values pada kolom kategorikal '{col}' dengan Modus: '{mode_val}'")

    # C. Outlier Handling menggunakan Interquartile Range (IQR) & Clip
    # Dilakukan khusus pada atribut kondisi psikologis
    psych_cols = ['stress_level', 'mental_health_rating', 'exam_anxiety_score', 'motivation_level']
    print("   -> Menangani Outliers pada variabel psikologis dengan metode IQR:")
    for col in psych_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        df[col] = df[col].clip(lower_bound, upper_bound)
        print(f"      - '{col}': Batas Bawah = {lower_bound:.2f}, Batas Atas = {upper_bound:.2f}")

    # D. Normalisasi & Standardisasi Data (Scikit-Learn)
    # Gunakan MinMaxScaler untuk normalisasi data numerik umum ke skala [0, 1]
    general_num_cols = [
        'study_hours_per_day', 'time_management_score', 'stress_level', 
        'mental_health_rating', 'exam_anxiety_score', 'attendance_percentage'
    ]
    min_max_scaler = MinMaxScaler()
    df_normalized = pd.DataFrame(
        min_max_scaler.fit_transform(df[general_num_cols]),
        columns=[f"{col}_normalized" for col in general_num_cols],
        index=df.index
    )
    df = pd.concat([df, df_normalized], axis=1)
    print("   -> Berhasil melakukan normalisasi dengan MinMaxScaler.")

    # Gunakan StandardScaler khusus untuk atribut gaya hidup (lifestyle_cols)
    lifestyle_cols = ['sleep_hours', 'screen_time', 'exercise_frequency', 'social_activity']
    std_scaler = StandardScaler()
    df_standardized = pd.DataFrame(
        std_scaler.fit_transform(df[lifestyle_cols]),
        columns=[f"{col}_std" for col in lifestyle_cols],
        index=df.index
    )
    df = pd.concat([df, df_standardized], axis=1)
    print("   -> Berhasil melakukan standardisasi dengan StandardScaler untuk lifestyle_cols.")

    # E. Validasi Konsistensi Data menggunakan Assert
    print("   -> Melakukan validasi konsistensi data (Assert)...")
    try:
        assert df['previous_gpa'].between(0.0, 4.0).all(), "Validasi Gagal: Terdapat nilai previous_gpa di luar batas 0.0 - 4.0!"
        assert df['exam_score'].between(0, 100).all(), "Validasi Gagal: Terdapat nilai Exam Score di luar batas 0 - 100!"
        assert df['attendance_percentage'].between(0.0, 100.0).all(), "Validasi Gagal: Terdapat nilai Kehadiran di luar batas 0% - 100%!"
        print("   -> [VALIDASI OK] Seluruh aturan validasi data terpenuhi!")
    except AssertionError as e:
        print(f"   -> [VALIDASI GAGAL] {str(e)}")
        raise e

    # ============================================================================
    # 3. STEP: LOAD (Memuat Data ke Data Mart MySQL)
    # ============================================================================
    print("\n[LOAD] Menghubungkan ke database MySQL...")
    engine = get_db_engine()
    
    with engine.begin() as conn:
        print("[LOAD] Mengosongkan data mart sebelum diisi (TRUNCATE)...")
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
        conn.execute(text("TRUNCATE TABLE fact_academic_performance;"))
        conn.execute(text("TRUNCATE TABLE dim_student;"))
        conn.execute(text("TRUNCATE TABLE dim_study_habit;"))
        conn.execute(text("TRUNCATE TABLE dim_lifestyle;"))
        conn.execute(text("TRUNCATE TABLE dim_psychology;"))
        conn.execute(text("TRUNCATE TABLE dim_engagement;"))
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))
        print("[LOAD] Seluruh tabel berhasil dikosongkan.")

        # --- A. Memasukkan Data Dimensi ---

        # 1. dim_student
        print("[LOAD] Memasukkan data ke dim_student...")
        dim_std = df[['student_id', 'age', 'gender', 'major']].drop_duplicates(subset=['student_id'])
        dim_std.to_sql('dim_student', con=conn, if_exists='append', index=False, chunksize=10000)

        # 2. dim_study_habit
        print("[LOAD] Memasukkan data ke dim_study_habit...")
        dim_habit = df[['study_hours_per_day', 'time_management_score', 'learning_style']]
        dim_habit.to_sql('dim_study_habit', con=conn, if_exists='append', index=False, chunksize=10000)

        # 3. dim_lifestyle
        print("[LOAD] Memasukkan data ke dim_lifestyle...")
        dim_life = df[['sleep_hours', 'screen_time', 'exercise_frequency', 'diet_quality', 'social_activity']]
        dim_life.to_sql('dim_lifestyle', con=conn, if_exists='append', index=False, chunksize=10000)

        # 4. dim_psychology
        print("[LOAD] Memasukkan data ke dim_psychology...")
        dim_psych = df[['stress_level', 'mental_health_rating', 'exam_anxiety_score', 'motivation_level']]
        dim_psych.to_sql('dim_psychology', con=conn, if_exists='append', index=False, chunksize=10000)

        # 5. dim_engagement
        print("[LOAD] Memasukkan data ke dim_engagement...")
        dim_engage = df[['attendance_percentage', 'extracurricular_participation', 'part_time_job']]
        dim_engage.to_sql('dim_engagement', con=conn, if_exists='append', index=False, chunksize=10000)

    # --- B. Mapping Surrogate Keys untuk Tabel Fakta ---
    # Menggunakan mapping index karena baris data 1-to-1 dengan panjang dataframe df
    print("[LOAD] Melakukan mapping surrogate keys untuk tabel fakta...")
    df['study_habit_key'] = np.arange(1, len(df) + 1)
    df['lifestyle_key'] = np.arange(1, len(df) + 1)
    df['psychology_key'] = np.arange(1, len(df) + 1)
    df['engagement_key'] = np.arange(1, len(df) + 1)

    # --- C. Memasukkan Data ke Tabel Fakta (fact_academic_performance) ---
    print("[LOAD] Memasukkan data ke fact_academic_performance...")
    
    fact_table = df[[
        'student_id', 'study_habit_key', 'lifestyle_key', 'psychology_key', 'engagement_key',
        'semester', 'previous_gpa', 'exam_score', 'dropout_risk'
    ]].rename(columns={'student_id': 'student_key'})
    
    fact_table.to_sql('fact_academic_performance', con=engine, if_exists='append', index=False, chunksize=10000)
    
    print("\n=== PROSES ETL SELESAI DENGAN SUKSES! ===")
    print(f"Jumlah data fakta baru yang dimuat: {len(fact_table)} baris.")

if __name__ == "__main__":
    try:
        run_etl()
    except Exception as e:
        print(f"\n[ERROR] ETL Gagal: {str(e)}")
        print("Harap pastikan database MySQL sudah berjalan dan skema 'data_mart.sql' telah dieksekusi.")
