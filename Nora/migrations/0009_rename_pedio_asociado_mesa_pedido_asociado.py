# Generated by Django 5.1.4 on 2025-02-18 16:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Nora', '0008_mesa_estado_mesa_mesa_pedio_asociado'),
    ]

    operations = [
        migrations.RenameField(
            model_name='mesa',
            old_name='pedio_asociado',
            new_name='pedido_asociado',
        ),
    ]
