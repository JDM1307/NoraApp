# Generated by Django 5.1.4 on 2025-02-10 19:36

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Nora', '0004_cierres'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Cierres',
            new_name='Cierre',
        ),
    ]
