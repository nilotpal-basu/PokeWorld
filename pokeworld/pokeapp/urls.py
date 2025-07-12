from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
   path("login/", views.user_login, name="login"),
   path("signup/", views.user_signup, name="signup"),
   path("logout/", views.user_logout, name="logout"),
   path("leaderboard/",views.leaderboard_view, name="leaderboard"),
   path('catch/', views.catch_pokemon, name='catch'),
   path('catch/submit/', views.submit_guess, name='submit_guess'),
   path('pokedex/', views.pokedex_upload, name='pokedex_upload'),
   path('pokedex/<str:pokemon_name>/', views.classify_pokemon, name='pokedex_result'),
   path('profile/', views.trainer_profile, name='trainer_profile'),
   path("", views.index, name="index")
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)