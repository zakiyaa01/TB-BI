-- ============================================================================
-- PROYEK TUGAS BESAR BUSINESS INTELLIGENCE
-- SKRIP INISIALISASI DATABASE DATA MART (NEW DATASET ALIGNED SCHEMA)
-- Deskripsi: Inisialisasi basis data untuk analisis performa mahasiswa.
-- ============================================================================

CREATE DATABASE IF NOT EXISTS student_performance_db;
USE student_performance_db;

-- Menghapus tabel fakta terlebih dahulu karena relasi Foreign Key
DROP TABLE IF EXISTS fact_academic_performance;

-- Menghapus tabel-tabel dimensi
DROP TABLE IF EXISTS dim_student;
DROP TABLE IF EXISTS dim_study_habit;
DROP TABLE IF EXISTS dim_lifestyle;
DROP TABLE IF EXISTS dim_psychology;
DROP TABLE IF EXISTS dim_engagement;

-- ============================================================================
-- PEMBUATAN TABEL DIMENSI
-- ============================================================================

-- Dimensi 1: Profil Mahasiswa (dim_student)
CREATE TABLE dim_student (
    student_id INT PRIMARY KEY,
    age INT NOT NULL,
    gender VARCHAR(10) NOT NULL,
    major VARCHAR(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Dimensi 2: Kebiasaan Belajar (dim_study_habit)
CREATE TABLE dim_study_habit (
    study_habit_key INT AUTO_INCREMENT PRIMARY KEY,
    study_hours_per_day DECIMAL(4,2) NOT NULL,
    time_management_score DECIMAL(4,2) NOT NULL,
    learning_style VARCHAR(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Dimensi 3: Gaya Hidup (dim_lifestyle)
CREATE TABLE dim_lifestyle (
    lifestyle_key INT AUTO_INCREMENT PRIMARY KEY,
    sleep_hours DECIMAL(4,2) NOT NULL,
    screen_time DECIMAL(4,2) NOT NULL,
    exercise_frequency INT NOT NULL,
    diet_quality VARCHAR(10) NOT NULL,
    social_activity INT NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Dimensi 4: Kondisi Psikologis (dim_psychology)
CREATE TABLE dim_psychology (
    psychology_key INT AUTO_INCREMENT PRIMARY KEY,
    stress_level DECIMAL(4,2) NOT NULL, -- Diubah ke DECIMAL karena dataset baru memiliki nilai desimal
    mental_health_rating DECIMAL(4,2) NOT NULL,
    exam_anxiety_score DECIMAL(4,2) NOT NULL,
    motivation_level INT NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Dimensi 5: Keterlibatan Akademik (dim_engagement)
CREATE TABLE dim_engagement (
    engagement_key INT AUTO_INCREMENT PRIMARY KEY,
    attendance_percentage DECIMAL(5,2) NOT NULL,
    extracurricular_participation VARCHAR(5) NOT NULL,
    part_time_job VARCHAR(5) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================================
-- PEMBUATAN TABEL FAKTA (fact_academic_performance)
-- ============================================================================
CREATE TABLE fact_academic_performance (
    fact_id INT AUTO_INCREMENT PRIMARY KEY,
    student_key INT NOT NULL,
    study_habit_key INT NOT NULL,
    lifestyle_key INT NOT NULL,
    psychology_key INT NOT NULL,
    engagement_key INT NOT NULL,
    
    -- Waktu semester disimpan langsung di tabel fakta
    semester INT NOT NULL,
    
    -- Metrik Fakta Utama
    previous_gpa DECIMAL(4,2) NOT NULL,
    exam_score INT NOT NULL,
    dropout_risk VARCHAR(5) NOT NULL,

    -- Constraint FK ke Dimensi
    CONSTRAINT fk_fact_student FOREIGN KEY (student_key) REFERENCES dim_student(student_id) ON DELETE CASCADE,
    CONSTRAINT fk_fact_study_habit FOREIGN KEY (study_habit_key) REFERENCES dim_study_habit(study_habit_key) ON DELETE CASCADE,
    CONSTRAINT fk_fact_lifestyle FOREIGN KEY (lifestyle_key) REFERENCES dim_lifestyle(lifestyle_key) ON DELETE CASCADE,
    CONSTRAINT fk_fact_psychology FOREIGN KEY (psychology_key) REFERENCES dim_psychology(psychology_key) ON DELETE CASCADE,
    CONSTRAINT fk_fact_engagement FOREIGN KEY (engagement_key) REFERENCES dim_engagement(engagement_key) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Indeks
CREATE INDEX idx_fact_student_key ON fact_academic_performance(student_key);
CREATE INDEX idx_fact_previous_gpa ON fact_academic_performance(previous_gpa);
CREATE INDEX idx_fact_exam_score ON fact_academic_performance(exam_score);
