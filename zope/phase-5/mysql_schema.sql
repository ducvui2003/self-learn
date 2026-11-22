-- Japan-enterprise MySQL 8.0 schema for Phase 5
-- Charset: utf8mb4 (required for Japanese Kanji/Kana & emoji)
-- Run in MySQL if you want to connect Phase 5 to a real MySQL server:
--   set DATABASE_URL=mysql+pymysql://root:your_password@127.0.0.1:3306/zope_hr?charset=utf8mb4

CREATE DATABASE IF NOT EXISTS zope_hr
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE zope_hr;

CREATE TABLE IF NOT EXISTS employees (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    emp_code VARCHAR(20) NOT NULL UNIQUE,
    name_en VARCHAR(100) NOT NULL,
    name_ja VARCHAR(100) NOT NULL,
    department_en VARCHAR(50) NOT NULL,
    department_ja VARCHAR(50) NOT NULL,
    role VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL,
    version INT NOT NULL DEFAULT 1,
    deleted_flg TINYINT(1) NOT NULL DEFAULT 0,
    created_at VARCHAR(40) NOT NULL,
    created_by VARCHAR(50) NOT NULL,
    updated_at VARCHAR(40) NOT NULL,
    updated_by VARCHAR(50) NOT NULL,
    INDEX idx_employees_dept (department_en, deleted_flg)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS audit_logs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    action VARCHAR(50) NOT NULL,
    emp_code VARCHAR(20) NOT NULL,
    actor VARCHAR(50) NOT NULL,
    detail VARCHAR(255) NOT NULL,
    created_at VARCHAR(40) NOT NULL,
    INDEX idx_audit_emp (emp_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
