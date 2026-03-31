from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.utils import timezone
from django.db import transaction

from .models import GroupInfo, GroupTheme, GroupMember
import logging

logger = logging.getLogger(__name__)


def index_view(request):
    """
    HOME PAGE - PUBLIC VIEW
    Menampilkan biodata kelompok yang bisa dilihat semua orang tanpa login.
    
    SECURITY: Tidak memerlukan autentikasi. Hanya menampilkan data publik.
    """
    try:
        group_info = GroupInfo.objects.get(group_id=1)
    except GroupInfo.DoesNotExist:
        group_info = None
    
    # Ambil tema yang ada
    theme = GroupTheme.get_or_create_theme()
    
    # Ambil anggota kelompok
    members = GroupMember.objects.all()
    
    context = {
        'group_info': group_info,
        'theme': theme,
        'members': members,
        'can_edit_theme': False,
    }
    
    # Jika user sudah login, check apakah dia bisa edit theme
    if request.user.is_authenticated:
        context['can_edit_theme'] = theme.can_be_modified_by(request.user)
    
    return render(request, 'group_bio/index.html', context)


@login_required(login_url='account_login')
@require_http_methods(["GET", "POST"])
@csrf_protect
def edit_theme_view(request):
    """
    THEME EDITOR - PROTECTED ROUTE
    Hanya anggota kelompok yang telah login via OAuth dapat mengubah tema.
    
    SECURITY FEATURES:
    1. @login_required - Memastikan user sudah login
    2. CSRF protection - Melindungi dari CSRF attacks
    3. Authorization check - Memastikan hanya GroupMember yang bisa edit
    4. Audit logging - Mencatat siapa yang mengubah apa dan kapan
    5. Transaction - Atomic operations untuk data consistency
    """
    
    theme = GroupTheme.get_or_create_theme()
    
    # AUTHORIZATION CHECK: Verifikasi user adalah GroupMember
    if not theme.can_be_modified_by(request.user):
        logger.warning(
            f"Unauthorized theme edit attempt by user: {request.user.username} ({request.user.id})",
            extra={'user_id': request.user.id, 'action': 'theme_edit_unauthorized'}
        )
        return HttpResponseForbidden(
            "Anda tidak memiliki izin untuk mengubah tema. "
            "Hanya anggota kelompok yang terdaftar yang dapat melakukan ini."
        )
    
    if request.method == 'GET':
        context = {
            'theme': theme,
            'font_choices': [choice[0] for choice in GroupTheme._meta.get_field('font_family').choices],
        }
        return render(request, 'group_bio/edit_theme.html', context)
    
    elif request.method == 'POST':
        try:
            with transaction.atomic():
                # Ambil data dari form dengan validasi
                primary_color = request.POST.get('primary_color', theme.primary_color)
                secondary_color = request.POST.get('secondary_color', theme.secondary_color)
                accent_color = request.POST.get('accent_color', theme.accent_color)
                background_color = request.POST.get('background_color', theme.background_color)
                text_color = request.POST.get('text_color', theme.text_color)
                font_family = request.POST.get('font_family', theme.font_family)
                font_size_base = request.POST.get('font_size_base', theme.font_size_base)
                
                # Validasi color format (basic hex validation)
                colors = {
                    'primary_color': primary_color,
                    'secondary_color': secondary_color,
                    'accent_color': accent_color,
                    'background_color': background_color,
                    'text_color': text_color,
                }
                
                for color_name, color_value in colors.items():
                    if not _is_valid_hex_color(color_value):
                        return JsonResponse({
                            'success': False,
                            'error': f'Invalid color format for {color_name}'
                        }, status=400)
                
                # Validasi font size
                try:
                    font_size_base = int(font_size_base)
                    if font_size_base < 8 or font_size_base > 32:
                        return JsonResponse({
                            'success': False,
                            'error': 'Font size must be between 8 and 32 pixels'
                        }, status=400)
                except (ValueError, TypeError):
                    return JsonResponse({
                        'success': False,
                        'error': 'Invalid font size'
                    }, status=400)
                
                # Validasi font family
                valid_fonts = [choice[0] for choice in GroupTheme._meta.get_field('font_family').choices]
                if font_family not in valid_fonts:
                    return JsonResponse({
                        'success': False,
                        'error': 'Invalid font family'
                    }, status=400)
                
                # Update theme
                theme.primary_color = primary_color
                theme.secondary_color = secondary_color
                theme.accent_color = accent_color
                theme.background_color = background_color
                theme.text_color = text_color
                theme.font_family = font_family
                theme.font_size_base = font_size_base
                
                # Save dengan audit trail
                theme.save_with_audit(request.user)
                
                # Log untuk audit
                logger.info(
                    f"Theme updated by: {request.user.username}",
                    extra={
                        'user_id': request.user.id,
                        'action': 'theme_updated',
                        'colors': {k: v for k, v in colors.items()},
                        'font_family': font_family,
                        'font_size': font_size_base,
                    }
                )
                
                messages.success(request, 'Tema berhasil diubah!')
                return redirect('index')
        
        except Exception as e:
            logger.error(
                f"Error updating theme: {str(e)}",
                extra={'user_id': request.user.id, 'action': 'theme_update_error'},
                exc_info=True
            )
            return JsonResponse({
                'success': False,
                'error': 'Terjadi kesalahan saat mengubah tema'
            }, status=500)


def _is_valid_hex_color(color_code):
    """
    Validasi format warna hex.
    SECURITY: Input validation untuk mencegah injection attacks
    """
    import re
    if isinstance(color_code, str):
        return bool(re.match(r'^#[0-9A-F]{6}$', color_code.upper()))
    return False


def group_members_view(request):
    """
    PUBLIC VIEW - Menampilkan daftar anggota kelompok
    SECURITY: Public data, tidak memerlukan login
    """
    members = GroupMember.objects.all().order_by('-role', 'full_name')
    theme = GroupTheme.get_or_create_theme()
    
    context = {
        'members': members,
        'theme': theme,
        'member_count': members.count(),
    }
    
    return render(request, 'group_bio/members.html', context)


@login_required(login_url='account_login')
def theme_preview_view(request):
    """
    AJAX endpoint untuk preview theme changes
    SECURITY: Hanya authenticated users
    """
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    theme = GroupTheme.get_or_create_theme()
    
    if not theme.can_be_modified_by(request.user):
        return HttpResponseForbidden()
    
    return JsonResponse({
        'theme': {
            'primary_color': theme.primary_color,
            'secondary_color': theme.secondary_color,
            'accent_color': theme.accent_color,
            'background_color': theme.background_color,
            'text_color': theme.text_color,
            'font_family': theme.font_family,
            'font_size_base': theme.font_size_base,
        }
    })


@login_required(login_url='account_login')
def theme_history_view(request):
    """
    AUDIT LOG VIEW - Menampilkan history perubahan tema
    SECURITY: Hanya authenticated users bisa melihat audit trail
    """
    theme = GroupTheme.get_or_create_theme()
    
    if not theme.can_be_modified_by(request.user):
        return HttpResponseForbidden("Tidak memiliki akses ke audit log")
    
    context = {
        'theme': theme,
        'modification_history': theme.modification_history,
    }
    
    return render(request, 'group_bio/theme_history.html', context)
