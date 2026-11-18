# PROJECT_CONTEXT — Capit-in · SIA Tambak Kepiting

## 1. Fungsi Aplikasi
Sistem Informasi Akuntansi (SIA) untuk **Tambak Kepiting Bapak Salim**
(Jl. Tambak Layur, Desa Morodemak, Kec. Bonang, Kab. Demak, Jawa Tengah).
Aplikasi ini mencatat transaksi budidaya dan penjualan kepiting, lalu membuat jurnal otomatis, buku besar,
neraca saldo dan laporan keuangan. Stok dan master data juga dikelola di sini.
Ada 3 peran: **Admin**, **Akuntan** dan **Kasir**. Hak akses tiap peran diatur di `sia/security.py`.

## 2. Teknologi (versi terbaru: STREAMLIT)
- **Python 3.11**. UI dibangun dengan **Streamlit 1.67.0**, menggantikan NiceGUI 4.0.0 sejak sesi terakhir.
- **SQLite**: file `sia/data/sia.db`, dibuat otomatis beserta data awal saat aplikasi start.
- Library lain: `pandas` dan `altair` (grafik dashboard, editor saldo awal), `bcrypt` (hash password),
  `fpdf2` (ekspor PDF), `python-dotenv` (konfigurasi), `pytest` (tes).
- Tema teal & krem ada di `sia/.streamlit/config.toml` dan CSS di `sia/views/theme.py`.
  Logo kepiting ada di `sia/static/logo.png`.
- Login disimpan di cookie `sia_session` yang ditandatangani HMAC dengan `SIA_STORAGE_SECRET`.
  Dengan begitu, refresh browser tidak membuat pengguna keluar.

## 3. Struktur Folder (isi ZIP)
```
sia/                       <- APLIKASI UTAMA
├── main.py                launcher: menjalankan `streamlit run app.py` di port SIA_PORT
├── app.py                 entry Streamlit: init DB, login gate, navigasi per peran (st.navigation)
├── .streamlit/config.toml tema + server (headless, CORS/XSRF off untuk proxy)
├── config.py              baca .env (DB path, port, secret, akun seed)
├── database.py            skema SQLite + seed (akun, produk, karyawan, pengepul, user)
├── security.py            hash password + matriks hak akses
├── .env.example           daftar variabel lingkungan (TANPA nilai rahasia)
├── requirements.txt       dependensi Python
├── services/              LOGIKA BISNIS (tidak tergantung UI): accounts, auth, journal, master,
│                          pdf, reports, stock, transactions
├── views/                 UI Streamlit
│   ├── theme.py, components.py (tabel HTML, badge, KPI, report_block+PDF, dialog konfirmasi)
│   ├── crud.py (halaman CRUD generik + dialog form), period.py (filter periode)
│   ├── session.py (login/cookie), layout.py (logo, info user, tombol keluar), fmt.py (format Rp/kg/tanggal)
│   └── pages/  login, dashboard, transactions, journal, reports, master_data, accounts, stock
├── static/logo.png
└── tests/                 pytest (test_services.py, 5 tes)
data_backup/
├── sia-data.sql             dump data bisnis (INSERT, TANPA tabel users)
└── sia-data-tanpa-users.db  salinan SQLite siap dibuka di DB Browser (tabel users dikosongkan)
scripts/export_data.py       membuat ulang data_backup/sia-data.sql dari database
frontend/package.json        script "start" menjalankan sia/main.py (khusus workspace Emergent, port 3000)
backend/                     template FastAPI workspace + endpoint unduh backup (/api/download/...)
memory/PRD.md                catatan produk / progres
```

## 4. Fitur yang Sudah Selesai
- Login dengan 3 peran dan tombol akun demo yang mengisi form otomatis. Menu `Pengguna` hanya untuk Admin.
- Dashboard: KPI bulan berjalan, grafik pendapatan vs beban 6 bulan, ringkasan entitas, transaksi terbaru,
  dan peringatan bila saldo awal tidak seimbang.
- Transaksi: penjualan, penerimaan piutang, pakan, gaji, beban operasional, modal dan prive.
  - Jurnal dibuat otomatis, dengan pratinjau jurnal langsung.
  - Penjualan mengurangi stok dan ditolak bila stok tidak cukup.
  - Daftar transaksi bisa difilter dan dicari. Hanya Admin yang bisa menghapus.
- Jurnal Umum, Buku Besar per akun, Neraca Saldo, serta Jurnal Manual/Penyesuaian (Admin & Akuntan). Semuanya bisa diekspor ke PDF.
- Laporan Laba Rugi, Neraca, Arus Kas (metode langsung) dan Stok, dengan filter periode dan ekspor PDF.
- Master data: Produk Kepiting, Pengepul (beserta sisa piutang) dan Karyawan, dengan fitur tambah, ubah dan hapus.
- Bagan Akun bisa diedit, termasuk mode "Isi Saldo Awal" dan indikator Debit/Kredit/Selisih yang berubah langsung.
- Stok kepiting: panen, susut dan koreksi, beserta riwayatnya.
- Unit test service: 5/5 lulus.

## 5. Progres Terakhir
- UI **dimigrasikan dari NiceGUI ke Streamlit**. Layer `services/`, `database.py`, `config.py` dan
  `security.py` **tidak diubah**, jadi logika bisnis dan data tetap sama.
- Semua halaman sudah dimuat tanpa error saat dicek dengan screenshot (dashboard, transaksi, jurnal, laporan, akun, stok, produk).
- **Uji end-to-end versi Streamlit BELUM dijalankan.** Uji menyeluruh sebelumnya (100% lulus) dilakukan pada versi NiceGUI.

