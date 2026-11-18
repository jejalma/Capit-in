# PRD — Capit-in · SIA Tambak Kepiting Bapak Salim

## Original problem statement
Lanjutkan project dari file backup ZIP: ekstrak, pulihkan struktur, instal dependensi, atur env, hubungkan frontend/backend/DB, jalankan & perbaiki error migrasi workspace. Gunakan source code asli. Pilihan user: pulihkan data DB dari backup; pakai Emergent universal key bila perlu (tidak dibutuhkan—tidak ada integrasi pihak ketiga).

## Architecture
- Python 3.11 + Streamlit 1.67.0 (migrated from NiceGUI 4.0.0), SQLite (`/app/sia/data/sia.db`), bcrypt, fpdf2
- Run via supervisor `frontend` -> `frontend/package.json` start = `cd /app/sia && python main.py` (port 3000)
- `/app/backend` FastAPI+Mongo template: unused
- Config `/app/sia/.env` (generated new secrets/passwords); see memory/test_credentials.md

## Personas
Admin (Bapak Salim), Akuntan, Kasir

## Implemented (restored from backup)
Login 3 roles, dashboard, transaksi + jurnal otomatis, jurnal umum/buku besar/neraca saldo (+PDF), laba rugi/neraca/arus kas (+PDF), master data (produk, pengepul, karyawan), bagan akun editable + indikator saldo, stok kepiting, logo kepiting.

## 2026-06 Restore session
- Restored ZIP into /app, created sia/.env, installed deps, restored data_backup/sia-data.sql (19 akun, 8 transaksi, 9 jurnal, 4 mutasi stok)
- Unit tests 5/5; full E2E test (iteration_1) 100% pass
- Fixes: login error hides on edit/demo click; "Rp" non-breaking space; wider saldo awal inputs

## Backlog
- P1: Mobile — drawer default open covers content; /akun horizontal overflow
- P2: Exclude HPP from "Akun Beban" dropdown on Beban Operasional; login websocket race (rare)
- P2: Backup/restore data from UI; PDF format refinements
- Note: JU-00009 "TEST_Jurnal penyesuaian" exists in restored data (from original backup)

## 2026-06 Streamlit migration + backup
- UI rewritten NiceGUI -> Streamlit (views/*, app.py, main.py launcher, .streamlit/config.toml); services/database unchanged
- Login persisted via HMAC-signed cookie (SIA_STORAGE_SECRET)
- All pages load without exceptions (screenshot check); FULL E2E OF STREAMLIT VERSION NOT YET RUN
- Backup: /app/backups/project-backup.zip, PROJECT_CONTEXT.md, data_backup/sia-data.sql + sia-data-tanpa-users.db
- Download endpoint: GET /api/download/{name} (backend/server.py)
