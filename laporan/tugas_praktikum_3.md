# Tugas Praktikum 3 — Kontrak Data dan Catatan Telaah Perkakas Orkestrasi

## 1. Perluasan Aturan Kontrak Data (`src/data.py`)
Selain pengecekan tipe data 19 kolom, rentang nilai dasar, dan batas nilai hilang, kontrak data pada `src/data.py` diperluas dengan dua aturan spesifik domain kredit mikro:
1. **Validasi Nominal Finansial Positif (`penghasilan_bulanan`, `plafon_diajukan`, `angsuran_bulanan > 0`):** Mencegah masuknya catatan pengajuan dengan penghasilan atau nilai pinjaman nol maupun negatif akibat kesalahan entri sistem cabang.
2. **Validasi Domain Kategorikal Sah (`segmen` dan `status_restrukturisasi`):** Menjamin seluruh nilai kategori berada di dalam daftar kelas kredit mikro yang diakui sistem sehingga tidak memicu kegagalan *encoder* saat pelatihan model.

---

## 2. Telaah Komparatif: `Makefile` vs Apache Airflow

### Catatan Keterbatasan Lingkungan Eksekusi
Praktikum dilakukan pada sistem operasi **Windows** dengan keterbatasan sumber daya perangkat keras lokal. Karena Apache Airflow bergantung pada pustaka sistem POSIX Unix (`fcntl`, `pwd`, dan *process forking*) dan tidak berjalan secara asli (*native*) di Windows tanpa WSL2 atau Docker, evaluasi terhadap Apache Airflow 2.9 dilakukan melalui penelaahan dokumentasi resmi, sedangkan `Makefile` diuji langsung pada repositori `mlops-kredit-sumatera`.

### Perbandingan Empat Dimensi

| Dimensi | `Makefile` | Apache Airflow (2.9) |
| :--- | :--- | :--- |
| **1. Cara Menyatakan Kebergantungan** | Deklaratif berbasis target dan stempel waktu berkas (`latih: data`). Eksekusi dipicu secara manual oleh pengguna lewat perintah terminal (`make latih`). | Terprogram (*Python-as-code*) melalui objek `DAG` dan operator bitshift (`task_data >> task_latih`). Mendukung jadwal *cron*, sensor data eksternal, dan cabang kondisional. |
| **2. Cara Menangani Tugas Gagal** | Berhenti seketika (*fail-fast*) saat menerima kode keluar non-nol tanpa mekanisme *retry* otomatis, tanpa jeda ulang, dan tanpa notifikasi peringatan. | Mendukung kebijakan pemulihan per tugas: jumlah *retry* otomatis, *exponential backoff*, batas waktu (*execution_timeout*), *callback* peringatan (email/Slack), serta *rerun* parsial dari titik gagal. |
| **3. Visibilitas Saat Pipeline Berjalan** | Hanya menampilkan aliran teks baris demi baris (`stdout`/`stderr`) di terminal lokal; tidak ada antarmuka grafis dan riwayat eksekusi hilang setelah sesi terminal ditutup. | Menyediakan antarmuka web terpusat (`localhost:8080`) berisi *Graph View*, *Grid View* riwayat eksekusi, *Gantt Chart* durasi per tahap, kode warna status, dan penyimpanan log terstruktur per tugas. |
| **4. Manajemen State & Isolasi Lingkungan *(Dimensi Tambahan)*** | Tidak menyimpan *state* di basis data; seluruh tahap berjalan di mesin lokal dan lingkungan virtual yang sama. | Menyimpan metadata dan status eksekusi di basis data relasional (PostgreSQL/MySQL) sehingga tahan terhadap *restart*, serta mendukung isolasi kontainer per tugas (*DockerOperator* / *KubernetesPodOperator*). |

---

## 3. Analisis Skala Organisasi: Kapan `Makefile` Berhenti Memadai?
- **`Makefile` memadai ketika:** proyek dikerjakan oleh tim kecil (1–3 orang) pada satu mesin kerja (*single-node*), eksekusi bersifat *ad-hoc* saat pengembangan atau pengujian CI, durasi pipeline singkat (hitungan detik hingga menit), serta tidak memerlukan penjadwalan berkala.
- **`Makefile` berhenti memadai dan perlu diganti dengan Airflow ketika:**
  1. Pipeline harus berjalan terjadwal secara otomatis tanpa intervensi manusia (misalnya *retraining* mingguan atau *scoring* harian).
  2. Tahapan pipeline tersebar di infrastruktur berbeda (penarikan data dari *data warehouse*, pelatihan di klaster GPU terpisah, lalu publikasi ke registri model).
  3. Organisasi membutuhkan audit riwayat eksekusi, *alerting* kegagalan otomatis, dan pemulihan parsial lintas tim Data Engineer dan ML Engineer.
