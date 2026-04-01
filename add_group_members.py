#!/usr/bin/env python
"""
Script untuk menambah anggota kelompok Bismillah A ke database.
Anggota dapat login via Google OAuth dan akan di-link ke account Django mereka.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bismillah_a.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth.models import User
from group_bio.models import GroupMember

# Data anggota kelompok Bismillah A
ANGGOTA_KELOMPOK = [
    {
        'nim': '2406429885',
        'nama': 'Nimaisya Gina Herapati',
        'email': 'nimaisya@example.com',
        'role': 'ketua',
    },
    {
        'nim': '2406351806',
        'nama': 'Nadin Ananda',
        'email': 'nadin@example.com',
        'role': 'anggota',
    },
    {
        'nim': '2406437054',
        'nama': 'Felicia Evangeline',
        'email': 'felicia@example.com',
        'role': 'anggota',
    },
    {
        'nim': '2406350955',
        'nama': 'Flora Cahaya Putri',
        'email': 'flora@example.com',
        'role': 'anggota',
    },
]

def add_members():
    """Tambah anggota kelompok ke database"""
    print("📝 Adding group members...\n")
    
    for member_data in ANGGOTA_KELOMPOK:
        nim = member_data['nim']
        nama = member_data['nama']
        email = member_data['email']
        role = member_data['role']
        
        # Check apakah GroupMember sudah ada
        if GroupMember.objects.filter(nim=nim).exists():
            print(f"⚠️  {nama} ({nim}) - Already exists")
            continue
        
        # Buat GroupMember (tanpa link ke Django user terlebih dahulu)
        # User akan di-link setelah mereka login via Google OAuth
        try:
            # Cek apakah ada user dengan email yang sama
            user = User.objects.filter(email=email).first()
            
            if user:
                # Link ke existing user
                member, created = GroupMember.objects.get_or_create(
                    user=user,
                    defaults={
                        'nim': nim,
                        'full_name': nama,
                        'email': email,
                        'role': role,
                    }
                )
                if created:
                    print(f"✅ {nama} ({nim}) - Linked to existing user")
                else:
                    print(f"⚠️  {nama} ({nim}) - Already linked")
            else:
                # Belum ada user, akan di-create saat mereka login via Google
                print(f"⏳ {nama} ({nim}) - Waiting for OAuth login")
                print(f"   (User will be created when they login with Google)\n")
        
        except Exception as e:
            print(f"❌ {nama} ({nim}) - Error: {str(e)}")
    
    print("\n✅ Done!")
    print("\n📝 Next steps:")
    print("1. Anggota kelompok login via Google OAuth")
    print("2. Admin akan link user ke GroupMember di admin panel")
    print("3. Atau gunakan script: python add_members_oauth.py <email>")

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--remove':
        print("Removing all group members...")
        GroupMember.objects.all().delete()
        print("✅ All members removed")
    else:
        add_members()
