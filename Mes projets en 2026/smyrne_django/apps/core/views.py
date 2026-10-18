"""
=============================================================
VUES — App Core (Page d'accueil, SEO, PWA, Erreurs)
=============================================================
"""

import os
import re
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core import signing
from django.db.models import F, Count
from django.db.models.functions import Coalesce
from django.http import HttpResponse, FileResponse, HttpResponseNotFound, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse
from django.db.models import Q
from django.utils.http import urlencode

from .models import SlideCarousel, MoyenDon, ParametreSite, HomeFeedLike, HomeFeedComment
from .security import is_rate_limited
from apps.cultes.models import Culte
from apps.articles.models import Article, Commentaire, Like
from apps.evenements.models import Evenement
from apps.galerie.models import PhotoGalerie
from apps.predications.models import Predication


HOME_FEED_PAGE_SIZE = 8
HOME_FEED_CURSOR_SALT = 'smyrne.home-feed'
HOME_FEED_MODELS = {
    'article': Article,
    'evenement': Evenement,
    'predication': Predication,
    'galerie': PhotoGalerie,
}


def _home_feed_offsets(cursor):
    """Charge des offsets signés afin que le fil reste borné sans table dédiée."""
    source_keys = ('articles', 'evenements', 'predications', 'galerie')
    offsets = {key: 0 for key in source_keys}
    if not cursor:
        return offsets

    try:
        payload = signing.loads(cursor, salt=HOME_FEED_CURSOR_SALT, max_age=60 * 60 * 24 * 30)
    except (signing.BadSignature, TypeError, ValueError):
        return offsets

    if not isinstance(payload, dict):
        return offsets
    for key in source_keys:
        value = payload.get(key, 0)
        if type(value) is int and value >= 0:
            offsets[key] = value
    return offsets


