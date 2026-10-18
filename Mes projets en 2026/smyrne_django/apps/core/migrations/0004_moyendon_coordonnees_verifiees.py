from django.db import migrations, models


def supprimer_whatsapp_de_demo(apps, schema_editor):
    ParametreSite = apps.get_model('core', 'ParametreSite')
    ParametreSite.objects.filter(whatsapp__in=['+243812345678', '243812345678']).update(whatsapp='')


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_moyendon_logo'),
    ]

    operations = [
        migrations.AddField(
            model_name='moyendon',
            name='coordonnees_verifiees',
            field=models.BooleanField(
                default=False,
                help_text="N'afficher ce moyen de paiement qu'après confirmation du numéro ou compte par l'église.",
                verbose_name='Coordonnées vérifiées',
            ),
        ),
        migrations.RunPython(supprimer_whatsapp_de_demo, migrations.RunPython.noop),
    ]