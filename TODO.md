

## Implemented Features

### 1. Authentication & Security
- [x] **Register User**: Validasi format email & kekuatan password (Regex).
- [x] **Login System**: Session management menggunakan Flask-Session.
- [x] **Password Hashing**: Keamanan password menggunakan BCrypt.
- [x] **Route Protection**: Middleware untuk mencegah akses paksa ke Dashboard/History tanpa login.

### 2. Core AI & Backend
- [x] **RAG Pipeline**: Pencarian resep relevan dari dataset CSV (Vector Search).
- [x] **LLM Integration**: Implementasi Model Qwen 1.5B dengan optimasi 4-bit Quantization (Hemat VRAM).
- [x] **Recipe Generation**: Prompt engineering untuk menghasilkan resep terstruktur (Bahan, Cara, Nutrisi).
- [x] **Rate Limiting**: Mencegah spam request ke API AI.

### 3. Frontend & UI/UX (Responsive)
- [x] **Landing Page**: Halaman depan dinamis (Tombol berubah sesuai status login).
- [x] **Dashboard**: Layout Vertikal (Stack) yang responsif di Mobile & Desktop.
- [x] **Interactive Input**: Kolom pencarian bahan dengan sistem "Pool & Selected Tags".
- [x] **History Page**: Grid layout responsif (1 kolom HP, 3 kolom Desktop).
- [x] **Modal Detail**: Pop-up untuk melihat detail resep tanpa pindah halaman.
- [x] **User Feedback**: Toast Notification & Loading Animation.

### 4. Data Management (Basic)
- [x] **Save History**: Menyimpan hasil generate ke database SQLite.
- [x] **Toggle Favorite**: Menandai resep sebagai favorit (Update status).
- [x] **Client-Side Filtering**: Filter tampilan (All vs Favorite) menggunakan JS.

---

## TODO List (Should Have Features)

### 1. Delete History (CRUD Completeness)
- [x] Buat endpoint API `DELETE /api/history/<id>`.
- [x] Tambahkan tombol "Hapus" (Tong Sampah) di kartu history.
- [x] Konfirmasi hapus (SweetAlert/Modal) sebelum eksekusi.

### 2. Advanced Filtering (Server-Side Logic)
- [ ] Filter berdasarkan rentang tanggal (Date Range Picker).
- [ ] Pencarian teks riwayat (`LIKE %query%`) yang dieksekusi di backend, bukan filter JS biasa.

### 3. Server-Side Pagination (Scalability & Performance)
- [ ] Ubah query database menggunakan `LIMIT` dan `OFFSET`.
- [ ] Kirim parameter `page` dan `per_page` dari frontend.
- [ ] Buat UI tombol navigasi halaman (Next, Prev, Page Numbers).

### 4. Edit Profil & Security (User Management)
- [ ] Halaman pengaturan profil user.
- [ ] Fitur ganti Username.
- [ ] Fitur ganti Password (dengan validasi password lama & hashing password baru).

## Optional Features (Nice to Have)

### 5. Ekspor Resep
- [ ] Integrasi library JS (`html2canvas` atau `jspdf`).
- [ ] Tombol "Simpan sebagai Gambar/PDF" di modal detail resep.
- [ ] Formatting hasil ekspor agar layak cetak.