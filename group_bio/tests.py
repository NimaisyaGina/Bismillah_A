from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.test import RequestFactory
from django.test.utils import override_settings
from allauth.socialaccount.models import SocialLogin

from group_bio.adapters import AllowedGoogleSocialAccountAdapter
from group_bio.models import GroupTheme


@override_settings(ALLOWED_MEMBER_EMAILS={'nimaisya@example.com'})
class AuthRouteTests(TestCase):
    def test_home_page_renders_without_missing_account_routes(self):
        response = self.client.get(reverse('group_bio:index'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse('account_login'))
        self.assertContains(response, 'Nimaisya Gina Herapati')
        self.assertContains(response, 'Nadin Ananda')
        self.assertContains(response, 'Felicia Evangeline')
        self.assertContains(response, 'Flora Cahaya Putri')

    def test_login_page_shows_google_sign_in_link(self):
        response = self.client.get(reverse('account_login'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse('google_login'))

    def test_signup_page_shows_google_sign_in_link(self):
        response = self.client.get(reverse('account_signup'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse('google_login'))

    def test_members_page_shows_all_default_group_members(self):
        response = self.client.get(reverse('group_bio:members'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Nimaisya Gina Herapati')
        self.assertContains(response, 'Nadin Ananda')
        self.assertContains(response, 'Felicia Evangeline')
        self.assertContains(response, 'Flora Cahaya Putri')

    def test_theme_authorization_uses_whitelisted_email(self):
        allowed_user = User.objects.create_user(
            username='nimaisya',
            email='nimaisya@example.com',
            password='SandiKuat12345',
        )
        other_user = User.objects.create_user(
            username='lain',
            email='lain@example.com',
            password='SandiKuat12345',
        )
        theme = GroupTheme.get_or_create_theme()

        self.assertTrue(theme.can_be_modified_by(allowed_user))
        self.assertFalse(theme.can_be_modified_by(other_user))

    def test_logout_redirects_back_to_homepage(self):
        user = User.objects.create_user(
            username='nimaisya',
            email='nimaisya@example.com',
            password='SandiKuat12345',
        )
        self.client.force_login(user)

        response = self.client.post(reverse('account_logout'))

        self.assertRedirects(response, reverse('group_bio:index'))


@override_settings(ALLOWED_MEMBER_EMAILS={'nimaisya@example.com'})
class SocialAdapterTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.adapter = AllowedGoogleSocialAccountAdapter()

    def test_adapter_rejects_non_whitelisted_google_email(self):
        request = self.factory.get(reverse('account_login'))
        sociallogin = SocialLogin(user=User(email='lain@example.com'))

        with self.assertRaises(Exception):
            self.adapter.pre_social_login(request, sociallogin)

    def test_adapter_accepts_whitelisted_google_email(self):
        request = self.factory.get(reverse('account_login'))
        sociallogin = SocialLogin(user=User(email='nimaisya@example.com'))

        result = self.adapter.pre_social_login(request, sociallogin)

        self.assertIsNone(result)
