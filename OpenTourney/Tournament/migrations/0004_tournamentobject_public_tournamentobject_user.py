# Generated by Django 4.1.7 on 2023-04-11 16:03

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Tournament', '0003_alter_match_date_alter_match_description_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='tournamentobject',
            name='public',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='tournamentobject',
            name='user',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tourney', to=settings.AUTH_USER_MODEL),
        ),
    ]