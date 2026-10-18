from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class AccountNavigationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='membre-test', password='test-password')

    def test_logout_refreshes_the_anonymous_account_navigation(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse('accounts:deconnexion'), follow=True)
        connexion_url = reverse('accounts:connexion')
        inscription_url = reverse('accounts:inscription')

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        self.assertContains(response, f'href="{connexion_url}" data-app-tab="space"')
        self.assertNotContains(response, 'href="/profil/" data-app-tab="space"')
        self.assertContains(response, f'href="{inscription_url}"')

    def test_login_page_offers_account_registration(self):
        response = self.client.get(reverse('accounts:connexion'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse('accounts:inscription'))
        self.assertContains(response, 'Créer un compte membre')
