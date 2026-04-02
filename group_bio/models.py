from django.db import models
from django.conf import settings
from django.contrib.auth.models import User


class GroupMember(models.Model):
    """
    Model untuk anggota kelompok yang telah login via OAuth Google.
    Fokus: AUTHORIZATION - hanya member yang terdaftar yang bisa edit theme.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='group_member')
    nim = models.CharField(max_length=20)
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    role = models.CharField(
        max_length=50,
        choices=[
            ('ketua', 'Ketua Kelompok'),
            ('anggota', 'Anggota'),
        ],
        default='anggota'
    )
    bio = models.TextField(blank=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    
    last_modified_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='modified_group_members'
    )
    last_modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.full_name} ({self.user.username})"

    class Meta:
        verbose_name_plural = "Group Members"
        ordering = ['-role', 'full_name']


class GroupTheme(models.Model):
    """
    Model untuk menyimpan preferensi tampilan website (warna, font, dll).
    Fokus: AUTHORIZATION - hanya GroupMember yang bisa mengubah theme.
    
    Security Features:
    - Tracking siapa yang melakukan perubahan (audit log)
    - Timestamp perubahan untuk audit trail
    - Satu theme per grup (singleton pattern)
    """
    group_id = models.IntegerField(default=1, unique=True)
    
    primary_color = models.CharField(max_length=7, default="#f4bae4") 
    secondary_color = models.CharField(max_length=7, default="#aac6f2") 
    accent_color = models.CharField(max_length=7, default="#ffc69d") 
    
    font_family = models.CharField(
        max_length=50,
        choices=[
            ('Arial', 'Arial'),
            ('Verdana', 'Verdana'),
            ('Georgia', 'Georgia'),
            ('Times New Roman', 'Times New Roman'),
            ('Courier New', 'Courier New'),
            ('Trebuchet MS', 'Trebuchet MS'),
            ('Comic Sans MS', 'Comic Sans MS'),
            ('Poppins', 'Poppins'),
        ],
        default='Poppins'
    )
    font_size_base = models.IntegerField(default=16, help_text="Base font size in pixels")
    
    background_color = models.CharField(max_length=7, default='#f4f7ff')
    text_color = models.CharField(max_length=7, default='#1c2a4d')
    
    last_modified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='modified_group_themes'
    )
    modification_history = models.JSONField(
        default=list,
        help_text="Audit trail of all modifications"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Group Theme #{self.group_id}"

    class Meta:
        verbose_name_plural = "Group Themes"

    def save_with_audit(self, user, *args, **kwargs):
        """
        Save dengan audit trail.
        SECURITY IMPLEMENTATION: Track siapa dan kapan perubahan dilakukan.
        """
        if user:
            self.last_modified_by = user
            
            if not self.modification_history:
                self.modification_history = []
            
            self.modification_history.append({
                'modified_by': user.username,
                'modified_at': str(__import__('django.utils.timezone', fromlist=['now']).now()),
                'changes': {
                    'primary_color': self.primary_color,
                    'secondary_color': self.secondary_color,
                    'accent_color': self.accent_color,
                    'text_color': self.text_color,
                    'font_family': self.font_family,
                    'font_size_base': self.font_size_base,
                }
            })
        
        self.save(*args, **kwargs)

    @classmethod
    def get_or_create_theme(cls):
        """Get atau create default theme untuk grup."""
        theme, created = cls.objects.get_or_create(group_id=1)
        return theme

    def can_be_modified_by(self, user):
        """
        AUTHORIZATION CHECK: Hanya GroupMember yang bisa modify theme.
        Implementasi authorization yang ketat.
        """
        if not user or not user.is_authenticated:
            return False

        if user.email and user.email.strip().lower() in settings.ALLOWED_MEMBER_EMAILS:
            return True

        return GroupMember.objects.filter(user=user).exists()


class GroupInfo(models.Model):
    """
    Model untuk biodata kelompok yang ditampilkan secara publik.
    SECURITY: Hanya membaca, tidak ada yang bisa mengubah melalui web interface.
    """
    group_id = models.IntegerField(default=1, unique=True)
    group_name = models.CharField(max_length=255, default="Bismillah Group A")
    class_name = models.CharField(max_length=255, default="Pengantar Keamanan Perangkat Lunak")
    year = models.IntegerField(default=2024)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.group_name

    class Meta:
        verbose_name_plural = "Group Info"