def _home_feed(request):
    """Mélange les dernières publications des modèles existants par date."""
    offsets = _home_feed_offsets(request.GET.get('feed_cursor'))
    sources = (
        (
            'articles', 'article', 0,
            Article.objects.filter(statut='publie')
            .select_related('categorie', 'auteur')
            .annotate(
                feed_sort_date=Coalesce('date_publication', 'date_creation'),
                like_count=Count('likes', distinct=True),
                comment_count=Count('commentaires', filter=Q(commentaires__approuve=True), distinct=True),
            )
            .order_by('-feed_sort_date', '-pk'),
        ),
        (
            'evenements', 'evenement', 1,
            Evenement.objects.filter(publie=True)
            .annotate(feed_sort_date=F('date_creation'))
            .order_by('-feed_sort_date', '-pk'),
        ),
        (
            'predications', 'predication', 2,
            Predication.objects.filter(publie=True)
            .annotate(feed_sort_date=F('date_creation'))
            .order_by('-feed_sort_date', '-pk'),
        ),
        (
            'galerie', 'galerie', 3,
            PhotoGalerie.objects.filter(publie=True)
            .select_related('categorie')
            .annotate(feed_sort_date=F('date_ajout'))
            .order_by('-feed_sort_date', '-pk'),
        ),
    )

    feed_items = []
    for source_key, kind, source_rank, queryset in sources:
        start = offsets[source_key]
        objects = queryset[start:start + HOME_FEED_PAGE_SIZE + 1]
        for obj in objects:
            if kind == 'article':
                category = obj.categorie.nom if obj.categorie_id else 'Actualité'
                title = obj.titre
                excerpt = obj.resume or obj.corps
                image = obj.image
                item_date = obj.date_publication or obj.date_creation
                url = reverse('articles:detail', kwargs={'slug': obj.slug})
                like_url = reverse('core:feed_like', kwargs={'kind': kind, 'object_id': obj.pk})
                comment_api_url = reverse('core:feed_comment', kwargs={'kind': kind, 'object_id': obj.pk})
                comment_url = f'{url}#commentaires'
                like_count = obj.like_count
                comment_count = obj.comment_count
            elif kind == 'evenement':
                category = 'Événement'
                title = obj.titre
                excerpt = obj.description
                image = obj.image
                item_date = obj.date_debut
                url = reverse('evenements:detail', kwargs={'slug': obj.slug})
                like_url = reverse('core:feed_like', kwargs={'kind': kind, 'object_id': obj.pk})
                comment_api_url = reverse('core:feed_comment', kwargs={'kind': kind, 'object_id': obj.pk})
                comment_url = url
                like_count = 0
                comment_count = 0
            elif kind == 'predication':
                category = 'Prédication'
                title = obj.titre
                excerpt = obj.description or obj.contenu
                image = obj.image
                item_date = obj.date_publication or obj.date_creation
                url = reverse('predications:detail', kwargs={'slug': obj.slug})
                like_url = reverse('core:feed_like', kwargs={'kind': kind, 'object_id': obj.pk})
                comment_api_url = reverse('core:feed_comment', kwargs={'kind': kind, 'object_id': obj.pk})
                comment_url = url
                like_count = 0
                comment_count = 0
            else:
                category = obj.categorie.nom if obj.categorie_id else 'Galerie'
                title = obj.titre or 'Moments de la communauté'
                excerpt = ''
                image = obj.image
                item_date = obj.date_ajout
                url = reverse('galerie:liste')
                like_url = reverse('core:feed_like', kwargs={'kind': kind, 'object_id': obj.pk})
                comment_api_url = reverse('core:feed_comment', kwargs={'kind': kind, 'object_id': obj.pk})
                comment_url = url
                like_count = 0
                comment_count = 0

            feed_items.append({
                'source': source_key,
                'source_rank': source_rank,
                'id': obj.pk,
                'sort_date': obj.feed_sort_date,
                'kind': kind,
                'category': category,
                'title': title,
                'excerpt': excerpt,
                'image': image,
                'has_video': obj.has_video if kind == 'article' else False,
                'date': item_date,
                'url': url,
                'comment_url': comment_url,
                'comment_api_url': comment_api_url,
                'can_like': True,
                'like_url': like_url,
                'like_count': like_count,
                'comment_count': comment_count,
                'liked_by_user': False,
            })

    feed_items.sort(
        key=lambda item: (item['sort_date'], item['source_rank'], item['id']),
        reverse=True,
    )
    page_items = feed_items[:HOME_FEED_PAGE_SIZE]
    has_next = len(feed_items) > HOME_FEED_PAGE_SIZE
    next_cursor = None

    if has_next:
        next_offsets = dict(offsets)
        for item in page_items:
            next_offsets[item['source']] += 1
        next_cursor = signing.dumps(next_offsets, salt=HOME_FEED_CURSOR_SALT, compress=True)

    non_article_items = [item for item in page_items if item['kind'] != 'article']
    generic_like_counts = {}
    generic_comment_counts = {}
    generic_liked_items = set()
    content_type_ids = {}
    if non_article_items:
        models = {item['kind']: HOME_FEED_MODELS[item['kind']] for item in non_article_items}
        content_types = ContentType.objects.get_for_models(*set(models.values()))
        content_type_ids = {
            kind: content_types[model].pk
            for kind, model in models.items()
        }
        target_content_type_ids = set(content_type_ids.values())
        target_object_ids = {item['id'] for item in non_article_items}
        generic_like_counts = {
            (row['content_type_id'], row['object_id']): row['total']
            for row in HomeFeedLike.objects.filter(
                content_type_id__in=target_content_type_ids,
                object_id__in=target_object_ids,
            ).values('content_type_id', 'object_id').annotate(total=Count('pk'))
        }
        generic_comment_counts = {
            (row['content_type_id'], row['object_id']): row['total']
            for row in HomeFeedComment.objects.filter(
                content_type_id__in=target_content_type_ids,
                object_id__in=target_object_ids,
                approuve=True,
            ).values('content_type_id', 'object_id').annotate(total=Count('pk'))
        }
        if request.user.is_authenticated:
            generic_liked_items = set(
                HomeFeedLike.objects.filter(
                    content_type_id__in=target_content_type_ids,
                    object_id__in=target_object_ids,
                    utilisateur=request.user,
                ).values_list('content_type_id', 'object_id')
            )

    for item in non_article_items:
        interaction_key = (content_type_ids[item['kind']], item['id'])
        item['like_count'] = generic_like_counts.get(interaction_key, 0)
        item['comment_count'] = generic_comment_counts.get(interaction_key, 0)
        item['liked_by_user'] = interaction_key in generic_liked_items

    if request.user.is_authenticated:
        article_ids = [item['id'] for item in page_items if item['kind'] == 'article']
        if article_ids:
            liked_ids = set(
                Like.objects.filter(utilisateur=request.user, article_id__in=article_ids)
                .values_list('article_id', flat=True)
            )
            for item in page_items:
                if item['kind'] == 'article' and item['id'] in liked_ids:
                    item['liked_by_user'] = True

    return {
        'posts': page_items,
        'next_cursor': next_cursor,
    }


