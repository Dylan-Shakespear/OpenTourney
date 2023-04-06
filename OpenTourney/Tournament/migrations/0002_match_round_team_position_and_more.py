# Generated by Django 4.1.7 on 2023-04-06 21:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Tournament', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='match',
            name='round',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='team',
            name='position',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='match',
            unique_together={('tournament', 'round')},
        ),
        migrations.AlterUniqueTogether(
            name='team',
            unique_together={('tournament', 'position')},
        ),
    ]
