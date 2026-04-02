from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.db import transaction
from .models import GroupInfo, GroupTheme, GroupMember
from django.conf import settings
from pathlib import Path
import logging
from types import SimpleNamespace

logger = logging.getLogger(__name__)


DEFAULT_GROUP_MEMBERS = [
    {
        'nim': '2406429885',
        'full_name': 'Nimaisya Gina Herapati',
        'email': 'ginanimaisya7@gmail.com',
        'role': 'ketua',
        'bio': 'Ketua kelompok Bismillah Group A.',
    },
    {
        'nim': '2406351806',
        'full_name': 'Nadin Ananda',
        'email': 'nadinananda2006@gmail.com',
        'role': 'anggota',
        'bio': 'Anggota kelompok.',
    },
    {
        'nim': '2406437054',
        'full_name': 'Felicia Evangeline',
        'email': 'feliciaeva1503@gmail.com',
        'role': 'anggota',
        'bio': 'Anggota kelompok.',
    },
    {
        'nim': '2406350955',
        'full_name': 'Flora Cahaya Putri',
        'email': 'floracahayaputri@gmail.com',
        'role': 'anggota',
        'bio': 'Anggota kelompok.',
    },
]


def _build_public_members():
    existing_members = {
        member.email.strip().lower(): member
        for member in GroupMember.objects.all()
        if member.email
    }

    def _find_media_profile(item):
        folder = Path(settings.MEDIA_ROOT) / 'profile_images'
        if not folder.exists():
            return None

        email_key = item['email'].split('@')[0].lower() if item.get('email') else ''
        first_name = item.get('full_name', '').split()[0].lower() if item.get('full_name') else ''
        normalized_name = ''.join(item.get('full_name', '').lower().split())

        for ext in ['png', 'jpg', 'jpeg', 'gif', 'webp']:
            candidates = [
                folder / f"{item['nim']}.{ext}",
            ]
            if email_key:
                candidates.append(folder / f"{email_key}.{ext}")
            if first_name:
                candidates.append(folder / f"{first_name}.{ext}")
            if normalized_name:
                candidates.append(folder / f"{normalized_name}.{ext}")

            for path in candidates:
                if path.exists():
                    return path

        for path in folder.iterdir():
            if path.is_file():
                name_lower = path.stem.lower()
                if name_lower == first_name or name_lower == email_key or name_lower == normalized_name:
                    return path
        
        for path in folder.iterdir():
            if path.is_file():
                name_lower = path.stem.lower()
                if (
                    (email_key and email_key in name_lower)
                    or (first_name and first_name in name_lower)
                    or (normalized_name and normalized_name in name_lower)
                    or (item['nim'] in name_lower)
                ):
                    return path

        return None

    public_members = []
    for item in DEFAULT_GROUP_MEMBERS:
        email_key = item['email'].strip().lower()
        existing_member = existing_members.get(email_key) if email_key else None

        profile_image = None
        if existing_member and existing_member.profile_image:
            try:
                profile_image_url = existing_member.profile_image.url
                profile_image = SimpleNamespace(url=profile_image_url)
            except Exception:
                profile_image = None

        if not profile_image:
            found = _find_media_profile(item)
            if found:
                rel = found.relative_to(settings.MEDIA_ROOT).as_posix()
                profile_image = SimpleNamespace(url=f"{settings.MEDIA_URL}{rel}")

        public_members.append(
            SimpleNamespace(
                nim=item['nim'],
                full_name=item['full_name'],
                email=item['email'],
                role=item['role'],
                display_role='Ketua Kelompok' if item['role'] == 'ketua' else 'Anggota',
                bio=(existing_member.bio if existing_member and existing_member.bio else item['bio']),
                profile_image=profile_image or '',
                joined_at=(existing_member.joined_at if existing_member else None),
            )
        )

    return public_members


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
    
    theme = GroupTheme.get_or_create_theme()
    
    members = _build_public_members()
    
    context = {
        'group_info': group_info,
        'theme': theme,
        'members': members,
        'member_count': len(members),
        'can_edit_theme': False,
    }
    
    if request.user.is_authenticated:
        context['can_edit_theme'] = theme.can_be_modified_by(request.user)
    
    return render(request, 'group_bio/index.html', context)


