from django.contrib import admin
from django.utils.html import format_html
from .models import GroupMember, GroupTheme, GroupInfo


@admin.register(GroupInfo)
class GroupInfoAdmin(admin.ModelAdmin):
    """
    Admin interface untuk GroupInfo (biodata kelompok).
    SECURITY: Hanya admin Django yang dapat akses.
    """
    list_display = ['group_name', 'class_name', 'year', 'created_at']
    readonly_fields = ['created_at']
    fieldsets = (
        ('Informasi Dasar', {
            'fields': ('group_name', 'class_name', 'year', 'description')
        }),
        ('Audit', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(GroupMember)
class GroupMemberAdmin(admin.ModelAdmin):
    """
    Admin interface untuk GroupMember.
    SECURITY: Hanya admin Django yang dapat mengelola anggota.
    Track siapa yang melakukan perubahan.
    """
    list_display = ['full_name', 'nim', 'email', 'role_badge', 'user_link', 'joined_at']
    list_filter = ['role', 'joined_at']
    search_fields = ['full_name', 'nim', 'email', 'user__username']
    readonly_fields = ['user', 'joined_at', 'last_modified_at', 'modification_info']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Biodata', {
            'fields': ('nim', 'full_name', 'email', 'phone', 'role', 'bio', 'profile_image')
        }),
        ('Audit Trail', {
            'fields': ('joined_at', 'last_modified_at', 'last_modified_by', 'modification_info'),
            'classes': ('collapse',)
        }),
    )

    def role_badge(self, obj):
        """Display role dengan warna badge"""
        if obj.role == 'ketua':
            return format_html(
                '<span style="background-color: #dc3545; color: white; padding: 3px 8px; border-radius: 3px;">👑 {}</span>',
                obj.get_role_display()
            )
        return format_html(
            '<span style="background-color: #17a2b8; color: white; padding: 3px 8px; border-radius: 3px;">👤 {}</span>',
            obj.get_role_display()
        )
    role_badge.short_description = 'Role'

    def user_link(self, obj):
        """Link ke user Django"""
        if obj.user:
            return format_html(
                '<a href="/admin/auth/user/{}/change/">{}</a>',
                obj.user.id,
                obj.user.username
            )
        return '-'
    user_link.short_description = 'Django User'

    def modification_info(self, obj):
        """Info tentang modifikasi terakhir"""
        if obj.last_modified_by:
            return f"Modified by {obj.last_modified_by.username} at {obj.last_modified_at}"
        return "Never modified"
    modification_info.short_description = 'Last Modified'

    def save_model(self, request, obj, form, change):
        """Save dengan tracking siapa yang mengubah"""
        if change:
            obj.last_modified_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(GroupTheme)
class GroupThemeAdmin(admin.ModelAdmin):
    """
    Admin interface untuk GroupTheme.
    SECURITY: Hanya admin Django yang dapat langsung mengubah theme di sini.
    Perubahan via web interface sudah terproteksi dengan authorization checks.
    """
    list_display = ['theme_name', 'color_preview', 'font_family', 'last_modified_by', 'updated_at']
    readonly_fields = [
        'group_id', 'created_at', 'updated_at', 'last_modified_by',
        'color_preview_detailed', 'modification_history_display'
    ]
    
    fieldsets = (
        ('Identifikasi', {
            'fields': ('group_id',),
            'description': 'Identifikasi unik untuk grup (singleton pattern)'
        }),
        ('Warna', {
            'fields': (
                'primary_color', 'secondary_color', 'accent_color',
                'background_color', 'text_color', 'color_preview_detailed'
            ),
            'classes': ('wide',)
        }),
        ('Font', {
            'fields': ('font_family', 'font_size_base'),
        }),
        ('Audit Trail', {
            'fields': ('created_at', 'updated_at', 'last_modified_by', 'modification_history_display'),
            'classes': ('collapse',)
        }),
    )

    def theme_name(self, obj):
        return f"Group {obj.group_id} Theme"
    theme_name.short_description = 'Theme'

    def color_preview(self, obj):
        """Preview warna dalam list display"""
        return format_html(
            '<span style="display: inline-block; background: linear-gradient(90deg, {} 0%, {} 50%, {} 100%); '
            'width: 80px; height: 20px; border-radius: 3px; border: 1px solid #ccc;"></span>',
            obj.primary_color, obj.secondary_color, obj.accent_color
        )
    color_preview.short_description = 'Colors'

    def color_preview_detailed(self, obj):
        """Preview warna yang detail"""
        html = '<div style="display: flex; gap: 20px; flex-wrap: wrap;">'
        colors = [
            ('Primary', obj.primary_color),
            ('Secondary', obj.secondary_color),
            ('Accent', obj.accent_color),
            ('Background', obj.background_color),
            ('Text', obj.text_color),
        ]
        for name, color in colors:
            html += f'<div><strong>{name}:</strong><br>' \
                   f'<span style="display: inline-block; background-color: {color}; width: 40px; height: 40px; ' \
                   f'border: 1px solid #ccc; border-radius: 3px; margin-top: 5px;"></span><br>' \
                   f'<code>{color}</code></div>'
        html += '</div>'
        return format_html(html)
    color_preview_detailed.short_description = 'Color Preview'

    def modification_history_display(self, obj):
        """Display modification history"""
        if not obj.modification_history:
            return "No modifications recorded"
        
        html = '<div style="max-height: 300px; overflow-y: auto; font-size: 11px;">'
        for entry in obj.modification_history[-10:]:  # Show last 10
            html += f"<p><strong>{entry.get('modified_by', 'Unknown')}</strong> " \
                   f"at {entry.get('modified_at', 'Unknown')}</p>"
        html += '</div>'
        return format_html(html)
    modification_history_display.short_description = 'Modification History'

    def save_model(self, request, obj, form, change):
        """Save dengan tracking siapa yang mengubah"""
        if change:
            obj.save_with_audit(request.user)
        else:
            obj.last_modified_by = request.user
            super().save_model(request, obj, form, change)
