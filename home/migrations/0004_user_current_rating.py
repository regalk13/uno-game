# Generated by Django 4.0.2 on 2022-02-12 16:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0003_user_league'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='current_rating',
            field=models.IntegerField(default=500, verbose_name='Current Rating'),
        ),
    ]