def _get_public_feed_object(kind, object_id):
    """Retourne uniquement une publication publiée d'un type autorisé du fil."""
    model = HOME_FEED_MODELS.get(kind)
    if model is None:
        return None
    queryset = model.objects.all()
    if kind == 'article':
        queryset = queryset.filter(statut='publie')
    else:
        queryset = queryset.filter(publie=True)
    return get_object_or_404(queryset, pk=object_id)


def _interaction_error(request, message, status):
    login_url = reverse('accounts:connexion')
    next_url = f"{reverse('core:accueil')}#fil-actualites"
    return JsonResponse({
        'error': message,
        'login_url': f'{login_url}?{urlencode({"next": next_url})}',
    }, status=status)


def toggle_feed_like(request, kind, object_id):
    """Ajoute/retire un like depuis une carte du fil, sans navigation."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Méthode non autorisée'}, status=405)
    if not request.user.is_authenticated:
        return _interaction_error(request, 'Connectez-vous pour aimer cette publication.', 401)

    target = _get_public_feed_object(kind, object_id)
    if target is None:
        return JsonResponse({'error': 'Type de publication non autorisé.'}, status=404)

    if kind == 'article':
        like, created = Like.objects.get_or_create(article=target, utilisateur=request.user)
        if not created:
            like.delete()
            action = 'unlike'
        else:
            action = 'like'
        count = target.nombre_likes()
    else:
        content_type = ContentType.objects.get_for_model(target, for_concrete_model=False)
        like, created = HomeFeedLike.objects.get_or_create(
            content_type=content_type,
            object_id=target.pk,
            utilisateur=request.user,
        )
        if not created:
            like.delete()
            action = 'unlike'
        else:
            action = 'like'
        count = HomeFeedLike.objects.filter(content_type=content_type, object_id=target.pk).count()

    return JsonResponse({'action': action, 'count': count, 'liked': action == 'like'})


def create_feed_comment(request, kind, object_id):
    """Enregistre un commentaire depuis le fil, soumis à modération."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Méthode non autorisée.'}, status=405)
    if not request.user.is_authenticated:
        return _interaction_error(request, 'Connectez-vous pour commenter cette publication.', 401)

    target = _get_public_feed_object(kind, object_id)
    if target is None:
        return JsonResponse({'error': 'Type de publication non autorisé.'}, status=404)

    texte = request.POST.get('texte', '').strip()
    if not texte:
        return JsonResponse({'error': 'Saisissez un commentaire avant de l’envoyer.'}, status=400)
    if len(texte) > 2000:
        return JsonResponse({'error': 'Le commentaire ne peut pas dépasser 2 000 caractères.'}, status=400)
    if is_rate_limited(request, key_prefix='home_feed_comment', limit=5, period=120):
        return JsonResponse({'error': 'Vous commentez trop rapidement. Réessayez dans quelques instants.'}, status=429)

    if kind == 'article':
        Commentaire.objects.create(
            article=target,
            auteur=request.user,
            texte=texte,
            approuve=False,
        )
        approved_count = target.nombre_commentaires()
    else:
        content_type = ContentType.objects.get_for_model(target, for_concrete_model=False)
        HomeFeedComment.objects.create(
            content_type=content_type,
            object_id=target.pk,
            auteur=request.user,
            texte=texte,
            approuve=False,
        )
        approved_count = HomeFeedComment.objects.filter(
            content_type=content_type,
            object_id=target.pk,
            approuve=True,
        ).count()

    return JsonResponse({
        'success': True,
        'message': 'Merci ! Votre commentaire est en attente de modération.',
        'count': approved_count,
    }, status=201)


