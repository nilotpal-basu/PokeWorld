# Generated by Django 5.2.4 on 2025-07-04 18:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pokeapp', '0005_pokemon_num_caught'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pokemon',
            name='num_caught',
        ),
    ]
