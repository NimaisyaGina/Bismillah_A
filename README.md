# 🔐 Bismillah Group A - Authentication & Authorization dengan OAuth 2.0

**Tugas:** Pengantar Keamanan Perangkat Lunak  
**Fokus:** Authentication & Authorization  
**Technology:** Django, OAuth 2.0 (Google), django-allauth

## 👥 Anggota Kelompok

- **Nimaisya Gina Herapati** (2406429885) - Ketua
- **Nadin Ananda** (2406351806)
- **Felicia Evangeline** (2406437054)
- **Flora Cahaya Putri** (2406350955)

## ✨ Fitur Utama

✅ **Website Biodata Kelompok** - Public, tanpa login  
✅ **OAuth 2.0 dengan Google** - Secure authentication  
✅ **Kustomisasi Tema** - Hanya untuk member yang login  
✅ **Audit Trail** - Riwayat lengkap perubahan  
✅ **CSRF Protection** - Security best practices  

## 🚀 Quick Start

### 1. Setup

```bash
# Clone & activate
git clone <repo>
cd Bismillah_A
python3 -m venv env
source env/bin/activate

# Install & setup
pip install -r requirements.txt
python manage.py migrate
python setup_initial_data.py
```

### 2. Run

```bash
python manage.py runserver
```

**Akses:**
- Homepage: http://localhost:8000/
- Admin: http://localhost:8000/admin/ (admin/admin123)

## 🔐 Security Features

1. **Authentication** - OAuth 2.0 dengan Google
2. **Authorization** - GroupMember only dapat edit theme
3. **CSRF Protection** - Token validation di semua forms
4. **Audit Logging** - Track siapa mengubah apa & kapan
5. **Input Validation** - Strict validation untuk semua input
6. **Secure Sessions** - HTTPOnly, Secure, SameSite cookies

## 📡 Endpoints

### Public (Tanpa Login)
- `/` - Homepage dengan biodata & anggota
- `/members/` - Daftar anggota lengkap

### Protected (Require GroupMember Login)
- `/accounts/login/` - Login dengan Google
- `/edit-theme/` - Edit warna & font (GroupMember only)
- `/theme-history/` - Riwayat perubahan (GroupMember only)
- `/admin/` - Admin panel (superuser only)

## 📁 Structure

```
Bismillah_A/
├── group_bio/               # Main app
│   ├── models.py           # GroupMember, GroupTheme, GroupInfo
│   ├── views.py            # Authorization + security
│   ├── forms.py            # Input validation
│   ├── admin.py            # Django admin
│   ├── urls.py             # URL routing
│   └── templates/          # HTML templates
├── bismillah_a/            # Project config
│   ├── settings.py         # OAuth + Security settings
│   └── urls.py
├── setup_initial_data.py   # Initialize default data
├── add_group_members.py    # Add more members
└── requirements.txt
```

## 🧪 Testing

### Public Access (No Login)
```bash
curl http://localhost:8000/
curl http://localhost:8000/members/
```

### Protected Route (Login Required)
```bash
curl http://localhost:8000/edit-theme/
# Expected: Redirect to login
```

### Authorization (GroupMember Only)
- Login sebagai non-member → 403 Forbidden
- Login sebagai GroupMember → 200 OK

## 📚 Key Concepts

### Authentication vs Authorization
- **Authentication:** Verifikasi siapa user (OAuth 2.0)
- **Authorization:** Verifikasi apa yang boleh user lakukan (GroupMember check)

### Security Layers
1. Login (@login_required)
2. Authorization (GroupMember validation)
3. CSRF Protection (@csrf_protect)
4. Input Validation (regex, boundary checks)
5. Audit Logging (modification history)

## ⚙️ Credentials

**Admin Account:**
- Username: `admin`
- Password: `admin123`

⚠️ Change di production!

---

**Status:** ✅ Selesai  
**Version:** 1.0.0