def accueil(request):
    """Vue de la page d'accueil."""
    context = {
        'slides': SlideCarousel.objects.filter(actif=True).order_by('ordre'),
        'feed_page': _home_feed(request),
    }
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.GET.get('feed_cursor'):
        return HttpResponse(render_to_string(
            'core/includes/fil_actualites_items.html',
            {'feed_page': context['feed_page']},
            request=request,
        ))
    return render(request, 'core/accueil.html', context)


# ─────────────────────────────────────────
# RECHERCHE GLOBALE INSTANTANÉE (API AJAX)
# ─────────────────────────────────────────
def recherche_globale(request):
    """Recherche en direct multi-modèles pour la modale Ctrl+K."""
    from django.http import JsonResponse
    q = request.GET.get('q', '').strip()
    if not q or len(q) < 2:
        return JsonResponse({'query': q, 'results': [], 'count': 0})

    results = []

    # 1. Prédications
    for p in Predication.objects.filter(
        Q(titre__icontains=q) | Q(predicateur__icontains=q) | Q(description__icontains=q),
        publie=True
    ).order_by('-date_publication')[:5]:
        results.append({
            'category': 'Prédications',
            'title': p.titre,
            'subtitle': f"Par {p.predicateur}" if p.predicateur else "Prédication",
            'url': f"/predications/{p.slug}/",
            'icon': 'fa-solid fa-microphone',
            'badge': 'Prédication'
        })

    # 2. Actualités
    for a in Article.objects.filter(
        Q(titre__icontains=q) | Q(resume__icontains=q),
        statut='publie'
    ).order_by('-date_publication')[:5]:
        results.append({
            'category': 'Actualités',
            'title': a.titre,
            'subtitle': (a.resume[:90] + '...') if a.resume else "Actualité",
            'url': f"/actualites/{a.slug}/",
            'icon': 'fa-solid fa-newspaper',
            'badge': 'Actualité'
        })

    # 3. Événements
    for e in Evenement.objects.filter(
        Q(titre__icontains=q) | Q(lieu__icontains=q),
        publie=True
    ).order_by('-date_debut')[:4]:
        results.append({
            'category': 'Événements',
            'title': e.titre,
            'subtitle': f"Lieu : {e.lieu}" if e.lieu else "Événement",
            'url': f"/evenements/{e.slug}/",
            'icon': 'fa-solid fa-calendar-days',
            'badge': 'Événement'
        })

    # 4. Cultes
    for c in Culte.objects.filter(
        Q(titre__icontains=q) | Q(description__icontains=q),
        actif=True
    ).order_by('ordre')[:3]:
        heure_txt = c.get_heure_display() if hasattr(c, 'get_heure_display') else f"{c.heure_debut}"
        results.append({
            'category': 'Cultes',
            'title': c.titre,
            'subtitle': f"{c.get_jour_display()} ({heure_txt})",
            'url': '/cultes/',
            'icon': 'fa-solid fa-church',
            'badge': 'Culte'
        })


    return JsonResponse({'query': q, 'results': results, 'count': len(results)})


# ─────────────────────────────────────────
# DONS & OFFRANDES
# ─────────────────────────────────────────
def dons(request):
    """Page de dons et offrandes (Mobile Money & Comptes bancaires)."""
    moyens_dons = MoyenDon.objects.filter(
        actif=True,
        coordonnees_verifiees=True,
    ).order_by('ordre', 'nom')
    parametres = ParametreSite.objects.filter(pk=1).only('whatsapp').first()
    whatsapp_number = re.sub(r'\D', '', parametres.whatsapp) if parametres and parametres.whatsapp else ''
    if not 8 <= len(whatsapp_number) <= 15:
        whatsapp_number = ''

    return render(request, 'core/dons.html', {
        'moyens_dons': moyens_dons,
        'whatsapp_number': whatsapp_number,
    })


# ─────────────────────────────────────────
# PWA — Page offline & Service Worker
# ─────────────────────────────────────────
def offline(request):
    """Page affichée par le service worker quand l'utilisateur est hors ligne."""
    return render(request, 'offline.html')


