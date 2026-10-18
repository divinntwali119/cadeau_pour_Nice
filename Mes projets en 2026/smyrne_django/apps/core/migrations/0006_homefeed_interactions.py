from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('core', '0005_remove_contact_placeholders'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='HomeFeedLike',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.PositiveIntegerField()),
                ('date_creation', models.DateTimeField(auto_now_add=True)),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
                ('utilisateur', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='home_feed_likes', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Like du fil d’accueil',
                'verbose_name_plural': 'Likes du fil d’accueil',
            },
        ),
        migrations.CreateModel(
            name='HomeFeedComment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.PositiveIntegerField()),
                ('texte', models.TextField(verbose_name='Commentaire')),
                ('approuve', models.BooleanField(default=False, verbose_name='Approuvé')),
                ('date_creation', models.DateTimeField(auto_now_add=True)),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
                ('auteur', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='home_feed_comments', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Commentaire du fil d’accueil',
                'verbose_name_plural': 'Commentaires du fil d’accueil',
                'ordering': ['-date_creation'],
            },
        ),
        migrations.AddConstraint(
            model_name='homefeedlike',
            constraint=models.UniqueConstraint(fields=('content_type', 'object_id', 'utilisateur'), name='home_feed_like_unique'),
        ),
        migrations.AddIndex(
            model_name='homefeedcomment',
            index=models.Index(fields=['content_type', 'object_id', 'approuve'], name='core_hfc_content_approved_idx'),
        ),
    ]