@require_http_methods(["GET"])
def login_view(request):
    if request.user.is_authenticated:
        return redirect('group_bio:index')

    theme = GroupTheme.get_or_create_theme()
    return render(
        request,
        'registration/login.html',
        {
            'theme': theme,
            'can_edit_theme': False,
        }
    )


@require_http_methods(["GET"])
def signup_view(request):
    if request.user.is_authenticated:
        return redirect('group_bio:index')

    theme = GroupTheme.get_or_create_theme()
    return render(
        request,
        'registration/signup.html',
        {
            'theme': theme,
            'can_edit_theme': False,
        }
    )


@require_http_methods(["POST"])
@csrf_protect
def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, 'Kamu berhasil logout.')
    return redirect('group_bio:index')


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
                primary_color = request.POST.get('primary_color', theme.primary_color)
                secondary_color = request.POST.get('secondary_color', theme.secondary_color)
                accent_color = request.POST.get('accent_color', theme.accent_color)
                text_color = request.POST.get('text_color', theme.text_color)
                font_family = request.POST.get('font_family', theme.font_family)
                font_size_base = request.POST.get('font_size_base', theme.font_size_base)
                
                colors = {
                    'primary_color': primary_color,
                    'secondary_color': secondary_color,
                    'accent_color': accent_color,
                    'text_color': text_color,
                }
                
                for color_name, color_value in colors.items():
                    if not _is_valid_hex_color(color_value):
                        return JsonResponse({
                            'success': False,
                            'error': f'Invalid color format for {color_name}'
                        }, status=400)
                
                try:
                    font_size_base = int(font_size_base)
                    if font_size_base < 10 or font_size_base > 30:
                        return JsonResponse({
                            'success': False,
                            'error': 'Font size must be between 10 and 30 pixels'
                        }, status=400)
                except (ValueError, TypeError):
                    return JsonResponse({
                        'success': False,
                        'error': 'Invalid font size'
                    }, status=400)
                
                valid_fonts = [choice[0] for choice in GroupTheme._meta.get_field('font_family').choices]
                if font_family not in valid_fonts:
                    return JsonResponse({
                        'success': False,
                        'error': 'Invalid font family'
                    }, status=400)
                
                theme.primary_color = primary_color
                theme.secondary_color = secondary_color
                theme.accent_color = accent_color
                theme.text_color = text_color
                theme.font_family = font_family
                theme.font_size_base = font_size_base
                
                theme.save_with_audit(request.user)
                
                logger.info(
                    f"Theme updated by: {request.user.username}",
                    extra={
                        'user_id': request.user.id,
                        'action': 'theme_updated',
                        'aurora_colors': {
                            'warna_1': primary_color,
                            'warna_2': secondary_color,
                            'warna_3': accent_color,
                        },
                        'font_family': font_family,
                        'font_size': font_size_base,
                        'text_color': text_color,
                    }
                )
                
                messages.success(request, 'Tema berhasil diubah!')
                return redirect('group_bio:index')
        
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


@login_required(login_url='account_login')
def reset_theme_view(request):
    """
    RESET THEME TO DEFAULT - PROTECTED ROUTE
    Reset tema ke nilai default awal dengan warna aurora soft.
    """
    theme = GroupTheme.get_or_create_theme()
    
    if not theme.can_be_modified_by(request.user):
        return HttpResponseForbidden("Anda tidak memiliki izin untuk reset tema.")
    
    theme.primary_color = '#c2e7ff'    
    theme.secondary_color = '#f8dff0'  
    theme.accent_color = '#ffe9c9'     
    theme.background_color = '#f4f7ff'  
    theme.text_color = '#1c2a4d'
    theme.font_family = 'Poppins'
    theme.font_size_base = 16
    
    theme.save_with_audit(request.user)
    
    messages.success(request, 'Tema telah direset ke default.')
    return redirect('group_bio:index')


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
    members = _build_public_members()
    theme = GroupTheme.get_or_create_theme()
    
    context = {
        'members': members,
        'theme': theme,
        'member_count': len(members),
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
    
    if request.method == 'POST':
        if request.POST.get('action') == 'clear_history':
            theme.modification_history = []
            theme.save()
            messages.success(request, 'Riwayat perubahan tema telah dihapus.')
            return redirect('group_bio:theme_history')
    
    context = {
        'theme': theme,
        'modification_history': theme.modification_history,
    }
    
    return render(request, 'group_bio/theme_history.html', context)
