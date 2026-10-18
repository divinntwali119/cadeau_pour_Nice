from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import Predication


def liste_predications(request):
    """Liste paginée des prédications publiées."""
    predications_list = Predication.objects.filter(publie=True).order_by('-date_publication')
    paginator = Paginator(predications_list, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'predications/liste.html', {'page_obj': page_obj})


def detail_predication(request, slug):
    """Détail d'une prédication."""
    predication = get_object_or_404(Predication, slug=slug, publie=True)
    autres = Predication.objects.filter(publie=True).exclude(pk=predication.pk).order_by('-date_publication')[:3]
    return render(request, 'predications/detail.html', {
        'predication': predication,
        'autres': autres,
        'embed_url': predication.get_embed_url() if predication.video_url else None,
    })
