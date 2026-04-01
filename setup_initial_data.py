#!/usr/bin/env python
"""
Script untuk setup initial data untuk aplikasi.
Buat admin user, group info, theme default, dan anggota group sample.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bismillah_a.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth.models import User
from group_bio.models import GroupInfo, GroupTheme, GroupMember

def create_admin():
    """Buat admin user jika belum ada"""
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        print("✅ Admin user created (username: admin, password: admin123)")
    else:
        print("⚠️  Admin user already exists")

def create_group_info():
    """Buat GroupInfo"""
    group_info, created = GroupInfo.objects.get_or_create(
        group_id=1,
        defaults={
            'group_name': 'Bismillah Group A',
            'class_name': 'Pengantar Keamanan Perangkat Lunak',
            'year': 2024,
            'description': '''Tugas ini fokus pada implementasi Authentication & Authorization menggunakan OAuth 2.0 dengan Google sebagai Identity Provider.

**Fitur Utama:**
1. Website dengan biodata kelompok yang dapat dilihat tanpa login
2. OAuth 2.0 login menggunakan Google
3. Theme customization (warna, font) hanya untuk anggota kelompok yang login
4. Audit trail untuk semua perubahan
5. CSRF protection dan secure session handling

**Anggota Kelompok:**
Hanya anggota yang telah terdaftar sebagai GroupMember dapat mengubah tema. User lain hanya dapat melihat.
'''
        }
    )
    if created:
        print("✅ GroupInfo created")
    else:
        print("⚠️  GroupInfo already exists")

def create_theme():
    """Buat theme default"""
    theme, created = GroupTheme.objects.get_or_create(
        group_id=1,
        defaults={
            'primary_color': '#3498db',
            'secondary_color': '#2c3e50',
            'accent_color': '#e74c3c',
            'background_color': '#ffffff',
            'text_color': '#333333',
            'font_family': 'Arial',
            'font_size_base': 16,
        }
    )
    if created:
        print("✅ GroupTheme created with default values")
    else:
        print("⚠️  GroupTheme already exists")

def create_sample_members():
    """Buat anggota group Bismillah A"""
    admin_user = User.objects.get(username='admin')
    
    # Data anggota kelompok Bismillah A
    sample_members = [
        {
            'user': admin_user,
            'nim': '2406429885',
            'full_name': 'Nimaisya Gina Herapati',
            'email': 'nimaisya@example.com',
            'phone': '',
            'role': 'ketua',
            'bio': 'Ketua kelompok - Pengantar Keamanan Perangkat Lunak',
        },
    ]
    
    created_count = 0
    for member_data in sample_members:
        member, created = GroupMember.objects.get_or_create(
            user=member_data['user'],
            defaults={
                'nim': member_data['nim'],
                'full_name': member_data['full_name'],
                'email': member_data['email'],
                'phone': member_data['phone'],
                'role': member_data['role'],
                'bio': member_data['bio'],
            }
        )
        if created:
            created_count += 1
    
    if created_count > 0:
        print(f"✅ {created_count} GroupMember(s) created")
    else:
        print("⚠️  All members already exist")

if __name__ == '__main__':
    print("🔧 Setting up initial data...\n")
    create_admin()
    create_group_info()
    create_theme()
    create_sample_members()
    print("\n✅ Setup complete!")
    print("\n📝 Next steps:")
    print("1. Run: python manage.py runserver")
    print("2. Go to: http://localhost:8000/")
    print("3. Admin: http://localhost:8000/admin/ (username: admin, password: admin123)")
    print("4. Setup Google OAuth credentials in settings or add more group members via admin")
