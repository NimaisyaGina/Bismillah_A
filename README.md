# Website Biodata Kelompok + Google Sign-In

Project ini adalah aplikasi Django untuk tugas **Authentication & Authorization**:

- Biodata kelompok bisa dilihat publik tanpa login.
- Login memakai **Google Sign-In** melalui `django-allauth`.
- Hanya email anggota yang ada di `GROUP_MEMBER_EMAILS` yang bisa masuk.
- Hanya anggota yang lolos whitelist yang bisa mengubah tema.

## Cara Kerja

- User belum login: tetap bisa melihat biodata kelompok.
- User login dengan email Google yang tidak ada di whitelist: akses ditolak.
- User login dengan email Google yang ada di whitelist: bisa mengubah tema dan melihat riwayat perubahan.

Tidak ada registrasi akun lokal manual. User langsung memakai akun Google masing-masing.

## Setup Google Cloud

1. Buka [Google Cloud Console](https://console.cloud.google.com/).
2. Buat atau pilih project.
3. Konfigurasi **OAuth consent screen**.
4. Buat **OAuth Client ID** dengan tipe `Web application`.
5. Tambahkan `Authorized redirect URIs` berikut:
   - `http://127.0.0.1:8000/accounts/google/login/callback/`
   - `http://localhost:8000/accounts/google/login/callback/`
6. Simpan `Client ID` dan `Client Secret`.

## Environment

Salin `.env.example` menjadi `.env`, lalu isi:

```env
GOOGLE_CLIENT_ID=isi_dari_google_cloud
GOOGLE_CLIENT_SECRET=isi_dari_google_cloud
GROUP_MEMBER_EMAILS=email1@gmail.com,email2@gmail.com,email3@gmail.com
```

Catatan:
- `GROUP_MEMBER_EMAILS` adalah whitelist email anggota kelompok.
- Jika ada anggota yang belum bisa login, cek dulu apakah emailnya sudah masuk ke whitelist ini.

## Menjalankan Project

1. Aktifkan virtual environment.
2. Install dependency:

```bash
pip install -r requirements.txt
```

3. Jalankan migrasi:

```bash
python manage.py migrate
```

4. Jalankan server:

```bash
python manage.py runserver
```

5. Buka:

```text
http://127.0.0.1:8000/
```

## Fitur Keamanan

- **Authentication**: Google OAuth via `django-allauth`.
- **Authorization**: hanya email dalam whitelist yang bisa login dan mengubah tema.
- **CSRF Protection**: aktif pada form dan logout.
- **Session Handling**: memakai session bawaan Django.
- **Audit Trail**: perubahan tema disimpan ke `modification_history`.
- **Input Validation**: warna, ukuran font, dan pilihan font divalidasi di server.

## Testing

Jalankan:

```bash
python manage.py check
python manage.py test group_bio
```

## Catatan Penting

- Jangan commit `.env`.
- Jika `Client Secret` pernah tersebar, segera regenerate di Google Cloud Console.
- Gunakan host yang konsisten saat login. Untuk lokal, paling aman pakai `http://127.0.0.1:8000/`.
