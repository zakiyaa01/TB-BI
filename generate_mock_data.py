# ============================================================================
# PROYEK TUGAS BESAR BUSINESS INTELLIGENCE
# SKRIP PEMBUAT MOCK DATA (generate_mock_data.py)
# Deskripsi: Menghasilkan dataset simulasi mahasiswa sebanyak 80.000 baris
#            dengan relasi variabel yang logis untuk visualisasi dashboard.
# ============================================================================

import pandas as pd
import numpy as np
import os

def generate_student_dataset(output_path, num_rows=80000):
    print(f"Memulai pembuatan {num_rows} data simulasi...")
    
    # 1. Mengatur seed agar hasil acak selalu konsisten
    np.random.seed(42)
    
    # 2. Inisialisasi Dictionary Data
    data = {}
    
    # Profil Mahasiswa
    data['student_id'] = np.arange(1, num_rows + 1)
    data['age'] = np.random.randint(18, 26, size=num_rows)
    data['gender'] = np.random.choice(['Male', 'Female'], size=num_rows, p=[0.48, 0.52])
    data['major'] = np.random.choice(
        ['Computer Science', 'Engineering', 'Business', 'Natural Sciences', 'Arts & Design'],
        size=num_rows,
        p=[0.25, 0.20, 0.25, 0.15, 0.15]
    )
    data['parental_education_level'] = np.random.choice(
        ['High School', "Associate's Degree", "Bachelor's Degree", "Master's Degree", 'PhD'],
        size=num_rows,
        p=[0.30, 0.20, 0.35, 0.10, 0.05]
    )
    data['family_income_range'] = np.random.choice(
        ['Low', 'Medium', 'High'],
        size=num_rows,
        p=[0.35, 0.50, 0.15]
    )
    data['internet_quality'] = np.random.choice(['Good', 'Bad'], size=num_rows, p=[0.80, 0.20])
    data['access_to_tutoring'] = np.random.choice(['Yes', 'No'], size=num_rows, p=[0.30, 0.70])
    data['parental_support_level'] = np.random.randint(1, 6, size=num_rows)  # Skala 1-5
    
    # Dimensi Waktu
    data['semester'] = np.random.randint(1, 9, size=num_rows)
    data['academic_year'] = np.random.choice(['2023/2024', '2024/2025'], size=num_rows, p=[0.50, 0.50])
    
    # Kebiasaan Belajar (Belum Ditransformasikan)
    study_hours = np.random.gamma(shape=3.0, scale=1.5, size=num_rows)  # Distribusi gamma jam belajar
    data['study_hours_per_day'] = np.clip(study_hours, 0.5, 16.0).round(2)
    
    time_mgmt = np.random.normal(loc=6.5, scale=1.8, size=num_rows)     # Skor manajemen waktu (1-10)
    data['time_management_score'] = np.clip(time_mgmt, 1.0, 10.0).round(2)
    
    data['learning_style'] = np.random.choice(
        ['Visual', 'Auditory', 'Kinesthetic'],
        size=num_rows,
        p=[0.45, 0.35, 0.20]
    )
    data['study_environment'] = np.random.choice(
        ['Home', 'Library', 'Cafe', 'Dormitory', 'Co-working Space'],
        size=num_rows,
        p=[0.40, 0.30, 0.15, 0.10, 0.05]
    )
    
    soc_media = np.random.exponential(scale=2.5, size=num_rows)        # Jam medsos
    data['social_media_hours'] = np.clip(soc_media, 0.0, 10.0).round(2)
    
    netflix = np.random.exponential(scale=1.8, size=num_rows)          # Jam streaming
    data['netflix_hours'] = np.clip(netflix, 0.0, 8.0).round(2)
    
    # Gaya Hidup
    sleep_h = np.random.normal(loc=6.8, scale=1.2, size=num_rows)       # Jam tidur
    data['sleep_hours'] = np.clip(sleep_h, 3.0, 12.0).round(2)
    
    data['diet_quality'] = np.random.choice(['Good', 'Average', 'Poor'], size=num_rows, p=[0.30, 0.50, 0.20])
    
    data['exercise_frequency'] = np.random.choice(
        [0, 1, 2, 3, 4, 5, 6, 7],
        size=num_rows,
        p=[0.20, 0.25, 0.20, 0.15, 0.10, 0.05, 0.03, 0.02]
    )
    data['social_activity'] = np.random.randint(1, 11, size=num_rows)  # Skor sosial 1-10
    
    scr_time = np.random.normal(loc=5.5, scale=2.0, size=num_rows)     # Jam screen time
    data['screen_time_hours'] = np.clip(scr_time, 1.0, 14.0).round(2)
    
    # Kondisi Psikologis
    data['stress_level'] = np.random.randint(1, 11, size=num_rows)
    data['mental_health_rating'] = np.random.randint(1, 11, size=num_rows)
    data['exam_anxiety_score'] = np.random.randint(1, 11, size=num_rows)
    data['motivation_level'] = np.random.randint(1, 11, size=num_rows)
    
    # Keterlibatan Akademik
    attend = np.random.beta(a=8, b=1.5, size=num_rows) * 100           # Persentase kehadiran condong ke atas
    data['attendance_percentage'] = np.clip(attend, 45.0, 100.0).round(2)
    
    data['extracurricular_participation'] = np.random.choice(['Yes', 'No'], size=num_rows, p=[0.40, 0.60])
    data['part_time_job'] = np.random.choice(['Yes', 'No'], size=num_rows, p=[0.15, 0.85])
    
    # 3. Membuat Hubungan Antar-Variabel (Korelasi Sintetis yang Logis)
    # Skor gabungan performa (semakin tinggi nilai positif, performa semakin bagus)
    perf_index = (
        0.35 * (data['study_hours_per_day'] / 16.0) +
        0.30 * (data['attendance_percentage'] / 100.0) +
        0.20 * (data['time_management_score'] / 10.0) +
        0.15 * (data['sleep_hours'] / 12.0) -
        0.15 * (data['stress_level'] / 10.0) -
        0.10 * (data['social_media_hours'] / 10.0) -
        0.10 * (data['screen_time_hours'] / 14.0) +
        0.05 * (data['parental_support_level'] / 5.0) +
        np.random.normal(loc=0.1, scale=0.08, size=num_rows) # Noise acak
    )
    
    # Skalakan performa indeks ke rentang 0 - 1
    perf_index_min = perf_index.min()
    perf_index_max = perf_index.max()
    normalized_perf = (perf_index - perf_index_min) / (perf_index_max - perf_index_min)
    
    # Menghitung GPA (IPK) saat ini: Skala 1.5 - 4.0
    gpa = 1.5 + (2.5 * normalized_perf)
    data['gpa'] = np.clip(gpa, 1.5, 4.0).round(2)
    
    # Menghitung Exam Score: Skala 40 - 100 (Sangat berkolerasi dengan GPA)
    exam_score = 40 + (60 * normalized_perf) + np.random.normal(loc=0, scale=4, size=num_rows)
    data['exam_score'] = np.clip(exam_score, 40, 100).astype(int)
    
    # Membuat IPK Sebelumnya (Previous GPA)
    # IPK sebelumnya mirip dengan IPK sekarang dengan variasi kecil
    prev_gpa = data['gpa'] + np.random.normal(loc=-0.05, scale=0.25, size=num_rows)
    data['previous_gpa'] = np.clip(prev_gpa, 1.5, 4.0).round(2)
    
    # Tren IPK (gpa_trend)
    gpa_diff = data['gpa'] - data['previous_gpa']
    gpa_trend = np.where(gpa_diff > 0.15, 'Upward', np.where(gpa_diff < -0.15, 'Downward', 'Stable'))
    data['gpa_trend'] = gpa_trend
    
    # Risiko Dropout (dropout_risk)
    # Risiko tinggi jika IPK rendah (< 2.2) ATAU kehadiran sangat rendah (< 70%)
    dropout_prob = 1 / (1 + np.exp(-(-8 * (data['gpa'] - 2.2) - 0.2 * (data['attendance_percentage'] - 75))))
    data['dropout_risk'] = np.where(np.random.rand(num_rows) < dropout_prob, 'Yes', 'No')
    
    # Konversi ke DataFrame dan Simpan
    df = pd.DataFrame(data)
    
    # Masukkan beberapa Missing Value secara sengaja (sekitar 1-2%) untuk menunjukkan kemampuan pembersihan ETL
    missing_mask_num = np.random.rand(num_rows) < 0.015
    missing_mask_cat = np.random.rand(num_rows) < 0.010
    
    df.loc[missing_mask_num, 'study_hours_per_day'] = np.nan
    df.loc[missing_mask_num, 'sleep_hours'] = np.nan
    df.loc[missing_mask_cat, 'major'] = np.nan
    df.loc[missing_mask_cat, 'diet_quality'] = np.nan
    
    # Simpan ke CSV
    df.to_csv(output_path, index=False)
    print(f"Dataset berhasil disimpan ke: {output_path}")
    print(f"Ukuran file: {os.path.getsize(output_path) / (1024*1024):.2f} MB")
    print(f"Jumlah baris: {len(df)}, Jumlah kolom: {len(df.columns)}")

if __name__ == "__main__":
    out_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(out_dir, "enhanced_student_habits_performance_dataset.csv")
    generate_student_dataset(file_path)
