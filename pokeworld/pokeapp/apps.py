from django.apps import AppConfig


class PokeappConfig(AppConfig):
    default_auto_field = 'django_mongodb_backend.fields.ObjectIdAutoField'
    name = 'pokeapp'