def service_worker(request):
    """Sert le service worker avec headers optimisés pour les mises à jour PWA."""
    sw_path = os.path.join(settings.BASE_DIR, 'static', 'js', 'sw.js')
    if os.path.exists(sw_path):
        response = FileResponse(open(sw_path, 'rb'), content_type='application/javascript')
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Service-Worker-Allowed'] = '/'
        return response
    return HttpResponseNotFound("Service worker non trouvé")


def manifest_json(request):
    """Sert le manifest de la PWA."""
    manifest_path = os.path.join(settings.BASE_DIR, 'static', 'manifest.json')
    if os.path.exists(manifest_path):
        response = FileResponse(open(manifest_path, 'rb'), content_type='application/manifest+json')
        response['Cache-Control'] = 'public, max-age=86400'
        return response
    return HttpResponseNotFound("Manifest non trouvé")


# ─────────────────────────────────────────
# SEO — robots.txt
# ─────────────────────────────────────────
def robots_txt(request):
    """Fichier robots.txt pour les moteurs de recherche."""
    content = """User-agent: *
Allow: /
Disallow: /admin/
Disallow: /connexion/
Disallow: /inscription/
Disallow: /deconnexion/
Disallow: /ckeditor/
Disallow: /profil/

Sitemap: {scheme}://{host}/sitemap.xml
""".format(
        scheme='https' if request.is_secure() else 'http',
        host=request.get_host()
    )
    return HttpResponse(content, content_type='text/plain; charset=utf-8')


# ─────────────────────────────────────────
# SEO — sitemap.xml
# ─────────────────────────────────────────
def sitemap_xml(request):
    """Sitemap XML généré dynamiquement."""
    from apps.articles.models import Article
    from apps.evenements.models import Evenement
    from apps.predications.models import Predication

    scheme = 'https' if request.is_secure() else 'http'
    host = request.get_host()
    base = f"{scheme}://{host}"

    urls = []

    # Pages statiques
    static_pages = [
        ('/', '1.0', 'daily'),
        ('/actualites/', '0.9', 'daily'),
        ('/predications/', '0.9', 'weekly'),
        ('/evenements/', '0.9', 'weekly'),
        ('/galerie/', '0.8', 'weekly'),
        ('/cultes/', '0.8', 'monthly'),
        ('/notre-histoire/', '0.7', 'monthly'),
        ('/ministeres/', '0.7', 'monthly'),
        ('/priere/', '0.8', 'weekly'),
    ]
    for loc, priority, freq in static_pages:
        urls.append(f"""
  <url>
    <loc>{base}{loc}</loc>
    <changefreq>{freq}</changefreq>
    <priority>{priority}</priority>
  </url>""")

    # Articles publiés
    for article in Article.objects.filter(statut='publie').only('slug', 'date_modification'):
        urls.append(f"""
  <url>
    <loc>{base}/actualites/{article.slug}/</loc>
    <lastmod>{article.date_modification.strftime('%Y-%m-%d')}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.6</priority>
  </url>""")

    # Prédications publiées
    for pred in Predication.objects.filter(publie=True).only('slug', 'date_publication'):
        date_str = pred.date_publication.strftime('%Y-%m-%d') if pred.date_publication else ''
        urls.append(f"""
  <url>
    <loc>{base}/predications/{pred.slug}/</loc>
    {'<lastmod>' + date_str + '</lastmod>' if date_str else ''}
    <changefreq>monthly</changefreq>
    <priority>0.6</priority>
  </url>""")

    # Événements publiés
    for evt in Evenement.objects.filter(publie=True).only('slug', 'date_debut'):
        urls.append(f"""
  <url>
    <loc>{base}/evenements/{evt.slug}/</loc>
    <lastmod>{evt.date_debut.strftime('%Y-%m-%d')}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.7</priority>
  </url>""")

    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    xml += ''.join(urls)
    xml += '\n</urlset>'

    return HttpResponse(xml, content_type='application/xml; charset=utf-8')


# ─────────────────────────────────────────
# Gestionnaires d'erreurs personnalisés
# ─────────────────────────────────────────
def handler400(request, exception=None):
    return render(request, '404.html', status=400)


def handler403(request, exception=None):
    return render(request, '403.html', status=403)


def handler404(request, exception=None):
    return render(request, '404.html', status=404)


def handler500(request):
    return render(request, '500.html', status=500)
