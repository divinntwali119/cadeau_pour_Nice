# Patch de compatibilité Python 3.14 pour Django BaseContext.__copy__
# En Python 3.14, copy.copy(super()) retourne un proxy 'super' et non l'instance,
# ce qui casse la copie des Context de template Django.
from django.template import context as _django_context

def _patched_basecontext_copy(self):
    duplicate = object.__new__(self.__class__)
    duplicate.__dict__.update(self.__dict__)
    duplicate.dicts = self.dicts[:]
    return duplicate

_django_context.BaseContext.__copy__ = _patched_basecontext_copy
