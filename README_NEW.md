# 🔐 Bismillah Group A - Authentication & Authorization dengan OAuth 2.0

Website edukatif untuk tugas **Pengantar Keamanan Perangkat Lunak** yang mengimplementasikan Authentication & Authorization menggunakan OAuth 2.0 dengan Google sebagai Identity Provider.

## ✨ Fitur Utama

✅ **Website Biodata Kelompok** - Dapat dilihat tanpa login  
✅ **OAuth 2.0 dengan Google** - Secure authentication  
✅ **Kustomisasi Tema** - Hanya untuk member yang login  
✅ **Audit Trail** - Riwayat lengkap perubahan  
✅ **CSRF Protection** - Security best practices  
✅ **Authorization Checks** - Ketat enforcement

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Clone repository
git clone <repo-url>
cd Bismillah_A

# Create virtual environment
python3 -m venv env
source env/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Database & Initial Data

```bash
# Run migrations
python manage.py migrate

# Create initial data
python setup_initial_data.py
```

### 3. Setup Google OAuth (Optional)

```bash
# Copy environment template
cp .env.example .env

# Edit .env dengan Google OAuth credentials
# (Lihat SECURITY_DOCUMENTATION.md untuk detail)
```

### 4. Run Server

```bash
python manage.py runserver
```

Visit: **http://localhost:8000/**

## 📖 Dokumentasi

Untuk dokumentasi lengkap tentang implementasi security, flow authentication, dan authorization, lihat:

📋 **[SECURITY_DOCUMENTATION.md](./SECURITY_DOCUMENTATION.md)**

Dokumentasi mencakup:
- Arsitektur keamanan
- Setup & konfigurasi
- Security features
- Testing guidelines
- Production deployment

## 🔐 Security Architecture

```
┌─────────────────────────────────────────────┐
│         Authentication Layer                 │
│    OAuth 2.0 dengan Google Identity         │
└──────────────┬──────────────────────────────┘
               │
┌──────────────▼──────────────────────────────┐
│         Session Management Layer            │
│    HTTPOnly, Secure, SameSite Cookies       │
└──────────────┬──────────────────────────────┘
               │
┌──────────────▼──────────────────────────────┐
│        Authorization Layer                  │
│    GroupMember Role Checking & Validation   │
└──────────────┬──────────────────────────────┘
               │
┌──────────────▼──────────────────────────────┐
│        Protection Layer                     │
│    CSRF Tokens, Input Validation            │
└──────────────┬──────────────────────────────┘
               │
┌──────────────▼──────────────────────────────┐
│        Audit Layer                          │
│    Modification History & Logging           │
└─────────────────────────────────────────────┘
```

## 📁 Project Structure

```
Bismillah_A/
├── group_bio/                   # Main app
│   ├── models.py               # GroupMember, GroupTheme, GroupInfo
│   ├── views.py                # Views dengan authorization
│   ├── forms.py                # Input validation
│   ├── admin.py                # Admin interface
│   ├── urls.py                 # URL routing
│   ├── migrations/             # Database migrations
│   └── templates/              # HTML templates
├── bismillah_a/                # Project settings
│   ├── settings.py             # Django config + OAuth
│   ├── urls.py                 # Project URLs
│   └── wsgi.py
├── setup_initial_data.py       # Initialize data
├── requirements.txt            # Dependencies
├── SECURITY_DOCUMENTATION.md   # Detailed security docs
└── README.md                   # This file
```

## 🔑 Credentials

Untuk development, gunakan:
- **Admin Username:** admin
- **Admin Password:** admin123

⚠️ **Ubah password di production!**

## 🌐 Public Endpoints

| URL | Description |
|-----|-------------|
| `/` | Homepage - Biodata kelompok & anggota |
| `/members/` | Daftar lengkap anggota kelompok |

## 🔒 Protected Endpoints

| URL | Requirement |
|-----|-------------|
| `/accounts/login/` | Login dengan Google |
| `/edit-theme/` | GroupMember only |
| `/theme-history/` | GroupMember only |
| `/admin/` | Superuser only |

## 🧪 Testing

### Manual Testing

1. **Test Public Access**
   ```bash
   curl http://localhost:8000/
   ```

2. **Test OAuth Login**
   - Visit http://localhost:8000/
   - Click "Login dengan Google"
   - Authorize dengan akun Google

3. **Test Authorization**
   - Try access `/edit-theme/` tanpa login → Redirect to login
   - Login tapi bukan GroupMember → 403 Forbidden
   - Login sebagai GroupMember → Allowed

4. **Test Audit Trail**
   - Ubah tema → Check `/theme-history/`
   - Verify: siapa, kapan, apa diubah

## 🎯 Learning Outcomes

Dari project ini, pelajar akan memahami:

✅ **Authentication Concepts**
- OAuth 2.0 flow
- Session management
- Token handling

✅ **Authorization Concepts**
- Role-based access control
- Permission checks
- Authorization vs Authentication

✅ **Security Best Practices**
- CSRF protection
- Secure cookies
- Input validation
- Audit logging

✅ **Practical Implementation**
- Django security decorators
- Authorization middleware
- Audit trail implementation

## 📚 References

- [Django Security Docs](https://docs.djangoproject.com/en/5.2/topics/security/)
- [OAuth 2.0 RFC 6749](https://tools.ietf.org/html/rfc6749)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [django-allauth Docs](https://django-allauth.readthedocs.io/)

## ⚠️ Disclaimer

Project ini adalah untuk tujuan pendidikan. Jangan gunakan production credentials di dalam kode.

---

**Mata Kuliah:** Pengantar Keamanan Perangkat Lunak  
**Fokus:** Authentication & Authorization  
**Version:** 1.0.0
