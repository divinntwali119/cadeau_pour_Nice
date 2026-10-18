from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Article
from .validators import get_video_embed_url, validate_video_url


class ArticleVideoValidationTests(TestCase):
    def test_youtube_and_vimeo_links_are_normalized_to_safe_embed_urls(self):
        self.assertEqual(
            get_video_embed_url('https://youtu.be/dQw4w9WgXcQ?t=42'),
            'https://www.youtube-nocookie.com/embed/dQw4w9WgXcQ',
        )
        self.assertEqual(
            get_video_embed_url('https://vimeo.com/12345678'),
            'https://player.vimeo.com/video/12345678',
        )

    def test_unapproved_video_hosts_are_not_embedded_or_valid(self):
        url = 'https://video.example.test/watch/12345678'

        self.assertEqual(get_video_embed_url(url), '')
        with self.assertRaises(ValidationError):
            validate_video_url(url)

    def test_video_upload_extensions_and_mime_types(self):
        field = Article._meta.get_field('video_fichier')
        for filename, mime_type in (
            ('culte.mp4', 'video/mp4'),
            ('culte.webm', 'video/webm'),
            ('culte.mov', 'video/quicktime'),
        ):
            with self.subTest(filename=filename):
                uploaded = SimpleUploadedFile(filename, b'video-content')
                article = Article(video_fichier=uploaded)
                field.run_validators(uploaded)

                self.assertTrue(article.has_video)
                self.assertEqual(article.video_mime_type, mime_type)

    def test_video_upload_rejects_unapproved_extensions(self):
        uploaded = SimpleUploadedFile('script.exe', b'not-a-video')

        with self.assertRaises(ValidationError):
            Article._meta.get_field('video_fichier').run_validators(uploaded)


class ArticleVideoRenderingTests(TestCase):
    def setUp(self):
        self.auteur = User.objects.create_user(username='auteur-video', password='test-password')

    def creer_article(self, slug, **overrides):
        donnees = {
            'titre': f'Actualité vidéo {slug}',
            'slug': slug,
            'resume': 'Présentation de la vidéo publiée.',
            'corps': '<p>Contenu de cette actualité.</p>',
            'auteur': self.auteur,
            'statut': 'publie',
            'date_publication': timezone.now(),
        }
        donnees.update(overrides)
        return Article.objects.create(**donnees)

    def test_video_url_is_shown_in_detail_and_actualites_list(self):
        article = self.creer_article(
            'temoignage-video',
            video_url='https://youtu.be/dQw4w9WgXcQ',
        )

        detail = self.client.get(reverse('articles:detail', kwargs={'slug': article.slug}))
        liste = self.client.get(reverse('articles:liste'))

        self.assertContains(
            detail,
            'src="https://www.youtube-nocookie.com/embed/dQw4w9WgXcQ"',
        )
        self.assertContains(liste, 'video-play-indicator')
        self.assertContains(liste, 'Cette actualité contient une vidéo')

    def test_uploaded_video_renders_a_native_player_with_its_mime_type(self):
        article = self.creer_article(
            'culte-en-video',
            video_fichier='articles/videos/culte.webm',
        )

        response = self.client.get(reverse('articles:detail', kwargs={'slug': article.slug}))

        self.assertContains(response, '<video controls preload="metadata" playsinline')
        self.assertContains(response, '/media/articles/videos/culte.webm')
        self.assertContains(response, 'type="video/webm"')
        self.assertNotContains(response, '<iframe')
