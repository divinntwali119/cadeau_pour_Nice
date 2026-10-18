"""Vues — App Articles (Actualités)"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.paginator import Paginator
from .models import Article, CategorieArticle, Commentaire, Like


def liste_articles(request):
    """Liste paginée des articles publiés, avec filtre par catégorie."""
    categorie_slug = request.GET.get('categorie')
    articles_list = Article.objects.filter(statut='publie').order_by('-date_publication')
    categorie_active = None

    if categorie_slug:
        categorie_active = get_object_or_404(CategorieArticle, slug=categorie_slug)
        articles_list = articles_list.filter(categorie=categorie_active)

    paginator = Paginator(articles_list, 9)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'articles/liste.html', {
        'page_obj': page_obj,
        'categories': CategorieArticle.objects.all(),
        'categorie_active': categorie_active,
    })


def detail_article(request, slug):
    """Détail d'un article avec gestion des commentaires et comptage de vues."""
    article = get_object_or_404(Article, slug=slug, statut='publie')

    # Incrémenter les vues une seule fois par session
    session_key = f'viewed_article_{article.pk}'
    if not request.session.get(session_key, False):
        article.vues += 1
        article.save(update_fields=['vues'])
        request.session[session_key] = True

    commentaires = article.commentaires.filter(approuve=True).order_by('-date_creation')
    articles_similaires = Article.objects.filter(
        statut='publie', categorie=article.categorie
    ).exclude(pk=article.pk).order_by('-date_publication')[:3]

    # Vérifier si l'utilisateur a déjà liké
    utilisateur_a_like = False
    if request.user.is_authenticated:
        utilisateur_a_like = Like.objects.filter(article=article, utilisateur=request.user).exists()

    # Traitement du formulaire de commentaire
    if request.method == 'POST' and request.user.is_authenticated:
        from apps.core.security import is_rate_limited
        from django.contrib import messages

        if is_rate_limited(request, key_prefix='comment', limit=5, period=120):
            messages.warning(request, "⏳ Vous commentez trop rapidement. Veuillez patienter deux minutes.")
            return redirect('articles:detail', slug=slug)

        texte = request.POST.get('texte', '').strip()
        if texte:
            Commentaire.objects.create(
                article=article,
                auteur=request.user,
                texte=texte,
                approuve=False  # En attente de modération
            )
            messages.success(request, 'Merci pour votre commentaire ! Il sera visible après modération.')
            return redirect('articles:detail', slug=slug)

    return render(request, 'articles/detail.html', {
        'article': article,
        'commentaires': commentaires,
        'articles_similaires': articles_similaires,
        'utilisateur_a_like': utilisateur_a_like,
    })


@login_required
def toggle_like(request, slug):
    """Ajouter ou retirer un like (requête AJAX)."""
    if request.method == 'POST':
        article = get_object_or_404(Article, slug=slug)
        like, created = Like.objects.get_or_create(article=article, utilisateur=request.user)
        if not created:
            like.delete()
            action = 'unlike'
        else:
            action = 'like'
        return JsonResponse({'action': action, 'count': article.nombre_likes()})
    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)
