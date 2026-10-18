"""
=============================================================
TESTS — App Core, PWA, Sécurité & SEO
=============================================================
"""

import json
from datetime import timedelta
from django.contrib.auth.models import User
from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.articles.models import Article, Commentaire, Like
from apps.core.models import HomeFeedComment, HomeFeedLike, MoyenDon, ParametreSite
from apps.core.security import is_rate_limited, get_client_ip
from apps.core.validators import validate_file_size, validate_image_file, validate_audio_file, validate_video_file
from apps.predications.models import Predication


class PWATestCase(TestCase):
    """Tests du Service Worker, du Manifest PWA et de la page offline."""

    def setUp(self):
        self.client = Client()

    def test_service_worker_served(self):
        """Vérifie que /sw.js est servi avec le bon type MIME et headers."""
        response = self.client.get('/sw.js')
        self.assertEqual(response.status_code, 200)
        self.assertIn('application/javascript', response['Content-Type'])
        self.assertEqual(response['Service-Worker-Allowed'], '/')
        self.assertIn('no-cache', response['Cache-Control'])
        self.assertContains(response, 'smyrne-v13', html=False)

    def test_manifest_json_served(self):
        """Vérifie que /manifest.json est valide et contient les métadonnées PWA."""
        response = self.client.get('/manifest.json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('application/manifest+json', response['Content-Type'])
        content = b''.join(response.streaming_content) if hasattr(response, 'streaming_content') else response.content
        data = json.loads(content.decode('utf-8'))
        self.assertEqual(data.get('short_name'), 'Smyrne')
        self.assertEqual(data.get('start_url'), '/')
        self.assertTrue(len(data.get('icons', [])) > 0)

    def test_offline_page(self):
        """Vérifie que la page offline est rendue correctement."""
        response = self.client.get(reverse('core:offline'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Hors connexion")
        self.assertContains(response, "Réessayer")

    def test_navigation_shell_has_a_fixed_home_link_without_back_button(self):
        response = self.client.get(reverse('core:accueil'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'href="/" data-app-tab="home"')
        self.assertNotContains(response, 'id="appBackButton"')


class SEOTestCase(TestCase):
    """Tests des fichiers robots.txt et sitemap.xml."""

    def setUp(self):
        self.client = Client()

    def test_robots_txt(self):
        """Vérifie le contenu de robots.txt."""
        response = self.client.get('/robots.txt')
        self.assertEqual(response.status_code, 200)
        self.assertIn('text/plain', response['Content-Type'])
        self.assertContains(response, 'User-agent: *')
        self.assertContains(response, 'Disallow: /admin/')
        self.assertContains(response, 'Sitemap:')

    def test_sitemap_xml(self):
        """Vérifie que le sitemap.xml est généré sans erreur."""
        response = self.client.get('/sitemap.xml')
        self.assertEqual(response.status_code, 200)
        self.assertIn('application/xml', response['Content-Type'])
        self.assertContains(response, '<urlset')
        self.assertContains(response, '<loc>')


class SecurityTestCase(TestCase):
    """Tests des mécanismes de sécurité et rate limiting."""

    def setUp(self):
        self.factory = RequestFactory()
        cache.clear()

    def test_rate_limiting(self):
        """Vérifie que le rate limiting bloque après le quota défini."""
        request = self.factory.get('/priere/')
        request.META['REMOTE_ADDR'] = '192.168.1.100'

        # Limite à 3 requêtes
        for _ in range(3):
            self.assertFalse(is_rate_limited(request, key_prefix='test_rl', limit=3, period=60))

        # La 4e requête doit être bloquée
        self.assertTrue(is_rate_limited(request, key_prefix='test_rl', limit=3, period=60))

    def test_file_size_validation(self):
        """Vérifie le rejet des fichiers trop volumineux."""
        # Fichier simulé de 12 Mo (limite 10 Mo)
        large_content = b'x' * (12 * 1024 * 1024)
        large_file = SimpleUploadedFile("gros.pdf", large_content)

        with self.assertRaises(ValidationError):
            validate_file_size(large_file, max_mb=10)

    def test_audio_extension_validation(self):
        """Vérifie le rejet des fichiers audio avec une mauvaise extension."""
        fake_audio = SimpleUploadedFile("virus.exe", b'fake-data')
        with self.assertRaises(ValidationError):
            validate_audio_file(fake_audio)

    def test_video_extension_validation(self):
        """Vérifie le rejet des fichiers vidéo non conformes."""
        fake_video = SimpleUploadedFile("script.sh", b'fake-video-content')
        with self.assertRaises(ValidationError):
            validate_video_file(fake_video)


class ErrorPagesTestCase(TestCase):
    """Vérifie le comportement de la page 404."""

    def test_custom_404_page(self):
        response = self.client.get('/page-totalement-inconnue/')
        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "404", status_code=404)
        self.assertContains(response, "Page introuvable", status_code=404)


class DonsTestCase(TestCase):
    """Vérifie la page publique des dons et la validation des coordonnées."""

    def creer_moyen(self, **overrides):
        donnees = {
            'nom': 'M-Pesa (Vodacom)',
            'type_moyen': 'mobile_money',
            'numero_compte': '+243 970 000 001',
            'intitule_compte': 'PAROISSE SMYRNE',
            'devise': 'USD & CDF',
            'actif': True,
            'coordonnees_verifiees': False,
        }
        donnees.update(overrides)
        return MoyenDon.objects.create(**donnees)

    def test_moyens_non_verifies_sont_masques(self):
        self.creer_moyen()

        response = self.client.get(reverse('core:dons'))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, '+243 970 000 001')
        self.assertContains(response, 'Coordonnées en cours de vérification')
        self.assertNotContains(response, '+243 812 345 678')

    def test_moyen_verifie_affiche_le_logo_officiel_local(self):
        moyen = self.creer_moyen(coordonnees_verifiees=True)
        self.creer_moyen(
            nom='Airtel Money',
            numero_compte='+243 970 000 002',
        )

        response = self.client.get(reverse('core:dons'))

        self.assertContains(response, moyen.numero_compte)
        self.assertContains(response, '/static/images/paiements/vodacom.svg')
        self.assertNotContains(response, '+243 970 000 002')
        self.assertNotContains(response, 'mpesa.svg')

    def test_modifier_les_coordonnees_revoque_la_validation(self):
        moyen = self.creer_moyen(coordonnees_verifiees=True)

        moyen.numero_compte = '+243 970 000 099'
        moyen.save()
        moyen.refresh_from_db()

        self.assertFalse(moyen.coordonnees_verifiees)

    def test_modifier_les_coordonnees_avec_update_fields_revoque_la_validation(self):
        moyen = self.creer_moyen(coordonnees_verifiees=True)

        moyen.numero_compte = '+243 970 000 098'
        moyen.save(update_fields=['numero_compte'])
        moyen.refresh_from_db()

        self.assertFalse(moyen.coordonnees_verifiees)

    def test_formulaire_whatsapp_utilise_seulement_le_contact_configure(self):
        ParametreSite.objects.create(whatsapp='+243 976 555 888')

        response = self.client.get(reverse('core:dons'))

        self.assertContains(response, 'data-whatsapp-number="243976555888"')
        self.assertContains(response, 'reportReference')
        self.assertNotContains(response, 'wa.me/243812345678')

    def test_absence_de_whatsapp_n_utilise_pas_un_numero_de_demo(self):
        ParametreSite.objects.create(whatsapp='')

        response = self.client.get(reverse('core:dons'))

        self.assertContains(response, 'contact WhatsApp de l’église n’est pas encore configuré')
        self.assertNotContains(response, 'wa.me/243812345678')


class HomeFeedTestCase(TestCase):
    """Vérifie le fil paginé de l'accueil et son rendu progressif."""

    def setUp(self):
        self.client = Client()
        cache.clear()
        self.auteur = User.objects.create_user(username='auteur-fil', password='test-password')
        maintenant = timezone.now()
        for index in range(9):
            Article.objects.create(
                titre=f'Publication accueil {index}',
                slug=f'publication-accueil-{index}',
                resume=f'Résumé de la publication {index}',
                corps=f'<p>Contenu de la publication {index}</p>',
                auteur=self.auteur,
                video_url='https://youtu.be/dQw4w9WgXcQ' if index in (0, 8) else '',
                statut='publie',
                date_publication=maintenant - timedelta(minutes=index),
            )

    def test_accueil_affiche_le_fil_et_conserve_le_carrousel(self):
        response = self.client.get(reverse('core:accueil'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="heroSlides"')
        self.assertContains(response, 'id="fil-actualites"')
        self.assertContains(response, 'Publication accueil 0')
        self.assertContains(response, 'Publication accueil 7')
        self.assertNotContains(response, 'Publication accueil 8')
        self.assertContains(response, 'Cette actualité contient une vidéo')
        self.assertContains(response, 'Charger plus d’actualités')
        self.assertNotContains(response, 'Vie de l’église')

    def test_accueil_affiche_les_actions_sociales_et_le_formulaire_en_ligne(self):
        self.client.force_login(self.auteur)

        response = self.client.get(reverse('core:accueil'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-feed-like')
        self.assertContains(response, 'data-feed-comment-toggle')
        self.assertContains(response, 'data-feed-comment-form')
        self.assertContains(response, 'data-comment-count')

    def test_like_article_est_ajoute_et_retire_depuis_le_fil(self):
        self.client.force_login(self.auteur)
        article = Article.objects.get(slug='publication-accueil-0')
        url = reverse('core:feed_like', kwargs={'kind': 'article', 'object_id': article.pk})

        like_response = self.client.post(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(like_response.status_code, 200)
        self.assertEqual(like_response.json(), {'action': 'like', 'count': 1, 'liked': True})
        self.assertTrue(Like.objects.filter(article=article, utilisateur=self.auteur).exists())

        unlike_response = self.client.post(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(unlike_response.status_code, 200)
        self.assertEqual(unlike_response.json(), {'action': 'unlike', 'count': 0, 'liked': False})
        self.assertFalse(Like.objects.filter(article=article, utilisateur=self.auteur).exists())

    def test_commentaire_article_peut_etre_envoye_sans_quitter_l_accueil(self):
        self.client.force_login(self.auteur)
        article = Article.objects.get(slug='publication-accueil-0')
        url = reverse('core:feed_comment', kwargs={'kind': 'article', 'object_id': article.pk})

        response = self.client.post(url, {'texte': 'Un commentaire depuis le fil.'})

        self.assertEqual(response.status_code, 201)
        self.assertIn('modération', response.json()['message'])
        commentaire = Commentaire.objects.get(article=article, auteur=self.auteur)
        self.assertFalse(commentaire.approuve)

    def test_like_et_commentaire_generiques_pour_une_predication(self):
        self.client.force_login(self.auteur)
        predication = Predication.objects.create(
            titre='Message du dimanche',
            slug='message-du-dimanche',
            predicateur='Pasteur Smyrne',
            description='Un message de foi.',
            publie=True,
        )
        like_url = reverse('core:feed_like', kwargs={'kind': 'predication', 'object_id': predication.pk})
        comment_url = reverse('core:feed_comment', kwargs={'kind': 'predication', 'object_id': predication.pk})

        like_response = self.client.post(like_url)
        comment_response = self.client.post(comment_url, {'texte': 'Amen.'})

        self.assertEqual(like_response.status_code, 200)
        self.assertTrue(HomeFeedLike.objects.filter(utilisateur=self.auteur).exists())
        self.assertEqual(comment_response.status_code, 201)
        self.assertTrue(HomeFeedComment.objects.filter(auteur=self.auteur, approuve=False).exists())

    def test_actions_sociales_exigent_une_connexion(self):
        article = Article.objects.get(slug='publication-accueil-0')
        url = reverse('core:feed_like', kwargs={'kind': 'article', 'object_id': article.pk})

        response = self.client.post(url)

        self.assertEqual(response.status_code, 401)
        self.assertIn(reverse('accounts:connexion'), response.json()['login_url'])

    def test_cursor_charge_la_suite_en_fragment_ou_en_page_complete(self):
        accueil = self.client.get(reverse('core:accueil'))
        cursor = accueil.context['feed_page']['next_cursor']
        url = f"{reverse('core:accueil')}?feed_cursor={cursor}"

        fragment = self.client.get(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(fragment.status_code, 200)
        self.assertContains(fragment, 'Publication accueil 8')
        self.assertContains(fragment, 'Cette actualité contient une vidéo')
        self.assertNotContains(fragment, 'Publication accueil 0')
        self.assertNotContains(fragment, 'id="appMain"')

        fallback = self.client.get(url)
        self.assertEqual(fallback.status_code, 200)
        self.assertContains(fallback, 'Publication accueil 8')
        self.assertNotContains(fallback, 'Publication accueil 0')
