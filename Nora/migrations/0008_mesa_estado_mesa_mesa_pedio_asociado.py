# Generated by Django 5.1.4 on 2025-02-17 23:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Nora', '0007_pedido_usuario'),
    ]

    operations = [
        migrations.AddField(
            model_name='mesa',
            name='estado_mesa',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='mesa',
            name='pedio_asociado',
            field=models.IntegerField(null=True),
        ),
    ]
