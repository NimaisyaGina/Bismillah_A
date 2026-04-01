from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect

from allauth.core.exceptions import ImmediateHttpResponse
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


class AllowedGoogleSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        email = (sociallogin.user.email or "").strip().lower()
        if not email or email not in settings.ALLOWED_MEMBER_EMAILS:
            messages.error(
                request,
                "Email Google ini tidak terdaftar sebagai anggota kelompok.",
            )
            raise ImmediateHttpResponse(redirect('account_login'))