## 6. Pekerjaan yang Masih Perlu Dilanjutkan
1. Jalankan uji end-to-end penuh versi Streamlit: login 3 peran, simpan transaksi, jurnal manual,
   simpan saldo awal, tambah/ubah/hapus master data, stok, dan unduhan PDF.
2. Uji persistensi login setelah browser di-refresh, dan pastikan tombol Keluar menghapus cookie.
3. Perbedaan perilaku dibanding versi NiceGUI:
   - Tombol hapus/ubah per baris diganti menjadi "pilih data + tombol Ubah/Hapus".
   - Semua dialog memakai `st.dialog`.
4. Opsional:
   - Tampilan mobile.
   - Mengeluarkan akun HPP dari pilihan "Akun Beban" di Beban Operasional.
   - Backup/restore data dari UI.

## 7. Cara Melanjutkan di Workspace Baru
1. Ekstrak `project-backup.zip` ke `/app` dengan struktur folder tetap.
2. Buat `sia/.env` dari `sia/.env.example` dan isi nilai baru:
   - Password harus kuat.
   - Untuk `SIA_STORAGE_SECRET`, buat secret acak dengan:
     `python -c "import secrets;print(secrets.token_hex(32))"`.
   - `SIA_PORT=3000` di Emergent.
3. Instal dependensi: `pip install -r sia/requirements.txt`
4. Jalankan aplikasi: `cd sia && python main.py`. Perintah ini memanggil `streamlit run app.py` di port `SIA_PORT`.
   - Di Emergent, `frontend/package.json` sudah berisi `"start": "cd /app/sia && /root/.venv/bin/python main.py"`.
     Cukup jalankan `sudo supervisorctl restart frontend`.
   - Health check: `curl localhost:3000/_stcore/health` harus mengembalikan `ok`.
5. Database dan akun dibuat otomatis. Untuk memulihkan data bisnis, lihat bagian 8.
6. Tes: `cd sia && python -m pytest tests -q`
7. Perbarui `memory/test_credentials.md` sesuai nilai `.env` yang baru.

## 8. Database SQLite & DB Browser for SQLite
- Lokasi database diatur oleh `SIA_DB_PATH` (default `data/sia.db`, relatif terhadap folder `sia/`).
- Database **tidak** ikut di ZIP karena berisi hash password. Sebagai gantinya tersedia dua file:
  - `data_backup/sia-data-tanpa-users.db`: salinan lengkap semua tabel bisnis, dengan tabel users dikosongkan.
  - `data_backup/sia-data.sql`: dump INSERT yang sama.

**Membuka di DB Browser for SQLite:**
1. Instal dari https://sqlitebrowser.org/dl/
2. Pilih *Open Database*, lalu buka `data_backup/sia-data-tanpa-users.db` untuk melihat data saja.
   Untuk database aktif, buka `sia/data/sia.db`.
3. Hentikan aplikasi dulu sebelum mengedit lewat DB Browser. Setelah itu klik *Write Changes*.
4. Jangan mengubah tabel `users` secara manual, karena password disimpan sebagai hash bcrypt.
   Akun dibuat ulang dari `.env` saat aplikasi start.

**Memulihkan data ke database baru:** jalankan aplikasi sekali supaya skema dan akun terbentuk, lalu hentikan.
```bash
cd sia
python - <<'EOF'
import sqlite3, os
from dotenv import load_dotenv; load_dotenv('.env')
c = sqlite3.connect(os.environ['SIA_DB_PATH'])
for t in ['journal_lines','journal_entries','stock_movements','transactions','employees','collectors','products','accounts']:
    c.execute(f'DELETE FROM "{t}"')
c.execute("DELETE FROM sqlite_sequence WHERE name != 'users'")
c.executescript(open('../data_backup/sia-data.sql').read()); c.commit()
EOF
```
Catatan: `created_by` di data merujuk ke id user 1–3 (Admin, Akuntan, Kasir) sesuai urutan seed.
Untuk membuat dump baru: `python scripts/export_data.py`.

**MongoDB:** tidak dipakai oleh aplikasi. `backend/server.py` hanya template workspace, ditambah endpoint unduh backup.

## 9. Deployment Railway
Belum ada konfigurasi Railway (railway.json/Procfile) dan proyek ini belum pernah di-deploy ke Railway. Langkahnya:
1. Push isi ZIP ke repo GitHub, lalu buat project Railway dari repo tersebut.
2. Isi **Root Directory** dengan `sia` dan **Start Command** dengan `python main.py`.
   Railway/Nixpacks akan membaca `requirements.txt`.
3. Isi **Variables** dengan semua kunci di `.env.example` dan nilai baru:
   - `SIA_PORT` = `${{PORT}}`
   - `SIA_DB_PATH` = `/data/sia.db`
4. Tambahkan **Volume** Railway yang di-mount ke `/data` supaya SQLite tidak hilang saat redeploy.
5. Pulihkan data dengan `data_backup/sia-data.sql` (bagian 8), atau upload `sia-data-tanpa-users.db` ke volume
   sebagai `/data/sia.db`. Akun dibuat otomatis saat start.
6. Streamlit memakai WebSocket (`/_stcore/stream`). Railway mendukungnya tanpa pengaturan tambahan.

## 10. Keamanan
ZIP ini **tidak** berisi file-file berikut:
- `.env`, password, API key dan secret
- `sia/data/sia.db` (berisi hash password)
- `node_modules`, `__pycache__` dan cache lainnya

Semua nilai rahasia harus dibuat baru di workspace berikutnya.
Deploy Emergent sebelumnya (https://zip-recovery-23.emergent.host) masih versi NiceGUI. Data produksinya
tidak diakses dan tidak diubah.
