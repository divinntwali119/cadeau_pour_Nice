from django.db import migrations


def supprimer_coordonnees_de_demo(apps, schema_editor):
    ParametreSite = apps.get_model('core', 'ParametreSite')
    ParametreSite.objects.filter(
        telephone__in=['+243 812 345 678', '+243812345678'],
    ).update(telephone='')
    ParametreSite.objects.filter(email='contact@5celpasmyrne.org').update(email='')


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_moyendon_coordonnees_verifiees'),
    ]

    operations = [
        migrations.RunPython(supprimer_coordonnees_de_demo, migrations.RunPython.noop),
    ]