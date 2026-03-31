from django import forms
from django.core.exceptions import ValidationError
from .models import GroupTheme, GroupMember
import re


class ThemeEditForm(forms.ModelForm):
    """
    Form untuk edit tema dengan validasi input yang ketat.
    SECURITY: Input validation untuk mencegah injection attacks
    """
    
    class Meta:
        model = GroupTheme
        fields = [
            'primary_color',
            'secondary_color',
            'accent_color',
            'background_color',
            'text_color',
            'font_family',
            'font_size_base',
        ]
        widgets = {
            'primary_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control'}),
            'secondary_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control'}),
            'accent_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control'}),
            'background_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control'}),
            'text_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control'}),
            'font_family': forms.Select(attrs={'class': 'form-select'}),
            'font_size_base': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '8',
                'max': '32',
                'type': 'number',
            }),
        }

    def clean_primary_color(self):
        """Validasi format hex color"""
        color = self.cleaned_data.get('primary_color')
        if not self._is_valid_hex_color(color):
            raise ValidationError('Format warna tidak valid. Gunakan format hex (#RRGGBB)')
        return color

    def clean_secondary_color(self):
        """Validasi format hex color"""
        color = self.cleaned_data.get('secondary_color')
        if not self._is_valid_hex_color(color):
            raise ValidationError('Format warna tidak valid. Gunakan format hex (#RRGGBB)')
        return color

    def clean_accent_color(self):
        """Validasi format hex color"""
        color = self.cleaned_data.get('accent_color')
        if not self._is_valid_hex_color(color):
            raise ValidationError('Format warna tidak valid. Gunakan format hex (#RRGGBB)')
        return color

    def clean_background_color(self):
        """Validasi format hex color"""
        color = self.cleaned_data.get('background_color')
        if not self._is_valid_hex_color(color):
            raise ValidationError('Format warna tidak valid. Gunakan format hex (#RRGGBB)')
        return color

    def clean_text_color(self):
        """Validasi format hex color"""
        color = self.cleaned_data.get('text_color')
        if not self._is_valid_hex_color(color):
            raise ValidationError('Format warna tidak valid. Gunakan format hex (#RRGGBB)')
        return color

    def clean_font_size_base(self):
        """Validasi ukuran font"""
        size = self.cleaned_data.get('font_size_base')
        if size < 8 or size > 32:
            raise ValidationError('Ukuran font harus antara 8 dan 32 pixel')
        return size

    @staticmethod
    def _is_valid_hex_color(color_code):
        """
        Validasi format warna hex.
        SECURITY: Input validation untuk mencegah injection
        """
        if isinstance(color_code, str):
            return bool(re.match(r'^#[0-9A-F]{6}$', color_code.upper()))
        return False


class GroupMemberForm(forms.ModelForm):
    """
    Form untuk membuat atau mengedit anggota kelompok
    SECURITY: Hanya admin yang bisa menggunakan form ini
    """
    
    class Meta:
        model = GroupMember
        fields = ['nim', 'full_name', 'email', 'phone', 'role', 'bio']
        widgets = {
            'nim': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'NIM'}),
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nama Lengkap'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nomor HP'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Biodata'}),
        }

    def clean_nim(self):
        """Validasi NIM format"""
        nim = self.cleaned_data.get('nim')
        if nim:
            # Validasi NIM hanya berisi angka dan huruf, max 20 karakter
            if not re.match(r'^[A-Z0-9]{6,20}$', nim):
                raise ValidationError('NIM harus berisi 6-20 karakter alfanumerik')
        return nim

    def clean_email(self):
        """Validasi email"""
        email = self.cleaned_data.get('email')
        if email:
            # Check apakah email sudah terdaftar untuk user lain
            existing = GroupMember.objects.filter(email=email)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise ValidationError('Email ini sudah terdaftar untuk anggota lain')
        return email
