from django.contrib import admin
from django.urls import path, include
from group_bio.views import signup_view, logout_view, login_view
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path(
        'accounts/login/',
        login_view,
        name='account_login',
    ),
    path(
        'accounts/logout/',
        logout_view,
        name='account_logout',
    ),
    path('accounts/signup/', signup_view, name='account_signup'),
    path('accounts/', include('allauth.urls')),
    path('', include('group_bio.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
